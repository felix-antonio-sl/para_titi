# =============================================================================
# app/services/ipr_service.py — Lógica de Negocio para IPR
# =============================================================================

from datetime import date, datetime
import uuid
from uuid import UUID
from app.extensions import db
from app.models import Iniciativa, InformeAvance


class IPRService:
    """Servicio para la gestión de Iniciativas de Inversión (IPR)."""

    @staticmethod
    def crear_iniciativa(data: dict, creador_id: UUID = None) -> Iniciativa:
        """
        Crea una nueva iniciativa de inversión.
        """
        try:
            # Validar campos obligatorios
            required = [
                "codigo_interno",
                "nombre",
                "instrumento_id",
                "anio_presupuestario",
            ]
            for field in required:
                if not data.get(field):
                    raise ValueError(f"El campo {field} es obligatorio")

            # Crear instancia
            try:
                ipr_id = UUID(data.get("id")) if data.get("id") else uuid.uuid4()
            except (ValueError, TypeError):
                # Fallback o re-raise limpio
                raise ValueError(f"ID inválido: {data.get('id')}")

            iniciativa = Iniciativa(
                id=ipr_id,
                codigo_interno=data["codigo_interno"].strip(),
                nombre=data["nombre"].strip(),
                instrumento_id=UUID(data["instrumento_id"]),
                anio_presupuestario=int(data["anio_presupuestario"]),
                monto_solicitado=int(data.get("monto_solicitado", 0)),
                descripcion=data.get("descripcion", ""),
                # Defaults
                nivel_alerta="BAJO",
                tiene_problemas_abiertos=False,
                estado_fsm_id=uuid.uuid4(),  # Provisional hasta implementar FSM real
            )

            # Asignar división si viene
            if data.get("division_responsable_id"):
                iniciativa.division_responsable_id = UUID(
                    data["division_responsable_id"]
                )

            db.session.add(iniciativa)
            db.session.commit()
            return iniciativa

        except (ValueError, TypeError) as e:
            db.session.rollback()
            raise ValueError(f"Error al crear iniciativa: {str(e)}")

    @staticmethod
    def asignar_responsable(ipr_id: UUID, responsable_id: UUID) -> Iniciativa:
        """
        Asigna un responsable a una iniciativa.
        """
        iniciativa = Iniciativa.query.get(ipr_id)
        if not iniciativa:
            raise ValueError(f"Iniciativa {ipr_id} no encontrada")

        iniciativa.responsable_id = responsable_id
        db.session.commit()
        return iniciativa

    @staticmethod
    def registrar_avance(
        ipr_id: UUID, data: dict, usuario_id: UUID = None
    ) -> InformeAvance:
        """
        Registra un nuevo informe de avance y actualiza la IPR.
        """
        iniciativa = Iniciativa.query.get(ipr_id)
        if not iniciativa:
            raise ValueError(f"Iniciativa {ipr_id} no encontrada")

        # Extraer datos
        try:
            convenio_id = UUID(data["convenio_id"])
            numero = int(data["numero"])
            tipo = data.get("tipo", "MENSUAL")
            periodo_desde = datetime.strptime(data["periodo_desde"], "%Y-%m-%d").date()
            periodo_hasta = datetime.strptime(data["periodo_hasta"], "%Y-%m-%d").date()
            avance_fisico = (
                float(data["avance_fisico"]) if data.get("avance_fisico") else None
            )
            avance_financiero = (
                float(data["avance_financiero"])
                if data.get("avance_financiero")
                else None
            )
            resumen = data.get("resumen", "").strip()
        except (ValueError, KeyError) as e:
            raise ValueError(f"Datos inválidos para informe de avance: {str(e)}")

        # Obtener ID de persona desde el usuario
        from app.models import Usuario

        elaborador_persona_id = None
        if usuario_id:
            usuario = Usuario.query.get(usuario_id)
            if usuario:
                elaborador_persona_id = usuario.persona_id

        # Crear informe
        informe = InformeAvance(
            convenio_id=convenio_id,
            numero=numero,
            tipo=tipo,
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta,
            elaborador_id=elaborador_persona_id,
            resumen=resumen,
        )
        db.session.add(informe)

        # Actualizar IPR
        if avance_fisico is not None:
            iniciativa.avance_fisico = avance_fisico
        if avance_financiero is not None:
            iniciativa.avance_financiero = avance_financiero

        db.session.commit()
        return informe
