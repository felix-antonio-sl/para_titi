# =============================================================================
# app/routes/compromisos.py — Gestión de Compromisos Operativos
# =============================================================================

from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import CompromisoOperativo, TipoCompromisoOperativo, Iniciativa, Usuario
from app.services.compromisos_service import CompromisosService

compromisos_bp = Blueprint("compromisos", __name__)


@compromisos_bp.route("/")
@login_required
def lista():
    """Lista de compromisos con filtros."""
    page = request.args.get("page", 1, type=int)

    # Filtros
    estado = request.args.get("estado")
    responsable_id = request.args.get("responsable")
    solo_vencidos = request.args.get("vencidos") == "1"
    solo_mios = request.args.get("mios") == "1"

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
        query = query.filter(
            CompromisoOperativo.estado.in_(["PENDIENTE", "EN_PROGRESO"])
        )

    if responsable_id:
        query = query.filter(CompromisoOperativo.responsable_id == responsable_id)

    if solo_vencidos:
        query = query.filter(CompromisoOperativo.fecha_limite < date.today())

    if solo_mios:
        query = query.filter(CompromisoOperativo.responsable_id == current_user.id)

    # Ordenar y paginar
    query = query.order_by(
        CompromisoOperativo.fecha_limite, CompromisoOperativo.prioridad.desc()
    )

    paginacion = query.paginate(page=page, per_page=20, error_out=False)

    # Datos para filtros
    tipos = TipoCompromisoOperativo.query.filter_by(activo=True).all()

    return render_template(
        "compromisos/lista.html",
        compromisos=paginacion.items,
        paginacion=paginacion,
        tipos=tipos,
        filtros={
            "estado": estado,
            "responsable": responsable_id,
            "vencidos": solo_vencidos,
            "mios": solo_mios,
        },
    )


@compromisos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    """Crear nuevo compromiso."""
    if not current_user.puede_crear_compromisos():
        abort(403)

    if request.method == "POST":
        tipo_id = request.form.get("tipo_id")
        descripcion = request.form.get("descripcion", "").strip()
        responsable_id = request.form.get("responsable_id")
        fecha_limite = request.form.get("fecha_limite")
        prioridad = request.form.get("prioridad", "MEDIA")
        iniciativa_id = request.form.get("iniciativa_id") or None
        problema_id = request.form.get("problema_id") or None

        if not all([tipo_id, descripcion, responsable_id, fecha_limite]):
            flash("Todos los campos obligatorios deben completarse.", "error")
        else:
            try:
                CompromisosService.crear_compromiso(
                    request.form.to_dict(), current_user.id
                )
                flash("Compromiso creado correctamente.", "success")
                # Nota: Si necesitamos redirigir al ID, el servicio deberia retornar el objeto.
                # Asumimos que retornamos al listado o buscamos el ultimo creado si fuera critico,
                # pero para simplificar la refactorizacion, redirigimos a la lista o capturamos el objeto devuelto.
                # Update: el servicio retorna el objeto compromiso.
                return redirect(url_for("compromisos.lista"))
            except ValueError as e:
                flash(str(e), "error")

    # Datos para formulario
    tipos = (
        TipoCompromisoOperativo.query.filter_by(activo=True)
        .order_by(TipoCompromisoOperativo.nombre)
        .all()
    )
    usuarios = Usuario.query.filter_by(activo=True).order_by(Usuario.username).all()
    iniciativas = Iniciativa.query.order_by(Iniciativa.nombre).limit(100).all()

    return render_template(
        "compromisos/nuevo.html",
        tipos=tipos,
        usuarios=usuarios,
        iniciativas=iniciativas,
    )


@compromisos_bp.route("/<uuid:id>")
@login_required
def ver(id):
    """Ver detalle de un compromiso."""
    compromiso = CompromisoOperativo.query.get_or_404(id)
    historial = compromiso.historial.all()

    return render_template(
        "compromisos/ver.html", compromiso=compromiso, historial=historial
    )


@compromisos_bp.route("/<uuid:id>/completar", methods=["POST"])
@login_required
def completar(id):
    """Marcar compromiso como completado."""
    compromiso = CompromisoOperativo.query.get_or_404(id)

    if not compromiso.puede_completar(current_user):
        abort(403)

    observaciones = request.form.get("observaciones", "").strip()

    try:
        compromiso = CompromisosService.completar_compromiso(
            id, observaciones, current_user.id
        )
        flash("Compromiso marcado como completado.", "success")
    except ValueError as e:
        flash(str(e), "error")

    # Si es HTMX, retornar fragmento
    if request.headers.get("HX-Request"):
        return render_template("compromisos/_estado.html", compromiso=compromiso)

    return redirect(url_for("compromisos.ver", id=id))


@compromisos_bp.route("/<uuid:id>/verificar", methods=["POST"])
@login_required
def verificar(id):
    """Verificar un compromiso completado."""
    if not current_user.puede_verificar_compromisos():
        abort(403)

    compromiso = CompromisoOperativo.query.get_or_404(id)

    if compromiso.estado != "COMPLETADO":
        flash("Solo se pueden verificar compromisos completados.", "error")
        return redirect(url_for("compromisos.ver", id=id))

    try:
        compromiso = CompromisosService.verificar_compromiso(id, current_user.id)
        flash("Compromiso verificado.", "success")
    except ValueError as e:
        flash(str(e), "error")

    if request.headers.get("HX-Request"):
        # Re-consultar si hubo error o usar el objeto si funcionó
        # Para seguridad, recargamos si hubo excepcion (aunque variable compromiso podria no estar actualizada en excepcion)
        # Mejor simplificacion:
        c = CompromisoOperativo.query.get(id)
        return render_template("compromisos/_estado.html", compromiso=c)

    return redirect(url_for("compromisos.ver", id=id))


@compromisos_bp.route("/<uuid:id>/rechazar", methods=["POST"])
@login_required
def rechazar(id):
    """Rechazar un compromiso completado (volver a pendiente)."""
    if not current_user.puede_verificar_compromisos():
        abort(403)

    compromiso = CompromisoOperativo.query.get_or_404(id)
    motivo = request.form.get("motivo", "").strip()

    if compromiso.estado != "COMPLETADO":
        flash("Solo se pueden rechazar compromisos completados.", "error")
        return redirect(url_for("compromisos.ver", id=id))

    motivo = request.form.get("motivo", "").strip()

    try:
        compromiso = CompromisosService.rechazar_compromiso(id, motivo, current_user.id)
        flash("Compromiso rechazado y devuelto a pendiente.", "warning")
    except ValueError as e:
        flash(str(e), "error")

    if request.headers.get("HX-Request"):
        c = CompromisoOperativo.query.get(id)
        return render_template("compromisos/_estado.html", compromiso=c)

    return redirect(url_for("compromisos.ver", id=id))
