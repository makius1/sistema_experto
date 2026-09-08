# -*- coding: utf-8 -*-
"""
Taller de Laboratorio: Lógica Difusa Comercial - Experiencia de Conductores
==========================================================================
Asignatura : Sistemas Expertos e Inteligencia Artificial - VIII Semestre
Sesión 3   : Incertidumbre y Lógica Difusa
Docente    : Amaury Giovanni Méndez Aguirre

Problema
--------
Una empresa de logística automotriz necesita evaluar la "Experiencia" de sus
conductores a partir de los años trabajados. El problema de la lógica booleana
es el límite estricto: con una regla como "SI años > 5 ENTONCES es experto", un
conductor con 4.9 años quedaría clasificado igual que uno de 1 año, lo cual no
imita el criterio humano.

La lógica difusa resuelve esto con GRADOS DE MEMBRESÍA: un conductor de 6 años
puede pertenecer al conjunto "Intermedio" en 0.67 y al conjunto "Experto" en
0.20 al mismo tiempo.

Conjuntos difusos definidos (funciones triangulares):
    Novato      -> vértices (0, 0, 5)
    Intermedio  -> vértices (2, 5, 8)
    Experto     -> vértices (5, 10, 20)
"""


# ---------------------------------------------------------------------------
# 1. FUNCIÓN DE MEMBRESÍA TRIANGULAR
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
# 2. DEFINICIÓN DE LOS CONJUNTOS DIFUSOS
# ---------------------------------------------------------------------------
# Las etiquetas lingüísticas se guardan como datos, igual que las reglas de la
# sesión 2: el algoritmo no cambia si mañana la empresa redefine los rangos.

conjuntos_experiencia = {
    "NOVATO":     (0, 0, 5),
    "INTERMEDIO": (2, 5, 8),
    "EXPERTO":    (5, 10, 20),
}


def fuzzificar(anios):
    """Retorna el grado de pertenencia del conductor a cada conjunto difuso."""
    return {
        etiqueta: membresia_triangular(anios, a, b, c)
        for etiqueta, (a, b, c) in conjuntos_experiencia.items()
    }


# ---------------------------------------------------------------------------
# 3. EVALUACIÓN DE LOS CONDUCTORES
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    conductores = [3, 6, 12]

    print("\nEVALUACIÓN DIFUSA DE LA EXPERIENCIA DE CONDUCTORES")
    print("=" * 66)

    for anios in conductores:
        grados = fuzzificar(anios)

        print("\nConductor con {} años de experiencia:".format(anios))
        for etiqueta, grado in grados.items():
            # Barra visual proporcional al grado de verdad.
            barra = "#" * int(round(grado * 20))
            print("  - Pertenece a {:<11} en un {:6.2f} %  {}".format(
                etiqueta, grado * 100, barra))

        # --- Decisión algorítmica: la etiqueta de mayor grado de verdad ------
        # max() sobre los items del diccionario, comparando por el valor.
        categoria, grado_maximo = max(grados.items(), key=lambda par: par[1])

        print("  => Encaja mejor en: {} (grado {:.2f})".format(
            categoria, grado_maximo))

        # Un grado alto en dos conjuntos a la vez indica un caso de frontera:
        # información que la lógica booleana habría perdido por completo.
        ambiguos = [e for e, g in grados.items() if g > 0 and e != categoria]
        if ambiguos:
            print("     También pertenece parcialmente a: {}".format(
                ", ".join(ambiguos)))

    print("\n" + "=" * 66)

    # -----------------------------------------------------------------------
    # 4. VERIFICACIÓN DEL TALLER ANALÍTICO
    # -----------------------------------------------------------------------
    # Conjunto "Temperatura Agradable" con vértices (18, 22, 26). Comprueba
    # computacionalmente los grados calculados a mano en el taller analítico.

    print("VERIFICACIÓN DEL TALLER ANALÍTICO: Temperatura Agradable (18, 22, 26)")
    print("-" * 66)
    for temperatura in (20, 25):
        grado = membresia_triangular(temperatura, 18, 22, 26)
        print("  μ({} °C) = {:.2f}".format(temperatura, grado))
    print("=" * 66)
