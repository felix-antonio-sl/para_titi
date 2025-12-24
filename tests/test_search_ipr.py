# =============================================================================
# tests/test_search_ipr.py — Tests de Búsqueda Avanzada
# =============================================================================

import pytest
from uuid import uuid4
from app.models import Iniciativa, Usuario, Persona, Instrumento


class TestIPRSearch:

    @pytest.fixture
    def setup_data(self, db_session):
        """Crea usuario y datos base para búsqueda."""
        # Usuario Admin
        persona_id = uuid4()
        persona = Persona(
            id=persona_id,
            rut="11111111-1",
            nombres="Admin",
            apellido_paterno="Search",
            email="search@gore.cl",
        )
        db_session.add(persona)

        user_id = uuid4()
        usuario = Usuario(
            id=user_id,
            persona_id=persona_id,
            username="admin_search",
            rol_crisis="ADMIN_SISTEMA",
        )
        db_session.add(usuario)

        # Instrumentos
        inst_fndr = Instrumento(id=uuid4(), codigo="FNDR", nombre="Fondo Nacional")
        inst_fic = Instrumento(id=uuid4(), codigo="FIC", nombre="Fondo Innovacion")
        db_session.add(inst_fndr)
        db_session.add(inst_fic)

        # IPRs para probar búsqueda
        # 1. Coincidencia por nombre parcial
        ipr1 = Iniciativa(
            id=uuid4(),
            codigo_interno="IPR-001",
            nombre="Construcción Puente Rio Ñuble",
            descripcion="Obras civiles mayores en puente.",
            instrumento_id=inst_fndr.id,
            anio_presupuestario=2025,
            estado_fsm_id=uuid4(),
        )

        # 2. Coincidencia por descripción
        ipr2 = Iniciativa(
            id=uuid4(),
            codigo_interno="IPR-002",
            nombre="Mejoramiento Vial Chillán",
            descripcion="Incluye pavimentación acceso puente y señalética.",
            instrumento_id=inst_fndr.id,
            anio_presupuestario=2025,
            estado_fsm_id=uuid4(),
        )

        # 3. Coincidencia por código interno
        ipr3 = Iniciativa(
            id=uuid4(),
            codigo_interno="IPR-BIP-TEST",
            nombre="Capacitación Emprendedores",
            descripcion="Programa de fomento productivo.",
            instrumento_id=inst_fic.id,
            anio_presupuestario=2025,
            estado_fsm_id=uuid4(),
        )

        db_session.add(ipr1)
        db_session.add(ipr2)
        db_session.add(ipr3)

        db_session.commit()
        return {
            "usuario": usuario,
            "ipr1": ipr1,
            "ipr2": ipr2,
            "ipr3": ipr3,
            "fndr": inst_fndr,
        }

    def test_search_multi_term(self, client, setup_data):
        """Test: Búsqueda con múltiples términos (AND)."""
        user = setup_data["usuario"]
        with client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)

        # "puente" debería traer ipr1 (nombre) y ipr2 (descripción)
        response = client.get("/ipr/?q=puente")
        assert response.status_code == 200
        assert (
            b"Construcci\xc3\xb3n Puente Rio" in response.data
            or "Construcción Puente Rio".encode("utf-8") in response.data
        )
        assert b"Mejoramiento Vial Chill" in response.data

        # "puente nuble" -> Solo ipr1
        response = client.get("/ipr/?q=puente+nuble")
        assert response.status_code == 200
        assert b"Construcci\xc3\xb3n Puente Rio" in response.data
        assert b"Mejoramiento Vial Chill" not in response.data

        # "pavimentacion" -> ipr2
        response = client.get("/ipr/?q=pavimentacion")
        assert response.status_code == 200
        assert b"Mejoramiento Vial Chill" in response.data

    def test_filter_instrumento(self, client, setup_data):
        """Test: Filtro por instrumento."""
        user = setup_data["usuario"]
        with client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)

        fndr_id = str(setup_data["fndr"].id)

        # Filtrar por FNDR (ipr1 y ipr2)
        response = client.get(f"/ipr/?instrumento={fndr_id}")
        assert response.status_code == 200
        assert b"IPR-001" in response.data
        assert b"IPR-002" in response.data
        assert b"IPR-003" not in response.data
