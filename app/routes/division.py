# =============================================================================
# app/routes/division.py — Vista "Mi División" para Jefes (JD-01 a JD-07)
# =============================================================================

from datetime import date, timedelta
from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models import (
    Iniciativa, CompromisoOperativo, Usuario, Division, ProblemaIPR
)

division_bp = Blueprint('division', __name__)


@division_bp.route('/mi-division')
@login_required
def mi_division():
    """
    Vista "Mi División" para Jefes de División.
    Casos de uso: JD-01, JD-02, JD-03
    """
    # Obtener división del usuario
    division = current_user.get_division()
    
    if not division and not current_user.puede_ver_todas_ipr():
        # Si no tiene división asignada y no es admin, mostrar mensaje
        return render_template('dashboard/mi_division.html',
                               division=None,
                               stats={},
                               equipo=[],
                               compromisos_vencidos=[],
                               ipr_con_problemas=[],
                               today=date.today())
    
    # Para admins sin división, pueden ver todas
    division_id = division.id if division else None
    
    # Estadísticas de la división
    stats = _get_division_stats(division_id)
    
    # Estado del equipo
    equipo = _get_equipo_stats(division_id)
    
    # Compromisos vencidos de la división
    compromisos_vencidos = _get_compromisos_vencidos(division_id, limit=10)
    
    # IPR con problemas
    ipr_con_problemas = _get_ipr_con_problemas(division_id, limit=10)
    
    return render_template('dashboard/mi_division.html',
                           division=division,
                           stats=stats,
                           equipo=equipo,
                           compromisos_vencidos=compromisos_vencidos,
                           ipr_con_problemas=ipr_con_problemas,
                           today=date.today())


def _get_division_stats(division_id):
    """Obtiene estadísticas de la división."""
    query_ipr = Iniciativa.query
    query_comp = CompromisoOperativo.query
    
    if division_id:
        query_ipr = query_ipr.filter(Iniciativa.division_responsable_id == division_id)
        query_comp = query_comp.filter(CompromisoOperativo.division_id == division_id)
    
    today = date.today()
    
    return {
        'total_ipr': query_ipr.count(),
        'ipr_con_problemas': query_ipr.filter(Iniciativa.tiene_problemas_abiertos == True).count(),
        'compromisos_pendientes': query_comp.filter(
            CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO'])
        ).count(),
        'compromisos_vencidos': query_comp.filter(
            CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
            CompromisoOperativo.fecha_limite < today
        ).count()
    }


def _get_equipo_stats(division_id):
    """Obtiene estadísticas por miembro del equipo."""
    today = date.today()
    
    # Query base de compromisos
    query = db.session.query(
        Usuario.id,
        func.concat(Usuario.username).label('nombre'),
        func.count(CompromisoOperativo.id).label('total_compromisos'),
        func.sum(
            db.case(
                (db.and_(
                    CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
                    CompromisoOperativo.fecha_limite < today
                ), 1),
                else_=0
            )
        ).label('vencidos'),
        func.sum(
            db.case(
                (CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']), 1),
                else_=0
            )
        ).label('pendientes')
    ).join(
        CompromisoOperativo, CompromisoOperativo.responsable_id == Usuario.id
    ).filter(
        Usuario.activo == True
    )
    
    if division_id:
        query = query.filter(CompromisoOperativo.division_id == division_id)
    
    query = query.group_by(Usuario.id, Usuario.username)
    
    results = query.all()
    
    equipo = []
    for r in results:
        # Obtener nombre completo
        usuario = Usuario.query.get(r.id)
        equipo.append({
            'id': r.id,
            'nombre': usuario.nombre_completo if usuario else r.nombre,
            'total_compromisos': r.total_compromisos or 0,
            'vencidos': r.vencidos or 0,
            'pendientes': r.pendientes or 0
        })
    
    # Ordenar por vencidos desc, luego por pendientes desc
    equipo.sort(key=lambda x: (-x['vencidos'], -x['pendientes']))
    
    return equipo


def _get_compromisos_vencidos(division_id, limit=10):
    """Obtiene compromisos vencidos de la división."""
    today = date.today()
    
    query = CompromisoOperativo.query.filter(
        CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
        CompromisoOperativo.fecha_limite < today
    )
    
    if division_id:
        query = query.filter(CompromisoOperativo.division_id == division_id)
    
    return query.order_by(CompromisoOperativo.fecha_limite).limit(limit).all()


def _get_ipr_con_problemas(division_id, limit=10):
    """Obtiene IPR con problemas abiertos."""
    query = Iniciativa.query.filter(Iniciativa.tiene_problemas_abiertos == True)
    
    if division_id:
        query = query.filter(Iniciativa.division_responsable_id == division_id)
    
    return query.order_by(Iniciativa.nivel_alerta.desc()).limit(limit).all()


@division_bp.route('/mis-compromisos')
@login_required
def mis_compromisos():
    """
    Vista "Mis Compromisos" para Encargados Operativos.
    Casos de uso: EO-01, EO-02
    """
    today = date.today()
    fin_semana = today + timedelta(days=(6 - today.weekday()))
    inicio_mes = today.replace(day=1)
    
    # Compromisos del usuario actual
    base_query = CompromisoOperativo.query.filter(
        CompromisoOperativo.responsable_id == current_user.id
    )
    
    # Vencidos
    vencidos = base_query.filter(
        CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
        CompromisoOperativo.fecha_limite < today
    ).order_by(CompromisoOperativo.fecha_limite).all()
    
    # Esta semana (no vencidos)
    esta_semana = base_query.filter(
        CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
        CompromisoOperativo.fecha_limite >= today,
        CompromisoOperativo.fecha_limite <= fin_semana
    ).order_by(CompromisoOperativo.fecha_limite).all()
    
    # Otros pendientes (después de esta semana)
    pendientes = base_query.filter(
        CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
        CompromisoOperativo.fecha_limite > fin_semana
    ).order_by(CompromisoOperativo.fecha_limite).limit(20).all()
    
    # Completados este mes
    completados_mes = base_query.filter(
        CompromisoOperativo.estado == 'COMPLETADO',
        CompromisoOperativo.completado_en >= inicio_mes
    ).count()
    
    stats = {
        'vencidos': len(vencidos),
        'esta_semana': len(esta_semana),
        'pendientes': base_query.filter(
            CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO'])
        ).count(),
        'completados_mes': completados_mes
    }
    
    return render_template('dashboard/mis_compromisos.html',
                           vencidos=vencidos,
                           esta_semana=esta_semana,
                           pendientes=pendientes,
                           stats=stats,
                           today=today)
