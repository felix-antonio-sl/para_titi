Voy a revisar el agente de ingeniería de software para completar el análisis.

Ahora tengo el contexto completo. Voy a generar los journeys y flujos de trabajo para cada rol.

---

# Roles del Sistema y User Journeys

## Estructura de Roles

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ROLES DEL SISTEMA                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  ADMINISTRADOR DEL SISTEMA (rol técnico)                                ││
│  │  Gestiona usuarios, divisiones, configuración, datos maestros           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  ADMINISTRADOR REGIONAL (rol ejecutivo)                                 ││
│  │  Visión 360°, gestión de crisis, coordinación inter-divisional         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                              │                                               │
│              ┌───────────────┼───────────────┐                              │
│              ▼               ▼               ▼                              │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐                     │
│  │ JEFE DIVISIÓN │ │ JEFE DIVISIÓN │ │ JEFE DIVISIÓN │                     │
│  │    DIPIR      │ │     DAF       │ │    INFRA      │  ...                │
│  │ (supervisa)   │ │ (supervisa)   │ │ (supervisa)   │                     │
│  └───────────────┘ └───────────────┘ └───────────────┘                     │
│         │                 │                 │                               │
│         ▼                 ▼                 ▼                               │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐                     │
│  │  ENCARGADO    │ │  ENCARGADO    │ │  ENCARGADO    │                     │
│  │  OPERATIVO    │ │  OPERATIVO    │ │  OPERATIVO    │  ...                │
│  │ (responsable  │ │ (responsable  │ │ (responsable  │                     │
│  │  de IPR)      │ │  de IPR)      │ │  de IPR)      │                     │
│  └───────────────┘ └───────────────┘ └───────────────┘                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# PARTE 1: PERSPECTIVA GOREÓLOGO
## Journeys de Roles Operativos del GORE

---

## 1. ADMINISTRADOR REGIONAL

### Perfil del Rol

| Aspecto | Descripción |
|---------|-------------|
| **Nombre** | Administrador/a Regional |
| **Posición** | Cargo de confianza del Gobernador/a |
| **Función principal** | Coordinar divisiones, gestionar crisis, asesorar al Gobernador |
| **Contexto de uso** | Reuniones semanales, entrevistas con responsables, informes ejecutivos |
| **Disponibilidad** | Alta carga de reuniones, necesita información rápida y accionable |

### Journey: Semana Típica de Gestión de Crisis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LUNES 09:00 - PREPARACIÓN DE SEMANA                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: El Administrador llega temprano para revisar el estado de la     │
│  cartera antes de las reuniones del día.                                    │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│  1. Abre Dashboard → Ve resumen ejecutivo                                   │
│     • 127 IPR activas                                                       │
│     • 12 con problemas (3 críticos)                                         │
│     • 8 compromisos vencidos                                                │
│                                                                              │
│  2. Revisa "Nudos Críticos" → 3 proyectos requieren atención inmediata      │
│     • Gimnasio Coihueco: Obra terminada, pago pendiente                     │
│     • Televigilancia: Convenio por vencer                                   │
│     • CESFAM Quirihue: Rendición vencida                                    │
│                                                                              │
│  3. Revisa "Compromisos Vencidos" → Identifica responsables                 │
│     • J.Pérez (DIPIR): 2 vencidos                                           │
│     • M.López (DIPIR): 1 vencido                                            │
│                                                                              │
│  4. Anota mentalmente: "Hablar con Jefe DIPIR sobre estos casos"            │
│                                                                              │
│  SALIDA: Tiene panorama claro para el día                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LUNES 10:00 - REUNIÓN SEMANAL DE CRISIS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: Reunión con jefes de división y encargados clave.                │
│  El sistema ya generó agenda sugerida basada en alertas.                    │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre "Reunión de hoy" → Ve agenda pre-generada                          │
│     • 3 alertas críticas                                                    │
│     • 5 compromisos vencidos para revisar                                   │
│     • 8 compromisos completados para verificar                              │
│                                                                              │
│  2. Durante la reunión, para cada proyecto crítico:                         │
│     a) Abre "Ficha IPR" del proyecto                                        │
│     b) Revisa: avance físico, financiero, problemas, historial              │
│     c) Pregunta al responsable: "¿Qué pasó? ¿Qué necesitas?"                │
│     d) Crea compromiso con fecha límite                                     │
│                                                                              │
│  3. Para compromisos vencidos:                                              │
│     a) Pregunta al responsable por qué no se cumplió                        │
│     b) Decide: extender plazo, reasignar, o escalar                         │
│     c) Actualiza en sistema                                                 │
│                                                                              │
│  4. Para compromisos completados:                                           │
│     a) Responsable explica qué hizo                                         │
│     b) Jefe de división valida                                              │
│     c) Marca como "Verificado" en sistema                                   │
│                                                                              │
│  5. Al final de la reunión:                                                 │
│     a) Sistema muestra resumen: "12 compromisos creados"                    │
│     b) Cada responsable tiene sus tareas asignadas                          │
│                                                                              │
│  SALIDA: Compromisos claros, responsables definidos, plazos establecidos    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  MARTES 15:00 - ENTREVISTA CON ENCARGADO OPERATIVO                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: El Administrador cita a Juan Pérez (encargado de Gimnasio        │
│  Coihueco) para entender el problema y destrabar el nudo.                   │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Antes de la reunión, abre "Ficha IPR" de Gimnasio Coihueco              │
│     • Ve historial completo de compromisos                                  │
│     • Ve problema registrado: "Cuota diferida a 2026"                       │
│     • Ve que hay 2 compromisos vencidos del responsable                     │
│                                                                              │
│  2. Durante la entrevista:                                                  │
│     a) "Juan, veo que la obra está 100% terminada pero falta pagar $420MM"  │
│     b) "¿Qué necesitas para resolver esto?"                                 │
│     c) Juan explica: "Necesito que DAF tramite modificación presupuestaria" │
│                                                                              │
│  3. Registra en sistema:                                                    │
│     a) Actualiza problema: "Requiere modificación presupuestaria"           │
│     b) Crea compromiso para DAF: "Evaluar modificación ppto Gimnasio"       │
│     c) Crea compromiso para Juan: "Preparar memo justificativo"             │
│                                                                              │
│  4. Agenda reunión con Jefe DAF para el día siguiente                       │
│                                                                              │
│  SALIDA: Problema entendido, acciones definidas, responsables claros        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  VIERNES 17:00 - PREPARACIÓN INFORME PARA GOBERNADOR                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: El Administrador debe informar al Gobernador sobre el estado     │
│  de la cartera y los avances en la gestión de crisis.                       │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre "Reportes" → "Resumen Semanal"                                     │
│     • Compromisos cumplidos: 18 de 25 (72%)                                 │
│     • Problemas resueltos: 2                                                │
│     • Problemas nuevos: 1                                                   │
│     • Proyectos críticos: 3 → 2 (uno destrabado)                            │
│                                                                              │
│  2. Revisa "Proyectos Críticos" para preparar talking points                │
│     • Gimnasio Coihueco: En gestión, modificación ppto en trámite           │
│     • Televigilancia: Prórroga convenio aprobada                            │
│     • CESFAM Quirihue: Rendición recibida, en revisión                      │
│                                                                              │
│  3. Exporta resumen ejecutivo a PDF                                         │
│                                                                              │
│  SALIDA: Informe listo para el Gobernador                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Casos de Uso del Administrador Regional

| ID | Caso de Uso | Descripción | Frecuencia |
|----|-------------|-------------|------------|
| AR-01 | Ver dashboard ejecutivo | Visualizar resumen de cartera, alertas, compromisos | Diaria |
| AR-02 | Revisar nudos críticos | Ver proyectos con problemas graves | Diaria |
| AR-03 | Preparar reunión semanal | Ver agenda sugerida, alertas pendientes | Semanal |
| AR-04 | Conducir reunión | Revisar fichas IPR, crear compromisos | Semanal |
| AR-05 | Verificar compromisos | Validar que compromisos se cumplieron | Semanal |
| AR-06 | Entrevistar responsable | Revisar ficha IPR, registrar problema, crear compromisos | Ad-hoc |
| AR-07 | Generar informe ejecutivo | Exportar resumen para Gobernador | Semanal |
| AR-08 | Ver cumplimiento por división | Comparar desempeño entre divisiones | Semanal |

---

## 2. JEFE DE DIVISIÓN

### Perfil del Rol

| Aspecto | Descripción |
|---------|-------------|
| **Nombre** | Jefe/a de División |
| **Posición** | Jefatura de división (DIPIR, DAF, INFRA, etc.) |
| **Función principal** | Supervisar encargados, verificar compromisos, reportar al Administrador |
| **Contexto de uso** | Supervisión diaria, reuniones de equipo, coordinación con otras divisiones |
| **Disponibilidad** | Múltiples reuniones, necesita vista de su equipo |

### Journey: Semana Típica del Jefe DIPIR

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LUNES 08:30 - REVISIÓN MATINAL                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: El Jefe DIPIR revisa el estado de su división antes de la        │
│  reunión semanal con el Administrador.                                      │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre "Mi División" → Ve resumen de DIPIR                                │
│     • 45 IPR activas                                                        │
│     • 5 con problemas                                                       │
│     • 18 compromisos pendientes en mi equipo                                │
│     • 3 compromisos vencidos                                                │
│                                                                              │
│  2. Revisa "Mi Equipo" → Ve estado por encargado                            │
│     • Juan Pérez: 8 compromisos, 2 vencidos ⚠️                              │
│     • María López: 6 compromisos, 1 vencido ⚠️                              │
│     • Pedro Soto: 4 compromisos, 0 vencidos ✅                               │
│                                                                              │
│  3. Hace clic en compromisos vencidos de Juan                               │
│     • "Gestionar CDP cuota 2 - Gimnasio Coihueco" - Vencido hace 3 días     │
│     • "Preparar informe avance - Estadio Bulnes" - Vencido hace 5 días      │
│                                                                              │
│  4. Anota: "Hablar con Juan antes de la reunión"                            │
│                                                                              │
│  SALIDA: Sabe qué explicar al Administrador, qué pedir a su equipo          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LUNES 09:30 - REUNIÓN RÁPIDA CON ENCARGADO                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: El Jefe DIPIR llama a Juan Pérez para entender los atrasos       │
│  antes de la reunión con el Administrador.                                  │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre ficha de Juan → Ve sus compromisos vencidos                        │
│                                                                              │
│  2. Juan explica:                                                           │
│     • "El CDP del Gimnasio está trabado porque DAF no tiene el memo"        │
│     • "El informe del Estadio lo tengo listo, solo falta subirlo"           │
│                                                                              │
│  3. Jefe DIPIR:                                                             │
│     a) Actualiza compromiso del Estadio: Juan lo sube hoy                   │
│     b) Registra problema en Gimnasio: "Falta memo para DAF"                 │
│     c) Crea compromiso para Juan: "Enviar memo a DAF hoy"                   │
│                                                                              │
│  SALIDA: Entiende la situación, tiene respuestas para el Administrador      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LUNES 10:00 - REUNIÓN SEMANAL DE CRISIS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: El Jefe DIPIR participa en la reunión conducida por el           │
│  Administrador Regional.                                                    │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Cuando se revisa Gimnasio Coihueco:                                     │
│     a) Explica: "Juan está enviando el memo hoy a DAF"                      │
│     b) Administrador crea compromiso para DAF                               │
│     c) Jefe DIPIR se compromete a hacer seguimiento                         │
│                                                                              │
│  2. Cuando se revisan compromisos completados de su división:               │
│     a) Verifica que efectivamente se cumplieron                             │
│     b) Marca como "Verificado" los que corresponden                         │
│                                                                              │
│  3. Recibe nuevos compromisos asignados a su división                       │
│     a) Los asigna a encargados específicos                                  │
│                                                                              │
│  SALIDA: Compromisos claros para su equipo                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  MIÉRCOLES 11:00 - SEGUIMIENTO DE EQUIPO                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: El Jefe DIPIR hace seguimiento a mitad de semana.                │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre "Mi División" → Filtra compromisos que vencen esta semana          │
│     • 6 compromisos vencen entre hoy y viernes                              │
│                                                                              │
│  2. Revisa cada uno:                                                        │
│     a) "Enviar memo a DAF" (Juan) - Vence hoy → Verifica que se hizo        │
│     b) "Revisar informe avance" (María) - Vence mañana → Pregunta estado    │
│                                                                              │
│  3. Envía mensaje a María: "¿Cómo vas con el informe de avance?"            │
│                                                                              │
│  4. María responde y actualiza su compromiso a "En progreso"                │
│                                                                              │
│  SALIDA: Equipo al día, sin sorpresas para la próxima reunión               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Casos de Uso del Jefe de División

| ID | Caso de Uso | Descripción | Frecuencia |
|----|-------------|-------------|------------|
| JD-01 | Ver resumen de división | IPR, problemas, compromisos de mi división | Diaria |
| JD-02 | Ver estado de equipo | Compromisos por encargado | Diaria |
| JD-03 | Revisar compromisos vencidos | Identificar atrasos en mi equipo | Diaria |
| JD-04 | Asignar compromisos | Distribuir compromisos a encargados | Semanal |
| JD-05 | Verificar compromisos | Validar que encargados cumplieron | Semanal |
| JD-06 | Registrar problema | Documentar problema detectado en IPR | Ad-hoc |
| JD-07 | Coordinar con otra división | Ver IPR compartidas, crear compromisos cruzados | Ad-hoc |

---

## 3. ENCARGADO OPERATIVO

### Perfil del Rol

| Aspecto | Descripción |
|---------|-------------|
| **Nombre** | Encargado/a Operativo |
| **Posición** | Profesional de división (analista, supervisor, etc.) |
| **Función principal** | Gestionar IPR asignadas, actualizar avances, cumplir compromisos |
| **Contexto de uso** | Trabajo diario, visitas a terreno, gestión documental |
| **Disponibilidad** | Trabajo operativo intenso, necesita vista simple de sus tareas |

### Journey: Semana Típica del Encargado Operativo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LUNES 08:00 - INICIO DE SEMANA                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: Juan Pérez (encargado DIPIR) revisa sus tareas de la semana.     │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre "Mis Compromisos" → Ve lista priorizada                            │
│     🔴 Vencidos (2):                                                        │
│     • Gestionar CDP cuota 2 - Gimnasio Coihueco (hace 3 días)               │
│     • Preparar informe avance - Estadio Bulnes (hace 5 días)                │
│                                                                              │
│     🟠 Vencen esta semana (4):                                              │
│     • Enviar memo a DAF - Gimnasio Coihueco (hoy)                           │
│     • Visita terreno - Piscina Quillón (miércoles)                          │
│     • Revisar rendición - Centro Cultural (viernes)                         │
│     • Actualizar BIP - 3 proyectos (viernes)                                │
│                                                                              │
│  2. Abre "Mis IPR" → Ve sus 8 proyectos asignados                           │
│     • 2 con alertas (Gimnasio, Estadio)                                     │
│     • 6 en estado normal                                                    │
│                                                                              │
│  3. Prioriza: "Primero el memo del Gimnasio, luego subir informe Estadio"   │
│                                                                              │
│  SALIDA: Sabe qué hacer hoy                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LUNES 09:00 - GESTIÓN DE COMPROMISO URGENTE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: Juan prepara y envía el memo para DAF sobre el Gimnasio.         │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre compromiso "Enviar memo a DAF"                                     │
│     • Ve descripción y contexto                                             │
│     • Ve que está vinculado a IPR "Gimnasio Coihueco"                       │
│                                                                              │
│  2. Prepara memo (fuera del sistema)                                        │
│                                                                              │
│  3. Vuelve al sistema:                                                      │
│     a) Actualiza estado: "En progreso" → "Completado"                       │
│     b) Agrega comentario: "Memo enviado por SGDOC, folio 12345"             │
│                                                                              │
│  4. Sistema notifica al Jefe DIPIR que el compromiso está completado        │
│                                                                              │
│  SALIDA: Compromiso cumplido, trazabilidad registrada                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LUNES 11:00 - ACTUALIZACIÓN DE AVANCE DE IPR                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: Juan recibe informe de avance del contratista del Estadio        │
│  Bulnes y debe actualizar el sistema.                                       │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre "Mis IPR" → Selecciona "Estadio Bulnes"                            │
│                                                                              │
│  2. Hace clic en "Registrar Informe de Avance"                              │
│     a) Número de informe: 5                                                 │
│     b) Fecha: 02/12/2025                                                    │
│     c) Avance físico: 65% (antes era 55%)                                   │
│     d) Avance financiero: 50%                                               │
│     e) Descripción: "Terminada estructura, iniciando terminaciones"         │
│     f) Adjunta documento PDF del informe                                    │
│                                                                              │
│  3. Sistema actualiza automáticamente:                                      │
│     • Avance físico de la IPR: 65%                                          │
│     • Última actualización: hoy                                             │
│                                                                              │
│  4. Marca compromiso "Preparar informe avance" como completado              │
│                                                                              │
│  SALIDA: IPR actualizada, compromiso cumplido                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  MIÉRCOLES 10:00 - VISITA A TERRENO                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: Juan visita la obra de Piscina Quillón para verificar avance.    │
│                                                                              │
│  ACCIONES EN EL SISTEMA (antes de salir):                                   │
│                                                                              │
│  1. Abre ficha IPR "Piscina Quillón" desde el celular                       │
│     • Ve último avance reportado: 40%                                       │
│     • Ve cuotas: 2 de 4 pagadas                                             │
│     • Ve último informe: hace 25 días                                       │
│                                                                              │
│  ACCIONES EN EL SISTEMA (después de la visita):                             │
│                                                                              │
│  2. Registra informe de avance:                                             │
│     a) Avance físico: 55% (avanzó 15%)                                      │
│     b) Descripción: "Piscina terminada, falta equipamiento"                 │
│     c) Adjunta fotos de la visita                                           │
│                                                                              │
│  3. Detecta problema: "Equipamiento retrasado por proveedor"                │
│     a) Registra problema en la IPR                                          │
│     b) Tipo: Técnico                                                        │
│     c) Impacto: Retrasa entrega 30 días                                     │
│                                                                              │
│  4. Marca compromiso "Visita terreno" como completado                       │
│                                                                              │
│  SALIDA: Avance actualizado, problema registrado para discutir en reunión   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  VIERNES 16:00 - CIERRE DE SEMANA                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: Juan revisa que no le queden compromisos pendientes.             │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre "Mis Compromisos" → Filtra "Vencen hoy"                            │
│     • Revisar rendición Centro Cultural → Pendiente                         │
│     • Actualizar BIP 3 proyectos → Pendiente                                │
│                                                                              │
│  2. Completa compromiso de rendición:                                       │
│     a) Abre ficha IPR "Centro Cultural"                                     │
│     b) Revisa rendición recibida                                            │
│     c) Marca compromiso como completado                                     │
│     d) Comentario: "Rendición conforme, enviada a UCR"                      │
│                                                                              │
│  3. Completa actualización de BIP:                                          │
│     a) Actualiza avance en BIP (fuera del sistema)                          │
│     b) Marca compromiso como completado                                     │
│                                                                              │
│  4. Revisa "Mis IPR" → Verifica que todas estén actualizadas                │
│                                                                              │
│  SALIDA: Semana cerrada, sin compromisos vencidos                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Casos de Uso del Encargado Operativo

| ID | Caso de Uso | Descripción | Frecuencia |
|----|-------------|-------------|------------|
| EO-01 | Ver mis compromisos | Lista priorizada de tareas pendientes | Diaria |
| EO-02 | Ver mis IPR | Proyectos asignados con estado | Diaria |
| EO-03 | Actualizar compromiso | Cambiar estado, agregar comentario | Diaria |
| EO-04 | Marcar compromiso completado | Indicar que se cumplió la tarea | Diaria |
| EO-05 | Registrar informe de avance | Actualizar avance físico/financiero de IPR | Semanal/Mensual |
| EO-06 | Registrar problema | Documentar problema detectado en IPR | Ad-hoc |
| EO-07 | Ver ficha IPR | Consultar estado completo de un proyecto | Ad-hoc |
| EO-08 | Ver historial de IPR | Revisar compromisos y eventos pasados | Ad-hoc |

---

# PARTE 2: PERSPECTIVA INGENIERO DE SOFTWARE
## Journey del Administrador del Sistema

---

## 4. ADMINISTRADOR DEL SISTEMA

### Perfil del Rol

| Aspecto | Descripción |
|---------|-------------|
| **Nombre** | Administrador/a del Sistema |
| **Posición** | Profesional TI o encargado de sistemas |
| **Función principal** | Configurar sistema, gestionar usuarios, mantener datos maestros |
| **Contexto de uso** | Configuración inicial, mantenimiento, soporte a usuarios |
| **Disponibilidad** | Trabajo técnico, necesita acceso a configuración avanzada |

### Journey: Configuración Inicial del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DÍA 1 - CONFIGURACIÓN DE ESTRUCTURA ORGANIZACIONAL                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: El sistema se despliega por primera vez. El Administrador        │
│  del Sistema debe configurar la estructura organizacional.                  │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Accede con credenciales de admin del sistema                            │
│                                                                              │
│  2. Abre "Configuración" → "Divisiones"                                     │
│     a) Crea divisiones:                                                     │
│        • DIPIR - División de Presupuesto e Inversión Regional               │
│        • DAF - División de Administración y Finanzas                        │
│        • DIPLADE - División de Planificación y Desarrollo                   │
│        • DIDESOH - División de Desarrollo Social y Humano                   │
│        • DIFOP - División de Fomento Productivo                             │
│        • INFRA - División de Infraestructura                                │
│                                                                              │
│  3. Abre "Configuración" → "Usuarios"                                       │
│     a) Crea usuario Administrador Regional:                                 │
│        • Nombre: Ana Martínez                                               │
│        • Email: admin.regional@gorenuble.cl                                 │
│        • Rol: administrador_regional                                        │
│        • División: (ninguna - transversal)                                  │
│                                                                              │
│     b) Crea usuarios Jefes de División:                                     │
│        • Carlos Muñoz - jefe - DIPIR                                        │
│        • Patricia Soto - jefe - DAF                                         │
│        • Roberto Díaz - jefe - INFRA                                        │
│        • ...                                                                │
│                                                                              │
│     c) Crea usuarios Encargados Operativos:                                 │
│        • Juan Pérez - encargado - DIPIR                                     │
│        • María López - encargado - DIPIR                                    │
│        • Pedro Soto - encargado - DIPIR                                     │
│        • ...                                                                │
│                                                                              │
│  4. Asigna jefes a divisiones:                                              │
│     • DIPIR → Carlos Muñoz                                                  │
│     • DAF → Patricia Soto                                                   │
│     • ...                                                                   │
│                                                                              │
│  SALIDA: Estructura organizacional configurada                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  DÍA 2 - CARGA DE DATOS MAESTROS (IPR)                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: Se deben cargar las IPR existentes desde los archivos Excel.     │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre "Configuración" → "Importar Datos"                                 │
│                                                                              │
│  2. Selecciona "Importar IPR desde Excel"                                   │
│     a) Sube archivo "SIG CARTERA DE PROYECTOS GORE.xlsx"                    │
│     b) Sistema muestra preview de datos                                     │
│     c) Mapea columnas:                                                      │
│        • "Código Único" → codigo_unico                                      │
│        • "Nombre Iniciativa" → nombre                                       │
│        • "Instrumento" → instrumento                                        │
│        • "Monto Aprobado" → monto_aprobado                                  │
│        • ...                                                                │
│     d) Ejecuta importación                                                  │
│     e) Sistema reporta: "127 IPR importadas, 3 errores"                     │
│     f) Revisa errores y corrige manualmente                                 │
│                                                                              │
│  3. Selecciona "Importar Convenios desde Excel"                             │
│     a) Sube archivo "ESTADO DE CONVENIOS.xlsx"                              │
│     b) Mapea columnas                                                       │
│     c) Ejecuta importación                                                  │
│                                                                              │
│  4. Asigna responsables a IPR:                                              │
│     a) Abre "IPR" → "Asignación masiva"                                     │
│     b) Filtra por división                                                  │
│     c) Asigna responsables según planilla de referencia                     │
│                                                                              │
│  SALIDA: Datos maestros cargados                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  DÍA 3 - CONFIGURACIÓN DE ALERTAS                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: Se configuran las reglas de alertas automáticas.                 │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre "Configuración" → "Alertas"                                        │
│                                                                              │
│  2. Configura reglas:                                                       │
│     a) Alerta "Obra terminada sin pago":                                    │
│        • Condición: avance_fisico >= 95% AND saldo_pendiente > 0            │
│        • Nivel: Crítico                                                     │
│        • Notificar a: Responsable, Jefe División, Admin Regional            │
│                                                                              │
│     b) Alerta "Cuota vencida":                                              │
│        • Condición: fecha_cuota < hoy AND estado != 'pagada'                │
│        • Nivel: Crítico                                                     │
│        • Notificar a: Responsable, Jefe División                            │
│                                                                              │
│     c) Alerta "Convenio por vencer":                                        │
│        • Condición: fecha_termino < hoy + 30 días                           │
│        • Nivel: Alto                                                        │
│        • Notificar a: Responsable                                           │
│                                                                              │
│     d) Alerta "Compromiso vencido":                                         │
│        • Condición: fecha_limite < hoy AND estado != 'completado'           │
│        • Nivel: Alto                                                        │
│        • Notificar a: Responsable, Jefe División                            │
│                                                                              │
│  3. Configura frecuencia de evaluación: Diaria a las 07:00                  │
│                                                                              │
│  SALIDA: Alertas configuradas                                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Journey: Mantenimiento Continuo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TAREA RECURRENTE - GESTIÓN DE USUARIOS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: Llega un nuevo profesional a DIPIR y hay que darle acceso.       │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre "Configuración" → "Usuarios" → "Nuevo Usuario"                     │
│                                                                              │
│  2. Completa formulario:                                                    │
│     • Nombre: Andrea Fuentes                                                │
│     • Email: andrea.fuentes@gorenuble.cl                                    │
│     • Rol: encargado                                                        │
│     • División: DIPIR                                                       │
│     • Contraseña temporal: (genera automáticamente)                         │
│                                                                              │
│  3. Sistema envía email con credenciales                                    │
│                                                                              │
│  4. Reasigna IPR:                                                           │
│     a) Abre IPR que se transferirán a Andrea                                │
│     b) Cambia responsable de Juan a Andrea                                  │
│     c) Sistema notifica a ambos del cambio                                  │
│                                                                              │
│  SALIDA: Nuevo usuario activo con IPR asignadas                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  TAREA RECURRENTE - SOPORTE A USUARIOS                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: Un usuario olvidó su contraseña.                                 │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre "Configuración" → "Usuarios"                                       │
│  2. Busca usuario por nombre o email                                        │
│  3. Hace clic en "Restablecer contraseña"                                   │
│  4. Sistema envía email con link de restablecimiento                        │
│                                                                              │
│  SALIDA: Usuario puede acceder nuevamente                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  TAREA RECURRENTE - MONITOREO DEL SISTEMA                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTEXTO: Revisión semanal del estado del sistema.                         │
│                                                                              │
│  ACCIONES EN EL SISTEMA:                                                    │
│                                                                              │
│  1. Abre "Configuración" → "Monitoreo"                                      │
│                                                                              │
│  2. Revisa métricas:                                                        │
│     • Usuarios activos última semana: 45                                    │
│     • Compromisos creados: 87                                               │
│     • Alertas generadas: 12                                                 │
│     • Errores de sistema: 0                                                 │
│                                                                              │
│  3. Revisa logs de errores (si hay)                                         │
│                                                                              │
│  4. Verifica backups automáticos                                            │
│                                                                              │
│  SALIDA: Sistema funcionando correctamente                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Casos de Uso del Administrador del Sistema

| ID | Caso de Uso | Descripción | Frecuencia |
|----|-------------|-------------|------------|
| AS-01 | Crear división | Agregar nueva división al sistema | Inicial/Raro |
| AS-02 | Editar división | Modificar nombre, descripción, jefe | Raro |
| AS-03 | Crear usuario | Agregar nuevo usuario con rol y división | Mensual |
| AS-04 | Editar usuario | Modificar datos, rol, división | Ad-hoc |
| AS-05 | Desactivar usuario | Inhabilitar acceso sin eliminar | Ad-hoc |
| AS-06 | Restablecer contraseña | Enviar link de restablecimiento | Ad-hoc |
| AS-07 | Importar IPR | Carga masiva desde Excel | Inicial/Anual |
| AS-08 | Importar convenios | Carga masiva desde Excel | Inicial/Anual |
| AS-09 | Asignación masiva | Asignar responsables a múltiples IPR | Inicial/Raro |
| AS-10 | Configurar alertas | Definir reglas y umbrales | Inicial/Raro |
| AS-11 | Ver logs del sistema | Revisar errores y actividad | Semanal |
| AS-12 | Gestionar backups | Verificar y restaurar si es necesario | Semanal |

---

# Resumen de Roles y Permisos

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MATRIZ DE PERMISOS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Función                    │ Admin  │ Admin  │ Jefe   │ Encargado          │
│                             │ Sistema│ Regional│División│ Operativo          │
│  ───────────────────────────┼────────┼────────┼────────┼──────────          │
│  CONFIGURACIÓN              │        │        │        │                    │
│  Gestionar divisiones       │   ✅   │   ❌   │   ❌   │   ❌               │
│  Gestionar usuarios         │   ✅   │   ❌   │   ❌   │   ❌               │
│  Configurar alertas         │   ✅   │   ❌   │   ❌   │   ❌               │
│  Importar datos             │   ✅   │   ❌   │   ❌   │   ❌               │
│  ───────────────────────────┼────────┼────────┼────────┼──────────          │
│  IPR                        │        │        │        │                    │
│  Ver todas las IPR          │   ✅   │   ✅   │   ❌   │   ❌               │
│  Ver IPR de mi división     │   ✅   │   ✅   │   ✅   │   ❌               │
│  Ver mis IPR asignadas      │   ✅   │   ✅   │   ✅   │   ✅               │
│  Editar IPR                 │   ✅   │   ✅   │   ✅   │   ❌               │
│  Actualizar avance          │   ✅   │   ✅   │   ✅   │   ✅ (solo suyas)  │
│  Registrar problema         │   ✅   │   ✅   │   ✅   │   ✅               │
│  Asignar responsable        │   ✅   │   ✅   │   ✅   │   ❌               │
│  ───────────────────────────┼────────┼────────┼────────┼──────────          │
│  COMPROMISOS                │        │        │        │                    │
│  Ver todos                  │   ✅   │   ✅   │   ❌   │   ❌               │
│  Ver de mi división         │   ✅   │   ✅   │   ✅   │   ❌               │
│  Ver mis compromisos        │   ✅   │   ✅   │   ✅   │   ✅               │
│  Crear compromiso           │   ✅   │   ✅   │   ✅   │   ❌               │
│  Asignar a otro             │   ✅   │   ✅   │   ✅   │   ❌               │
│  Actualizar estado          │   ✅   │   ✅   │   ✅   │   ✅ (solo suyos)  │
│  Verificar completado       │   ✅   │   ✅   │   ✅   │   ❌               │
│  ───────────────────────────┼────────┼────────┼────────┼──────────          │
│  REUNIONES                  │        │        │        │                    │
│  Crear reunión              │   ✅   │   ✅   │   ✅   │   ❌               │
│  Iniciar/Terminar reunión   │   ✅   │   ✅   │   ❌   │   ❌               │
│  Agregar tema a agenda      │   ✅   │   ✅   │   ✅   │   ✅               │
│  ───────────────────────────┼────────┼────────┼────────┼──────────          │
│  REPORTES                   │        │        │        │                    │
│  Ver dashboard global       │   ✅   │   ✅   │   ❌   │   ❌               │
│  Ver dashboard división     │   ✅   │   ✅   │   ✅   │   ❌               │
│  Exportar reportes          │   ✅   │   ✅   │   ✅   │   ❌               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```
