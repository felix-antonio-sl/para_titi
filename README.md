# 🏛️ Sistema de Gestión de Crisis IPR — GORE Ñuble

Sistema web para la gestión de crisis en Iniciativas de Inversión Pública Regional (IPR) del Gobierno Regional de Ñuble.

## 📋 Características

- **Dashboard de Crisis**: Vista consolidada del estado de las IPR
- **Gestión de Compromisos**: Creación, seguimiento y verificación de compromisos operativos
- **Registro de Problemas**: Detección y seguimiento de nudos/problemas en IPR
- **Sistema de Alertas**: Alertas automáticas por vencimientos y situaciones críticas
- **Control de Acceso por Roles**: Admin Sistema, Admin Regional, Jefe División, Encargado Operativo

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.11, Flask 3.x, SQLAlchemy 2.x
- **Frontend**: Jinja2, HTMX, Alpine.js, TailwindCSS
- **Base de Datos**: PostgreSQL 16 + PostGIS, con **modelo IS-GORE ÑUBLE v4.1 ya cargado**
- **Infraestructura**: Docker, Docker Compose

## 🚀 Inicio Rápido

### Prerrequisitos

1. Docker y Docker Compose instalados
2. Una base de datos PostgreSQL con el **modelo IS-GORE ÑUBLE v4.1** y datos migrados.
   - Por ejemplo, levantando el stack definido en el repositorio `data-gore` y
     ejecutando las Olas 1–4 descritas en `etl/README.md` de ese proyecto.

```bash
# Ejemplo: levantar gore_db desde el repo data-gore
cd /path/to/data-gore
docker compose up -d
```

### Desarrollo

#### Opción recomendada: stack completo (data-gore + app)

```bash
# Entrar al proyecto de la app
cd /path/to/para_titi

# (Primera vez o cuando quieras re-aplicar modelo v4.1)
bash dev_stack.sh --init-model

# Uso habitual (BD ya inicializada)
bash dev_stack.sh

# La aplicación estará en http://localhost:5001
```

Este script asume que el repositorio `data-gore` está como proyecto hermano
(`../data-gore`) y orquesta:

- Levantar/asegurar el contenedor `gore_db` (PostgreSQL + PostGIS)
- (Opcional) ejecutar `etl/init_modelo.sh` para cargar el modelo IS-GORE v4.1
- Levantar `docker-compose.dev.yml` con hot reload (puerto 5001)

#### Opción directa: sólo app (BD ya levantada)

```bash
# Clonar y entrar al proyecto
cd /path/to/para_titi

# Copiar variables de entorno
cp .env.example .env

# Levantar en modo desarrollo (requiere gore_db ya corriendo y con v4.1)
docker compose -f docker-compose.dev.yml up

# La aplicación estará en http://localhost:5001
```

### Producción

```bash
# Build y levantar
docker compose up -d --build

# Con nginx (perfil production)
docker compose --profile production up -d
```

## 📁 Estructura del Proyecto

```
para_titi/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuración
│   ├── extensions.py        # Flask extensions
│   ├── models/              # SQLAlchemy models (v4.1)
│   ├── routes/              # Blueprints
│   ├── services/            # Lógica de negocio
│   ├── templates/           # Jinja2 templates
│   └── static/              # Assets
├── nginx/                   # Configuración nginx
├── docker-compose.yml       # Producción
├── docker-compose.dev.yml   # Desarrollo
├── Dockerfile               # Build producción
├── Dockerfile.dev           # Build desarrollo
└── requirements.txt         # Dependencias Python
```

## 🔐 Roles del Sistema

| Rol | Permisos |
|-----|----------|
| `ADMIN_SISTEMA` | Acceso total, gestión de usuarios |
| `ADMIN_REGIONAL` | Ver todo, crear compromisos, verificar |
| `JEFE_DIVISION` | Ver su división, verificar compromisos |
| `ENCARGADO_OPERATIVO` | Ver sus IPR, completar sus compromisos |

## 🗄️ Base de Datos

Este sistema se conecta a la base de datos IS-GORE ÑUBLE v4.1, que incluye:

- `gore_inversion.iniciativa` — IPR con extensiones de crisis
- `gore_ejecucion.problema_ipr` — Problemas detectados
- `gore_ejecucion.compromiso_operativo` — Compromisos operativos
- `gore_ejecucion.alerta_ipr` — Alertas automáticas
- `gore_autenticacion.usuario` — Usuarios con rol_crisis

## 📝 Comandos Útiles

```bash
# Ver logs
docker compose logs -f app

# Shell Flask
docker compose exec app flask shell

# Ejecutar tests
docker compose exec app pytest

# Reiniciar app
docker compose restart app
```

## 📄 Documentación

- `casos_uso.md` — Casos de uso y user journeys
- `diseno_tecnico_v4_1.md` — Diseño técnico detallado

---

**Versión**: 1.0.0  
**Basado en**: IS-GORE ÑUBLE v4.1
