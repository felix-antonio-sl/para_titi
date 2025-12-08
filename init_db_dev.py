from app import create_app, db
from sqlalchemy import text
from app.models import *  # Force registration

app = create_app()

with app.app_context():
    print("Initialize DB for Development...")

    # Schemas from conftest.py
    schemas = [
        "gore_financiero",
        "gore_inversion",
        "gore_actores",
        "gore_autenticacion",
        "gore_ejecucion",
        "gore_normativo",
        "gore_instancias",
        "gore_organizacion",
    ]

    with db.session.begin():
        for schema in schemas:
            print(f"Creating schema {schema}...")
            db.session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))

    print("Creating tables...")
    db.create_all()
    print("DONE. Database ready for use.")
