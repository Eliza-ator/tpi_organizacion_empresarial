"""
VacaBot — TechSoluciones S.R.L.
Chatbot de gestión de vacaciones
Materia: Organización Empresarial — TUPaD UTN
"""

import csv
import os
import re
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# RUTAS DE ARCHIVOS (base de datos simulada)
# ─────────────────────────────────────────────
DIR = os.path.dirname(os.path.abspath(__file__))
EMPLEADOS_CSV   = os.path.join(DIR, "data", "empleados.csv")
SOLICITUDES_CSV = os.path.join(DIR, "data", "solicitudes.csv")
ESTADOS_CSV     = os.path.join(DIR, "data", "estados_bot.csv")


# ─────────────────────────────────────────────
# UTILIDADES DE BASE DE DATOS (CSV)
# ─────────────────────────────────────────────

def leer_csv(path):
    """Lee un archivo CSV y retorna lista de diccionarios."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def escribir_csv(path, filas, campos):
    """Sobreescribe un CSV con las filas dadas."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)

def buscar_empleado(legajo):
    """Retorna el dict del empleado o None si no existe."""
    for emp in leer_csv(EMPLEADOS_CSV):
        if emp["legajo"].upper() == legajo.upper():
            return emp
    return None

def descontar_dias(legajo, dias):
    """Descuenta días usados al empleado en el CSV."""
    filas = leer_csv(EMPLEADOS_CSV)
    campos = filas[0].keys() if filas else []
    for f in filas:
        if f["legajo"].upper() == legajo.upper():
            f["dias_usados"]      = str(int(f["dias_usados"]) + dias)
            f["dias_disponibles"] = str(int(f["dias_disponibles"]) - dias)
    escribir_csv(EMPLEADOS_CSV, filas, list(campos))

def registrar_solicitud(legajo, jefe, fecha_inicio, fecha_fin, dias, estado, obs=""):
    """Agrega una fila nueva a solicitudes.csv."""
    filas = leer_csv(SOLICITUDES_CSV)
    nuevo_id = f"SOL{str(len(filas)+1).zfill(3)}"
    campos = ["id_solicitud","legajo_empleado","fecha_inicio","fecha_fin",
              "dias_solicitados","estado","legajo_jefe","fecha_solicitud","observacion"]
    filas.append({
        "id_solicitud":    nuevo_id,
        "legajo_empleado": legajo,
        "fecha_inicio":    fecha_inicio,
        "fecha_fin":       fecha_fin,
        "dias_solicitados":str(dias),
        "estado":          estado,
        "legajo_jefe":     jefe,
        "fecha_solicitud": datetime.now().strftime("%d/%m/%Y"),
        "observacion":     obs,
    })
    escribir_csv(SOLICITUDES_CSV, filas, campos)
    return nuevo_id

def registrar_estado_sesion(legajo, estado, ultimo_paso, dato_temp=""):
    """Escribe/actualiza el estado de la sesión activa."""
    filas = leer_csv(ESTADOS_CSV)
    campos = ["id_sesion","legajo","estado_actual","ultimo_paso","fecha_hora","dato_temp"]
    # Busca si ya existe sesión para este legajo
    encontrado = False
    nuevo_id = f"SES{str(len(filas)+1).zfill(3)}"
    for f in filas:
        if f["legajo"].upper() == legajo.upper():
            f["estado_actual"] = estado
            f["ultimo_paso"]   = ultimo_paso
            f["fecha_hora"]    = datetime.now().strftime("%d/%m/%Y %H:%M")
            f["dato_temp"]     = dato_temp
            encontrado = True
            break
    if not encontrado:
        filas.append({
            "id_sesion":    nuevo_id,
            "legajo":       legajo,
            "estado_actual":estado,
            "ultimo_paso":  ultimo_paso,
            "fecha_hora":   datetime.now().strftime("%d/%m/%Y %H:%M"),
            "dato_temp":    dato_temp,
        })
    escribir_csv(ESTADOS_CSV, filas, campos)


# ─────────────────────────────────────────────
# VALIDACIONES (Camino infeliz / Unhappy Path)
# ─────────────────────────────────────────────

def validar_entero_positivo(texto):
    """Retorna el entero si es válido, o None."""
    try:
        n = int(texto.strip())
        return n if n > 0 else None
    except ValueError:
        return None

def validar_fecha(texto):
    """Valida formato DD/MM/AAAA. Retorna datetime o None."""
    patron = r"^\d{2}/\d{2}/\d{4}$"
    if not re.match(patron, texto.strip()):
        return None
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y")
    except ValueError:
        return None


# ─────────────────────────────────────────────
# HELPERS DE PRESENTACIÓN
# ─────────────────────────────────────────────

def sep():
    print("─" * 50)

def bot(msg):
    print(f"\n🤖 Bot: {msg}")

def error(msg):
    print(f"\n⚠️  Error: {msg}")

def ok(msg):
    print(f"\n✅  {msg}")

def pedir(prompt):
    return input(f"\n👤 Vos: [{prompt}] ").strip()


# ─────────────────────────────────────────────
# MÁQUINA DE ESTADOS — FLUJO PRINCIPAL
# ─────────────────────────────────────────────

def paso_inicio():
    """
    ESTADO: inicio
    Pide el legajo y valida contra la base de datos.
    Corresponde a: U1 → S1 del diagrama BPMN
    """
    bot("Bienvenido/a al sistema de gestión de vacaciones de TechSoluciones S.R.L.")
    bot("Por favor ingresá tu número de legajo (ej: EMP001):")

    while True:
        legajo = pedir("legajo").upper()
        if not legajo:
            error("El legajo no puede estar vacío.")
            continue
        emp = buscar_empleado(legajo)
        if not emp:
            error(f"Legajo '{legajo}' no encontrado. Verificá el número e intentá de nuevo.")
            bot("Legajos válidos de ejemplo: EMP001, EMP003, EMP005")
            continue
        return legajo, emp


def paso_consulta_saldo(legajo, emp):
    """
    ESTADO: consulta_saldo
    Muestra saldo y pide cantidad de días.
    Corresponde a: S2 → GW1 del diagrama BPMN
    """
    bot(f"Legajo encontrado. Bienvenido/a, {emp['nombre']} {emp['apellido']} ({emp['area']}).")
    bot(f"Días disponibles: {emp['dias_disponibles']} de {emp['dias_totales']} totales.")
    registrar_estado_sesion(legajo, "consulta_saldo", "S2 - Consulta saldo")

    # GW1: ¿Tiene días disponibles?
    if int(emp["dias_disponibles"]) == 0:
        registrar_solicitud(legajo, emp["jefe_legajo"], "—", "—", 0, "Sin saldo", "Saldo 0 días")
        registrar_estado_sesion(legajo, "finalizado_sin_saldo", "Fin - Sin saldo")
        bot("Lo sentimos, no tenés días disponibles. La solicitud no puede continuar.")
        return None  # Señal de fin por sin saldo

    bot(f"¿Cuántos días querés solicitar? (máximo {emp['dias_disponibles']}):")

    while True:
        dias = validar_entero_positivo(pedir("número de días"))
        if dias is None:
            error("Ingresá un número entero mayor a 0 (ej: 5).")
            continue
        if dias > int(emp["dias_disponibles"]):
            error(f"Solicitaste {dias} días pero solo tenés {emp['dias_disponibles']} disponibles.")
            bot(f"Ingresá un número entre 1 y {emp['dias_disponibles']}:")
            continue
        return dias


def paso_fechas(dias):
    """
    ESTADO: ingreso_fechas
    Pide y valida la fecha de inicio.
    Corresponde a: U2 del diagrama BPMN
    """
    bot("¿Cuál es la fecha de inicio de tus vacaciones? (formato DD/MM/AAAA):")

    while True:
        texto = pedir("fecha inicio")
        fecha_inicio = validar_fecha(texto)
        if fecha_inicio is None:
            error("Formato inválido. Usá DD/MM/AAAA (ej: 15/07/2025).")
            continue
        if fecha_inicio < datetime.now():
            error("La fecha de inicio no puede ser anterior a hoy.")
            continue
        break

    fecha_fin = fecha_inicio + timedelta(days=dias - 1)
    return fecha_inicio.strftime("%d/%m/%Y"), fecha_fin.strftime("%d/%m/%Y")


def paso_confirmacion(emp, dias, fecha_inicio, fecha_fin):
    """
    ESTADO: esperando_confirmacion
    Muestra resumen y pide confirmación.
    """
    sep()
    bot("Resumen de tu solicitud:")
    print(f"   • Empleado : {emp['nombre']} {emp['apellido']}")
    print(f"   • Días     : {dias}")
    print(f"   • Desde    : {fecha_inicio}")
    print(f"   • Hasta    : {fecha_fin}")
    print(f"   • Jefe     : {emp['jefe_legajo']}")
    sep()
    bot("¿Confirmás el envío? (si / no):")

    while True:
        resp = pedir("si / no").lower()
        if resp in ("si", "sí", "s"):
            return True
        if resp in ("no", "n"):
            return False
        error("Respuesta no reconocida. Escribí 'si' o 'no'.")


def paso_aprobacion(legajo, emp, dias, fecha_inicio, fecha_fin):
    """
    ESTADO: esperando_aprobacion → GW2
    Simula la decisión del jefe.
    Corresponde a: S3 → GW2 → S4/S6 del diagrama BPMN
    """
    id_sol = registrar_solicitud(
        legajo, emp["jefe_legajo"], fecha_inicio, fecha_fin, dias, "Pendiente"
    )
    registrar_estado_sesion(legajo, "esperando_aprobacion", "S3 - Registra solicitud", id_sol)
    bot(f"Solicitud {id_sol} registrada. Notificando a tu jefe ({emp['jefe_legajo']})...")

    # ── GW2: simulación de decisión del jefe ──
    # En un sistema real esto vendría de una respuesta del jefe.
    # Aquí simulamos: aprueba si hay más de 2 días de margen.
    aprueba = int(emp["dias_disponibles"]) - dias >= 0

    bot("El jefe revisó la solicitud...")

    if aprueba:
        descontar_dias(legajo, dias)
        registrar_solicitud(
            legajo, emp["jefe_legajo"], fecha_inicio, fecha_fin, dias, "Aprobada"
        )
        registrar_estado_sesion(legajo, "finalizado_aprobado", "Fin - Aprobado", id_sol)
        ok(f"¡Solicitud APROBADA! Tus días fueron descontados. "
           f"Días restantes: {int(emp['dias_disponibles']) - dias}")
    else:
        registrar_solicitud(
            legajo, emp["jefe_legajo"], fecha_inicio, fecha_fin, dias,
            "Rechazada", "Alta carga de trabajo"
        )
        registrar_estado_sesion(legajo, "finalizado_rechazado", "Fin - Rechazado", id_sol)
        error("Solicitud RECHAZADA. Motivo: alta carga de trabajo en el área.")
        bot("Podés intentar con otras fechas en una nueva consulta.")


# ─────────────────────────────────────────────
# PUNTO DE ENTRADA PRINCIPAL
# ─────────────────────────────────────────────

def main():
    sep()
    print("   VACABOT — TechSoluciones S.R.L.")
    print("   Sistema de Gestión de Vacaciones")
    sep()

    continuar = True
    while continuar:
        # ESTADO 1: Inicio — validar legajo
        legajo, emp = paso_inicio()

        # ESTADO 2: Consulta saldo — GW1
        dias = paso_consulta_saldo(legajo, emp)
        if dias is None:
            # GW1 → camino infeliz: sin saldo
            pass
        else:
            # ESTADO 3: Ingreso de fechas
            fecha_inicio, fecha_fin = paso_fechas(dias)

            # ESTADO 4: Confirmación
            confirmado = paso_confirmacion(emp, dias, fecha_inicio, fecha_fin)

            if confirmado:
                # ESTADO 5: Aprobación del jefe — GW2
                paso_aprobacion(legajo, emp, dias, fecha_inicio, fecha_fin)
            else:
                bot("Solicitud cancelada. No se realizaron cambios.")
                registrar_estado_sesion(legajo, "cancelado", "Fin - Cancelado por usuario")

        sep()
        resp = input("\n¿Querés realizar otra consulta? (si / no): ").strip().lower()
        continuar = resp in ("si", "sí", "s")

    sep()
    bot("Gracias por usar VacaBot. ¡Hasta luego!")
    sep()


if __name__ == "__main__":
    main()
