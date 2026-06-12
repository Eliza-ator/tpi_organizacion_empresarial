# VacaBot — TechSoluciones S.R.L.

Chatbot de gestión de vacaciones desarrollado como Trabajo Práctico Integrador para la materia Organización Empresarial — TUPaD UTN.

## Requisitos

- Python 3.8 o superior
- No requiere librerías externas (solo módulos estándar)

## Cómo ejecutar

```bash
python chatbot.py
```

## Estructura del proyecto
vacabot/

├── chatbot.py          # Código principal del bot

├── README.md           # Este archivo

└── data/

├── empleados.csv   # Base de datos de empleados

├── solicitudes.csv # Registro de solicitudes

└── estados_bot.csv # Máquina de estados (sesiones)

## Legajos de prueba

| Legajo | Nombre | Días disponibles | Caso de prueba |
|--------|--------|-----------------|----------------|
| EMP001 | Ana García | 10 | Flujo completo |
| EMP002 | Lucas Pérez | 0 | Sin saldo (GW1 = No) |
| EMP005 | Valentina Ruiz | 15 | Flujo completo |
| EMP004 | Mateo López | 3 | Pocos días disponibles |

## Proceso automatizado (BPMN To-Be)

1. Usuario ingresa legajo → Sistema valida en BD
2. Sistema consulta saldo de días → **GW1: ¿tiene días?**
   - ❌ NO → informa saldo insuficiente → Fin
   - ✅ SÍ → usuario ingresa fechas
3. Usuario confirma solicitud → Sistema registra como Pendiente
4. **GW2: ¿jefe aprueba?**
   - ✅ SÍ → descuenta días → Fin (Aprobada)
   - ❌ NO → notifica rechazo → Fin (Rechazada)

## Manejo de errores (Camino Infeliz)

- Legajo inexistente → mensaje de error + reintento
- Cantidad de días inválida (texto, negativo, mayor al disponible) → reintento
- Fecha con formato incorrecto → reintento
- Fecha anterior a hoy → reintento
- Confirmación con texto no reconocido → reintento
