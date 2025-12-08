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

    print(" Applying Mock SQL Functions...")
    try:
        with open("scripts/mock_db_functions.sql", "r") as f:
            sql_script = f.read()
            # Split by statement if needed, or execute block if simple
            db.session.execute(text(sql_script))
            db.session.commit()
            print("✓ Mock functions applied.")
    except FileNotFoundError:
        print("! Warning: scripts/mock_db_functions.sql not found.")
    except Exception as e:
        print(f"Error applying SQL mocks: {e}")
        db.session.rollback()

    print(" Seeding Catalogs...")
    try:
        from scripts.seed_data import seed_catalogs

        seed_catalogs()
    except Exception as e:
        print(f"Error seeding data: {e}")

    print("DONE. Database ready for use.")
