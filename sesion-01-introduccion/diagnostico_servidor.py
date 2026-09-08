# -*- coding: utf-8 -*-
"""
Taller de Laboratorio: Sistema Experto de Diagnóstico IT (HelpDesk)
==================================================================
Asignatura : Sistemas Expertos e Inteligencia Artificial - VIII Semestre
Sesión 1   : Introducción a Sistemas Expertos y repaso de Python
Docente    : Amaury Giovanni Méndez Aguirre

Arquitectura del sistema experto implementada:
  * BASE DE HECHOS (memoria de trabajo) -> diccionario `servidor_estado`
  * BASE DE REGLAS + MOTOR DE INFERENCIA -> función `diagnosticar_servidor(hechos)`
  * MÓDULO DE EXPLICACIÓN -> la regla disparada y su justificación se retornan
    junto al veredicto, de modo que el diagnóstico sea auditable.

El motor usa encadenamiento hacia adelante con reglas ordenadas por prioridad:
la primera regla que se satisface concluye y detiene la inferencia (return).
"""


# ---------------------------------------------------------------------------
# 1. MEMORIA DE TRABAJO (Base de Hechos)
# ---------------------------------------------------------------------------
# Diccionario (hash map): acceso a cada hecho en tiempo constante O(1).

servidor_estado = {
    "cpu_uso": 45.0,            # % de uso de CPU
    "memoria_libre": 62.0,      # % de RAM disponible
    "ping_respuesta": 25.0,     # latencia en milisegundos
    "temperatura": 58.0,        # grados Celsius
    "ventilador_activo": True,  # True = ventilador encendido
    "disco_libre": 40.0,        # % de espacio libre en disco
}


# ---------------------------------------------------------------------------
# 2. BASE DE REGLAS Y MOTOR DE INFERENCIA
# ---------------------------------------------------------------------------

def diagnosticar_servidor(hechos):
    """Evalúa la memoria de trabajo y retorna el diagnóstico del servidor.

    Retorna una tupla (nivel, regla, diagnostico, accion):
        nivel       -- "CRÍTICO" | "ADVERTENCIA" | "DEGRADADO" | "NORMAL"
        regla       -- identificador de la regla disparada (trazabilidad)
        diagnostico -- explicación en lenguaje natural
        accion      -- recomendación para el técnico del HelpDesk
    """

    # === R1 - REGLAS DE ESTADO CRÍTICO (prioridad 1: riesgo de daño físico
    #     o caída total del servicio). Bloque de reglas anidadas. ===
    if hechos["temperatura"] > 80 or hechos["cpu_uso"] > 95 or hechos["memoria_libre"] < 5:

        # R1.1 - Sobrecalentamiento con refrigeración inoperante
        if hechos["temperatura"] > 80 and not hechos["ventilador_activo"]:
            return ("CRÍTICO", "R1.1",
                    "Sobrecalentamiento con ventilador apagado ({}°C).".format(hechos["temperatura"]),
                    "Apagado preventivo inmediato y revisión física de la refrigeración.")

        # R1.2 - Sobrecalentamiento con refrigeración activa
        elif hechos["temperatura"] > 80:
            return ("CRÍTICO", "R1.2",
                    "Temperatura crítica ({}°C) pese a tener el ventilador activo.".format(hechos["temperatura"]),
                    "Migrar las cargas de trabajo y programar mantenimiento del disipador.")

        # R1.3 - Agotamiento simultáneo de recursos de cómputo
        elif hechos["cpu_uso"] > 95 and hechos["memoria_libre"] < 5:
            return ("CRÍTICO", "R1.3",
                    "Recursos agotados: CPU al {}% y solo {}% de memoria libre.".format(
                        hechos["cpu_uso"], hechos["memoria_libre"]),
                    "Reiniciar el servicio y aislar el proceso que consume los recursos.")

        # R1.4 - Saturación de un único recurso
        else:
            return ("CRÍTICO", "R1.4",
                    "Saturación de un recurso: CPU {}% / memoria libre {}%.".format(
                        hechos["cpu_uso"], hechos["memoria_libre"]),
                    "Escalar a infraestructura y revisar los procesos activos.")

    # === R2 - REGLAS DE ADVERTENCIA (prioridad 2: el servicio funciona,
    #     pero la tendencia conduce a un estado crítico). ===
    elif (hechos["temperatura"] > 65 or hechos["cpu_uso"] > 80
          or hechos["memoria_libre"] < 20 or hechos["disco_libre"] < 15):

        # R2.1 - Calentamiento anticipado por falla de refrigeración
        if hechos["temperatura"] > 65 and not hechos["ventilador_activo"]:
            return ("ADVERTENCIA", "R2.1",
                    "Temperatura elevada ({}°C) y ventilador apagado.".format(hechos["temperatura"]),
                    "Activar la refrigeración antes de alcanzar el umbral crítico.")

        # R2.2 - Presión combinada sobre CPU y memoria
        elif hechos["cpu_uso"] > 80 and hechos["memoria_libre"] < 20:
            return ("ADVERTENCIA", "R2.2",
                    "Carga sostenida: CPU {}% con solo {}% de memoria libre.".format(
                        hechos["cpu_uso"], hechos["memoria_libre"]),
                    "Planificar balanceo de carga en la próxima ventana de mantenimiento.")

        # R2.3 - Espacio en disco por agotarse
        elif hechos["disco_libre"] < 15:
            return ("ADVERTENCIA", "R2.3",
                    "Espacio en disco bajo: {}% libre.".format(hechos["disco_libre"]),
                    "Purgar logs y temporales; evaluar ampliación del volumen.")

        # R2.4 - Umbral de advertencia superado en un solo indicador
        else:
            return ("ADVERTENCIA", "R2.4",
                    "Un indicador superó el umbral de advertencia (temp {}°C, CPU {}%, mem libre {}%).".format(
                        hechos["temperatura"], hechos["cpu_uso"], hechos["memoria_libre"]),
                    "Mantener el servidor bajo monitoreo reforzado.")

    # === R3 - REGLAS DE RED (prioridad 3: el hardware está sano, pero la
    #     conectividad degrada la experiencia del usuario). ===
    elif hechos["ping_respuesta"] > 100 or hechos["ping_respuesta"] < 0:

        # R3.1 - Servidor inalcanzable (ping negativo = sin respuesta)
        if hechos["ping_respuesta"] < 0:
            return ("CRÍTICO", "R3.1",
                    "Sin respuesta a ping: el servidor está inalcanzable en la red.",
                    "Verificar enlace físico, switch y reglas de firewall.")

        # R3.2 - Latencia degradada
        else:
            return ("DEGRADADO", "R3.2",
                    "Latencia alta: {} ms de respuesta.".format(hechos["ping_respuesta"]),
                    "Revisar saturación del enlace y calidad de servicio (QoS).")

    # === R4 - REGLA POR DEFECTO (fallback: garantiza que todo caso reciba un
    #     veredicto, es decir, que la base de reglas sea completa). ===
    return ("NORMAL", "R4",
            "Todas las métricas se encuentran dentro de los rangos operativos.",
            "No se requiere intervención; continuar con el monitoreo rutinario.")


# ---------------------------------------------------------------------------
# 3. INTERFAZ DE USUARIO / MÓDULO DE EXPLICACIÓN
# ---------------------------------------------------------------------------

def imprimir_diagnostico(nombre_caso, hechos):
    """Muestra los hechos de entrada y el veredicto justificado del motor."""
    nivel, regla, diagnostico, accion = diagnosticar_servidor(hechos)

    print("=" * 74)
    print("CASO: {}".format(nombre_caso))
    print("-" * 74)
    print("  Hechos     : CPU {}% | Mem libre {}% | Disco libre {}% | Ping {} ms".format(
        hechos["cpu_uso"], hechos["memoria_libre"], hechos["disco_libre"], hechos["ping_respuesta"]))
    print("               Temp {}°C | Ventilador {}".format(
        hechos["temperatura"], "ENCENDIDO" if hechos["ventilador_activo"] else "APAGADO"))
    print("  Veredicto  : [{}]".format(nivel))
    print("  Regla      : {}   (trazabilidad de la inferencia)".format(regla))
    print("  Diagnóstico: {}".format(diagnostico))
    print("  Acción     : {}".format(accion))
    print()


# ---------------------------------------------------------------------------
# 4. EJECUCIÓN: COBERTURA DE RAMAS DEL MOTOR DE INFERENCIA
# ---------------------------------------------------------------------------
# Se modifican los valores del diccionario original para comprobar que el
# motor recorre caminos lógicos distintos según los hechos que recibe.

if __name__ == "__main__":

    print("\nSISTEMA EXPERTO DE DIAGNÓSTICO IT - HELPDESK\n")

    # --- Caso 1: estado inicial (rama R4 - fallback) ---
    imprimir_diagnostico("Estado inicial del servidor", servidor_estado)

    # --- Caso 2: crítico por sobrecalentamiento sin ventilador (R1.1) ---
    servidor_estado["temperatura"] = 87.0
    servidor_estado["ventilador_activo"] = False
    imprimir_diagnostico("Sobrecalentamiento con ventilador apagado", servidor_estado)

    # --- Caso 3: crítico por temperatura con ventilador encendido (R1.2) ---
    servidor_estado["ventilador_activo"] = True
    imprimir_diagnostico("Temperatura crítica con refrigeración activa", servidor_estado)

    # --- Caso 4: crítico por agotamiento de CPU y memoria (R1.3) ---
    servidor_estado["temperatura"] = 60.0
    servidor_estado["cpu_uso"] = 98.0
    servidor_estado["memoria_libre"] = 3.0
    imprimir_diagnostico("Recursos de cómputo agotados", servidor_estado)

    # --- Caso 5: advertencia por temperatura y ventilador apagado (R2.1) ---
    servidor_estado["cpu_uso"] = 50.0
    servidor_estado["memoria_libre"] = 55.0
    servidor_estado["temperatura"] = 70.0
    servidor_estado["ventilador_activo"] = False
    imprimir_diagnostico("Calentamiento temprano sin refrigeración", servidor_estado)

    # --- Caso 6: advertencia por carga combinada CPU + memoria (R2.2) ---
    servidor_estado["temperatura"] = 55.0
    servidor_estado["ventilador_activo"] = True
    servidor_estado["cpu_uso"] = 85.0
    servidor_estado["memoria_libre"] = 12.0
    imprimir_diagnostico("Carga sostenida de CPU y memoria", servidor_estado)

    # --- Caso 7: advertencia por disco (R2.3) ---
    servidor_estado["cpu_uso"] = 40.0
    servidor_estado["memoria_libre"] = 60.0
    servidor_estado["disco_libre"] = 8.0
    imprimir_diagnostico("Espacio en disco por agotarse", servidor_estado)

    # --- Caso 8: red degradada por latencia (R3.2) ---
    servidor_estado["disco_libre"] = 45.0
    servidor_estado["ping_respuesta"] = 350.0
    imprimir_diagnostico("Latencia de red elevada", servidor_estado)

    # --- Caso 9: servidor inalcanzable (R3.1) ---
    servidor_estado["ping_respuesta"] = -1
    imprimir_diagnostico("Servidor sin respuesta a ping", servidor_estado)

    # --- Caso 10: crítico por saturación de un solo recurso (R1.4) ---
    servidor_estado["ping_respuesta"] = 20.0
    servidor_estado["cpu_uso"] = 97.0
    imprimir_diagnostico("Saturación de CPU sin agotamiento de memoria", servidor_estado)

    # --- Caso 11: advertencia por un único indicador (R2.4) ---
    servidor_estado["cpu_uso"] = 45.0
    servidor_estado["temperatura"] = 70.0
    imprimir_diagnostico("Temperatura de advertencia con ventilador activo", servidor_estado)

    print("=" * 74)
    print("Cobertura verificada: R1.1, R1.2, R1.3, R1.4, R2.1, R2.2, R2.3, R2.4,")
    print("                      R3.1, R3.2 y R4 (todas las ramas del motor).")
    print("=" * 74)
