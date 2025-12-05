# =============================================================================
# app/services/problemas_service.py — Servicio de Problemas IPR
# =============================================================================

from datetime import datetime
from uuid import UUID
from app.extensions import db
from app.models import ProblemaIPR


class ProblemasService:
    """Servicio para la gestión de Problemas IPR."""

    @staticmethod
    def crear_problema(data: dict, creador_id: UUID) -> ProblemaIPR:
        """Crea un nuevo problema IPR."""
        try:
            iniciativa_id = UUID(data["iniciativa_id"])
            convenio_id = UUID(data["convenio_id"]) if data.get("convenio_id") else None
            tipo = data["tipo"]
            impacto = data["impacto"]
            descripcion = data["descripcion"].strip()
            impacto_descripcion = data.get("impacto_descripcion", "").strip() or None
            solucion_propuesta = data.get("solucion_propuesta", "").strip() or None
        except (ValueError, KeyError) as e:
            raise ValueError(f"Datos inválidos para registrar problema: {str(e)}")

        problema = ProblemaIPR(
            iniciativa_id=iniciativa_id,
            convenio_id=convenio_id,
            tipo=tipo,
            impacto=impacto,
            descripcion=descripcion,
            impacto_descripcion=impacto_descripcion,
            solucion_propuesta=solucion_propuesta,
            detectado_por_id=creador_id,
            estado="ABIERTO",
        )
        db.session.add(problema)
        db.session.commit()
        return problema

    @staticmethod
    def resolver_problema(
        problema_id: UUID, solucion: str, usuario_id: UUID
    ) -> ProblemaIPR:
        """Marca un problema como resuelto."""
        problema = ProblemaIPR.query.get(problema_id)
        if not problema:
            raise ValueError("Problema no encontrado")

        if not solucion:
            raise ValueError("Debe describir la solución aplicada")

        problema.estado = "RESUELTO"
        problema.solucion_aplicada = solucion
        problema.resuelto_por_id = usuario_id
        problema.resuelto_en = datetime.utcnow()

        db.session.commit()
        return problema

    @staticmethod
    def cerrar_problema(
        problema_id: UUID, motivo: str, usuario_id: UUID
    ) -> ProblemaIPR:
        """Cierra un problema sin resolver."""
        problema = ProblemaIPR.query.get(problema_id)
        if not problema:
            raise ValueError("Problema no encontrado")

        problema.estado = "CERRADO_SIN_RESOLVER"
        problema.solucion_aplicada = (
            f"Cerrado sin resolver: {motivo}" if motivo else "Cerrado sin resolver"
        )
        problema.resuelto_por_id = usuario_id
        problema.resuelto_en = datetime.utcnow()

        db.session.commit()
        return problema
