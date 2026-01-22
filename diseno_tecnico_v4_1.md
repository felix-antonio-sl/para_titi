# 🏗️ DISEÑO TÉCNICO DEL SISTEMA
## Sistema de Gestión de Crisis IPR — GORE Ñuble
### Versión: Basado en IS-GORE ÑUBLE v4.1

---

# 1. CONTEXTO Y DECISIÓN ARQUITECTÓNICA

## 1.1 Situación Actual

El modelo de datos **IS-GORE ÑUBLE v4.1** ya incluye todas las extensiones necesarias para la gestión de crisis:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IS-GORE ÑUBLE v4.1 — YA IMPLEMENTADO                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  gore_ejecucion (extensiones de crisis)                                     │
│  ├─ tipo_compromiso_operativo    ✅ Catálogo de 9 tipos                     │
│  ├─ problema_ipr                 ✅ Nudos/problemas detectados              │
│  ├─ compromiso_operativo         ✅ Tareas con responsable/plazo            │
│  ├─ historial_compromiso         ✅ Event sourcing de estados               │
│  └─ alerta_ipr                   ✅ Alertas automáticas                     │
│                                                                              │
│  gore_inversion.iniciativa (columnas nuevas)                                │
│  ├─ responsable_id               ✅ FK → usuario                            │
│  ├─ division_responsable_id      ✅ FK → division                           │
│  ├─ nivel_alerta                 ✅ ENUM (NORMAL, ATENCION, CRITICO)        │
│  └─ tiene_problemas_abiertos     ✅ BOOLEAN derivado por trigger            │
│                                                                              │
│  gore_autenticacion.usuario (columna nueva)                                 │
│  └─ rol_crisis                   ✅ ENUM (ADMIN_SISTEMA, ADMIN_REGIONAL,    │
│                                          JEFE_DIVISION, ENCARGADO_OPERATIVO)│
│                                                                              │
│  Vistas de dashboard                                                        │
│  ├─ v_iniciativa_crisis          ✅ Métricas de crisis por IPR              │
│  └─ v_compromiso_completo        ✅ Compromisos con contexto                │
│                                                                              │
│  Funciones y Triggers                                                       │
│  ├─ fn_division_de_usuario()     ✅ Deriva división desde usuario           │
│  ├─ trg_compromiso_coherencia    ✅ Deriva cuota→convenio→iniciativa        │
│  └─ trg_problema_sync_iniciativa ✅ Sincroniza tiene_problemas_abiertos     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 1.2 Decisión Arquitectónica

**Este proyecto NO requiere DDL propio.** 

La aplicación es una **capa de presentación pura** sobre la base de datos v4.1 existente.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ARQUITECTURA SIMPLIFICADA                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                    APLICACIÓN WEB (para_titi)                           ││
│  │                                                                          ││
│  │  • Dashboard de crisis                                                   ││
│  │  • Gestión de compromisos                                                ││
│  │  • Registro de problemas                                                 ││
│  │  • Visualización de alertas                                              ││
│  │  • Reportes ejecutivos                                                   ││
│  │                                                                          ││
│  └──────────────────────────────────┬──────────────────────────────────────┘│
│                                      │                                       │
│                                      │ Conexión directa                      │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                    BASE DE DATOS v4.1 (existente)                       ││
│  │                                                                          ││
│  │  PostgreSQL 16 + PostGIS                                                 ││
│  │  Container: gore_db (puerto 5432)                                        ││
│  │  Credenciales: gore / gore_dev_2025                                      ││
│  │  Base de datos: gore_nuble                                               ││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 2. MODELO DE DOMINIO (Reflejo de v4.1)

## 2.1 Diagrama ER — Gestión de Crisis

```mermaid
erDiagram
    %% ENTIDADES CORE (v4.1)
    iniciativa ||--o{ problema_ipr : "detecta"
    iniciativa ||--o{ compromiso_operativo : "asigna"
    iniciativa ||--o{ alerta_ipr : "genera"
    iniciativa }o--o| usuario : "responsable"
    iniciativa }o--o| division : "division_responsable"
    iniciativa ||--o{ convenio : "tiene"
    
    convenio ||--o{ cuota : "programa"
    
    %% PROBLEMA IPR
    problema_ipr }o--|| usuario : "detectado_por"
    problema_ipr }o--o| usuario : "resuelto_por"
    problema_ipr }o--o| convenio : "afecta"
    problema_ipr ||--o{ compromiso_operativo : "resuelve"
    
    %% COMPROMISO OPERATIVO
    compromiso_operativo }o--|| tipo_compromiso_operativo : "tipifica"
    compromiso_operativo }o--|| usuario : "responsable"
    compromiso_operativo }o--o| usuario : "verificado_por"
    compromiso_operativo }o--o| usuario : "creado_por"
    compromiso_operativo }o--o| division : "asigna"
    compromiso_operativo }o--o| instancia_colectiva : "origen"
    compromiso_operativo }o--o| convenio : "vincula"
    compromiso_operativo }o--o| cuota : "vincula"
    compromiso_operativo ||--o{ historial_compromiso : "traza"
    
    %% HISTORIAL
    historial_compromiso }o--|| usuario : "registra"
    
    %% ALERTA
    alerta_ipr }o--o| usuario : "atendida_por"
    
    %% USUARIO Y ORGANIZACIÓN
    usuario }o--o| division : "pertenece"
    usuario }o--|| persona : "es"
    division ||--o{ departamento : "contiene"
```

## 2.2 Entidades Principales

### gore_ejecucion.problema_ipr

| Campo                | Tipo      | Descripción                                                          |
| -------------------- | --------- | -------------------------------------------------------------------- |
| `id`                 | UUID      | PK                                                                   |
| `iniciativa_id`      | UUID      | FK → iniciativa (NOT NULL)                                           |
| `convenio_id`        | UUID      | FK → convenio (opcional)                                             |
| `tipo`               | ENUM      | TECNICO, FINANCIERO, ADMINISTRATIVO, LEGAL, COORDINACION, EXTERNO    |
| `impacto`            | ENUM      | BLOQUEA_PAGO, RETRASA_OBRA, RETRASA_CONVENIO, RIESGO_RENDICION, OTRO |
| `descripcion`        | TEXT      | Descripción del problema                                             |
| `estado`             | ENUM      | ABIERTO, EN_GESTION, RESUELTO, CERRADO_SIN_RESOLVER                  |
| `detectado_por_id`   | UUID      | FK → usuario                                                         |
| `detectado_en`       | TIMESTAMP | Fecha de detección                                                   |
| `solucion_propuesta` | TEXT      | Solución propuesta                                                   |
| `solucion_aplicada`  | TEXT      | Solución implementada                                                |
| `resuelto_por_id`    | UUID      | FK → usuario                                                         |
| `resuelto_en`        | TIMESTAMP | Fecha de resolución                                                  |

### gore_ejecucion.compromiso_operativo

| Campo               | Tipo | Descripción                                               |
| ------------------- | ---- | --------------------------------------------------------- |
| `id`                | UUID | PK                                                        |
| `tipo_id`           | UUID | FK → tipo_compromiso_operativo                            |
| `descripcion`       | TEXT | Descripción de la tarea                                   |
| `responsable_id`    | UUID | FK → usuario (NOT NULL)                                   |
| `division_id`       | UUID | FK → division (derivado automáticamente)                  |
| `fecha_limite`      | DATE | Fecha límite                                              |
| `prioridad`         | ENUM | BAJA, MEDIA, ALTA, URGENTE                                |
| `estado`            | ENUM | PENDIENTE, EN_PROGRESO, COMPLETADO, VERIFICADO, CANCELADO |
| `iniciativa_id`     | UUID | FK → iniciativa (derivado)                                |
| `convenio_id`       | UUID | FK → convenio (derivado)                                  |
| `cuota_id`          | UUID | FK → cuota                                                |
| `problema_id`       | UUID | FK → problema_ipr                                         |
| `instancia_id`      | UUID | FK → instancia_colectiva (reunión origen)                 |
| `verificado_por_id` | UUID | FK → usuario                                              |
| `creado_por_id`     | UUID | FK → usuario                                              |

### gore_ejecucion.alerta_ipr

| Campo             | Tipo      | Descripción                                                       |
| ----------------- | --------- | ----------------------------------------------------------------- |
| `id`              | UUID      | PK                                                                |
| `iniciativa_id`   | UUID      | FK → iniciativa (NOT NULL)                                        |
| `target_tipo`     | VARCHAR   | INICIATIVA, CONVENIO, CUOTA, COMPROMISO, PROBLEMA                 |
| `target_id`       | UUID      | ID del objeto que genera la alerta                                |
| `tipo`            | ENUM      | OBRA_TERMINADA_SIN_PAGO, CUOTA_VENCIDA, CONVENIO_POR_VENCER, etc. |
| `nivel`           | ENUM      | INFO, ATENCION, ALTO, CRITICO                                     |
| `mensaje`         | TEXT      | Mensaje descriptivo                                               |
| `activa`          | BOOLEAN   | Si la alerta está activa                                          |
| `atendida_por_id` | UUID      | FK → usuario                                                      |
| `atendida_en`     | TIMESTAMP | Fecha de atención                                                 |

---

# 3. VISTAS DISPONIBLES EN v4.1

## 3.1 gore_ejecucion.v_iniciativa_crisis

Vista optimizada para el dashboard de crisis:

```sql
SELECT 
    id, codigo_interno, nombre,
    responsable_id, responsable_nombre,
    division_responsable_id, division_responsable_nombre,
    nivel_alerta, tiene_problemas_abiertos,
    problemas_abiertos_count,
    compromisos_pendientes_count,
    compromisos_vencidos_count,
    alertas_activas_count
FROM gore_ejecucion.v_iniciativa_crisis;
```

## 3.2 gore_ejecucion.v_compromiso_completo

Vista de compromisos con contexto:

```sql
SELECT
    id, descripcion, fecha_limite,
    tipo_codigo, tipo_nombre,
    responsable_id, responsable_nombre,
    division_nombre,
    iniciativa_id, iniciativa_codigo, iniciativa_nombre,
    problema_id, problema_tipo,
    dias_restantes, vencido
FROM gore_ejecucion.v_compromiso_completo;
```

---

# 4. ROLES Y PERMISOS

## 4.1 Roles del Sistema (gore_ejecucion.rol_crisis)

| Rol                   | Descripción            | Permisos                               |
| --------------------- | ---------------------- | -------------------------------------- |
| `ADMIN_SISTEMA`       | Administrador técnico  | Todo                                   |
| `ADMIN_REGIONAL`      | Administrador Regional | Ver todo, crear compromisos, verificar |
| `JEFE_DIVISION`       | Jefe de División       | Ver su división, verificar compromisos |
| `ENCARGADO_OPERATIVO` | Encargado operativo    | Ver sus IPR, completar sus compromisos |

## 4.2 Matriz de Permisos

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MATRIZ DE PERMISOS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Función                    │ Admin  │ Admin  │ Jefe   │ Encargado          │
│                             │ Sistema│ Regional│División│ Operativo          │
│  ───────────────────────────┼────────┼────────┼────────┼──────────          │
│  Ver todas las IPR          │   ✅   │   ✅   │   ❌   │   ❌               │
│  Ver IPR de mi división     │   ✅   │   ✅   │   ✅   │   ❌               │
│  Ver mis IPR asignadas      │   ✅   │   ✅   │   ✅   │   ✅               │
│  Crear compromiso           │   ✅   │   ✅   │   ✅   │   ❌               │
│  Completar compromiso       │   ✅   │   ✅   │   ✅   │   ✅ (solo suyos)  │
│  Verificar compromiso       │   ✅   │   ✅   │   ✅   │   ❌               │
│  Registrar problema         │   ✅   │   ✅   │   ✅   │   ✅               │
│  Resolver problema          │   ✅   │   ✅   │   ✅   │   ❌               │
│  Atender alerta             │   ✅   │   ✅   │   ✅   │   ❌               │
│  Gestionar usuarios         │   ✅   │   ❌   │   ❌   │   ❌               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 5. ESTRUCTURA DEL PROYECTO

```
/Users/felixsanhueza/fx_felixiando/para_titi/
│
├── README.md                          # Documentación del proyecto
├── casos_uso.md                       # Casos de uso y user journeys
├── diseno_tecnico_v4_1.md             # Este documento
│
├── app/                               # Aplicación web
│   ├── __init__.py                    # Factory de la app
│   ├── config.py                      # Configuración (conexión a v4.1)
│   ├── extensions.py                  # Extensiones (db, login, etc.)
│   │
│   ├── models/                        # ORM Models (reflejan v4.1)
│   │   ├── __init__.py
│   │   ├── organizacion.py            # Division, Departamento
│   │   ├── actores.py                 # Persona, Usuario
│   │   ├── inversion.py               # Iniciativa
│   │   ├── financiero.py              # Convenio, Cuota
│   │   └── crisis.py                  # ProblemaIPR, Compromiso, Alerta
│   │
│   ├── services/                      # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── ipr_service.py
│   │   ├── compromiso_service.py
│   │   ├── problema_service.py
│   │   ├── alerta_service.py
│   │   └── reporte_service.py
│   │
│   ├── routes/                        # Endpoints / Blueprints
│   │   ├── __init__.py
│   │   ├── main.py                    # Dashboard
│   │   ├── ipr.py                     # Iniciativas
│   │   ├── compromisos.py             # Compromisos
│   │   ├── problemas.py               # Problemas
│   │   ├── alertas.py                 # Alertas
│   │   ├── reuniones.py               # Reuniones
│   │   ├── reportes.py                # Reportes
│   │   ├── admin.py                   # Administración
│   │   └── auth.py                    # Autenticación
│   │
│   ├── templates/                     # Templates HTML
│   │   ├── base.html
│   │   ├── components/
│   │   ├── dashboard/
│   │   ├── ipr/
│   │   ├── compromisos/
│   │   └── ...
│   │
│   └── static/                        # Assets estáticos
│       ├── css/
│       ├── js/
│       └── img/
│
├── tests/                             # Tests
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_routes.py
│
├── docker-compose.yml                 # Orquestación (usa gore_db existente)
├── Dockerfile                         # Build de la app
├── requirements.txt                   # Dependencias Python
└── .env.example                       # Variables de entorno
```

---

# 6. CONEXIÓN A BASE DE DATOS

## 6.1 Configuración

La aplicación se conecta a la base de datos v4.1 existente:

```python
# app/config.py

import os

class Config:
    # Conexión a gore_db (v4.1)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://gore:gore_dev_2025@localhost:5432/gore_nuble'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
```

## 6.2 Docker Compose (extensión)

```yaml
# docker-compose.yml (para_titi)

services:
  app:
    build: .
    container_name: para_titi_app
    environment:
      DATABASE_URL: postgresql://gore:gore_dev_2025@gore_db:5432/gore_nuble
      SECRET_KEY: ${SECRET_KEY:-dev-secret-key}
    ports:
      - "5000:5000"
    networks:
      - gore_network
    depends_on:
      - gore_db

networks:
  gore_network:
    external: true
    name: data-gore_default  # Red del docker-compose de data-gore
```

---

# 7. OPCIONES DE STACK TECNOLÓGICO

## 7.1 Opción A: Flask + Jinja2 (Server-Side Rendering)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  OPCIÓN A: FLASK + JINJA2 (SSR)                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Backend: Flask + SQLAlchemy                                                │
│  Frontend: Jinja2 templates + HTMX + TailwindCSS                            │
│  Auth: Flask-Login                                                          │
│                                                                              │
│  PROS:                                                                       │
│  ✅ Stack simple y probado                                                  │
│  ✅ Consistente con proyecto `abran` existente                              │
│  ✅ Rápido de desarrollar                                                   │
│  ✅ SEO-friendly (SSR)                                                      │
│  ✅ Menor complejidad de deployment                                         │
│  ✅ HTMX permite interactividad sin SPA                                     │
│                                                                              │
│  CONTRAS:                                                                    │
│  ❌ Menos interactivo que SPA                                               │
│  ❌ Más tráfico de red (páginas completas)                                  │
│  ❌ Difícil de escalar a móvil nativo                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 7.2 Opción B: FastAPI + React/Next.js (SPA/SSR híbrido)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  OPCIÓN B: FASTAPI + REACT/NEXT.JS                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Backend: FastAPI + SQLAlchemy (async)                                      │
│  Frontend: Next.js + React + TailwindCSS + shadcn/ui                        │
│  Auth: JWT + NextAuth                                                       │
│                                                                              │
│  PROS:                                                                       │
│  ✅ UI más moderna e interactiva                                            │
│  ✅ Mejor UX (SPA con SSR)                                                  │
│  ✅ API reutilizable para móvil                                             │
│  ✅ Ecosistema React maduro                                                 │
│  ✅ Componentes shadcn/ui listos                                            │
│                                                                              │
│  CONTRAS:                                                                    │
│  ❌ Más complejo de desarrollar                                             │
│  ❌ Dos proyectos separados (backend + frontend)                            │
│  ❌ Mayor curva de aprendizaje                                              │
│  ❌ Más recursos de servidor                                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 7.3 Opción C: Flask + Inertia.js + React/Vue

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  OPCIÓN C: FLASK + INERTIA.JS + REACT/VUE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Backend: Flask + SQLAlchemy + Inertia                                      │
│  Frontend: React o Vue (via Inertia) + TailwindCSS                          │
│  Auth: Flask-Login                                                          │
│                                                                              │
│  PROS:                                                                       │
│  ✅ Mejor de ambos mundos (SPA feel, server routing)                        │
│  ✅ Un solo proyecto                                                        │
│  ✅ Componentes React/Vue modernos                                          │
│  ✅ Sin API separada                                                        │
│                                                                              │
│  CONTRAS:                                                                    │
│  ❌ Inertia menos maduro en Python                                          │
│  ❌ Documentación limitada para Flask                                       │
│  ❌ Comunidad más pequeña                                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 7.4 Opción D: Django + HTMX

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  OPCIÓN D: DJANGO + HTMX                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Backend: Django + Django ORM                                               │
│  Frontend: Django templates + HTMX + TailwindCSS                            │
│  Auth: Django Auth                                                          │
│                                                                              │
│  PROS:                                                                       │
│  ✅ Framework más completo (admin, auth, forms)                             │
│  ✅ ORM potente                                                             │
│  ✅ Comunidad grande                                                        │
│  ✅ Django Admin gratis                                                     │
│                                                                              │
│  CONTRAS:                                                                    │
│  ❌ Más pesado que Flask                                                    │
│  ❌ Menos flexible                                                          │
│  ❌ Diferente a `abran` (inconsistencia)                                    │
│  ❌ ORM diferente a SQLAlchemy                                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 8. RECOMENDACIÓN

## Análisis de Factores

| Factor                   | Peso | A (Flask+Jinja) | B (FastAPI+React) | C (Flask+Inertia) | D (Django) |
| ------------------------ | ---- | --------------- | ----------------- | ----------------- | ---------- |
| Velocidad de desarrollo  | 25%  | ⭐⭐⭐⭐⭐           | ⭐⭐⭐               | ⭐⭐⭐⭐              | ⭐⭐⭐⭐       |
| Consistencia con `abran` | 20%  | ⭐⭐⭐⭐⭐           | ⭐⭐                | ⭐⭐⭐⭐              | ⭐⭐         |
| UX/Interactividad        | 20%  | ⭐⭐⭐             | ⭐⭐⭐⭐⭐             | ⭐⭐⭐⭐              | ⭐⭐⭐        |
| Mantenibilidad           | 15%  | ⭐⭐⭐⭐            | ⭐⭐⭐               | ⭐⭐⭐               | ⭐⭐⭐⭐       |
| Escalabilidad móvil      | 10%  | ⭐⭐              | ⭐⭐⭐⭐⭐             | ⭐⭐⭐               | ⭐⭐         |
| Recursos servidor        | 10%  | ⭐⭐⭐⭐⭐           | ⭐⭐⭐               | ⭐⭐⭐⭐              | ⭐⭐⭐⭐       |

## Recomendación: Opción A (Flask + Jinja2 + HTMX)

**Razones:**

1. **Consistencia**: El proyecto `abran` ya usa Flask, lo que permite reutilizar código y conocimiento.

2. **Velocidad**: Es el stack más rápido de implementar para un MVP.

3. **HTMX**: Permite agregar interactividad (actualizaciones parciales, modales, etc.) sin la complejidad de un SPA.

4. **Simplicidad**: Un solo proyecto, un solo deployment, menos puntos de falla.

5. **Suficiente para el caso de uso**: El sistema es principalmente CRUD + dashboards, no requiere interactividad extrema.

---

# 9. STACK FINAL

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STACK TECNOLÓGICO                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  BACKEND                                                                     │
│  ├─ Python 3.11+                                                            │
│  ├─ Flask 3.x                                                               │
│  ├─ SQLAlchemy 2.x (ORM)                                                    │
│  ├─ Flask-Login (autenticación)                                             │
│  ├─ Flask-WTF (formularios)                                                 │
│  └─ Gunicorn (servidor WSGI)                                                │
│                                                                              │
│  FRONTEND                                                                    │
│  ├─ Jinja2 (templates)                                                      │
│  ├─ HTMX 2.x (interactividad sin JS)                                        │
│  ├─ TailwindCSS 3.x (estilos)                                               │
│  ├─ Alpine.js 3.x (interactividad ligera)                                   │
│  └─ Chart.js 4.x (gráficos dashboard)                                       │
│                                                                              │
│  BASE DE DATOS                                                               │
│  └─ PostgreSQL 16 + PostGIS (v4.1 existente en gore_db)                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 10. DOCKERIZACIÓN (VITAL)

## 10.1 Arquitectura de Contenedores

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA DOCKER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Red: gore_network (compartida con data-gore)                               │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  CONTENEDOR: para_titi_app                                              ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │  Python 3.11-slim                                                   │││
│  │  │  ├─ Flask App                                                       │││
│  │  │  ├─ Gunicorn (4 workers)                                            │││
│  │  │  └─ Assets compilados (Tailwind)                                    │││
│  │  │                                                                      │││
│  │  │  Puerto: 5000                                                       │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                              │                                               │
│                              │ postgresql://gore:***@gore_db:5432/gore_nuble │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  CONTENEDOR: gore_db (existente en data-gore)                           ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │  PostgreSQL 16 + PostGIS                                            │││
│  │  │  Base de datos: gore_nuble (v4.1)                                   │││
│  │  │  Puerto: 5432                                                       │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  CONTENEDOR: nginx (opcional, para producción)                          ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │  Nginx Alpine                                                       │││
│  │  │  ├─ Reverse proxy → para_titi_app:5000                              │││
│  │  │  ├─ SSL termination                                                 │││
│  │  │  └─ Static files caching                                            │││
│  │  │                                                                      │││
│  │  │  Puerto: 80, 443                                                    │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 10.2 Dockerfile

```dockerfile
# Dockerfile
# Multi-stage build para imagen optimizada

# ============================================================================
# STAGE 1: Build de assets (Tailwind CSS)
# ============================================================================
FROM node:20-alpine AS assets-builder

WORKDIR /build

# Copiar archivos de configuración de Node
COPY package.json package-lock.json* ./
RUN npm ci

# Copiar fuentes de CSS y templates (para purge de Tailwind)
COPY tailwind.config.js ./
COPY app/static/src/ ./app/static/src/
COPY app/templates/ ./app/templates/

# Build de Tailwind
RUN npm run build:css

# ============================================================================
# STAGE 2: Aplicación Python
# ============================================================================
FROM python:3.11-slim AS runtime

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Usuario no-root
RUN useradd --create-home --shell /bin/bash app
WORKDIR /home/app
USER app

# Dependencias Python
COPY --chown=app:app requirements.txt .
RUN pip install --user -r requirements.txt

# Código de la aplicación
COPY --chown=app:app app/ ./app/
COPY --chown=app:app migrations/ ./migrations/
COPY --chown=app:app wsgi.py ./

# Assets compilados desde stage 1
COPY --from=assets-builder --chown=app:app /build/app/static/dist/ ./app/static/dist/

# Puerto
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "wsgi:app"]
```

## 10.3 Docker Compose

```yaml
# docker-compose.yml

services:
  # =========================================================================
  # Aplicación Flask
  # =========================================================================
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: para_titi_app
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://gore:gore_dev_2025@gore_db:5432/gore_nuble
      - SECRET_KEY=${SECRET_KEY:-cambiar-en-produccion}
      - FLASK_ENV=${FLASK_ENV:-production}
    ports:
      - "5000:5000"
    networks:
      - gore_network
    depends_on:
      gore_db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  # =========================================================================
  # Nginx (producción)
  # =========================================================================
  nginx:
    image: nginx:alpine
    container_name: para_titi_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    networks:
      - gore_network
    depends_on:
      - app
    profiles:
      - production

# =========================================================================
# Red compartida con data-gore
# =========================================================================
networks:
  gore_network:
    external: true
    name: data-gore_default
```

## 10.4 Docker Compose para Desarrollo

```yaml
# docker-compose.dev.yml

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: para_titi_dev
    environment:
      - DATABASE_URL=postgresql://gore:gore_dev_2025@gore_db:5432/gore_nuble
      - SECRET_KEY=dev-secret-key
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    ports:
      - "5000:5000"
    volumes:
      # Hot reload: montar código fuente
      - ./app:/home/app/app:ro
      - ./migrations:/home/app/migrations:ro
    networks:
      - gore_network

networks:
  gore_network:
    external: true
    name: data-gore_default
```

## 10.5 Dockerfile para Desarrollo

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/app

COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements.txt -r requirements-dev.txt

COPY . .

EXPOSE 5000

# Flask dev server con hot reload
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]
```

## 10.6 Comandos de Operación

```bash
# ============================================================================
# DESARROLLO
# ============================================================================

# Levantar en modo desarrollo (hot reload)
docker compose -f docker-compose.dev.yml up

# Ver logs
docker compose -f docker-compose.dev.yml logs -f app

# Ejecutar migraciones
docker compose -f docker-compose.dev.yml exec app flask db upgrade

# Shell interactivo
docker compose -f docker-compose.dev.yml exec app flask shell

# ============================================================================
# PRODUCCIÓN
# ============================================================================

# Build de imagen
docker compose build

# Levantar (sin nginx)
docker compose up -d

# Levantar con nginx (perfil production)
docker compose --profile production up -d

# Ver estado
docker compose ps

# Ver logs
docker compose logs -f app

# Reiniciar app
docker compose restart app

# Actualizar (rebuild + restart)
docker compose build app && docker compose up -d app

# ============================================================================
# MANTENIMIENTO
# ============================================================================

# Backup de sesiones/cache (si usamos Redis en futuro)
# docker compose exec redis redis-cli BGSAVE

# Limpiar imágenes antiguas
docker image prune -f

# Ver uso de recursos
docker stats para_titi_app
```

## 10.7 Integración con data-gore

La aplicación se conecta a la misma red que `data-gore`:

```bash
# Primero, asegurar que gore_db está corriendo
cd /Users/felixsanhueza/fx_felixiando/data-gore
docker compose up -d

# Verificar que la red existe
docker network ls | grep data-gore

# Luego, levantar para_titi
cd /Users/felixsanhueza/fx_felixiando/para_titi
docker compose up -d

# Verificar conectividad
docker compose exec app python -c "
from sqlalchemy import create_engine, text
engine = create_engine('postgresql://gore:gore_dev_2025@gore_db:5432/gore_nuble')
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM gore_inversion.iniciativa'))
    print(f'IPR en v4.1: {result.scalar()}')
"
```

---

# 11. PRÓXIMOS PASOS

## Fase 0: Setup (2 días)
1. Crear estructura del proyecto
2. Configurar conexión a v4.1
3. Crear modelos SQLAlchemy que reflejen v4.1
4. Setup de autenticación básica

## Fase 1: MVP Core (1 semana)
1. Dashboard principal
2. Lista de IPR con filtros
3. Ficha de IPR
4. CRUD de compromisos
5. CRUD de problemas

## Fase 2: Reuniones y Alertas (1 semana)
1. Gestión de reuniones
2. Visualización de alertas
3. Reportes básicos

## Fase 3: Refinamiento (3 días)
1. Tests
2. Documentación
3. Deployment

---

**Documento**: diseno_tecnico_v4_1.md  
**Versión**: 1.0  
**Fecha**: 2024-12-03  
**Basado en**: IS-GORE ÑUBLE v4.1
