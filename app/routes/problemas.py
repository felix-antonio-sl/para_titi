# =============================================================================
# app/routes/problemas.py — Gestión de Problemas IPR
# =============================================================================

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import ProblemaIPR, Iniciativa, Convenio
from app.services.problemas_service import ProblemasService

problemas_bp = Blueprint("problemas", __name__)


@problemas_bp.route("/")
@login_required
def lista():
    """Lista de problemas con filtros."""
    page = request.args.get("page", 1, type=int)

    # Filtros
    estado = request.args.get("estado")
    tipo = request.args.get("tipo")
    impacto = request.args.get("impacto")

    # Query base
    query = ProblemaIPR.query

    # Aplicar filtros
    if estado:
        query = query.filter(ProblemaIPR.estado == estado)
    else:
        # Por defecto, solo abiertos
        query = query.filter(ProblemaIPR.estado.in_(["ABIERTO", "EN_GESTION"]))

    if tipo:
        query = query.filter(ProblemaIPR.tipo == tipo)

    if impacto:
        query = query.filter(ProblemaIPR.impacto == impacto)

    # Ordenar
    query = query.order_by(ProblemaIPR.detectado_en.desc())

    paginacion = query.paginate(page=page, per_page=20, error_out=False)

    return render_template(
        "problemas/lista.html",
        problemas=paginacion.items,
        paginacion=paginacion,
        filtros={"estado": estado, "tipo": tipo, "impacto": impacto},
    )


@problemas_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    """Registrar nuevo problema."""
    if request.method == "POST":
        iniciativa_id = request.form.get("iniciativa_id")
        convenio_id = request.form.get("convenio_id") or None
        tipo = request.form.get("tipo")
        impacto = request.form.get("impacto")
        descripcion = request.form.get("descripcion", "").strip()
        impacto_descripcion = request.form.get("impacto_descripcion", "").strip()
        solucion_propuesta = request.form.get("solucion_propuesta", "").strip()

        if not all([iniciativa_id, tipo, impacto, descripcion]):
            flash("Todos los campos obligatorios deben completarse.", "error")
        else:
            try:
                problema = ProblemasService.crear_problema(
                    request.form.to_dict(), current_user.id
                )
                flash("Problema registrado correctamente.", "success")
                return redirect(url_for("problemas.ver", id=problema.id))
            except ValueError as e:
                flash(str(e), "error")

    # Datos para formulario
    iniciativas = Iniciativa.query.order_by(Iniciativa.nombre).limit(100).all()

    # Tipos y impactos (desde ENUMs de v4.1)
    tipos = [
        "TECNICO",
        "FINANCIERO",
        "ADMINISTRATIVO",
        "LEGAL",
        "COORDINACION",
        "EXTERNO",
    ]
    impactos = [
        "BLOQUEA_PAGO",
        "RETRASA_OBRA",
        "RETRASA_CONVENIO",
        "RIESGO_RENDICION",
        "AFECTA_IMAGEN",
        "OTRO",
    ]

    return render_template(
        "problemas/nuevo.html", iniciativas=iniciativas, tipos=tipos, impactos=impactos
    )


@problemas_bp.route("/<uuid:id>")
@login_required
def ver(id):
    """Ver detalle de un problema."""
    problema = ProblemaIPR.query.get_or_404(id)
    compromisos = problema.compromisos.all()

    return render_template(
        "problemas/ver.html", problema=problema, compromisos=compromisos
    )


@problemas_bp.route("/<uuid:id>/resolver", methods=["POST"])
@login_required
def resolver(id):
    """Marcar problema como resuelto."""
    if not current_user.puede_verificar_compromisos():
        abort(403)

    problema = ProblemaIPR.query.get_or_404(id)
    solucion_aplicada = request.form.get("solucion_aplicada", "").strip()

    try:
        ProblemasService.resolver_problema(id, solucion_aplicada, current_user.id)
        flash("Problema marcado como resuelto.", "success")
    except ValueError as e:
        flash(str(e), "error")

    return redirect(url_for("problemas.ver", id=id))


@problemas_bp.route("/<uuid:id>/cerrar", methods=["POST"])
@login_required
def cerrar_sin_resolver(id):
    """Cerrar problema sin resolver."""
    if not current_user.puede_verificar_compromisos():
        abort(403)

    problema = ProblemaIPR.query.get_or_404(id)
    motivo = request.form.get("motivo", "").strip()

    try:
        ProblemasService.cerrar_problema(id, motivo, current_user.id)
        flash("Problema cerrado.", "info")
    except ValueError as e:
        flash(str(e), "error")

    return redirect(url_for("problemas.ver", id=id))
