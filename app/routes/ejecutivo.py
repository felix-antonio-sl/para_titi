# =============================================================================
# app/routes/ejecutivo.py — Dashboard Ejecutivo por Perfil de Usuario
# Soporta User Journeys según agent_gestor_ipr_360.yaml
# =============================================================================

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.services.dashboard_service import DashboardService
from app.services.kpi_service import KPIService

ejecutivo_bp = Blueprint('ejecutivo', __name__)


@ejecutivo_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard principal adaptado al perfil del usuario.
    
    Perfiles detectados por rol:
    - ADMIN_SISTEMA, JEFE_DIVISION → Dashboard Jefatura
    - ANALISTA_DIPIR → Dashboard DIPIR
    - PROFESIONAL_DAF → Dashboard DAF
    - CONSEJERO → Dashboard Consejero
    - DEFAULT → Dashboard básico
    """
    # Detectar perfil según rol del usuario
    rol = current_user.rol if hasattr(current_user, 'rol') else 'DEFAULT'
    division_id = getattr(current_user, 'division_id', None)

    # Seleccionar dashboard según perfil
    if rol in ('ADMIN_SISTEMA', 'JEFE_DIVISION', 'GOBERNADOR', 'ADMINISTRADOR_REGIONAL'):
        return _dashboard_jefatura(division_id)
    elif rol in ('ANALISTA_DIPIR', 'JEFE_PREINVERSION'):
        return _dashboard_dipir(division_id)
    elif rol in ('PROFESIONAL_DAF', 'JEFE_PRESUPUESTO', 'ENCARGADO_RENDICIONES'):
        return _dashboard_daf()
    elif rol == 'CONSEJERO':
        return _dashboard_consejero()
    else:
        # Dashboard básico para otros roles
        return _dashboard_basico()


def _dashboard_jefatura(division_id=None):
    """Dashboard para Jefaturas Divisionales y Gobernador."""
    datos = DashboardService.get_dashboard_jefatura(division_id)
    kpis = KPIService.get_kpis_jefatura(division_id)
    alertas = DashboardService.get_alertas_activas(limite=5, nivel_minimo='ATENCION')

    return render_template('dashboard/ejecutivo.html',
                           tipo='jefatura',
                           datos=datos,
                           kpis=kpis,
                           alertas=alertas)


def _dashboard_dipir(division_id=None):
    """Dashboard para Analistas DIPIR."""
    datos = DashboardService.get_dashboard_dipir(division_id=division_id)
    kpis = KPIService.get_kpis_dipir(division_id)

    return render_template('dashboard/dipir.html',
                           datos=datos,
                           kpis=kpis)


def _dashboard_daf():
    """Dashboard para Profesionales DAF."""
    datos = DashboardService.get_dashboard_daf()
    kpis = KPIService.get_kpis_daf()

    return render_template('dashboard/daf.html',
                           datos=datos,
                           kpis=kpis)


def _dashboard_consejero():
    """Dashboard para Consejeros Regionales."""
    datos = DashboardService.get_dashboard_consejero()
    kpis = KPIService.get_kpis_consejero()

    return render_template('dashboard/consejero.html',
                           datos=datos,
                           kpis=kpis)


def _dashboard_basico():
    """Dashboard básico para usuarios sin perfil específico."""
    return render_template('dashboard/basico.html')


# =============================================================================
# APIs JSON para componentes HTMX / JavaScript
# =============================================================================

@ejecutivo_bp.route('/api/kpis/<perfil>')
@login_required
def api_kpis(perfil):
    """API JSON de KPIs por perfil."""
    division_id = request.args.get('division_id')

    if perfil == 'dipir':
        kpis = KPIService.get_kpis_dipir(division_id)
    elif perfil == 'daf':
        kpis = KPIService.get_kpis_daf()
    elif perfil == 'jefatura':
        kpis = KPIService.get_kpis_jefatura(division_id)
    elif perfil == 'consejero':
        kpis = KPIService.get_kpis_consejero()
    else:
        return jsonify({'error': 'Perfil no válido'}), 400

    return jsonify(kpis)


@ejecutivo_bp.route('/api/alertas')
@login_required
def api_alertas():
    """API JSON de alertas activas."""
    limite = request.args.get('limite', 10, type=int)
    nivel_minimo = request.args.get('nivel_minimo')

    alertas = DashboardService.get_alertas_activas(limite, nivel_minimo)

    return jsonify([
        {
            'id': str(a.id),
            'tipo': a.tipo,
            'nivel': a.nivel,
            'mensaje': a.mensaje,
            'target_tipo': a.target_tipo,
            'target_id': str(a.target_id),
            'generada_en': a.generada_en.isoformat() if a.generada_en else None,
        }
        for a in alertas
    ])


@ejecutivo_bp.route('/api/compromisos-vencidos-division')
@login_required
def api_compromisos_vencidos_division():
    """API JSON de compromisos vencidos por división."""
    datos = DashboardService.get_compromisos_vencidos_por_division()
    return jsonify([
        {'division': nombre, 'count': count}
        for nombre, count in datos
    ])
