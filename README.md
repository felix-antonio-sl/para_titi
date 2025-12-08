# 🏛️ Sistema de Gestión de Crisis IPR — GORE Ñuble

Sistema web para la gestión de crisis en Iniciativas de Inversión Pública Regional (IPR) del Gobierno Regional de Ñuble. Diseñado para centralizar el monitoreo, resolución de problemas y seguimiento de compromisos operativos.

## 📋 Características Principales

- **Dashboard de Crisis**: Vista consolidada del estado crítico de las IPR.
- **Gestión de Compromisos**: Flujo completo (Creación → Completitud → Verificación) con historial de auditoría.
- **Registro de Problemas**: Detección y ciclo de vida de nudos/problemas (Abierto → Resuelto).
- **Sistema de Alertas**: Notificaciones automáticas por vencimientos y situaciones críticas.
- **Arquitectura en Capas**: Separación clara entre Rutas (Controladores), Servicios (Lógica de Negocio) y Modelos (Datos).

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.11, Flask 3.x
- **ORM**: SQLAlchemy 2.x
- **Base de Datos**: PostgreSQL 16 + PostGIS (Modelo IS-GORE ÑUBLE v4.1)
- **Frontend**: Jinja2, HTMX, Alpine.js, TailwindCSS
- **Infraestructura**: Docker, Docker Compose

## 🏗️ Arquitectura del Proyecto

El proyecto sigue una arquitectura por capas para garantizar mantenibilidad y testabilidad:

1. **Routes (`app/routes/`)**: Manejan las peticiones HTTP, validan entrada básica y delegan a los servicios.
2. **Services (`app/services/`)**: Contienen toda la lógica de negocio (ej: `IPRService`, `CompromisosService`, `ProblemasService`). Manejan transacciones y reglas de dominio.
3. **Models (`app/models/`)**: Definiciones SQLAlchemy mapeadas al esquema de base de datos.

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker Desktop instalado.
- Git.

### Instalación y Ejecución

1. **Clonar el repositorio**:

    ```bash
    git clone <url-repo>
    cd para_titi
    ```

2. **Configurar entorno**:

    ```bash
    cp .env.example .env
    ```

3. **Levantar servicios (Desarrollo)**:
    Esto levantará la aplicación y una base de datos de pruebas (`db_test`) automáticamente.

    ```bash
    docker compose -f docker-compose.dev.yml up --build
    ```

    La aplicación estará disponible en: [http://localhost:5001](http://localhost:5001)

## 🧪 Estrategia de Testing (Real DB)

El proyecto utiliza una estrategia de **Testing de Integración con Base de Datos Real**. En lugar de usar mocks para la base de datos, levantamos una instancia real de PostgreSQL (contenedor `db_test`) idéntica a producción.

### Ejecutar Tests

Para correr la suite completa de pruebas:

```bash
docker compose -f docker-compose.dev.yml run --rm app sh -c "pip install pytest-mock && python -m pytest"
```

**Que sucede al correr los tests:**

1. Se conecta al contenedor `db_test`.
2. `tests/conftest.py` crea los esquemas necesarios (`gore_financiero`, `gore_ejecucion`, etc.).
3. Se crean las tablas y se limpian después de cada test.
4. Se validan Constraints reales (Foreign Keys, Not Null, etc.).

## 📁 Estructura del Proyecto

```
para_titi/
├── app/
│   ├── models/            # Modelos SQLAlchemy (Crisis, Actores, Inversión, etc.)
│   ├── routes/            # Blueprints (Endpoints)
│   ├── services/          # Lógica de Negocio (Service Layer)
│   ├── templates/         # Vistas Jinja2
│   └── ...
├── tests/                 # Suite de Pruebas
│   ├── test_services.py   # Tests de Lógica de Negocio
│   ├── test_routes.py     # Tests de Integración HTTP
│   └── conftest.py        # Configuración de Fixtures y DB Real
├── docker-compose.dev.yml # Orquestación para Desarrollo y Tests
└── requirements.txt       # Dependencias
```

## 🔐 Roles y Permisos

| Rol                   | Alcance                                                      |
| --------------------- | ------------------------------------------------------------ |
| `ADMIN_SISTEMA`       | Acceso total, gestión de usuarios y configuración.           |
| `ADMIN_REGIONAL`      | Visibilidad completa, verificar compromisos.                 |
| `JEFE_DIVISION`       | Visibilidad de sus IPRs, verificar compromisos de su equipo. |
| `ENCARGADO_OPERATIVO` | Gestión diaria, reportar avances y completar compromisos.    |

---
**GORE Ñuble** — Sistema de Gestión de Crisis IPR
