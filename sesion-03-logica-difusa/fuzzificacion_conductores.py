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
    """
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    elif b < x < c:
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
# 3. EJECUCIÓN
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
