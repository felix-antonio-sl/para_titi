# =============================================================================
# scripts/etl_funcionarios.py — ETL para cargar funcionarios desde CSV
# =============================================================================
#
# Uso:
#   docker compose -f docker-compose.dev.yml exec app python scripts/etl_funcionarios.py
#
# Fuente: gore_os/etl/sources/funcionarios/listado_funcionarios_integrado_remediado.csv
#

import csv
import uuid
import re
from pathlib import Path

# Ruta al CSV (dentro del contenedor, montado desde scripts/)
CSV_PATH = Path("/home/app/scripts/funcionarios.csv")


def inferir_rol_crisis(cargo: str) -> str:
    """Infiere el rol de crisis basado en el cargo del funcionario."""
    cargo_lower = cargo.lower()

    if "gobernador" in cargo_lower:
        return "ADMIN_SISTEMA"
    elif "administrador" in cargo_lower or "administradora" in cargo_lower:
        return "ADMIN_REGIONAL"
    elif "jefe" in cargo_lower or "jefa" in cargo_lower:
        return "JEFE_DIVISION"
    else:
        return "ENCARGADO_OPERATIVO"


def inferir_division(cargo: str) -> str | None:
    """Infiere la división basada en el cargo."""
    cargo_lower = cargo.lower()

    division_map = {
        "dipir": "DIPIR",
        "presupuesto": "DIPIR",
        "inversión": "DIPIR",
        "inversiones": "DIPIR",
        "preinversión": "DIPIR",
        "dideso": "DIDESOH",
        "desarrollo social": "DIDESOH",
        "difoi": "DIFOI",
        "fomento": "DIFOI",
        "industria": "DIFOI",
        "dit": "DIT",
        "infraestructura": "DIT",
        "transporte": "DIT",
        "daf": "DAF",
        "finanzas": "DAF",
        "administración": "DAF",
        "tesorería": "DAF",
        "diplade": "DIPLADE",
        "planificación": "DIPLADE",
        "desarrollo": "DIPLADE",
        "gabinete": "GAB",
        "comunicaciones": "COM",
        "cies": "CIES",
        "core": "CORE",
        "jurídica": "JUR",
        "auditoría": "AUD",
        "control": "AUD",
    }

    for keyword, division in division_map.items():
        if keyword in cargo_lower:
            return division

    return None


def generar_rut_ficticio(index: int) -> str:
    """Genera un RUT ficticio para desarrollo (no usar en producción)."""
    base = 10000000 + index
    # Calcular dígito verificador (simplificado)
    dv = index % 10
    return f"{base}-{dv}"


def generar_username(nombre_completo: str) -> str:
    """Genera un username a partir del nombre completo."""
    # Formato esperado: "Apellido1 Apellido2, Nombre1 Nombre2"
    partes = nombre_completo.split(",")
    if len(partes) == 2:
        apellidos = partes[0].strip()
        nombres = partes[1].strip()

        # Tomar primer nombre y primer apellido
        primer_nombre = nombres.split()[0].lower() if nombres else "user"
        primer_apellido = apellidos.split()[0].lower() if apellidos else "gore"

        # Limpiar caracteres especiales
        username = f"{primer_nombre}.{primer_apellido}"
        username = re.sub(r"[^a-z.]", "", username)
        return username
    else:
        # Fallback
        return f"user_{uuid.uuid4().hex[:6]}"


def cargar_funcionarios():
    """Carga funcionarios desde CSV a las tablas persona y usuario."""
    from app import create_app, db
    from app.models import Persona, Usuario, Division

    app = create_app()

    with app.app_context():
        print(f"📂 Leyendo CSV: {CSV_PATH}")

        if not CSV_PATH.exists():
            print(f"❌ ERROR: No se encuentra el archivo {CSV_PATH}")
            return

        # Cargar datos existentes para evitar duplicados
        personas_existentes = {p.rut: p for p in Persona.query.all()}
        usuarios_existentes = {u.username: u for u in Usuario.query.all()}
        divisiones = {d.codigo: d for d in Division.query.all()}

        print(f"📊 Personas existentes: {len(personas_existentes)}")
        print(f"📊 Usuarios existentes: {len(usuarios_existentes)}")
        print(f"📊 Divisiones: {list(divisiones.keys())}")

        # Leer CSV
        funcionarios_procesados = set()
        creados = 0
        actualizados = 0

        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader):
                nombre_completo = row.get("Nombre completo", "").strip()
                cargo = row.get("Cargo o función", "").strip()

                if not nombre_completo or nombre_completo in funcionarios_procesados:
                    continue

                # Filtrar honorarios con descripciones largas (no son cargos reales)
                if len(cargo) > 150 or cargo.startswith("?") or cargo.startswith("1."):
                    # Es una descripción de funciones, usar un cargo genérico
                    tipo_vinculo = row.get("Tipo vínculo", "").strip()
                    if "Honorarios" in tipo_vinculo:
                        cargo = "Profesional Honorarios"
                    else:
                        cargo = cargo[:197] + "..." if len(cargo) > 200 else cargo

                funcionarios_procesados.add(nombre_completo)

                # Parsear nombre
                partes = nombre_completo.split(",")
                if len(partes) == 2:
                    apellidos = partes[0].strip().split()
                    nombres = partes[1].strip()
                    apellido_paterno = apellidos[0] if apellidos else "Sin"
                    apellido_materno = apellidos[1] if len(apellidos) > 1 else None
                else:
                    nombres = nombre_completo
                    apellido_paterno = "Gore"
                    apellido_materno = None

                # Generar datos
                rut = generar_rut_ficticio(i + 1)
                username = generar_username(nombre_completo)
                rol_crisis = inferir_rol_crisis(cargo)
                division_codigo = inferir_division(cargo)

                # Buscar o crear persona
                if rut not in personas_existentes:
                    persona = Persona(
                        id=uuid.uuid4(),
                        rut=rut,
                        nombres=nombres,
                        apellido_paterno=apellido_paterno,
                        apellido_materno=apellido_materno,
                        cargo=cargo,
                        activo=True,
                    )
                    db.session.add(persona)
                    personas_existentes[rut] = persona
                else:
                    persona = personas_existentes[rut]

                # Buscar o crear usuario
                if username not in usuarios_existentes:
                    usuario = Usuario(
                        id=uuid.uuid4(),
                        persona_id=persona.id,
                        username=username,
                        activo=True,
                        rol_crisis=rol_crisis,
                    )
                    db.session.add(usuario)
                    usuarios_existentes[username] = usuario
                    creados += 1
                    print(f"  ✅ Creado: {username} ({rol_crisis}) - {cargo}")
                else:
                    # Actualizar rol si es necesario
                    usuario = usuarios_existentes[username]
                    if usuario.rol_crisis != rol_crisis:
                        usuario.rol_crisis = rol_crisis
                        actualizados += 1
                        print(f"  🔄 Actualizado: {username} → {rol_crisis}")

        # Commit
        try:
            db.session.commit()
            print(f"\n✅ ETL completado:")
            print(f"   - Usuarios creados: {creados}")
            print(f"   - Usuarios actualizados: {actualizados}")
            print(f"   - Total funcionarios procesados: {len(funcionarios_procesados)}")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al guardar: {e}")
            raise


if __name__ == "__main__":
    cargar_funcionarios()
