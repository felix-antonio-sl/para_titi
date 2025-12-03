# =============================================================================
# app/routes/reuniones.py — Sistema de Reuniones de Crisis
# Casos de uso: AR-03, AR-04, AR-05
# =============================================================================

from datetime import date, datetime, timedelta
from uuid import UUID

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import inspect, func

from app.extensions import db
from app.models import (
    Iniciativa,
    CompromisoOperativo,
    AlertaIPR,
    Usuario,
    Division,
)
from app.models.reuniones import Reunion, TemaReunion, ContextoPuntoCrisis, InstanciaColectiva

reuniones_bp = Blueprint('reuniones', __name__)


def _reuniones_habilitadas() -> bool:
    """Verifica si la extensión gore_instancias.reunion_crisis existe en la BD."""
    insp = inspect(db.engine)
    return insp.has_table('reunion_crisis', schema='gore_instancias')


@reuniones_bp.route('/')
@login_required
def lista():
    """Lista de reuniones."""
    if not _reuniones_habilitadas():
        flash('El sistema de reuniones aún no está habilitado en el modelo de datos v4.1.', 'info')
        return render_template('reuniones/no_disponible.html')

    page = request.args.get('page', 1, type=int)
    
    query = Reunion.query.join(InstanciaColectiva).order_by(InstanciaColectiva.fecha.desc())
    paginacion = query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('reuniones/lista.html',
                           reuniones=paginacion.items,
                           paginacion=paginacion)


@reuniones_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    """Crear nueva reunión."""
    if not _reuniones_habilitadas():
        return render_template('reuniones/no_disponible.html')

    if not current_user.puede_verificar_compromisos():
        abort(403)
    
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        fecha_str = request.form.get('fecha')
        hora_inicio_str = request.form.get('hora_inicio')

        if not all([titulo, fecha_str]):
            flash('Título y fecha son obligatorios.', 'error')
        else:
            try:
                fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d')
            except ValueError:
                flash('Fecha inválida.', 'error')
                return redirect(url_for('reuniones.nueva'))

            hora_inicio = None
            if hora_inicio_str:
                try:
                    hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
                except ValueError:
                    flash('Hora inválida.', 'error')
                    return redirect(url_for('reuniones.nueva'))

            # Crear instancia_colectiva + reunion_crisis de forma categóricamente coherente
            reunion = Reunion.crear(
                fecha=fecha_dt,
                titulo=titulo,
                lugar=None,
                hora_inicio=hora_inicio,
                organizador_id=current_user.id,
            )
            db.session.commit()

            flash('Reunión creada. Ahora puede agregar temas a la agenda.', 'success')
            return redirect(url_for('reuniones.preparar', id=reunion.id))
    
    # Fecha sugerida: próximo lunes
    hoy = date.today()
    dias_hasta_lunes = (7 - hoy.weekday()) % 7
    if dias_hasta_lunes == 0:
        dias_hasta_lunes = 7
    fecha_sugerida = hoy + timedelta(days=dias_hasta_lunes)
    
    return render_template('reuniones/nueva.html', fecha_sugerida=fecha_sugerida)


@reuniones_bp.route('/<uuid:id>/preparar')
@login_required
def preparar(id):
    """Preparar agenda de reunión (AR-03)."""
    if not _reuniones_habilitadas():
        return render_template('reuniones/no_disponible.html')

    reunion = Reunion.query.get_or_404(id)
    
    # Obtener temas actuales
    temas = reunion.temas.order_by(TemaReunion.numero).all()
    
    # Sugerencias automáticas basadas en alertas y compromisos
    sugerencias = _generar_sugerencias()
    
    return render_template('reuniones/preparar.html',
                           reunion=reunion,
                           temas=temas,
                           sugerencias=sugerencias)


def _generar_sugerencias():
    """Genera sugerencias de temas basadas en alertas y compromisos."""
    sugerencias = []
    today = date.today()
    
    # Alertas críticas activas
    alertas = AlertaIPR.query.filter(
        AlertaIPR.activa == True,
        AlertaIPR.nivel.in_(['CRITICO', 'ALTO'])
    ).limit(5).all()
    
    for alerta in alertas:
        sugerencias.append({
            'tipo': 'ALERTA',
            'titulo': f'Alerta: {alerta.mensaje[:50]}',
            'descripcion': alerta.mensaje,
            'alerta_id': str(alerta.id),
            'iniciativa_id': str(alerta.iniciativa_id) if alerta.iniciativa_id else None
        })
    
    # Compromisos vencidos
    vencidos = CompromisoOperativo.query.filter(
        CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
        CompromisoOperativo.fecha_limite < today
    ).limit(5).all()
    
    for comp in vencidos:
        sugerencias.append({
            'tipo': 'COMPROMISO_VENCIDO',
            'titulo': f'Vencido: {comp.descripcion[:50]}',
            'descripcion': f'Responsable: {comp.responsable.nombre_completo if comp.responsable else "Sin asignar"}. Vencido hace {(today - comp.fecha_limite).days} días.',
            'compromiso_id': str(comp.id),
            'iniciativa_id': str(comp.iniciativa_id) if comp.iniciativa_id else None
        })
    
    # Compromisos completados pendientes de verificación
    completados = CompromisoOperativo.query.filter(
        CompromisoOperativo.estado == 'COMPLETADO'
    ).limit(5).all()
    
    for comp in completados:
        sugerencias.append({
            'tipo': 'COMPROMISO_COMPLETADO',
            'titulo': f'Verificar: {comp.descripcion[:50]}',
            'descripcion': f'Completado por: {comp.responsable.nombre_completo if comp.responsable else "Sin asignar"}',
            'compromiso_id': str(comp.id),
            'iniciativa_id': str(comp.iniciativa_id) if comp.iniciativa_id else None
        })
    
    # IPR críticas
    ipr_criticas = Iniciativa.query.filter(
        Iniciativa.nivel_alerta == 'CRITICO'
    ).limit(3).all()
    
    for ipr in ipr_criticas:
        sugerencias.append({
            'tipo': 'IPR_CRITICA',
            'titulo': f'IPR Crítica: {ipr.nombre[:50]}',
            'descripcion': f'Responsable: {ipr.responsable.nombre_completo if ipr.responsable else "Sin asignar"}',
            'iniciativa_id': str(ipr.id)
        })
    
    return sugerencias


@reuniones_bp.route('/<uuid:id>/agregar-tema', methods=['POST'])
@login_required
def agregar_tema(id):
    """Agregar tema a la agenda."""
    if not _reuniones_habilitadas():
        return render_template('reuniones/no_disponible.html')

    reunion = Reunion.query.get_or_404(id)

    titulo = request.form.get('titulo', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    iniciativa_id = request.form.get('iniciativa_id') or None
    compromiso_id = request.form.get('compromiso_id') or None
    alerta_id = request.form.get('alerta_id') or None

    if not titulo:
        flash('El título del tema es obligatorio.', 'error')
        return redirect(url_for('reuniones.preparar', id=id))

    # Calcular siguiente número de punto_tabla usando consulta directa a la BD
    max_numero = db.session.query(func.max(TemaReunion.numero)).filter(
        TemaReunion.instancia_id == reunion.id
    ).scalar()
    orden = (max_numero + 1) if max_numero is not None else 1

    # Crear punto de tabla base (gore_instancias.punto_tabla)
    tema = TemaReunion(
        instancia_id=reunion.id,
        numero=orden,
        # Todos los temas de crisis se consideran RESOLUTIVOS a nivel de dominio
        tipo='RESOLUTIVO',
        titulo=titulo,  # alias sobre materia
        estado='PENDIENTE',
    )
    db.session.add(tema)
    db.session.flush()  # Necesario para obtener tema.id

    # Si hay algún target de crisis, crear contexto_punto_crisis
    target_uuid = None
    target_tipo = None
    if iniciativa_id:
        target_tipo = 'INICIATIVA'
        target_uuid = UUID(iniciativa_id)
    elif problema_id := request.form.get('problema_id'):
        target_tipo = 'PROBLEMA'
        target_uuid = UUID(problema_id)
    elif alerta_id:
        target_tipo = 'ALERTA'
        target_uuid = UUID(alerta_id)
    elif compromiso_id:
        target_tipo = 'COMPROMISO'
        target_uuid = UUID(compromiso_id)

    if target_uuid and target_tipo:
        contexto = ContextoPuntoCrisis(
            punto_tabla_id=tema.id,
            target_tipo=target_tipo,
            target_id=target_uuid,
            notas=descripcion,
            # iniciativa_id se derivará en BD por trigger; este valor es placeholder
            iniciativa_id=target_uuid,
        )
        db.session.add(contexto)

    db.session.commit()

    flash('Tema agregado a la agenda.', 'success')
    return redirect(url_for('reuniones.preparar', id=id))


@reuniones_bp.route('/<uuid:id>/conducir')
@login_required
def conducir(id):
    """Conducir reunión en curso (AR-04)."""
    if not _reuniones_habilitadas():
        return render_template('reuniones/no_disponible.html')

    reunion = Reunion.query.get_or_404(id)

    # Iniciar reunión si está convocada (FSM de instancia_colectiva)
    if reunion.iniciar():
        db.session.commit()
    
    temas = reunion.temas.order_by(TemaReunion.numero).all()
    
    # Usuarios para asignar compromisos
    usuarios = Usuario.query.filter_by(activo=True).order_by(Usuario.username).all()
    
    return render_template('reuniones/conducir.html',
                           reunion=reunion,
                           temas=temas,
                           usuarios=usuarios)


@reuniones_bp.route('/<uuid:id>/tema/<uuid:tema_id>/revisar', methods=['POST'])
@login_required
def revisar_tema(id, tema_id):
    """Marcar tema como revisado."""
    if not _reuniones_habilitadas():
        return render_template('reuniones/no_disponible.html')

    tema = TemaReunion.query.get_or_404(tema_id)

    notas = request.form.get('notas', '').strip()
    # En el dominio base, el estado equivalente es TRATADO
    tema.estado = 'TRATADO'
    tema.resumen_discusion = notas
    db.session.commit()
    
    flash('Tema marcado como revisado.', 'success')
    return redirect(url_for('reuniones.conducir', id=id))


@reuniones_bp.route('/<uuid:id>/finalizar', methods=['POST'])
@login_required
def finalizar(id):
    """Finalizar reunión."""
    if not _reuniones_habilitadas():
        return render_template('reuniones/no_disponible.html')

    reunion = Reunion.query.get_or_404(id)

    resumen = request.form.get('resumen', '').strip()
    reunion.finalizar(resumen_texto=resumen)
    db.session.commit()
    
    flash('Reunión finalizada.', 'success')
    return redirect(url_for('reuniones.ver', id=id))


@reuniones_bp.route('/<uuid:id>')
@login_required
def ver(id):
    """Ver detalle de reunión."""
    if not _reuniones_habilitadas():
        return render_template('reuniones/no_disponible.html')

    reunion = Reunion.query.get_or_404(id)
    temas = reunion.temas.order_by(TemaReunion.numero).all()
    
    return render_template('reuniones/ver.html',
                           reunion=reunion,
                           temas=temas)
