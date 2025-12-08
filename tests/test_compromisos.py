# =============================================================================
# tests/test_compromisos.py — Tests de CompromisosService (BD Real)
# =============================================================================

import pytest
from uuid import uuid4
from datetime import date
from app.services.compromisos_service import CompromisosService
from app.models import (
    CompromisoOperativo,
    TipoCompromisoOperativo,
    Usuario,
    Persona,
    Iniciativa,
    Instrumento,
    HistorialCompromiso,
)


class TestCompromisosService:

    @pytest.fixture
    def setup_data(self, db_session):
        """Fixture crea dependencias complejas."""
        # 1. Persona y Usuario
        unique_suffix = str(uuid4())[:4]
        persona_id = uuid4()
        persona = Persona(
            id=persona_id,
            rut=f"99{unique_suffix}-K",
            nombres="Jefe",
            apellido_paterno="Division",
            email=f"jefe.{unique_suffix}@gore.cl",
        )
        db_session.add(persona)

        user_id = uuid4()
        usuario = Usuario(
            id=user_id,
            persona_id=persona_id,
            username="jefe_div",
            rol_crisis="JEFE_DIVISION",
        )
        db_session.add(usuario)

        # 2. Instrumento e Iniciativa
        inst = Instrumento(id=uuid4(), codigo="FNDR-02", nombre="FNDR CULTURA")
        db_session.add(inst)

        ipr = Iniciativa(
            id=uuid4(),
            codigo_interno="IPR-COMPROMISO",
            nombre="IPR Test Comp",
            instrumento_id=inst.id,
            anio_presupuestario=2025,
            estado_fsm_id=uuid4(),
        )
        db_session.add(ipr)

        # 3. Tipo Compromiso
        tipo = TipoCompromisoOperativo(
            id=uuid4(), codigo="ADMI", nombre="Gestion Administrativa", activo=True
        )
        db_session.add(tipo)

        db_session.commit()

        return {"usuario": usuario, "iniciativa": ipr, "tipo": tipo}

    def test_crear_compromiso_exito(self, db_session, setup_data):
        """Test: Crear compromiso correctamente."""
        user = setup_data["usuario"]
        tipo = setup_data["tipo"]
        ipr = setup_data["iniciativa"]

        data = {
            "tipo_id": str(tipo.id),
            "descripcion": "Test compromiso real",
            "responsable_id": str(user.id),
            "fecha_limite": "2023-12-31",
            "prioridad": "ALTA",
            "iniciativa_id": str(ipr.id),
            "problema_id": "",
        }

        compromiso = CompromisosService.crear_compromiso(data, user.id)

        assert compromiso.descripcion == "Test compromiso real"
        assert compromiso.prioridad == "ALTA"
        assert compromiso.estado == "PENDIENTE"

        # Validar persistencia
        c_db = db_session.get(CompromisoOperativo, compromiso.id)
        assert c_db is not None
        assert c_db.creado_por_id == user.id

    def test_completar_compromiso(self, db_session, setup_data):
        """Test: Completar compromiso actualiza estado y crea historial."""
        user = setup_data["usuario"]
        tipo = setup_data["tipo"]

        # Crear compromiso inicial
        comp = CompromisoOperativo(
            id=uuid4(),
            tipo_id=tipo.id,
            descripcion="Para completar",
            fecha_limite=date(2025, 12, 31),
            prioridad="MEDIA",
            estado="PENDIENTE",
            creado_por_id=user.id,
            responsable_id=user.id,
        )
        db_session.add(comp)
        db_session.commit()

        # Completar
        result = CompromisosService.completar_compromiso(
            comp.id, "Realizado ok", user.id
        )

        assert result.estado == "COMPLETADO"
        assert result.observaciones == "Realizado ok"

        # Verificar historial
        assert result.historial.count() > 0
        ultimo_hist = result.historial.order_by(
            HistorialCompromiso.created_at.desc()
        ).first()
        assert ultimo_hist.estado_nuevo == "COMPLETADO"

    def test_verificar_compromiso_error_no_completado(self, db_session, setup_data):
        """Test: Error al verificar compromiso no completado."""
        user = setup_data["usuario"]
        tipo = setup_data["tipo"]

        comp = CompromisoOperativo(
            id=uuid4(),
            tipo_id=tipo.id,
            descripcion="Pendiente",
            fecha_limite=date(2025, 12, 31),
            estado="PENDIENTE",
            creado_por_id=user.id,
            responsable_id=user.id,
        )
        db_session.add(comp)
        db_session.commit()

        with pytest.raises(ValueError, match="Solo se pueden verificar"):
            CompromisosService.verificar_compromiso(comp.id, user.id)
