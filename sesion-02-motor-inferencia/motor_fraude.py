# -*- coding: utf-8 -*-
"""
Taller de Laboratorio: Motor de Inferencia para Detección de Fraude Bancario
===========================================================================
Asignatura : Sistemas Expertos e Inteligencia Artificial - VIII Semestre
Sesión 2   : Motor de Inferencia y Modus Ponens
Docente    : Amaury Giovanni Méndez Aguirre

Diferencia central frente a la Sesión 1
---------------------------------------
En la sesión anterior las reglas estaban ESCRITAS EN EL CÓDIGO (if/elif). Aquí
las reglas son DATOS: una lista de diccionarios que el motor lee y evalúa. El
motor no sabe nada de fraude ni de motocicletas; solo sabe aplicar Modus Ponens.
Por eso al final del archivo el MISMO motor resuelve una base de conocimientos
totalmente distinta sin cambiar una sola línea de su código.

Ciclo de vida implementado (el de la teoría de la sesión):
    1. EQUIPARACIÓN (Match)      -> qué reglas tienen sus premisas satisfechas
    2. RESOLUCIÓN DE CONFLICTOS  -> si hay varias candidatas, cuál se ejecuta
    3. EJECUCIÓN (Fire)          -> se agrega la conclusión como hecho nuevo
    ... y se vuelve al paso 1 hasta que no se deduzcan hechos nuevos.
"""


# ===========================================================================
# PARTE 1. MOTOR DE INFERENCIA GENÉRICO (lógica de control)
# ===========================================================================

def evaluar_condicion(memoria, clave, criterio):
    """Evalúa UNA premisa contra la memoria de trabajo.

    Soporta dos formas de criterio:
      * Valor directo      -> {"pais_extranjero": True}   se compara por igualdad
      * Tupla (op, valor)  -> {"monto": (">", 5000)}      se compara por operador

    La versión vista en clase solo compara por igualdad (hechos.get(k) == v).
    Se amplía aquí porque el enunciado exige la premisa [monto > 5000], que es
    una comparación numérica y no una igualdad.
    """
    if clave not in memoria:
        return False

    valor = memoria[clave]

    # Criterio simple: igualdad estricta (comportamiento original del motor).
    if not isinstance(criterio, tuple):
        return valor == criterio

    operador, referencia = criterio

    # Los operadores relacionales solo tienen sentido sobre números.
    if not isinstance(valor, (int, float)) or isinstance(valor, bool):
        return False

    if operador == ">":
        return valor > referencia
    if operador == ">=":
        return valor >= referencia
    if operador == "<":
        return valor < referencia
    if operador == "<=":
        return valor <= referencia
    if operador == "==":
        return valor == referencia
    if operador == "!=":
        return valor != referencia

    raise ValueError("Operador no soportado: {}".format(operador))


def premisas_satisfechas(regla, memoria):
    """all() actúa como la COMPUERTA LÓGICA AND entre todas las premisas.

    Basta que una premisa sea falsa para que la regla completa no se dispare.
    Sobre una lista vacía all() retorna True, es decir, una regla sin premisas
    sería un axioma que siempre dispara.
    """
    return all(
        evaluar_condicion(memoria, clave, criterio)
        for clave, criterio in regla["condiciones"].items()
    )


def aporta_hechos_nuevos(regla, memoria):
    """True si la conclusión agrega al menos un hecho que aún no está en memoria.

    Sin esta verificación el motor volvería a disparar eternamente las mismas
    reglas: es la condición que garantiza que el ciclo while termine.
    """
    return any(clave not in memoria for clave in regla["conclusion"])


def motor_inferencia(hechos_iniciales, base_reglas, mostrar_traza=True, limite=100):
    """Encadenamiento hacia adelante (forward chaining) dirigido por datos.

    Dispara UNA regla por ciclo, tal como describe el ciclo de vida teórico:
    tras cada ejecución se reinicia la equiparación, porque el hecho recién
    deducido puede habilitar reglas que antes no aplicaban.

    Retorna (memoria_final, cadena_de_inferencia, ciclos_ejecutados).
    """
    memoria = dict(hechos_iniciales)   # copia: no se contamina el hecho original
    ya_disparadas = []                 # refractariedad: cada regla dispara una vez
    ciclo = 0

    while ciclo < limite:
        ciclo += 1

        # --- PASO 1: EQUIPARACIÓN (Match) --------------------------------
        # Se construye el CONJUNTO DE CONFLICTO: reglas aplicables ahora mismo.
        conjunto_conflicto = [
            regla for regla in base_reglas
            if regla["id"] not in ya_disparadas
            and premisas_satisfechas(regla, memoria)
            and aporta_hechos_nuevos(regla, memoria)
        ]

        # Condición de parada: no hay nada más que deducir.
        if not conjunto_conflicto:
            if mostrar_traza:
                print("  Ciclo {}: conjunto de conflicto vacío -> el motor se detiene.".format(ciclo))
            break

        # --- PASO 2: RESOLUCIÓN DE CONFLICTOS ----------------------------
        # Criterio: mayor prioridad. En caso de empate gana la que aparece
        # primero en la base de reglas (max() conserva el primer máximo).
        regla = max(conjunto_conflicto, key=lambda r: r.get("prioridad", 0))

        # --- PASO 3: EJECUCIÓN (Fire) ------------------------------------
        # Modus Ponens: si las premisas son verdaderas, la conclusión pasa a
        # ser un hecho verdadero de la memoria de trabajo.
        nuevos = {c: v for c, v in regla["conclusion"].items() if c not in memoria}
        memoria.update(nuevos)
        ya_disparadas.append(regla["id"])

        if mostrar_traza:
            candidatas = ", ".join(r["id"] for r in conjunto_conflicto)
            deducidos = ", ".join("{} = {}".format(c, v) for c, v in nuevos.items())
            print("  Ciclo {}: conflicto [{}] -> dispara {} (prioridad {})".format(
                ciclo, candidatas, regla["id"], regla.get("prioridad", 0)))
            print("           Modus Ponens: {}".format(regla["descripcion"]))
            print("           Nuevo(s) hecho(s): {}".format(deducidos))

    return memoria, ya_disparadas, ciclo


# ===========================================================================
# PARTE 2. BASE DE CONOCIMIENTOS: DETECCIÓN DE FRAUDE BANCARIO
# ===========================================================================
# Las reglas son DATOS, no código. Un analista de riesgo podría editarlas sin
# tocar el motor. Nótese que la disyunción (OR) no se escribe dentro de una
# regla, porque all() solo modela conjunción: se expresa como DOS reglas
# distintas que concluyen el mismo hecho (R1 y R2, R3 y R5).

reglas_fraude = [
    {
        "id": "R1",
        "descripcion": "SI monto > 5000 ENTONCES transaccion_inusual",
        "prioridad": 8,
        "condiciones": {"monto": (">", 5000)},
        "conclusion": {"transaccion_inusual": True},
    },
    {
        "id": "R2",
        "descripcion": "SI intentos_fallidos >= 3 ENTONCES transaccion_inusual",
        "prioridad": 8,
        "condiciones": {"intentos_fallidos": (">=", 3)},
        "conclusion": {"transaccion_inusual": True},
    },
    {
        "id": "R3",
        "descripcion": ("SI transaccion_inusual Y pais_extranjero Y NO cliente_viajando "
                        "ENTONCES bloquear_tarjeta"),
        "prioridad": 10,
        "condiciones": {
            "transaccion_inusual": True,
            "pais_extranjero": True,
            "cliente_viajando": False,
        },
        "conclusion": {"bloquear_tarjeta": True},
    },
    {
        "id": "R4",
        "descripcion": ("SI hora < 6 Y NO dispositivo_conocido "
                        "ENTONCES dispositivo_sospechoso"),
        "prioridad": 8,
        "condiciones": {"hora": ("<", 6), "dispositivo_conocido": False},
        "conclusion": {"dispositivo_sospechoso": True},
    },
    {
        "id": "R5",
        "descripcion": ("SI dispositivo_sospechoso Y transaccion_inusual "
                        "ENTONCES bloquear_tarjeta"),
        "prioridad": 10,
        "condiciones": {"dispositivo_sospechoso": True, "transaccion_inusual": True},
        "conclusion": {"bloquear_tarjeta": True},
    },
    {
        "id": "R6",
        "descripcion": ("SI bloquear_tarjeta ENTONCES notificar_cliente Y "
                        "registrar_incidente"),
        "prioridad": 5,
        "condiciones": {"bloquear_tarjeta": True},
        "conclusion": {"notificar_cliente": True, "registrar_incidente": True},
    },
    {
        "id": "R7",
        "descripcion": ("SI bloquear_tarjeta Y monto > 10000 "
                        "ENTONCES escalar_a_investigacion"),
        "prioridad": 6,
        "condiciones": {"bloquear_tarjeta": True, "monto": (">", 10000)},
        "conclusion": {"escalar_a_investigacion": True},
    },
    {
        "id": "R8",
        "descripcion": ("SI transaccion_inusual Y cliente_viajando "
                        "ENTONCES solicitar_confirmacion"),
        "prioridad": 7,
        "condiciones": {"transaccion_inusual": True, "cliente_viajando": True},
        "conclusion": {"solicitar_confirmacion": True},
    },
]


def veredicto_fraude(memoria):
    """Traduce la memoria final a la decisión operativa del banco."""
    if memoria.get("escalar_a_investigacion"):
        return "TARJETA BLOQUEADA Y CASO ESCALADO A INVESTIGACIÓN"
    if memoria.get("bloquear_tarjeta"):
        return "TARJETA BLOQUEADA"
    if memoria.get("solicitar_confirmacion"):
        return "TRANSACCIÓN RETENIDA: se solicita confirmación al cliente"
    if memoria.get("transaccion_inusual"):
        return "TRANSACCIÓN MARCADA COMO INUSUAL: monitoreo reforzado"
    return "TRANSACCIÓN APROBADA: sin indicadores de fraude"


def analizar_transaccion(nombre, hechos):
    """Ejecuta el motor sobre una transacción y presenta la explicación."""
    print("=" * 78)
    print("TRANSACCIÓN: {}".format(nombre))
    print("-" * 78)
    print("  Hechos iniciales: {}".format(hechos))
    print("  --- Traza del motor de inferencia ---")

    memoria, cadena, ciclos = motor_inferencia(hechos, reglas_fraude)

    deducidos = {c: v for c, v in memoria.items() if c not in hechos}
    print("  --- Resultado ---")
    print("  Cadena de inferencia : {}".format(" -> ".join(cadena) if cadena else "(ninguna regla disparó)"))
    print("  Hechos deducidos     : {}".format(deducidos if deducidos else "ninguno"))
    print("  Ciclos ejecutados    : {}".format(ciclos))
    print("  VEREDICTO            : {}".format(veredicto_fraude(memoria)))
    print()


# ===========================================================================
# PARTE 3. VERIFICACIÓN DEL TALLER ANALÍTICO 2 (base de la motocicleta)
# ===========================================================================
# El mismo motor, sin modificar una línea, resuelve un dominio distinto. Esto
# comprueba que la lógica de control y el conocimiento están separados, y sirve
# para validar la traza hecha a mano en el Taller Analítico 2.

reglas_motocicleta = [
    {
        "id": "R1",
        "descripcion": "SI tiene_motor Y tiene_dos_ruedas ENTONCES es_motocicleta",
        "prioridad": 0,
        "condiciones": {"tiene_motor": True, "tiene_dos_ruedas": True},
        "conclusion": {"es_motocicleta": True},
    },
    {
        "id": "R2",
        "descripcion": "SI es_motocicleta ENTONCES requiere_casco",
        "prioridad": 0,
        "condiciones": {"es_motocicleta": True},
        "conclusion": {"requiere_casco": True},
    },
    {
        "id": "R3",
        "descripcion": "SI requiere_casco Y es_menor_de_edad ENTONCES permiso_denegado",
        "prioridad": 0,
        "condiciones": {"requiere_casco": True, "es_menor_de_edad": True},
        "conclusion": {"permiso_denegado": True},
    },
]


# ===========================================================================
# EJECUCIÓN
# ===========================================================================

if __name__ == "__main__":

    print("\nMOTOR DE INFERENCIA - SISTEMA DE DETECCIÓN DE FRAUDE BANCARIO\n")

    # --- Caso 1: flujo exigido por el enunciado -------------------------
    # monto > 5000 -> transaccion_inusual; inusual + pais extranjero -> bloqueo.
    analizar_transaccion("Compra en el exterior de madrugada", {
        "monto": 8500,
        "pais_extranjero": True,
        "hora": 3,
        "dispositivo_conocido": False,
        "intentos_fallidos": 1,
        "cliente_viajando": False,
    })

    # --- Caso 2: el aviso de viaje cambia por completo la conclusión ----
    analizar_transaccion("Compra en el exterior con aviso de viaje", {
        "monto": 7000,
        "pais_extranjero": True,
        "hora": 14,
        "dispositivo_conocido": True,
        "intentos_fallidos": 0,
        "cliente_viajando": True,
    })

    # --- Caso 3: cadena por la vía alterna (R2 y R5) --------------------
    # Monto bajo y transacción nacional: el fraude se detecta por intentos
    # fallidos y dispositivo desconocido, no por el monto.
    analizar_transaccion("Monto bajo con múltiples intentos fallidos", {
        "monto": 200,
        "pais_extranjero": False,
        "hora": 2,
        "dispositivo_conocido": False,
        "intentos_fallidos": 4,
        "cliente_viajando": False,
    })

    # --- Caso 4: escalamiento por cuantía -------------------------------
    analizar_transaccion("Transferencia de alta cuantía al exterior", {
        "monto": 25000,
        "pais_extranjero": True,
        "hora": 11,
        "dispositivo_conocido": True,
        "intentos_fallidos": 0,
        "cliente_viajando": False,
    })

    # --- Caso 5: transacción legítima (ninguna regla dispara) -----------
    analizar_transaccion("Compra habitual en comercio local", {
        "monto": 120,
        "pais_extranjero": False,
        "hora": 13,
        "dispositivo_conocido": True,
        "intentos_fallidos": 0,
        "cliente_viajando": False,
    })

    # --- Verificación de la traza del Taller Analítico 2 ----------------
    print("=" * 78)
    print("VERIFICACIÓN DEL TALLER ANALÍTICO 2: base de conocimientos de la motocicleta")
    print("(el mismo motor, otra base de conocimientos)")
    print("-" * 78)
    hechos_vehiculo = {
        "tiene_motor": True,
        "tiene_dos_ruedas": True,
        "es_menor_de_edad": True,
    }
    print("  Hechos iniciales: {}".format(hechos_vehiculo))
    print("  --- Traza del motor de inferencia ---")
    memoria_v, cadena_v, ciclos_v = motor_inferencia(hechos_vehiculo, reglas_motocicleta)
    print("  --- Resultado ---")
    print("  Cadena de inferencia : {}".format(" -> ".join(cadena_v)))
    print("  Memoria final        : {}".format(memoria_v))
    print("  Ciclos ejecutados    : {}".format(ciclos_v))
    print("=" * 78)
