# =============================================================================
# tests/test_problemas.py — Tests Unitarios de Problemas (BD Real)
# =============================================================================

import pytest
from uuid import uuid4
from unittest.mock import MagicMock

# Eliminamos MagicMock/patch en favor de DB real
from app.services.problemas_service import ProblemasService
from app.models import ProblemaIPR, Iniciativa, Usuario, Persona, Instrumento


class TestProblemasService:

    @pytest.fixture
    def setup_data(self, db_session):
        """Fixture crea dependencias complejas."""
        # 1. Persona y Usuario
        persona_id = uuid4()
        persona = Persona(
            id=persona_id,
            rut="22222222-2",
            nombres="Analista",
            apellido_paterno="Problematico",
            email="analista@gore.cl",
        )
        db_session.add(persona)

        user_id = uuid4()
        usuario = Usuario(
            id=user_id,
            persona_id=persona_id,
            username="analista",
            rol_crisis="ENCARGADO_OPERATIVO",
        )
        db_session.add(usuario)

        # 2. Instrumento e Iniciativa
        inst = Instrumento(id=uuid4(), codigo="FNDR-03", nombre="FNDR DEPORTES")
        db_session.add(inst)

        ipr = Iniciativa(
            id=uuid4(),
            codigo_interno="IPR-PROBLEMA",
            nombre="IPR Test Prob",
            instrumento_id=inst.id,
            anio_presupuestario=2025,
            estado_fsm_id=uuid4(),
        )
        db_session.add(ipr)

        db_session.commit()

        return {"usuario": usuario, "iniciativa": ipr}

    def test_crear_problema_exito(self, db_session, setup_data):
        """Test: Crear problema correctamente."""
        user = setup_data["usuario"]
        ipr = setup_data["iniciativa"]

        data = {
            "iniciativa_id": str(ipr.id),
            "convenio_id": "",  # Opcional
            "tipo": "TECNICO",
            "impacto": "RETRASA_OBRA",
            "descripcion": "Falla estructural",
        }

        problema = ProblemasService.crear_problema(data, user.id)

        assert problema.descripcion == "Falla estructural"
        assert problema.estado == "ABIERTO"

        # Validar persistencia
        p_db = db_session.get(ProblemaIPR, problema.id)
        assert p_db is not None
        assert p_db.detectado_por_id == user.id

    def test_resolver_problema(self, db_session, setup_data):
        """Test: Resolver problema."""
        user = setup_data["usuario"]
        ipr = setup_data["iniciativa"]

        # Crear problema inicial
        prob = ProblemaIPR(
            id=uuid4(),
            iniciativa_id=ipr.id,
            tipo="ADMINISTRATIVO",
            impacto="DETIENE_PAGO",
            descripcion="Falta firma",
            detectado_por_id=user.id,
            estado="ABIERTO",
        )
        db_session.add(prob)
        db_session.commit()

        result = ProblemasService.resolver_problema(prob.id, "Reparado", user.id)

        assert result.estado == "RESUELTO"
        assert result.solucion_aplicada == "Reparado"
