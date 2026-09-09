# -*- coding: utf-8 -*-
"""
Taller de Laboratorio: Motor Lógico de Recursos Humanos (Modelo Mamdani)
=======================================================================
Asignatura : Sistemas Expertos e Inteligencia Artificial - VIII Semestre
Sesión 4   : Inferencia Difusa (Modelo Mamdani)
Docente    : Amaury Giovanni Méndez Aguirre

Problema
--------
En una empresa el bono anual depende del desempeño y la antigüedad del
empleado. Ninguna de las dos es una variable de sí o no: un empleado puede ser
"excelente" en grado 0.85 y llevar "mucho tiempo" en grado 0.60 al mismo
tiempo. La pregunta que resuelve Mamdani es cómo evaluar una regla cuando sus
premisas no son ni completamente verdaderas ni completamente falsas.

Ebrahim Mamdani propuso en 1975 propagar la incertidumbre con operadores
matemáticos en lugar de lógica booleana estricta:

    AND (T-Norma)     -> MIN(a, b)    la conjunción vale lo que su premisa más débil
    OR  (T-Conorma)   -> MAX(a, b)    la disyunción vale lo que su premisa más fuerte
    NOT (Complemento) -> 1.0 - a

Y el paso ENTONCES, llamado IMPLICACIÓN, no traslada la conclusión completa:
la trunca a la altura de la fuerza de la premisa.
"""


# ---------------------------------------------------------------------------
# 1. OPERADORES LÓGICOS DIFUSOS
# ---------------------------------------------------------------------------
# Se definen como funciones con nombre propio y no se escribe min() o max()
# suelto en las reglas. El motivo es de mantenimiento: existen otras T-Normas
# (el producto algebraico, por ejemplo) y cambiar de criterio debe ser
# modificar una función, no rastrear todas las reglas del sistema.

def t_norma_and(*grados):
    """Conjunción difusa. Una regla no puede ser más verdadera que su premisa
    más débil, así que se toma el mínimo."""
    return min(grados)


def t_conorma_or(*grados):
    """Disyunción difusa. Basta que una premisa se cumpla, así que se toma el
    máximo: la disyunción vale lo que su premisa más fuerte."""
    return max(grados)


def complemento_not(grado):
    """Negación difusa. Si algo es verdadero en 0.8, su negación lo es en 0.2."""
    return 1.0 - grado


# ---------------------------------------------------------------------------
# 2. GRADOS DE MEMBRESÍA (resultado de la fuzzificación de la sesión 3)
# ---------------------------------------------------------------------------
# Este motor NO fuzzifica: recibe los grados ya calculados. Esa separación es
# deliberada, porque permite cambiar las funciones de membresía sin tocar la
# inferencia, y viceversa.
#
# Nótese que los grados de una misma variable no suman 1.0: en lógica difusa
# los conjuntos se solapan y eso es correcto, a diferencia de la probabilidad.

empleado = {
    "desempeno_pobre":     0.10,
    "desempeno_promedio":  0.30,
    "desempeno_excelente": 0.85,
    "antiguedad_corta":    0.20,
    "antiguedad_larga":    0.60,
}


# ---------------------------------------------------------------------------
# 3. LAS TRES REGLAS DEL NEGOCIO (versión directa)
# ---------------------------------------------------------------------------

def evaluar_reglas_bono(grados):
    """Evalúa la base de reglas y retorna la activación de cada nivel de bono.

    Es la forma explícita que pide el taller: cada regla combina los grados con
    min() y max() según su estructura lógica.
    """

    # R1: SI Desempeño es POBRE O Antigüedad es CORTA ENTONCES Bono BAJO
    # Disyunción: basta con que una de las dos condiciones se cumpla para que
    # el bono sea bajo, de modo que se toma el máximo.
    activacion_bajo = t_conorma_or(grados["desempeno_pobre"],
                                   grados["antiguedad_corta"])

    # R2: SI Desempeño es PROMEDIO ENTONCES Bono MEDIO
    # Una sola premisa: la fuerza de la regla es el grado tal cual, sin
    # operador que aplicar.
    activacion_medio = grados["desempeno_promedio"]

    # R3: SI Desempeño es EXCELENTE Y Antigüedad es LARGA ENTONCES Bono ALTO
    # Conjunción: se exigen ambas, así que la regla queda limitada por la más
    # débil de las dos.
    activacion_alto = t_norma_and(grados["desempeno_excelente"],
                                  grados["antiguedad_larga"])

    return {
        "BONO_BAJO":  activacion_bajo,
        "BONO_MEDIO": activacion_medio,
        "BONO_ALTO":  activacion_alto,
    }


# ---------------------------------------------------------------------------
# 4. MOTOR GENÉRICO CON PREMISAS ANIDADAS
# ---------------------------------------------------------------------------
# La versión anterior tiene las reglas escritas en el código, igual que el
# prototipo de la sesión 1. Aquí las reglas vuelven a ser DATOS, como en la
# sesión 2, pero ahora la premisa es un árbol que puede anidar operadores.
#
# Esto es lo que permite representar una premisa como (A O B) Y C, que es
# justamente la estructura del taller analítico y que la versión directa no
# podría expresar sin escribir una función nueva por cada regla.

def evaluar_premisa(premisa, grados):
    """Evalúa recursivamente el árbol de una premisa y retorna su fuerza.

    Una premisa es o bien una hoja {"var": nombre}, o bien un nodo con un
    operador y sus operandos. La recursión resuelve primero los nodos más
    internos, que es exactamente el orden de precedencia por paréntesis.
    """
    if "var" in premisa:
        return grados.get(premisa["var"], 0.0)

    operador = premisa["op"]

    if operador == "NOT":
        return complemento_not(evaluar_premisa(premisa["operando"], grados))

    fuerzas = [evaluar_premisa(p, grados) for p in premisa["operandos"]]

    if operador == "AND":
        return t_norma_and(*fuerzas)
    if operador == "OR":
        return t_conorma_or(*fuerzas)

    raise ValueError("Operador difuso no soportado: {}".format(operador))


def inferir(base_reglas, grados):
    """Aplica Mamdani sobre una base de reglas y agrega las conclusiones.

    Retorna (activaciones_agregadas, detalle_por_regla).
    """
    agregado = {}
    detalle = []

    for regla in base_reglas:
        fuerza = evaluar_premisa(regla["si"], grados)
        conclusion = regla["entonces"]

        # AGREGACIÓN: cuando varias reglas concluyen lo mismo con fuerzas
        # distintas, Mamdani las unifica con la T-Conorma, es decir el máximo.
        # Se toma el máximo y no la suma porque un grado de verdad no puede
        # superar 1.0: dos caminos que justifican la misma conclusión no la
        # hacen más verdadera que el más fuerte de los dos.
        previo = agregado.get(conclusion, 0.0)
        agregado[conclusion] = t_conorma_or(previo, fuerza)

        detalle.append({"id": regla["id"], "fuerza": fuerza,
                        "conclusion": conclusion,
                        "descripcion": regla["descripcion"]})

    return agregado, detalle


# --- Base de reglas de RRHH declarada como datos ---------------------------

reglas_bono = [
    {
        "id": "R1",
        "descripcion": "SI desempeño POBRE O antigüedad CORTA ENTONCES bono BAJO",
        "si": {"op": "OR", "operandos": [{"var": "desempeno_pobre"},
                                         {"var": "antiguedad_corta"}]},
        "entonces": "BONO_BAJO",
    },
    {
        "id": "R2",
        "descripcion": "SI desempeño PROMEDIO ENTONCES bono MEDIO",
        "si": {"var": "desempeno_promedio"},
        "entonces": "BONO_MEDIO",
    },
    {
        "id": "R3",
        "descripcion": "SI desempeño EXCELENTE Y antigüedad LARGA ENTONCES bono ALTO",
        "si": {"op": "AND", "operandos": [{"var": "desempeno_excelente"},
                                          {"var": "antiguedad_larga"}]},
        "entonces": "BONO_ALTO",
    },
]


# ---------------------------------------------------------------------------
# 5. EJECUCIÓN
# ---------------------------------------------------------------------------

def mostrar_activaciones(titulo, activaciones):
    print("  {}".format(titulo))
    for etiqueta, fuerza in activaciones.items():
        barra = "#" * int(round(fuerza * 30))
        print("    {:<12} {:.2f}  {}".format(etiqueta, fuerza, barra))


if __name__ == "__main__":

    print("\nMOTOR LÓGICO DE RECURSOS HUMANOS - INFERENCIA MAMDANI")
    print("=" * 70)

    print("\nGrados de membresía del empleado evaluado:")
    for variable, grado in empleado.items():
        print("    {:<22} {:.2f}".format(variable, grado))

    # --- Versión directa que pide el taller -------------------------------
    print("\n" + "-" * 70)
    activaciones = evaluar_reglas_bono(empleado)
    mostrar_activaciones("Niveles de activación (evaluación directa):", activaciones)

    # --- Versión genérica: mismo resultado, reglas como datos -------------
    print("\n" + "-" * 70)
    agregado, detalle = inferir(reglas_bono, empleado)
    print("  Traza del motor genérico:")
    for d in detalle:
        print("    {} fuerza {:.2f} -> {}".format(d["id"], d["fuerza"], d["conclusion"]))
        print("       {}".format(d["descripcion"]))
    print()
    mostrar_activaciones("Niveles de activación (motor genérico):", agregado)
    print("\n  Ambos métodos coinciden: {}".format(agregado == activaciones))

    # --- Punto 4: la pregunta teórica sobre agregación --------------------
    print("\n" + "=" * 70)
    print("PUNTO 4 - AGREGACIÓN DE REGLAS CON LA MISMA CONCLUSIÓN")
    print("-" * 70)
    print("  Si dos reglas concluyen BONO_ALTO con fuerzas 0.4 y 0.7, la")
    print("  agregación de Mamdani usa la T-Conorma (OR), o sea el máximo:")
    print()
    print("      bono_alto_final = max(0.4, 0.7)")
    print()
    print("  Resultado: {:.1f}".format(t_conorma_or(0.4, 0.7)))
    print()
    print("  Se toma el máximo y no la suma porque un grado de verdad nunca")
    print("  puede superar 1.0. Que existan dos caminos para justificar la")
    print("  misma conclusión no la hace más verdadera que el más fuerte de")
    print("  ellos: la refuerza, no la acumula.")

    # --- Verificación del taller analítico --------------------------------
    # El mismo motor genérico resuelve la premisa anidada (A O B) Y C del
    # taller analítico, sin modificar una sola línea de su código.
    print("\n" + "=" * 70)
    print("VERIFICACIÓN DEL TALLER ANALÍTICO: evaluación de proyectos")
    print("-" * 70)

    proyecto = {
        "rentabilidad_alta": 0.6,
        "impacto_alto":      0.2,
        "riesgo_bajo":       0.4,
        "riesgo_alto":       0.7,
    }

    reglas_proyecto = [
        {
            "id": "R1",
            "descripcion": "SI (rentabilidad ALTA O impacto ALTO) Y riesgo BAJO ENTONCES aprobación SEGURA",
            "si": {"op": "AND", "operandos": [
                {"op": "OR", "operandos": [{"var": "rentabilidad_alta"},
                                           {"var": "impacto_alto"}]},
                {"var": "riesgo_bajo"},
            ]},
            "entonces": "APROBACION_SEGURA",
        },
        {
            "id": "R2",
            "descripcion": "SI riesgo ALTO ENTONCES aprobación DENEGADA",
            "si": {"var": "riesgo_alto"},
            "entonces": "APROBACION_DENEGADA",
        },
    ]

    agregado_p, detalle_p = inferir(reglas_proyecto, proyecto)
    for d in detalle_p:
        print("    {} fuerza {:.2f} -> {}".format(d["id"], d["fuerza"], d["conclusion"]))
    print()
    print("    Paso a paso de R1:")
    print("      fuerza_or    = MAX(0.6, 0.2) = {:.1f}".format(
        t_conorma_or(0.6, 0.2)))
    print("      fuerza_total = MIN({:.1f}, 0.4) = {:.1f}".format(
        t_conorma_or(0.6, 0.2), t_norma_and(t_conorma_or(0.6, 0.2), 0.4)))
    print()
    print("    El conjunto APROBACION_SEGURA se trunca a la altura {:.1f}".format(
        agregado_p["APROBACION_SEGURA"]))
    print("    y APROBACION_DENEGADA queda activa en {:.1f}: la denegación pesa más.".format(
        agregado_p["APROBACION_DENEGADA"]))
    print("=" * 70)
