# =============================================================================
# app/services/kpi_service.py — Servicio de KPIs según kb_gn_019
# Métricas clave para gestión de IPR
# =============================================================================

from datetime import date, datetime, timedelta
from sqlalchemy import func, and_, or_, extract
from app.extensions import db
from app.models import (
    Iniciativa, Convenio, CompromisoOperativo, ProblemaIPR, AlertaIPR
)


class KPIService:
    """
    Servicio de KPIs operacionales según user_journeys.md.
    
    KPIs por perfil:
    - DIPIR: Tiempo ciclo IPR, % cartera verde
    - DAF: % ejecución, rendiciones pendientes
    - JEFATURA: Cumplimiento compromisos, problemas resueltos
    - CONSEJERO: Ejecución provincial, cumplimiento acuerdos
    """

    # =========================================================================
    # KPIs ANALISTA DIPIR
    # =========================================================================

    @staticmethod
    def kpi_tiempo_ciclo_ipr(anio=None):
        """
        KPI-NEXO-001: Tiempo promedio ciclo IPR.
        Mide: días desde fecha_creacion hasta fecha_cierre.
        Meta: < 180 días para FNDR.
        """
        anio = anio or date.today().year

        # Solo IPR cerradas en el año
        ipr_cerradas = Iniciativa.query.filter(
            Iniciativa.fecha_cierre.isnot(None),
            extract('year', Iniciativa.fecha_cierre) == anio
        ).all()

        if not ipr_cerradas:
            return {
                'valor': None,
                'meta': 180,
                'unidad': 'días',
                'semaforo': 'GRIS',
                'n_muestra': 0
            }

        # Calcular promedio
        dias_totales = sum(
            (ipr.fecha_cierre - ipr.fecha_creacion).days
            for ipr in ipr_cerradas
            if ipr.fecha_cierre and ipr.fecha_creacion
        )
        promedio = dias_totales / len(ipr_cerradas) if ipr_cerradas else 0

        # Determinar semáforo
        if promedio < 150:
            semaforo = 'VERDE'
        elif promedio <= 180:
            semaforo = 'AMARILLO'
        else:
            semaforo = 'ROJO'

        return {
            'valor': round(promedio, 1),
            'meta': 180,
            'unidad': 'días',
            'semaforo': semaforo,
            'n_muestra': len(ipr_cerradas)
        }

    @staticmethod
    def kpi_cartera_semaforo():
        """
        KPI: % de cartera por semáforo.
        Mide: distribución de IPR según nivel_alerta.
        Meta: > 80% en NORMAL.
        """
        total = Iniciativa.query.count()
        if total == 0:
            return {'valor': 0, 'meta': 80, 'semaforo': 'GRIS', 'detalle': {}}

        # Contar por nivel
        distribucion = db.session.query(
            Iniciativa.nivel_alerta,
            func.count(Iniciativa.id)
        ).group_by(Iniciativa.nivel_alerta).all()

        detalle = {nivel if nivel else 'NORMAL': count for nivel, count in distribucion}
        normales = detalle.get('NORMAL', 0)
        porcentaje_verde = (normales / total) * 100

        if porcentaje_verde >= 80:
            semaforo = 'VERDE'
        elif porcentaje_verde >= 60:
            semaforo = 'AMARILLO'
        else:
            semaforo = 'ROJO'

        return {
            'valor': round(porcentaje_verde, 1),
            'meta': 80,
            'unidad': '%',
            'semaforo': semaforo,
            'detalle': detalle,
            'total': total
        }

    @staticmethod
    def kpi_problemas_activos_por_analista(division_id=None):
        """
        KPI: N° de problemas activos por analista.
        Meta: < 5 por analista.
        """
        query = db.session.query(
            ProblemaIPR.detectado_por_id,
            func.count(ProblemaIPR.id)
        ).filter(
            ProblemaIPR.estado.in_(['ABIERTO', 'EN_GESTION'])
        ).group_by(ProblemaIPR.detectado_por_id)

        # TODO: Filtrar por división cuando se requiera
        resultado = query.all()

        if not resultado:
            return {'promedio': 0, 'maximo': 0, 'meta': 5, 'semaforo': 'VERDE'}

        conteos = [count for _, count in resultado]
        promedio = sum(conteos) / len(conteos)
        maximo = max(conteos)

        if promedio <= 3:
            semaforo = 'VERDE'
        elif promedio <= 5:
            semaforo = 'AMARILLO'
        else:
            semaforo = 'ROJO'

        return {
            'promedio': round(promedio, 1),
            'maximo': maximo,
            'meta': 5,
            'semaforo': semaforo,
            'n_analistas': len(conteos)
        }

    # =========================================================================
    # KPIs PROFESIONAL DAF
    # =========================================================================

    @staticmethod
    def kpi_ejecucion_presupuestaria(anio=None):
        """
        KPI: % ejecución presupuestaria mensual.
        TODO: Integrar con gore_presupuesto para cálculo real.
        """
        anio = anio or date.today().year
        mes_actual = date.today().month

        # Meta de ejecución mensual (lineal)
        meta_mensual = (mes_actual / 12) * 100

        # TODO: Calcular desde gore_presupuesto
        ejecutado = 0
        presupuesto = 0

        return {
            'valor': 0,
            'meta': round(meta_mensual, 1),
            'unidad': '%',
            'semaforo': 'GRIS',
            'presupuesto': presupuesto,
            'ejecutado': ejecutado
        }

    @staticmethod
    def kpi_rendiciones_pendientes():
        """
        KPI: Rendiciones pendientes > 30 días.
        Meta: < 5%.
        TODO: Integrar con gore_financiero.cuota para cálculo real.
        """
        # Placeholder - requiere integración con modelo de cuotas
        return {
            'valor': 0,
            'meta': 5,
            'unidad': '%',
            'semaforo': 'GRIS',
            'total_cuotas': 0,
            'pendientes_30d': 0
        }

    @staticmethod
    def kpi_tiempo_contabilizacion():
        """
        KPI: Tiempo promedio de contabilización.
        Meta: < 2 días hábiles.
        """
        # Placeholder - requiere trazabilidad de rendiciones
        return {
            'valor': None,
            'meta': 2,
            'unidad': 'días hábiles',
            'semaforo': 'GRIS'
        }

    # =========================================================================
    # KPIs JEFATURA
    # =========================================================================

    @staticmethod
    def kpi_cumplimiento_compromisos(division_id=None, dias=30):
        """
        KPI: Cumplimiento de compromisos en plazo.
        Mide: % completados antes de fecha_limite.
        Meta: > 90%.
        """
        desde = date.today() - timedelta(days=dias)

        query_base = CompromisoOperativo.query.filter(
            CompromisoOperativo.created_at >= desde
        )

        if division_id:
            query_base = query_base.filter(
                CompromisoOperativo.division_id == division_id
            )

        total = query_base.count()
        if total == 0:
            return {'valor': 0, 'meta': 90, 'semaforo': 'GRIS', 'total': 0}

        # Completados en plazo
        en_plazo = query_base.filter(
            CompromisoOperativo.estado.in_(['COMPLETADO', 'VERIFICADO']),
            CompromisoOperativo.completado_en <= CompromisoOperativo.fecha_limite
        ).count()

        porcentaje = (en_plazo / total) * 100

        if porcentaje >= 90:
            semaforo = 'VERDE'
        elif porcentaje >= 75:
            semaforo = 'AMARILLO'
        else:
            semaforo = 'ROJO'

        return {
            'valor': round(porcentaje, 1),
            'meta': 90,
            'unidad': '%',
            'semaforo': semaforo,
            'total': total,
            'en_plazo': en_plazo
        }

    @staticmethod
    def kpi_problemas_escalados_sin_resolver(division_id=None):
        """
        KPI: N° problemas escalados sin resolver.
        Meta: 0.
        """
        query = ProblemaIPR.query.filter(
            ProblemaIPR.estado.in_(['ABIERTO', 'EN_GESTION']),
            ProblemaIPR.impacto.in_(['ALTO', 'CRITICO'])
        )

        # TODO: Filtrar por división cuando la relación esté disponible

        count = query.count()

        if count == 0:
            semaforo = 'VERDE'
        elif count <= 2:
            semaforo = 'AMARILLO'
        else:
            semaforo = 'ROJO'

        return {
            'valor': count,
            'meta': 0,
            'unidad': 'problemas',
            'semaforo': semaforo
        }

    @staticmethod
    def kpi_desviacion_presupuestaria():
        """
        KPI: Desviación presupuestaria vs programado.
        Meta: < 5%.
        TODO: Integrar con gore_presupuesto.
        """
        return {
            'valor': 0,
            'meta': 5,
            'unidad': '%',
            'semaforo': 'GRIS'
        }

    # =========================================================================
    # KPIs CONSEJERO
    # =========================================================================

    @staticmethod
    def kpi_ejecucion_por_provincia():
        """
        KPI: % ejecución por provincia.
        TODO: Integrar con gore_territorial para distribución geográfica.
        """
        # Placeholder - requiere integración territorial
        return {
            'provincias': [],
            'semaforo_regional': 'GRIS'
        }

    @staticmethod
    def kpi_cumplimiento_acuerdos_core():
        """
        KPI: Cumplimiento de acuerdos CORE anteriores.
        TODO: Integrar con gore_gobernanza.acuerdo_core.
        """
        return {
            'valor': 0,
            'meta': 100,
            'unidad': '%',
            'semaforo': 'GRIS'
        }

    # =========================================================================
    # RESUMEN DE KPIs POR PERFIL
    # =========================================================================

    @classmethod
    def get_kpis_dipir(cls, division_id=None):
        """Retorna todos los KPIs relevantes para DIPIR."""
        return {
            'tiempo_ciclo': cls.kpi_tiempo_ciclo_ipr(),
            'cartera_semaforo': cls.kpi_cartera_semaforo(),
            'problemas_por_analista': cls.kpi_problemas_activos_por_analista(division_id),
        }

    @classmethod
    def get_kpis_daf(cls):
        """Retorna todos los KPIs relevantes para DAF."""
        return {
            'ejecucion_ppto': cls.kpi_ejecucion_presupuestaria(),
            'rendiciones_pendientes': cls.kpi_rendiciones_pendientes(),
            'tiempo_contabilizacion': cls.kpi_tiempo_contabilizacion(),
        }

    @classmethod
    def get_kpis_jefatura(cls, division_id=None):
        """Retorna todos los KPIs relevantes para Jefaturas."""
        return {
            'cumplimiento_compromisos': cls.kpi_cumplimiento_compromisos(division_id),
            'problemas_escalados': cls.kpi_problemas_escalados_sin_resolver(division_id),
            'desviacion_ppto': cls.kpi_desviacion_presupuestaria(),
        }

    @classmethod
    def get_kpis_consejero(cls):
        """Retorna todos los KPIs relevantes para Consejeros."""
        return {
            'ejecucion_provincial': cls.kpi_ejecucion_por_provincia(),
            'cumplimiento_acuerdos': cls.kpi_cumplimiento_acuerdos_core(),
        }
