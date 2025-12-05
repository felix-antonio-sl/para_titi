# =============================================================================
# tests/test_routes.py — Tests de Integración (Rutas con DB Real)
# =============================================================================

import pytest
from uuid import uuid4
from app.models import Iniciativa, Usuario, Persona, Instrumento


class TestIPRRoutes:

    @pytest.fixture
    def setup_data(self, db_session):
        """Crea usuario y datos base."""
        # Usuario
        persona_id = uuid4()
        persona = Persona(
            id=persona_id,
            rut="99999999-9",
            nombres="Admin",
            apellido_paterno="System",
            email="admin@gore.cl",
        )
        db_session.add(persona)

        user_id = uuid4()
        usuario = Usuario(
            id=user_id,
            persona_id=persona_id,
            username="admin_sys",
            rol_crisis="ADMIN_SISTEMA",
        )
        db_session.add(usuario)

        # Instrumento e IPR
        inst = Instrumento(id=uuid4(), codigo="FNDR-ROUTE", nombre="FNDR ROUTE TEST")
        db_session.add(inst)

        ipr = Iniciativa(
            id=uuid4(),
            codigo_interno="IPR-ROUTE-01",
            nombre="Iniciativa Route Test",
            instrumento_id=inst.id,
            anio_presupuestario=2025,
            estado_fsm_id=uuid4(),
        )
        db_session.add(ipr)

        db_session.commit()
        return {"usuario": usuario, "iniciativa": ipr}

    def test_lista_ipr(self, client, setup_data):
        """Test: Endpoint /ipr/ carga correctamente con datos reales."""
        user = setup_data["usuario"]

        # Login
        with client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)

        response = client.get("/ipr/")

        assert response.status_code == 200
        assert b"Iniciativa Route Test" in response.data

    def test_asignar_responsable_post(self, client, db_session, setup_data):
        """Test: Asignar responsable via POST real."""
        user = setup_data["usuario"]
        ipr = setup_data["iniciativa"]

        # Login
        with client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)

        # Nuevo responsable
        resp_persona_id = uuid4()
        resp_persona = Persona(
            id=resp_persona_id,
            rut="88888888-8",
            nombres="Nuevo",
            apellido_paterno="Responsable",
            email="nuevo@gore.cl",
        )
        db_session.add(resp_persona)

        resp_user_id = uuid4()
        resp_user = Usuario(
            id=resp_user_id,
            persona_id=resp_persona_id,
            username="nuevo_resp",
            rol_crisis="ENCARGADO_OPERATIVO",
        )
        # El usuario asignado debe ser encargado? o cualquiera.
        db_session.add(resp_user)
        db_session.commit()

        response = client.post(
            f"/ipr/{ipr.id}/asignar-responsable",
            data={"responsable_id": str(resp_user.id)},
        )

        assert response.status_code == 200  # HTMX retorna fragmento o 200

        # Validar cambio en DB
        db_session.expire(ipr)
        assert ipr.responsable_id == resp_user.id
