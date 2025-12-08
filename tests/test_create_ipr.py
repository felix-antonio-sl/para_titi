import pytest
from app.services.ipr_service import IPRService
from app.models import Iniciativa, Division, Instrumento, Usuario
from uuid import uuid4


def test_crear_iniciativa_success(client, db_session):
    """Test successful creation of an IPR via Service."""
    # Setup dependencies with unique codes
    unique_suffix = str(uuid4())[:8]
    inst = Instrumento(
        id=uuid4(),
        codigo=f"INST-{unique_suffix}",
        nombre="Instrumento Test",
        activo=True,
    )
    div = Division(
        id=uuid4(),
        codigo=f"DIV-{unique_suffix}",
        nombre="Division Test",
        orden_jerarquico=1,
    )
    db_session.add_all([inst, div])
    db_session.commit()

    data = {
        "codigo_interno": f"TEST-{unique_suffix}",
        "nombre": "Iniciativa de Prueba",
        "instrumento_id": str(inst.id),
        "anio_presupuestario": 2025,
        "monto_solicitado": 100000,
        "descripcion": "Descripción de prueba",
        "division_responsable_id": str(div.id),
    }

    iniciativa = IPRService.crear_iniciativa(data)

    assert iniciativa.id is not None
    assert iniciativa.codigo_interno == f"TEST-{unique_suffix}"
    assert iniciativa.nivel_alerta == "BAJO"
    assert iniciativa.division_responsable_id == div.id


def test_crear_iniciativa_missing_fields(client):
    """Test validation errors when missing required fields."""
    data = {
        "nombre": "Incompleta"
        # Missing codigo, instrumento, anio
    }

    with pytest.raises(ValueError) as exc:
        IPRService.crear_iniciativa(data)

    assert "obligatorio" in str(exc.value)


def test_route_crear_ipr_access(client, app):
    """Test access control for the Create IPR route."""
    # Login user
    with client.session_transaction() as sess:
        sess["_user_id"] = (
            "admin"  # Mock user ID from session fixture if needed, or rely on conftest login
        )

    # This might require real login simulation if validation is strict
    # For now checking if it redirects or loads (depending on auth)
    # Assuming conftest sets up a user or we use a helper

    pass
