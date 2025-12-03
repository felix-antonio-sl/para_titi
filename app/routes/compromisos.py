# =============================================================================
# app/routes/compromisos.py — Gestión de Compromisos Operativos
# =============================================================================

from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import (
    CompromisoOperativo, TipoCompromisoOperativo, HistorialCompromiso,
    Iniciativa, ProblemaIPR, Usuario, Division
)

compromisos_bp = Blueprint('compromisos', __name__)


@compromisos_bp.route('/')
@login_required
def lista():
    """Lista de compromisos con filtros."""
    page = request.args.get('page', 1, type=int)

    # Filtros
    estado = request.args.get('estado')
    responsable_id = request.args.get('responsable')
    solo_vencidos = request.args.get('vencidos') == '1'
    solo_mios = request.args.get('mios') == '1'

    # Query base según permisos
    if current_user.puede_ver_todas_ipr():
        query = CompromisoOperativo.query
    else:
        # Jefes y encargados ven solo sus compromisos asignados
        query = CompromisoOperativo.query.filter(
            CompromisoOperativo.responsable_id == current_user.id
        )

    # Aplicar filtros
    if estado:
        query = query.filter(CompromisoOperativo.estado == estado)
    else:
        # Por defecto, solo activos
        query = query.filter(CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']))

    if responsable_id:
        query = query.filter(CompromisoOperativo.responsable_id == responsable_id)

    if solo_vencidos:
        query = query.filter(CompromisoOperativo.fecha_limite < date.today())

    if solo_mios:
        query = query.filter(CompromisoOperativo.responsable_id == current_user.id)

    # Ordenar y paginar
    query = query.order_by(
        CompromisoOperativo.fecha_limite,
        CompromisoOperativo.prioridad.desc()
    )

    paginacion = query.paginate(page=page, per_page=20, error_out=False)

    # Datos para filtros
    tipos = TipoCompromisoOperativo.query.filter_by(activo=True).all()

    return render_template('compromisos/lista.html',
                           compromisos=paginacion.items,
                           paginacion=paginacion,
                           tipos=tipos,
                           filtros={
                               'estado': estado,
                               'responsable': responsable_id,
                               'vencidos': solo_vencidos,
                               'mios': solo_mios
                           })


@compromisos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    """Crear nuevo compromiso."""
    if not current_user.puede_crear_compromisos():
        abort(403)

    if request.method == 'POST':
        tipo_id = request.form.get('tipo_id')
        descripcion = request.form.get('descripcion', '').strip()
        responsable_id = request.form.get('responsable_id')
        fecha_limite = request.form.get('fecha_limite')
        prioridad = request.form.get('prioridad', 'MEDIA')
        iniciativa_id = request.form.get('iniciativa_id') or None
        problema_id = request.form.get('problema_id') or None

        if not all([tipo_id, descripcion, responsable_id, fecha_limite]):
            flash('Todos los campos obligatorios deben completarse.', 'error')
        else:
            from uuid import UUID
            compromiso = CompromisoOperativo(
                tipo_id=UUID(tipo_id),
                descripcion=descripcion,
                responsable_id=UUID(responsable_id),
                fecha_limite=datetime.strptime(fecha_limite, '%Y-%m-%d').date(),
                prioridad=prioridad,
                iniciativa_id=UUID(iniciativa_id) if iniciativa_id else None,
                problema_id=UUID(problema_id) if problema_id else None,
                creado_por_id=current_user.id,
                estado='PENDIENTE'
            )
            db.session.add(compromiso)

            # Registrar en historial
            historial = HistorialCompromiso(
                compromiso=compromiso,
                estado_anterior=None,
                estado_nuevo='PENDIENTE',
                usuario_id=current_user.id,
                comentario='Compromiso creado'
            )
            db.session.add(historial)

            db.session.commit()
            flash('Compromiso creado correctamente.', 'success')
            return redirect(url_for('compromisos.ver', id=compromiso.id))

    # Datos para formulario
    tipos = TipoCompromisoOperativo.query.filter_by(activo=True).order_by(TipoCompromisoOperativo.nombre).all()
    usuarios = Usuario.query.filter_by(activo=True).order_by(Usuario.username).all()
    iniciativas = Iniciativa.query.order_by(Iniciativa.nombre).limit(100).all()

    return render_template('compromisos/nuevo.html',
                           tipos=tipos,
                           usuarios=usuarios,
                           iniciativas=iniciativas)


@compromisos_bp.route('/<uuid:id>')
@login_required
def ver(id):
    """Ver detalle de un compromiso."""
    compromiso = CompromisoOperativo.query.get_or_404(id)
    historial = compromiso.historial.all()

    return render_template('compromisos/ver.html',
                           compromiso=compromiso,
                           historial=historial)


@compromisos_bp.route('/<uuid:id>/completar', methods=['POST'])
@login_required
def completar(id):
    """Marcar compromiso como completado."""
    compromiso = CompromisoOperativo.query.get_or_404(id)

    if not compromiso.puede_completar(current_user):
        abort(403)

    observaciones = request.form.get('observaciones', '').strip()
    estado_anterior = compromiso.estado

    compromiso.estado = 'COMPLETADO'
    compromiso.completado_en = datetime.utcnow()
    if observaciones:
        compromiso.observaciones = observaciones

    # Registrar en historial
    historial = HistorialCompromiso(
        compromiso_id=compromiso.id,
        estado_anterior=estado_anterior,
        estado_nuevo='COMPLETADO',
        usuario_id=current_user.id,
        comentario=observaciones or 'Marcado como completado'
    )
    db.session.add(historial)
    db.session.commit()

    flash('Compromiso marcado como completado.', 'success')

    # Si es HTMX, retornar fragmento
    if request.headers.get('HX-Request'):
        return render_template('compromisos/_estado.html', compromiso=compromiso)

    return redirect(url_for('compromisos.ver', id=id))


@compromisos_bp.route('/<uuid:id>/verificar', methods=['POST'])
@login_required
def verificar(id):
    """Verificar un compromiso completado."""
    if not current_user.puede_verificar_compromisos():
        abort(403)

    compromiso = CompromisoOperativo.query.get_or_404(id)

    if compromiso.estado != 'COMPLETADO':
        flash('Solo se pueden verificar compromisos completados.', 'error')
        return redirect(url_for('compromisos.ver', id=id))

    estado_anterior = compromiso.estado
    compromiso.estado = 'VERIFICADO'
    compromiso.verificado_por_id = current_user.id
    compromiso.verificado_en = datetime.utcnow()

    # Registrar en historial
    historial = HistorialCompromiso(
        compromiso_id=compromiso.id,
        estado_anterior=estado_anterior,
        estado_nuevo='VERIFICADO',
        usuario_id=current_user.id,
        comentario='Verificado'
    )
    db.session.add(historial)
    db.session.commit()

    flash('Compromiso verificado.', 'success')

    if request.headers.get('HX-Request'):
        return render_template('compromisos/_estado.html', compromiso=compromiso)

    return redirect(url_for('compromisos.ver', id=id))


@compromisos_bp.route('/<uuid:id>/rechazar', methods=['POST'])
@login_required
def rechazar(id):
    """Rechazar un compromiso completado (volver a pendiente)."""
    if not current_user.puede_verificar_compromisos():
        abort(403)

    compromiso = CompromisoOperativo.query.get_or_404(id)
    motivo = request.form.get('motivo', '').strip()

    if compromiso.estado != 'COMPLETADO':
        flash('Solo se pueden rechazar compromisos completados.', 'error')
        return redirect(url_for('compromisos.ver', id=id))

    estado_anterior = compromiso.estado
    compromiso.estado = 'PENDIENTE'
    compromiso.completado_en = None

    # Registrar en historial
    historial = HistorialCompromiso(
        compromiso_id=compromiso.id,
        estado_anterior=estado_anterior,
        estado_nuevo='PENDIENTE',
        usuario_id=current_user.id,
        comentario=f'Rechazado: {motivo}' if motivo else 'Rechazado'
    )
    db.session.add(historial)
    db.session.commit()

    flash('Compromiso rechazado y devuelto a pendiente.', 'warning')

    if request.headers.get('HX-Request'):
        return render_template('compromisos/_estado.html', compromiso=compromiso)

    return redirect(url_for('compromisos.ver', id=id))
