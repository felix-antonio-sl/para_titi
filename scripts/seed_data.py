# scripts/seed_data.py
from app import create_app, db
from app.models import Division, Instrumento, TipoCompromisoOperativo
from uuid import uuid4


def seed_catalogs():
    """Populate essential catalogs for development."""
    print("Seeding catalogs...")

    # 1. Divisiones
    divisions = [
        {"codigo": "GOB", "nombre": "Gobernador Regional", "orden": 1},
        {"codigo": "ADMR", "nombre": "Administración Regional", "orden": 2},
        {"codigo": "DIPIR", "nombre": "Div. Planificación y Des. Regional", "orden": 3},
        {"codigo": "DIDESOH", "nombre": "Div. Desarrollo Social y Humano", "orden": 4},
        {"codigo": "DAF", "nombre": "Div. Administración y Finanzas", "orden": 5},
        {
            "codigo": "DIPLADE",
            "nombre": "Div. Infraestructura y Transporte",
            "orden": 6,
        },
        {"codigo": "DFI", "nombre": "Div. Fomento e Industria", "orden": 7},
    ]

    for div_data in divisions:
        if not Division.query.filter_by(codigo=div_data["codigo"]).first():
            div = Division(
                id=uuid4(),
                codigo=div_data["codigo"],
                nombre=div_data["nombre"],
                orden_jerarquico=div_data["orden"],
            )
            db.session.add(div)
            print(f"+ Division: {div_data['nombre']}")

    # 2. Instrumentos (Financial sources)
    instrumentos = [
        {"codigo": "FNDR", "nombre": "Fondo Nacional de Desarrollo Regional"},
        {"codigo": "FIC", "nombre": "Fondo de Innovación para la Competitividad"},
        {"codigo": "PMU", "nombre": "Programa Mejoramiento Urbano"},
        {"codigo": "FRIL", "nombre": "Fondo Regional de Iniciativa Local"},
    ]

    for inst_data in instrumentos:
        if not Instrumento.query.filter_by(codigo=inst_data["codigo"]).first():
            inst = Instrumento(
                id=uuid4(),
                codigo=inst_data["codigo"],
                nombre=inst_data["nombre"],
                activo=True,
            )
            db.session.add(inst)
            print(f"+ Instrumento: {inst_data['nombre']}")

    # 3. Tipos de Compromiso
    tipos_comp = [
        {"codigo": "GESTION", "nombre": "Gestión Administrativa"},
        {"codigo": "TERRENO", "nombre": "Visita a Terreno"},
        {"codigo": "REUNION", "nombre": "Reunión de Coordinación"},
        {"codigo": "OFICIO", "nombre": "Elaboración de Oficio"},
        {"codigo": "OTROS", "nombre": "Otros"},
    ]

    for tipo_data in tipos_comp:
        if not TipoCompromisoOperativo.query.filter_by(
            codigo=tipo_data["codigo"]
        ).first():
            tc = TipoCompromisoOperativo(
                id=uuid4(),
                codigo=tipo_data["codigo"],
                nombre=tipo_data["nombre"],
                activo=True,
            )
            db.session.add(tc)
            print(f"+ Tipo Compromiso: {tipo_data['nombre']}")

    db.session.commit()
    print("Catalogs seeding completed.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_catalogs()
