# =============================================================================
# app/routes/ipr.py — Gestión de Iniciativas (IPR)
# Casos de uso: EO-05, EO-06, EO-07, EO-08
# =============================================================================

from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Iniciativa, Division, Usuario, Convenio, InformeAvance


from app.services.ipr_service import IPRService

ipr_bp = Blueprint("ipr", __name__)


@ipr_bp.route("/")
@login_required
def lista():
    """Lista de IPR con filtros."""
    page = request.args.get("page", 1, type=int)

    # Filtros
    division_id = request.args.get("division")
    nivel_alerta = request.args.get("nivel_alerta")
    con_problemas = request.args.get("con_problemas")
    busqueda = request.args.get("q", "").strip()

    # Query base según permisos
    if current_user.puede_ver_todas_ipr():
        query = Iniciativa.query
    else:
        # Jefes y encargados ven sus IPR asignadas
        query = Iniciativa.query.filter(Iniciativa.responsable_id == current_user.id)

    # Aplicar filtros
    if division_id:
        query = query.filter(Iniciativa.division_responsable_id == division_id)

    if nivel_alerta:
        query = query.filter(Iniciativa.nivel_alerta == nivel_alerta)

    if con_problemas == "1":
        query = query.filter(Iniciativa.tiene_problemas_abiertos == True)

    if busqueda:
        query = query.filter(
            Iniciativa.nombre.ilike(f"%{busqueda}%")
            | Iniciativa.codigo_interno.ilike(f"%{busqueda}%")
        )

    # Ordenar y paginar
    query = query.order_by(
        Iniciativa.nivel_alerta.desc(),
        Iniciativa.tiene_problemas_abiertos.desc(),
        Iniciativa.nombre,
    )

    paginacion = query.paginate(page=page, per_page=20, error_out=False)

    # Datos para filtros
    divisiones = Division.query.order_by(Division.nombre).all()

    return render_template(
        "ipr/lista.html",
        iniciativas=paginacion.items,
        paginacion=paginacion,
        divisiones=divisiones,
        filtros={
            "division": division_id,
            "nivel_alerta": nivel_alerta,
            "con_problemas": con_problemas,
            "q": busqueda,
        },
    )


@ipr_bp.route("/<uuid:id>")
@login_required
def ficha(id):
    """Ficha detallada de una IPR."""
    iniciativa = Iniciativa.query.get_or_404(id)

    # Verificar permisos
    if not puede_ver_ipr(current_user, iniciativa):
        abort(403)

    # Datos relacionados
    problemas = iniciativa.problemas.order_by(ProblemaIPR.detectado_en.desc()).all()
    compromisos = iniciativa.compromisos.order_by(
        CompromisoOperativo.fecha_limite
    ).all()
    alertas = iniciativa.alertas.filter(AlertaIPR.activa == True).all()
    convenios = iniciativa.convenios.all()

    return render_template(
        "ipr/ficha.html",
        ipr=iniciativa,
        problemas=problemas,
        compromisos=compromisos,
        alertas=alertas,
        convenios=convenios,
    )


@ipr_bp.route("/<uuid:id>/asignar-responsable", methods=["POST"])
@login_required
def asignar_responsable(id):
    """Asignar responsable a una IPR (solo admin)."""
    if not current_user.puede_ver_todas_ipr():
        abort(403)

    iniciativa = Iniciativa.query.get_or_404(id)
    responsable_id = request.form.get("responsable_id")

    if responsable_id:
        from uuid import UUID

        try:
            IPRService.asignar_responsable(id, UUID(responsable_id))
            flash("Responsable asignado correctamente.", "success")
        except ValueError as e:
            flash(str(e), "error")

    # Retornar fragmento HTMX
    return render_template("ipr/_responsable.html", ipr=iniciativa)


def puede_ver_ipr(usuario, iniciativa):
    """Verifica si el usuario puede ver la IPR."""
    if usuario.puede_ver_todas_ipr():
        return True
    if iniciativa.responsable_id == usuario.id:
        return True
    return False


def puede_editar_ipr(usuario, iniciativa):
    """Verifica si el usuario puede editar la IPR."""
    if usuario.puede_ver_todas_ipr():
        return True
    if iniciativa.responsable_id == usuario.id:
        return True
    return False


# =============================================================================
# Registrar Informe de Avance (EO-05)
# =============================================================================


@ipr_bp.route("/<uuid:id>/avance", methods=["GET", "POST"])
@login_required
def registrar_avance(id):
    """Registrar informe de avance para una IPR."""
    iniciativa = Iniciativa.query.get_or_404(id)

    if not puede_editar_ipr(current_user, iniciativa):
        abort(403)

    # Obtener convenios de la IPR para seleccionar
    convenios = iniciativa.convenios.all()

    if request.method == "POST":
        convenio_id = request.form.get("convenio_id")
        numero = request.form.get("numero", type=int)
        tipo = request.form.get("tipo", "MENSUAL")
        periodo_desde = request.form.get("periodo_desde")
        periodo_hasta = request.form.get("periodo_hasta")
        avance_fisico = request.form.get("avance_fisico", type=float)
        avance_financiero = request.form.get("avance_financiero", type=float)
        resumen = request.form.get("resumen", "").strip()

        if not all([convenio_id, numero, periodo_desde, periodo_hasta]):
            flash("Complete todos los campos obligatorios.", "error")
        else:
            try:
                # Preparar datos para el servicio
                data = request.form.to_dict()
                usuario_id = (
                    current_user.persona_id
                    if hasattr(current_user, "persona_id")
                    else None
                )

                IPRService.registrar_avance(id, data, usuario_id)

                flash(
                    f"Informe de avance #{numero} registrado correctamente.", "success"
                )
                return redirect(url_for("ipr.ficha", id=id))
            except ValueError as e:
                flash(f"Error al registrar avance: {str(e)}", "error")

    # Calcular siguiente número de informe
    ultimo_informe = None
    if convenios:
        ultimo_informe = (
            InformeAvance.query.filter(
                InformeAvance.convenio_id.in_([c.id for c in convenios])
            )
            .order_by(InformeAvance.numero.desc())
            .first()
        )

    siguiente_numero = (ultimo_informe.numero + 1) if ultimo_informe else 1

    return render_template(
        "ipr/registrar_avance.html",
        ipr=iniciativa,
        convenios=convenios,
        siguiente_numero=siguiente_numero,
        today=date.today(),
    )


@ipr_bp.route("/<uuid:id>/historial")
@login_required
def historial(id):
    """Ver historial de avances de una IPR."""
    iniciativa = Iniciativa.query.get_or_404(id)

    if not puede_ver_ipr(current_user, iniciativa):
        abort(403)

    # Obtener todos los informes de avance de los convenios de esta IPR
    convenios = iniciativa.convenios.all()
    informes = []

    for convenio in convenios:
        for informe in convenio.informes_avance.order_by(
            InformeAvance.numero.desc()
        ).all():
            informes.append({"informe": informe, "convenio": convenio})

    # Ordenar por fecha
    informes.sort(key=lambda x: x["informe"].fecha_emision or date.min, reverse=True)

    return render_template("ipr/historial.html", ipr=iniciativa, informes=informes)


# Imports al final para evitar circular
from app.models import ProblemaIPR, CompromisoOperativo, AlertaIPR
