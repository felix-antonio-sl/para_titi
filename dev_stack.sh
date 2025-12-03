#!/usr/bin/env bash
# =============================================================================
# dev_stack.sh — Orquestador de entorno de desarrollo
# GORE Ñuble: BD v4.1 (data-gore) + App Crisis IPR (para_titi)
# =============================================================================
#
# Uso básico:
#   bash dev_stack.sh
#       - Asegura que gore_db esté arriba (SIN borrar datos)
#       - Levanta docker-compose.dev.yml de para_titi (hot reload en 5001)
#
# Opciones:
#   --init-model   Inicializa/actualiza modelo v4.1 ejecutando etl/init_modelo.sh
#                  (no borra volumen, solo aplica DDL/funciones sobre la BD existente)
#   --reset-db     docker compose down -v en data-gore + docker compose up -d
#                  y luego etl/init_modelo.sh (REINICIO LIMPIO, PIERDE DATOS)
#
# Variables opcionales:
#   DATA_GORE_DIR  Ruta al repo data-gore (por defecto ../data-gore)
#
# Requisitos previos:
#   - Docker + Docker Compose
#   - Repositorios hermanos:
#       /.../fx_felixiando/data-gore
#       /.../fx_felixiando/para_titi (este script)
# =============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARA_TITI_DIR="$ROOT_DIR"
DATA_GORE_DIR="${DATA_GORE_DIR:-"$ROOT_DIR/../data-gore"}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "${CYAN}[STEP]${NC} $1"; }

usage() {
  cat <<EOF
Uso: bash dev_stack.sh [--init-model | --reset-db]

Sin opciones:
  - Asegura que gore_db esté arriba (sin tocar datos)
  - Levanta docker-compose.dev.yml (app en http://localhost:5001)

Opciones:
  --init-model   Ejecuta etl/init_modelo.sh sobre la BD existente
  --reset-db     docker compose down -v + up -d + etl/init_modelo.sh (borra datos)
EOF
}

RESET_DB=false
INIT_MODEL=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reset-db)
      RESET_DB=true
      INIT_MODEL=true  # reset implica siempre re-inicializar modelo
      shift
      ;;
    --init-model)
      INIT_MODEL=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      log_error "Opción desconocida: $1"
      usage
      exit 1
      ;;
  esac
done

# -----------------------------------------------------------------------------
# 1. Verificar repositorio data-gore
# -----------------------------------------------------------------------------
if [[ ! -d "$DATA_GORE_DIR" ]]; then
  log_error "No se encontró el directorio data-gore en: $DATA_GORE_DIR"
  log_info  "Configura DATA_GORE_DIR o ajusta la estructura de carpetas."
  exit 1
fi

# -----------------------------------------------------------------------------
# 2. Gestionar BD gore_db (data-gore)
# -----------------------------------------------------------------------------
log_step "Usando data-gore en: $DATA_GORE_DIR"

if [[ "$RESET_DB" == true ]]; then
  log_warn "Reiniciando COMPLETAMENTE la BD (docker compose down -v)."
  ( cd "$DATA_GORE_DIR" && docker compose down -v )
  log_info "Levantando gore_db desde cero..."
  ( cd "$DATA_GORE_DIR" && docker compose up -d postgres )
else
  log_info "Asegurando que gore_db esté corriendo (sin borrar volumen)..."
  ( cd "$DATA_GORE_DIR" && docker compose up -d postgres )
fi

# Espera breve para que Postgres quede listo (healthcheck también ayuda)
sleep 5 || true

if [[ "$INIT_MODEL" == true ]]; then
  log_step "Inicializando / actualizando modelo v4.1 con etl/init_modelo.sh..."
  ( cd "$DATA_GORE_DIR" && ./etl/init_modelo.sh )
else
  log_info "Saltando init_modelo.sh (no se pidió --init-model ni --reset-db)."
fi

# -----------------------------------------------------------------------------
# 3. Levantar app para_titi en modo desarrollo (hot reload)
# -----------------------------------------------------------------------------
log_step "Levantando para_titi con docker-compose.dev.yml (puerto 5001)..."
cd "$PARA_TITI_DIR"

echo ""
log_info "Comando: docker compose -f docker-compose.dev.yml up"
log_info "UI disponible en: http://localhost:5001 (admin/admin123)"
log_info "Ctrl+C para detener sólo la app (la BD sigue corriendo si no hiciste down -v)."

docker compose -f docker-compose.dev.yml up
