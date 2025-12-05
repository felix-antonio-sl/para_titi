# =============================================================================
# app/services/compromisos_service.py — Servicio de Compromisos
# =============================================================================

from datetime import datetime
from uuid import UUID
from app.extensions import db
from app.models import CompromisoOperativo, HistorialCompromiso


class CompromisosService:
    """CServicio para la gestión de Compromisos Operativos."""

    @staticmethod
    def crear_compromiso(data: dict, creador_id: UUID) -> CompromisoOperativo:
        """
        Crea un nuevo compromiso operativo y registra el historial.
        """
        try:
            tipo_id = UUID(data["tipo_id"])
            descripcion = data["descripcion"].strip()
            responsable_id = UUID(data["responsable_id"])
            fecha_limite = datetime.strptime(data["fecha_limite"], "%Y-%m-%d").date()
            prioridad = data.get("prioridad", "MEDIA")
            iniciativa_id = (
                UUID(data["iniciativa_id"]) if data.get("iniciativa_id") else None
            )
            problema_id = UUID(data["problema_id"]) if data.get("problema_id") else None
        except (ValueError, KeyError) as e:
            raise ValueError(f"Datos inválidos para crear compromiso: {str(e)}")

        compromiso = CompromisoOperativo(
            tipo_id=tipo_id,
            descripcion=descripcion,
            responsable_id=responsable_id,
            fecha_limite=fecha_limite,
            prioridad=prioridad,
            iniciativa_id=iniciativa_id,
            problema_id=problema_id,
            creado_por_id=creador_id,
            estado="PENDIENTE",
        )
        db.session.add(compromiso)

        # Historial inicial
        CompromisosService._registrar_historial(
            compromiso, None, "PENDIENTE", creador_id, "Compromiso creado"
        )

        db.session.commit()
        return compromiso

    @staticmethod
    def completar_compromiso(
        compromiso_id: UUID, observaciones: str, usuario_id: UUID
    ) -> CompromisoOperativo:
        """Marca un compromiso como completado."""
        compromiso = CompromisoOperativo.query.get(compromiso_id)
        if not compromiso:
            raise ValueError("Compromiso no encontrado")

        estado_anterior = compromiso.estado
        compromiso.estado = "COMPLETADO"
        compromiso.completado_en = datetime.utcnow()
        if observaciones:
            compromiso.observaciones = observaciones

        CompromisosService._registrar_historial(
            compromiso,
            estado_anterior,
            "COMPLETADO",
            usuario_id,
            observaciones or "Marcado como completado",
        )
        db.session.commit()
        return compromiso

    @staticmethod
    def verificar_compromiso(
        compromiso_id: UUID, usuario_id: UUID
    ) -> CompromisoOperativo:
        """Verifica un compromiso completado."""
        compromiso = CompromisoOperativo.query.get(compromiso_id)
        if not compromiso:
            raise ValueError("Compromiso no encontrado")

        if compromiso.estado != "COMPLETADO":
            raise ValueError("Solo se pueden verificar compromisos completados")

        estado_anterior = compromiso.estado
        compromiso.estado = "VERIFICADO"
        compromiso.verificado_por_id = usuario_id
        compromiso.verificado_en = datetime.utcnow()

        CompromisosService._registrar_historial(
            compromiso, estado_anterior, "VERIFICADO", usuario_id, "Verificado"
        )
        db.session.commit()
        return compromiso

    @staticmethod
    def rechazar_compromiso(
        compromiso_id: UUID, motivo: str, usuario_id: UUID
    ) -> CompromisoOperativo:
        """Rechaza un compromiso completado y lo devuelve a pendiente."""
        compromiso = CompromisoOperativo.query.get(compromiso_id)
        if not compromiso:
            raise ValueError("Compromiso no encontrado")

        if compromiso.estado != "COMPLETADO":
            raise ValueError("Solo se pueden rechazar compromisos completados")

        estado_anterior = compromiso.estado
        compromiso.estado = "PENDIENTE"
        compromiso.completado_en = None

        CompromisosService._registrar_historial(
            compromiso,
            estado_anterior,
            "PENDIENTE",
            usuario_id,
            f"Rechazado: {motivo}" if motivo else "Rechazado",
        )
        db.session.commit()
        return compromiso

    @staticmethod
    def _registrar_historial(
        compromiso, estado_ant, estado_nue, usuario_id, comentario
    ):
        """Helper para registrar historial."""
        historial = HistorialCompromiso(
            compromiso=compromiso,
            estado_anterior=estado_ant,
            estado_nuevo=estado_nue,
            usuario_id=usuario_id,
            comentario=comentario,
        )
        db.session.add(historial)
