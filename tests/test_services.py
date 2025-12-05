# =============================================================================
# tests/test_services.py — Tests de IPRService (BD Real)
# =============================================================================

import pytest
from uuid import uuid4
from datetime import date
from app.services.ipr_service import IPRService
from app.models import Iniciativa, Usuario, Persona, Convenio, Instrumento, Entidad


class TestIPRService:

    @pytest.fixture
    def user(self, db_session):
        """Fixture para crear un usuario completo con persona."""
        persona_id = uuid4()
        persona = Persona(
            id=persona_id,
            rut="12345678-9",
            nombres="Test",
            apellido_paterno="User",
            email="test@gore.cl",
        )
        db_session.add(persona)

        user_id = uuid4()
        # Nota: Usuario no tiene email, Persona si.
        usuario = Usuario(
            id=user_id,
            persona_id=persona_id,
            username="testuser",
            rol_crisis="ADMIN_SISTEMA",
        )
        db_session.add(usuario)
        db_session.commit()
        return usuario

    @pytest.fixture
    def instrumento(self, db_session):
        inst_id = uuid4()
        inst = Instrumento(
            id=inst_id,
            codigo="FNDR-01",
            nombre="Fondo Nacional Desarrollo Regional",
            activo=True,
        )
        db_session.add(inst)
        db_session.commit()
        return inst

    @pytest.fixture
    def entidad(self, db_session):
        ent_id = uuid4()
        ent = Entidad(
            id=ent_id,
            rut="60.111.222-3",
            nombre="Municipalidad de Test",
            tipo="MUNICIPALIDAD",
        )
        db_session.add(ent)
        db_session.commit()
        return ent

    def test_asignar_responsable_exito(self, db_session, user, instrumento):
        """Test: Asignar responsable correctamente."""
        ipr_id = uuid4()
        ipr = Iniciativa(
            id=ipr_id,
            codigo_interno="TEST-01",
            nombre="IPR Test",
            instrumento_id=instrumento.id,
            anio_presupuestario=2025,
            estado_fsm_id=uuid4(),  # Asumimos UUID valido
        )
        db_session.add(ipr)
        db_session.commit()

        # Ejecutar servicio
        result = IPRService.asignar_responsable(ipr.id, user.id)

        assert result.responsable_id == user.id

        # Validar en DB
        ipr_actualizada = db_session.get(Iniciativa, ipr_id)
        assert ipr_actualizada.responsable_id == user.id

    def test_asignar_responsable_ipr_no_existe(self, db_session):
        """Test: Error al asignar si IPR no existe."""
        with pytest.raises(ValueError, match="no encontrada"):
            IPRService.asignar_responsable(uuid4(), uuid4())

    def test_registrar_avance_exito(self, db_session, user, instrumento, entidad):
        """Test: Registrar informe de avance correctamente."""
        # Creacion Iniciativa
        ipr_id = uuid4()
        ipr = Iniciativa(
            id=ipr_id,
            codigo_interno="TEST-02",
            nombre="IPR Avance",
            instrumento_id=instrumento.id,
            anio_presupuestario=2025,
            estado_fsm_id=uuid4(),
        )
        db_session.add(ipr)

        # Creacion Convenio
        convenio_id = uuid4()
        convenio = Convenio(
            id=convenio_id,
            iniciativa_id=ipr_id,
            numero_resolucion="RES-001",
            fecha_inicio=date(2025, 1, 1),
            fecha_termino=date(2025, 12, 31),
            monto_total=1000000,
            entidad_ejecutora_id=entidad.id,
        )
        db_session.add(convenio)
        db_session.commit()

        data = {
            "convenio_id": str(convenio_id),
            "numero": "1",
            "periodo_desde": "2023-01-01",
            "periodo_hasta": "2023-01-31",
            "resumen": "Test resumen",
            "avance_fisico": "50.5",
            "avance_financiero": "10.0",
        }

        informe = IPRService.registrar_avance(ipr.id, data, user.id)

        assert informe.numero == 1
        assert ipr.avance_fisico == 50.5
        assert ipr.avance_financiero == 10.0

    def test_registrar_avance_datos_invalidos(self, db_session, instrumento):
        """Test: Error con datos incompletos."""
        ipr_id = uuid4()
        ipr = Iniciativa(
            id=ipr_id,
            codigo_interno="TEST-03",
            nombre="IPR Fail",
            instrumento_id=instrumento.id,
            anio_presupuestario=2025,
            estado_fsm_id=uuid4(),
        )
        db_session.add(ipr)
        db_session.commit()

        data_invalida = {"solo_esto": "nada mas"}

        with pytest.raises(ValueError, match="Datos inválidos"):
            IPRService.registrar_avance(ipr.id, data_invalida, uuid4())
