# -*- coding: utf-8 -*-
"""
Taller de Laboratorio: Lógica Difusa Comercial - Experiencia de Conductores
==========================================================================
Asignatura : Sistemas Expertos e Inteligencia Artificial - VIII Semestre
Sesión 3   : Incertidumbre y Lógica Difusa
Docente    : Amaury Giovanni Méndez Aguirre

Problema
--------
Una empresa de logística automotriz necesita evaluar a sus conductores. El
problema de la lógica booleana es el límite estricto: con una regla como
"SI años > 5 ENTONCES es experto", un conductor con 4.9 años quedaría
clasificado igual que uno de 1 año, lo cual no imita el criterio humano.

La lógica difusa resuelve esto con GRADOS DE MEMBRESÍA: un conductor de 6 años
puede pertenecer al conjunto "Intermedio" en 0.67 y al conjunto "Experto" en
0.20 al mismo tiempo.

Variables de entrada del sistema:
    Experiencia (años)   -> Novato (0,0,5)  Intermedio (2,5,8)  Experto (5,10,20)
    Incidentes (al año)  -> Pocos (0,0,3)   Moderados (2,4,6)   Muchos (5,8,12)

Variable de salida:
    Bonificación (%)     -> Baja, Media, Alta
"""


# ---------------------------------------------------------------------------
# 1. FUNCIÓN DE MEMBRESÍA TRIANGULAR (fuzzificación)
# ---------------------------------------------------------------------------

def membresia_triangular(x, a, b, c):
    """Convierte un valor exacto del mundo real en un grado de verdad [0, 1].

    Este proceso se llama FUZZIFICACIÓN. La función está definida a trozos:

        μ(x) = 0                si x <= a  o  x >= c   (fuera del conjunto)
        μ(x) = (x - a)/(b - a)  si a < x <= b          (rampa de subida)
        μ(x) = (c - x)/(c - b)  si b < x < c           (rampa de bajada)

    El vértice b es el punto de pertenencia total (μ = 1.0).

    El caso x == b se evalúa de primero porque cuando el triángulo es en
    realidad un hombro (a == b, como en "Pocos incidentes" con vértices
    (0, 0, 3)), la condición x <= a atrapaba el valor del vértice y devolvía
    0.0 en lugar de 1.0. Eso hacía que un conductor con 0 incidentes quedara
    sin pertenencia a ningún conjunto y, por lo tanto, sin bonificación, que
    es justamente lo contrario de lo que debería recibir. Verificar primero
    el vértice corrige el caso sin alterar ningún otro valor.
    """
    if x == b:
        return 1.0
    elif x <= a or x >= c:
        return 0.0
    elif x < b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)


# ---------------------------------------------------------------------------
# 2. VARIABLES LINGÜÍSTICAS DE ENTRADA
# ---------------------------------------------------------------------------
# Los conjuntos difusos se declaran como datos, igual que las reglas de la
# sesión 2: si mañana la empresa redefine los rangos, no se toca el algoritmo.

conjuntos_experiencia = {
    "NOVATO":     (0, 0, 5),
    "INTERMEDIO": (2, 5, 8),
    "EXPERTO":    (5, 10, 20),
}

# Segunda variable de entrada: incidentes registrados en el último año.
# Se agrega porque con una sola variable las reglas difusas serían triviales
# (una regla por conjunto). Con dos variables aparece la conjunción difusa,
# que es donde la lógica difusa se diferencia de la booleana: el AND deja de
# ser verdadero/falso y pasa a calcularse como el mínimo de los grados.
conjuntos_incidentes = {
    "POCOS":     (0, 0, 3),
    "MODERADOS": (2, 4, 6),
    "MUCHOS":    (5, 8, 12),
}


def fuzzificar(valor, conjuntos):
    """Retorna el grado de pertenencia del valor a cada conjunto difuso.

    La función recibe el diccionario de conjuntos como parámetro para poder
    reutilizarse con cualquier variable lingüística (experiencia, incidentes o
    las que se agreguen después) sin duplicar código.
    """
    return {
        etiqueta: membresia_triangular(valor, a, b, c)
        for etiqueta, (a, b, c) in conjuntos.items()
    }


def etiqueta_dominante(grados):
    """Devuelve la etiqueta con mayor grado de verdad y su valor.

    max() compara los pares (etiqueta, grado) por el grado, que es la forma
    algorítmica de responder "en qué categoría encaja mejor".
    """
    return max(grados.items(), key=lambda par: par[1])


def imprimir_grados(titulo, grados):
    """Muestra los grados de pertenencia con una barra proporcional."""
    print("  {}".format(titulo))
    for etiqueta, grado in grados.items():
        barra = "#" * int(round(grado * 20))
        print("    - {:<11} {:6.2f} %  {}".format(etiqueta, grado * 100, barra))



# ---------------------------------------------------------------------------
# 3. VARIABLE LINGÜÍSTICA DE SALIDA
# ---------------------------------------------------------------------------
# La bonificación mensual, expresada como porcentaje del salario base. Es lo
# que el sistema debe decidir a partir de las dos variables de entrada.

# Cada etiqueta de salida tiene asociado un valor representativo (su centro).
# Se usan valores puntuales en lugar de triángulos porque la defuzzificación
# por promedio ponderado solo necesita el punto donde cada conjunto alcanza su
# máximo, lo que simplifica el cálculo sin cambiar el resultado.
centros_bonificacion = {
    "BAJA":  5.0,    # 5 % del salario base
    "MEDIA": 12.0,   # 12 %
    "ALTA":  20.0,   # 20 %
}


# ---------------------------------------------------------------------------
# 4. BASE DE REGLAS DIFUSAS
# ---------------------------------------------------------------------------
# Matriz de decisión que cubre las 9 combinaciones posibles:
#
#                  POCOS      MODERADOS    MUCHOS
#   NOVATO         BAJA       BAJA         BAJA
#   INTERMEDIO     MEDIA      BAJA         BAJA
#   EXPERTO        ALTA       MEDIA        BAJA
#
# Las reglas se declaran como datos, igual que en la sesión 2. La diferencia
# es que aquí las premisas no son verdaderas o falsas: cada una aporta un
# grado, y la regla dispara con una FUERZA proporcional a ese grado.

reglas_difusas = [
    {"id": "R1", "si": {"experiencia": "NOVATO",     "incidentes": "POCOS"},     "entonces": "BAJA"},
    {"id": "R2", "si": {"experiencia": "NOVATO",     "incidentes": "MODERADOS"}, "entonces": "BAJA"},
    {"id": "R3", "si": {"experiencia": "NOVATO",     "incidentes": "MUCHOS"},    "entonces": "BAJA"},
    {"id": "R4", "si": {"experiencia": "INTERMEDIO", "incidentes": "POCOS"},     "entonces": "MEDIA"},
    {"id": "R5", "si": {"experiencia": "INTERMEDIO", "incidentes": "MODERADOS"}, "entonces": "BAJA"},
    {"id": "R6", "si": {"experiencia": "INTERMEDIO", "incidentes": "MUCHOS"},    "entonces": "BAJA"},
    {"id": "R7", "si": {"experiencia": "EXPERTO",    "incidentes": "POCOS"},     "entonces": "ALTA"},
    {"id": "R8", "si": {"experiencia": "EXPERTO",    "incidentes": "MODERADOS"}, "entonces": "MEDIA"},
    {"id": "R9", "si": {"experiencia": "EXPERTO",    "incidentes": "MUCHOS"},    "entonces": "BAJA"},
]


def fuerza_de_disparo(regla, grados):
    """Calcula con qué fuerza dispara una regla, usando el AND difuso.

    En lógica booleana, "A Y B" es verdadero solo si ambas lo son. En lógica
    difusa la conjunción se calcula como el MÍNIMO de los grados:

        fuerza = min(μ(premisa_1), μ(premisa_2), ...)

    El criterio del mínimo se usa porque una conjunción no puede ser más
    verdadera que su premisa más débil: si el conductor es EXPERTO en 0.8 pero
    tiene POCOS incidentes solo en 0.2, la regla que exige ambas cosas dispara
    con fuerza 0.2. Es el equivalente difuso de "la cadena se rompe por el
    eslabón más débil".

    Nótese que una fuerza de 0.0 significa que la regla no aplica a este caso,
    que es el equivalente difuso de que la premisa sea falsa.
    """
    return min(
        grados[variable][etiqueta]
        for variable, etiqueta in regla["si"].items()
    )


def evaluar_reglas(grados):
    """Evalúa toda la base de reglas y retorna las que disparan.

    A diferencia del motor de la sesión 2, aquí NO se elige una sola regla
    ganadora: en lógica difusa varias reglas pueden disparar simultáneamente
    con fuerzas distintas, y todas contribuyen al resultado final.
    """
    disparos = []
    for regla in reglas_difusas:
        fuerza = fuerza_de_disparo(regla, grados)
        if fuerza > 0:
            disparos.append({
                "id": regla["id"],
                "fuerza": fuerza,
                "conclusion": regla["entonces"],
                "premisas": regla["si"],
            })
    return disparos


# ---------------------------------------------------------------------------
# 5. AGREGACIÓN Y DEFUZZIFICACIÓN
# ---------------------------------------------------------------------------

def agregar_conclusiones(disparos):
    """Combina las reglas que llegan a la misma conclusión usando el OR difuso.

    Varias reglas pueden concluir lo mismo con fuerzas distintas. Así como la
    conjunción se resuelve con el mínimo, la DISYUNCIÓN se resuelve con el
    MÁXIMO: si dos caminos distintos justifican una bonificación BAJA, uno con
    fuerza 0.3 y otro con 0.7, la conclusión queda respaldada con 0.7. Se toma
    el máximo y no la suma porque un grado de verdad nunca puede superar 1.0.
    """
    agregado = {}
    for disparo in disparos:
        etiqueta = disparo["conclusion"]
        fuerza_previa = agregado.get(etiqueta, 0.0)
        agregado[etiqueta] = max(fuerza_previa, disparo["fuerza"])
    return agregado


def defuzzificar(agregado):
    """Convierte los grados de salida en un único número concreto.

    Es la operación inversa de la fuzzificación y la etapa que faltaba para
    que el sistema DECIDA en vez de solo informar. Se aplica el método del
    promedio ponderado:

        salida = Σ (fuerza_i × centro_i) / Σ fuerza_i

    Cada conclusión "jala" el resultado hacia su propio centro con una fuerza
    igual a su grado de verdad. Una conclusión ALTA con fuerza 0.8 pesa cuatro
    veces más que una MEDIA con fuerza 0.2.

    Este método es la versión simplificada del centroide de Mamdani: en lugar
    de calcular el área bajo los conjuntos recortados, usa el punto máximo de
    cada uno. Da el mismo orden de resultados con una fracción del cálculo, y
    es el que se usa en control industrial por su bajo costo computacional.

    Si ninguna regla dispara retorna 0.0, que es el caso en que el sistema no
    tiene conocimiento aplicable a esa combinación de entradas.
    """
    suma_fuerzas = sum(agregado.values())
    if suma_fuerzas == 0:
        return 0.0

    suma_ponderada = sum(
        fuerza * centros_bonificacion[etiqueta]
        for etiqueta, fuerza in agregado.items()
    )
    return suma_ponderada / suma_fuerzas


def evaluar_conductor(anios, incidentes):
    """Ejecuta el sistema difuso completo sobre un conductor.

    Encadena las cuatro etapas: fuzzificación de las entradas, evaluación de
    las reglas, agregación de las conclusiones y defuzzificación de la salida.
    """
    grados = {
        "experiencia": fuzzificar(anios, conjuntos_experiencia),
        "incidentes": fuzzificar(incidentes, conjuntos_incidentes),
    }
    disparos = evaluar_reglas(grados)
    agregado = agregar_conclusiones(disparos)
    bonificacion = defuzzificar(agregado)

    return {
        "grados": grados,
        "disparos": disparos,
        "agregado": agregado,
        "bonificacion": bonificacion,
    }


# ---------------------------------------------------------------------------
# 6. EJECUCIÓN
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    # Los tres conductores del enunciado (3, 6 y 12 años), a los que se les
    # agrega el número de incidentes del último año como segunda variable.
    conductores = [
        {"nombre": "Conductor A", "anios": 3,  "incidentes": 1},
        {"nombre": "Conductor B", "anios": 6,  "incidentes": 4},
        {"nombre": "Conductor C", "anios": 12, "incidentes": 0},
    ]

    print("\nEVALUACIÓN DIFUSA DE CONDUCTORES")
    print("=" * 66)

    for conductor in conductores:
        grados_exp = fuzzificar(conductor["anios"], conjuntos_experiencia)
        grados_inc = fuzzificar(conductor["incidentes"], conjuntos_incidentes)

        print("\n{} - {} años de experiencia, {} incidentes:".format(
            conductor["nombre"], conductor["anios"], conductor["incidentes"]))

        imprimir_grados("Experiencia:", grados_exp)
        imprimir_grados("Incidentes:", grados_inc)

        categoria, grado_maximo = etiqueta_dominante(grados_exp)
        print("  => Encaja mejor en: {} (grado {:.2f})".format(
            categoria, grado_maximo))

        # Pertenecer parcialmente a dos conjuntos a la vez es justamente la
        # información que la lógica booleana descarta.
        ambiguos = [e for e, g in grados_exp.items() if g > 0 and e != categoria]
        if ambiguos:
            print("     También pertenece parcialmente a: {}".format(
                ", ".join(ambiguos)))

        # Inferencia difusa: se evalúa toda la base de reglas. Varias pueden
        # disparar a la vez, cada una con su propia fuerza.
        grados = {"experiencia": grados_exp, "incidentes": grados_inc}
        disparos = evaluar_reglas(grados)

        print("  Reglas que disparan:")
        for d in disparos:
            print("    {} fuerza {:.2f}  (SI experiencia es {} Y incidentes es {} ENTONCES bonificación {})".format(
                d["id"], d["fuerza"],
                d["premisas"]["experiencia"], d["premisas"]["incidentes"],
                d["conclusion"]))

        # Agregación: las reglas con la misma conclusión se combinan con el
        # máximo, y el resultado se convierte en un número concreto.
        agregado = agregar_conclusiones(disparos)
        bonificacion = defuzzificar(agregado)

        print("  Conclusiones agregadas: {}".format(
            ", ".join("{} = {:.2f}".format(e, f) for e, f in agregado.items())))
        print("  >> BONIFICACIÓN ASIGNADA: {:.2f} % del salario base".format(
            bonificacion))

    print("\n" + "=" * 66)

    # -----------------------------------------------------------------------
    # VERIFICACIÓN DEL TALLER ANALÍTICO
    # -----------------------------------------------------------------------
    # Conjunto "Temperatura Agradable" con vértices (18, 22, 26). Comprueba
    # computacionalmente los grados calculados a mano en el taller analítico.

    print("VERIFICACIÓN DEL TALLER ANALÍTICO: Temperatura Agradable (18, 22, 26)")
    print("-" * 66)
    for temperatura in (20, 25):
        grado = membresia_triangular(temperatura, 18, 22, 26)
        print("  μ({} °C) = {:.2f}".format(temperatura, grado))
    print("=" * 66)
