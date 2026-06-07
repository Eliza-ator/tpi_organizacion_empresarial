VacaBot — TechSoluciones S.R.L.
Chatbot de gestión de vacaciones desarrollado como Trabajo Práctico Integrador
para la materia Organización Empresarial — TUPaD UTN.

Requisitos
- Python 3.8 o superior
- No requiere librerías externas (solo módulos estándar)

Cómo ejecutar
bashpython chatbot.py
Estructura del proyecto
vacabot/
├── chatbot.py          # Código principal del bot
├── README.md           # Este archivo
└── data/
    ├── empleados.csv   # Base de datos de empleados
    ├── solicitudes.csv # Registro de solicitudes
    └── estados_bot.csv # Máquina de estados (sesiones)

Legajos de prueba
LegajoNombreDías disponiblesCaso de pruebaEMP001Ana García10Flujo completoEMP002Lucas Pérez0Sin saldo (GW1 = No)EMP005Valentina Ruiz15Flujo completoEMP004Mateo López3Pocos días disponibles
Proceso automatizado (BPMN To-Be)

Usuario ingresa legajo → Sistema valida en BD
Sistema consulta saldo de días → GW1: ¿tiene días?

NO → informa saldo insuficiente → Fin
SÍ → usuario ingresa fechas


Usuario confirma solicitud → Sistema registra como Pendiente
GW2: ¿jefe aprueba?

SÍ → descuenta días → Fin (Aprobada)
NO → notifica rechazo → Fin (Rechazada)



Manejo de errores (Camino Infeliz)

Legajo inexistente → mensaje de error + reintento
Cantidad de días inválida (texto, negativo, mayor al disponible) → reintento
Fecha con formato incorrecto → reintento
Fecha anterior a hoy → reintento
Confirmación con texto no reconocido → reintento
