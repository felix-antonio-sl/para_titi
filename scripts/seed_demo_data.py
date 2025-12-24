# =============================================================================
# scripts/seed_demo_data.py — Inyección de Datos Demo (Crisis)
# =============================================================================
#
# Uso:
#   docker compose -f docker-compose.dev.yml exec app python scripts/seed_demo_data.py
#

import random
from datetime import datetime, timedelta
from uuid import uuid4
from app import create_app, db
from app.models import Iniciativa, Usuario, Division, TipoCompromisoOperativo
from app.models.crisis import ProblemaIPR, CompromisoOperativo, AlertaIPR

PROBLEMAS_TEMPLATE = [
    {
        "descripcion": "Retraso en licitación por falta de oferentes",
        "tipo": "ADMINISTRATIVO",
        "impacto": "RETRASA_OBRA",
    },
    {
        "descripcion": "Dificultades en expropiación de terrenos",
        "tipo": "LEGAL",
        "impacto": "BLOQUEA_PAGO",
    },
    {
        "descripcion": "Aumento de costos materiales por inflación",
        "tipo": "FINANCIERO",
        "impacto": "RIESGO_RENDICION",
    },
    {
        "descripcion": "Hallazgos arqueológicos detienen obras",
        "tipo": "TECNICO",
        "impacto": "RETRASA_OBRA",
    },
    {
        "descripcion": "Quiebra de la empresa constructora",
        "tipo": "ADMINISTRATIVO",
        "impacto": "AFECTA_IMAGEN",
    },
    {
        "descripcion": "Incumplimiento de plazos por parte del contratista",
        "tipo": "ADMINISTRATIVO",
        "impacto": "RETRASA_CONVENIO",
    },
    {
        "descripcion": "Falta de permisos ambientales",
        "tipo": "LEGAL",
        "impacto": "BLOQUEA_PAGO",
    },
    {
        "descripcion": "Conflicto con comunidad local",
        "tipo": "EXTERNO",
        "impacto": "AFECTA_IMAGEN",
    },
    {
        "descripcion": "Error en cálculo estructural requiere rediseño",
        "tipo": "TECNICO",
        "impacto": "RETRASA_OBRA",
    },
    {
        "descripcion": "Demora en aprobación de modificación de contrato",
        "tipo": "ADMINISTRATIVO",
        "impacto": "RETRASA_CONVENIO",
    },
    {
        "descripcion": "Problemas de coordinación con municipio",
        "tipo": "COORDINACION",
        "impacto": "RETRASA_OBRA",
    },
    {
        "descripcion": "Rendición observada por Contraloría",
        "tipo": "FINANCIERO",
        "impacto": "RIESGO_RENDICION",
    },
]

COMPROMISOS_TEMPLATE = [
    "Reunión con alcalde para gestionar permisos",
    "Oficio a Ministerio de Obras Públicas",
    "Visita a terreno para inspeccionar avance",
    "Gestión de suplemento presupuestario",
    "Revisión de bases de licitación",
    "Coordinación con Seremi para resolución",
    "Elaboración de informe técnico",
    "Reunión de seguimiento con contratista",
    "Tramitación de convenio modificatorio",
    "Gestión de boleta de garantía",
]

ALERTAS_TEMPLATE = [
    {
        "tipo": "AVANCE_DETENIDO",
        "nivel": "CRITICO",
        "mensaje": "Ejecución física detenida por más de 30 días",
    },
    {
        "tipo": "CONVENIO_POR_VENCER",
        "nivel": "ATENCION",
        "mensaje": "Convenio vence en menos de 60 días",
    },
    {
        "tipo": "PROBLEMA_PROLONGADO",
        "nivel": "ALTO",
        "mensaje": "Problema sin resolución por más de 45 días",
    },
    {
        "tipo": "CUOTA_VENCIDA",
        "nivel": "CRITICO",
        "mensaje": "Cuota de pago vencida sin transferencia",
    },
    {
        "tipo": "RENDICION_VENCIDA",
        "nivel": "ALTO",
        "mensaje": "Rendición pendiente supera plazo normativo",
    },
    {
        "tipo": "COMPROMISO_VENCIDO",
        "nivel": "ATENCION",
        "mensaje": "Compromiso operativo no cumplido en plazo",
    },
    {
        "tipo": "OBRA_TERMINADA_SIN_PAGO",
        "nivel": "CRITICO",
        "mensaje": "Obra recepcionada pero sin pago final",
    },
    {
        "tipo": "INCONSISTENCIA_DETECTADA",
        "nivel": "ALTO",
        "mensaje": "Diferencia entre avance físico y financiero >20%",
    },
    {
        "tipo": "AVANCE_DETENIDO",
        "nivel": "ATENCION",
        "mensaje": "Sin movimientos administrativos en 30 días",
    },
    {
        "tipo": "CONVENIO_POR_VENCER",
        "nivel": "CRITICO",
        "mensaje": "Convenio vence en menos de 15 días - urgente",
    },
]


def seed_demo_data():
    app = create_app()
    with app.app_context():
        print("🚀 Iniciando inyección de datos demo...")

        # 1. Obtener datos base
        iniciativas = Iniciativa.query.limit(50).all()
        usuarios = Usuario.query.filter(Usuario.activo == True).all()
        tipos_compromiso = TipoCompromisoOperativo.query.all()
        divisiones = Division.query.all()

        if not iniciativas or not usuarios:
            print("❌ No hay iniciativas o usuarios suficientes. Ejecuta ETL primero.")
            return

        print(f"📊 Base: {len(iniciativas)} iniciativas, {len(usuarios)} usuarios.")

        stats = {"problemas": 0, "compromisos": 0, "alertas": 0}

        # 2. Generar datos para cada iniciativa (aleatoriamente)
        for ipr in iniciativas:
            # Probabilidad de tener problemas (80%)
            if random.random() < 0.8:
                # Crear Problema
                tpl_prob = random.choice(PROBLEMAS_TEMPLATE)
                usuario = random.choice(usuarios)

                problema = ProblemaIPR(
                    id=uuid4(),
                    iniciativa_id=ipr.id,
                    tipo=tpl_prob["tipo"],
                    impacto=tpl_prob["impacto"],
                    descripcion=tpl_prob["descripcion"],
                    detectado_por_id=usuario.id,
                    detectado_en=datetime.now() - timedelta(days=random.randint(1, 60)),
                    estado=random.choice(["ABIERTO", "EN_GESTION", "RESUELTO"]),
                )
                db.session.add(problema)
                stats["problemas"] += 1

                # Actualizar flag en IPR
                ipr.tiene_problemas_abiertos = True
                ipr.nivel_alerta = (
                    "CRITICO" if tpl_prob["impacto"] == "CRITICO" else "ATENCION"
                )
                db.session.add(ipr)

                # Compromiso asociado al problema (100%)
                if True:
                    tipo_comp = (
                        random.choice(tipos_compromiso) if tipos_compromiso else None
                    )
                    if tipo_comp:
                        compromiso = CompromisoOperativo(
                            id=uuid4(),
                            problema_id=problema.id,
                            iniciativa_id=ipr.id,
                            tipo_id=tipo_comp.id,
                            descripcion=random.choice(COMPROMISOS_TEMPLATE),
                            responsable_id=random.choice(usuarios).id,
                            division_id=ipr.division_responsable_id,  # Asumir misma división
                            fecha_limite=datetime.now()
                            + timedelta(days=random.randint(5, 30)),
                            prioridad=random.choice(["ALTA", "URGENTE"]),
                            estado="PENDIENTE",
                            creado_por_id=usuario.id,
                        )
                        db.session.add(compromiso)
                        stats["compromisos"] += 1

            # Probabilidad de Alertas (60%)
            if random.random() < 0.6:
                tpl_alerta = random.choice(ALERTAS_TEMPLATE)
                alerta = AlertaIPR(
                    id=uuid4(),
                    target_tipo="INICIATIVA",
                    target_id=ipr.id,
                    iniciativa_id=ipr.id,
                    tipo=tpl_alerta["tipo"],
                    nivel=tpl_alerta["nivel"],
                    mensaje=tpl_alerta["mensaje"],
                    activa=True,
                )
                db.session.add(alerta)
                stats["alertas"] += 1

                if tpl_alerta["nivel"] == "CRITICO":
                    ipr.nivel_alerta = "CRITICO"
                    db.session.add(ipr)

        try:
            db.session.commit()
            print("\n✅ Datos inyectados exitosamente:")
            print(f"   - Problemas: {stats['problemas']}")
            print(f"   - Compromisos: {stats['compromisos']}")
            print(f"   - Alertas: {stats['alertas']}")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al guardar datos: {e}")


if __name__ == "__main__":
    seed_demo_data()
