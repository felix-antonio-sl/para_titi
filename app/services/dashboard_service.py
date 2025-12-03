# =============================================================================
# app/services/dashboard_service.py — Servicio de Dashboards por Perfil
# Soporta User Journeys según agent_gestor_ipr_360.yaml
# =============================================================================

from datetime import date, datetime, timedelta
from sqlalchemy import func, case, and_, or_
from app.extensions import db
from app.models import (
    Iniciativa, Convenio, CompromisoOperativo, ProblemaIPR,
    AlertaIPR, TipoCompromisoOperativo, Usuario, Division
)


class DashboardService:
    """
    Servicio centralizado para dashboards según perfil de usuario.
    
    Perfiles soportados:
    - ANALISTA_DIPIR (AD): Cartera, tracks evaluación, semáforos
    - PROFESIONAL_DAF (PD): Presupuesto, rendiciones, CDPs
    - JEFATURA (JD): KPIs, escalados, compromisos Gobernador
    - CONSEJERO (CR): Vista territorial, ejecución por provincia
    """

    # =========================================================================
    # DASHBOARD ANALISTA DIPIR (AD)
    # =========================================================================

    @staticmethod
    def get_dashboard_dipir(usuario=None, division_id=None):
        """
        Dashboard para Analistas DIPIR.
        Foco: Cartera IPR, estados, semáforos de ejecución.
        """
        hoy = date.today()

        # Métricas de cartera
        cartera = {
            'total_iniciativas': Iniciativa.query.count(),
            'con_problemas': Iniciativa.query.filter(
                Iniciativa.tiene_problemas_abiertos == True
            ).count(),
            'alertas_criticas': AlertaIPR.query.filter(
                AlertaIPR.activa == True,
                AlertaIPR.nivel == 'CRITICO'
            ).count(),
        }

        # Distribución por nivel de alerta (semáforos)
        semaforos = db.session.query(
            Iniciativa.nivel_alerta,
            func.count(Iniciativa.id)
        ).group_by(Iniciativa.nivel_alerta).all()

        cartera['semaforos'] = {
            nivel: count for nivel, count in semaforos
        }

        # Problemas por tipo
        problemas_por_tipo = db.session.query(
            ProblemaIPR.tipo,
            func.count(ProblemaIPR.id)
        ).filter(
            ProblemaIPR.estado.in_(['ABIERTO', 'EN_GESTION'])
        ).group_by(ProblemaIPR.tipo).all()

        cartera['problemas_por_tipo'] = dict(problemas_por_tipo)

        # Compromisos vencidos de la división/analista
        query_compromisos = CompromisoOperativo.query.filter(
            CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
            CompromisoOperativo.fecha_limite < hoy
        )
        if division_id:
            query_compromisos = query_compromisos.filter(
                CompromisoOperativo.division_id == division_id
            )
        cartera['compromisos_vencidos'] = query_compromisos.count()

        # IPR que requieren atención (alertas activas no atendidas)
        ipr_atencion = db.session.query(
            Iniciativa.id,
            Iniciativa.codigo_interno,
            Iniciativa.nombre,
            Iniciativa.nivel_alerta,
            func.count(AlertaIPR.id).label('n_alertas')
        ).join(
            AlertaIPR, AlertaIPR.iniciativa_id == Iniciativa.id
        ).filter(
            AlertaIPR.activa == True
        ).group_by(
            Iniciativa.id,
            Iniciativa.codigo_interno,
            Iniciativa.nombre,
            Iniciativa.nivel_alerta
        ).order_by(
            case(
                (Iniciativa.nivel_alerta == 'CRITICO', 1),
                (Iniciativa.nivel_alerta == 'ALTO', 2),
                (Iniciativa.nivel_alerta == 'ATENCION', 3),
                else_=4
            )
        ).limit(10).all()

        cartera['ipr_requieren_atencion'] = [
            {
                'id': str(ipr.id),
                'codigo': ipr.codigo_interno,
                'nombre': ipr.nombre[:50] + '...' if len(ipr.nombre) > 50 else ipr.nombre,
                'nivel_alerta': ipr.nivel_alerta,
                'n_alertas': ipr.n_alertas
            }
            for ipr in ipr_atencion
        ]

        return cartera

    # =========================================================================
    # DASHBOARD PROFESIONAL DAF (PD)
    # =========================================================================

    @staticmethod
    def get_dashboard_daf():
        """
        Dashboard para Profesionales DAF.
        Foco: Presupuesto, convenios, rendiciones pendientes.
        """
        hoy = date.today()

        # Convenios por estado
        convenios_estado = db.session.query(
            Convenio.estado,
            func.count(Convenio.id)
        ).group_by(Convenio.estado).all()

        # Rendiciones pendientes (cuotas vencidas sin rendición)
        # Simplificado - en producción consultaría gore_financiero.cuota
        rendiciones = {
            'pendientes_30': 0,  # TODO: Integrar con cuotas
            'pendientes_60': 0,
            'total_pendientes': 0,
        }

        # Compromisos financieros (tipo CDP, CONVENIO, etc.)
        compromisos_financieros = CompromisoOperativo.query.join(
            TipoCompromisoOperativo
        ).filter(
            TipoCompromisoOperativo.codigo.in_(['CDP', 'CONVENIO', 'PAGO', 'RENDICION']),
            CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO'])
        ).count()

        # Alertas financieras
        alertas_financieras = AlertaIPR.query.filter(
            AlertaIPR.activa == True,
            AlertaIPR.tipo.in_([
                'RENDICION_VENCIDA',
                'CUOTA_PROXIMA_VENCER',
                'CONVENIO_SIN_TRANSFERENCIA',
                'CDP_PROXIMO_VENCER'
            ])
        ).count()

        return {
            'convenios_por_estado': dict(convenios_estado),
            'total_convenios': sum(c for _, c in convenios_estado),
            'rendiciones': rendiciones,
            'compromisos_financieros': compromisos_financieros,
            'alertas_financieras': alertas_financieras,
        }

    # =========================================================================
    # DASHBOARD JEFATURA (JD)
    # =========================================================================

    @staticmethod
    def get_dashboard_jefatura(division_id=None):
        """
        Dashboard Ejecutivo para Jefaturas.
        Foco: KPIs, problemas escalados, compromisos críticos.
        """
        hoy = date.today()
        hace_7_dias = hoy - timedelta(days=7)
        hace_30_dias = hoy - timedelta(days=30)

        # Resumen general
        resumen = {
            'total_ipr': Iniciativa.query.count(),
            'ipr_con_problemas': Iniciativa.query.filter(
                Iniciativa.tiene_problemas_abiertos == True
            ).count(),
            'alertas_criticas': AlertaIPR.query.filter(
                AlertaIPR.activa == True,
                AlertaIPR.nivel == 'CRITICO'
            ).count(),
        }

        # Filtrar por división si aplica
        if division_id:
            resumen['ipr_division'] = Iniciativa.query.filter(
                Iniciativa.division_responsable_id == division_id
            ).count()

        # Problemas escalados (impacto ALTO o CRITICO)
        problemas_escalados = ProblemaIPR.query.filter(
            ProblemaIPR.estado.in_(['ABIERTO', 'EN_GESTION']),
            ProblemaIPR.impacto.in_(['ALTO', 'CRITICO'])
        ).order_by(
            case(
                (ProblemaIPR.impacto == 'CRITICO', 1),
                (ProblemaIPR.impacto == 'ALTO', 2),
                else_=3
            ),
            ProblemaIPR.detectado_en.desc()
        ).limit(5).all()

        resumen['problemas_escalados'] = [
            {
                'id': str(p.id),
                'tipo': p.tipo,
                'impacto': p.impacto,
                'descripcion': p.descripcion[:80] + '...' if len(p.descripcion) > 80 else p.descripcion,
                'dias_abierto': p.dias_abierto(),
            }
            for p in problemas_escalados
        ]

        # Compromisos urgentes (vencidos o próximos a vencer)
        compromisos_urgentes = CompromisoOperativo.query.filter(
            CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
            or_(
                CompromisoOperativo.prioridad == 'URGENTE',
                CompromisoOperativo.fecha_limite <= hoy + timedelta(days=3)
            )
        )
        if division_id:
            compromisos_urgentes = compromisos_urgentes.filter(
                CompromisoOperativo.division_id == division_id
            )
        compromisos_urgentes = compromisos_urgentes.order_by(
            CompromisoOperativo.fecha_limite
        ).limit(10).all()

        resumen['compromisos_urgentes'] = [
            {
                'id': str(c.id),
                'descripcion': c.descripcion[:60] + '...' if len(c.descripcion) > 60 else c.descripcion,
                'responsable': c.responsable.nombre_completo if c.responsable else 'Sin asignar',
                'fecha_limite': c.fecha_limite.isoformat(),
                'dias_restantes': c.dias_restantes(),
                'prioridad': c.prioridad,
                'vencido': c.esta_vencido(),
            }
            for c in compromisos_urgentes
        ]

        # Tendencias (últimos 7 días)
        nuevos_problemas_semana = ProblemaIPR.query.filter(
            ProblemaIPR.detectado_en >= hace_7_dias
        ).count()

        resueltos_semana = ProblemaIPR.query.filter(
            ProblemaIPR.resuelto_en >= hace_7_dias
        ).count()

        compromisos_completados_semana = CompromisoOperativo.query.filter(
            CompromisoOperativo.completado_en >= hace_7_dias
        ).count()

        resumen['tendencias'] = {
            'nuevos_problemas_7d': nuevos_problemas_semana,
            'problemas_resueltos_7d': resueltos_semana,
            'compromisos_completados_7d': compromisos_completados_semana,
        }

        return resumen

    # =========================================================================
    # DASHBOARD CONSEJERO REGIONAL (CR)
    # =========================================================================

    @staticmethod
    def get_dashboard_consejero(provincia=None):
        """
        Dashboard para Consejeros Regionales.
        Foco: Vista territorial, ejecución, transparencia.
        """
        # Resumen regional
        resumen = {
            'total_ipr': Iniciativa.query.count(),
            # TODO: Filtrar por provincia cuando se integre gore_territorial
            'total_inversión': 0,  # Sumar monto_aprobado
        }

        # IPR por nivel de alerta (semáforo regional)
        semaforos = db.session.query(
            Iniciativa.nivel_alerta,
            func.count(Iniciativa.id)
        ).group_by(Iniciativa.nivel_alerta).all()

        resumen['semaforos'] = {
            nivel if nivel else 'NORMAL': count 
            for nivel, count in semaforos
        }

        # Ejecución presupuestaria (simplificado)
        # TODO: Integrar con gore_presupuesto para cálculo real
        resumen['ejecucion'] = {
            'presupuesto_anual': 0,
            'ejecutado': 0,
            'porcentaje': 0,
        }

        # Últimas aprobaciones CORE (para seguimiento)
        # TODO: Integrar con gore_gobernanza.acuerdo_core

        return resumen

    # =========================================================================
    # MÉTODOS AUXILIARES
    # =========================================================================

    @staticmethod
    def get_alertas_activas(limite=10, nivel_minimo=None):
        """Obtiene alertas activas ordenadas por criticidad."""
        query = AlertaIPR.query.filter(AlertaIPR.activa == True)

        if nivel_minimo:
            niveles = ['INFO', 'ATENCION', 'ALTO', 'CRITICO']
            idx = niveles.index(nivel_minimo)
            query = query.filter(AlertaIPR.nivel.in_(niveles[idx:]))

        return query.order_by(
            case(
                (AlertaIPR.nivel == 'CRITICO', 1),
                (AlertaIPR.nivel == 'ALTO', 2),
                (AlertaIPR.nivel == 'ATENCION', 3),
                else_=4
            ),
            AlertaIPR.generada_en.desc()
        ).limit(limite).all()

    @staticmethod
    def get_compromisos_vencidos_por_division():
        """Agrupa compromisos vencidos por división."""
        hoy = date.today()
        return db.session.query(
            Division.nombre,
            func.count(CompromisoOperativo.id)
        ).join(
            Division, Division.id == CompromisoOperativo.division_id
        ).filter(
            CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
            CompromisoOperativo.fecha_limite < hoy
        ).group_by(Division.nombre).all()
