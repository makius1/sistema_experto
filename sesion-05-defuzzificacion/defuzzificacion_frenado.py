# -*- coding: utf-8 -*-
"""
Taller de Laboratorio: Defuzzificación por Centro de Gravedad
=============================================================
Asignatura : Sistemas Expertos e Inteligencia Artificial - VIII Semestre
Sesión 5   : Defuzzificación
Docente    : Amaury Giovanni Méndez Aguirre

Problema
--------
El motor de Mamdani de la sesión 4 produce respuestas como "el bono debería ser
un 70 % Alto y un 40 % Medio". Es correcto dentro del sistema pero inservible
fuera de él: nómina no puede pagar un salario "70 % Alto".

La DEFUZZIFICACIÓN cierra el ciclo. Toma la geometría del área bajo la curva
que dejó la inferencia y encuentra un único punto que la representa. El método
estándar de la industria es el Centro de Gravedad:

    COG = Σ (x · μ(x)) / Σ μ(x)

Es el punto donde la figura se sostendría en equilibrio si el área bajo la
curva fuera una lámina con masa.

Este archivo implementa el centroide propio con NumPy, como permite el
enunciado, en lugar de depender de scikit-fuzzy. La ventaja no es solo evitar
una dependencia: escribir la fórmula obliga a entenderla, y permite manejar
explícitamente el caso en que no hay área que equilibrar.
"""

import numpy as np


# ---------------------------------------------------------------------------
# 1. EL CENTRO DE GRAVEDAD
# ---------------------------------------------------------------------------

def centroide(x, curva):
    """Defuzzifica una curva de pertenencia por el método del centroide.

    Recibe el universo del discurso (x) y el grado de pertenencia de cada punto
    (curva), y retorna el valor exacto que representa la decisión.

    La operación es vectorial: NumPy multiplica los dos arreglos elemento a
    elemento y suma, sin ciclos explícitos. Con dominios de miles de puntos esa
    diferencia deja de ser estética y pasa a ser de rendimiento.

    Retorna None cuando el área total es cero. Ese caso no es un error de
    cálculo sino una situación real: ninguna regla se disparó, no hay nada que
    equilibrar y el sistema no tiene una recomendación que dar. Devolver un
    número inventado sería peor que admitirlo.
    """
    x = np.asarray(x, dtype=float)
    curva = np.asarray(curva, dtype=float)

    area = np.sum(curva)
    if area == 0:
        return None

    return float(np.sum(x * curva) / area)


def centroide_paso_a_paso(x, curva):
    """Misma fórmula sin NumPy, escrita para poder seguirla término a término.

    Sirve de verificación cruzada: si las dos implementaciones coinciden, el
    resultado no depende de la librería sino de la matemática.
    """
    numerador = 0.0
    denominador = 0.0
    for valor, grado in zip(x, curva):
        numerador += valor * grado
        denominador += grado

    if denominador == 0:
        return None
    return numerador / denominador


def media_de_maximos(x, curva):
    """Método alternativo: promedia solo los puntos de máxima pertenencia.

    Se implementa para poder compararlo con el centroide. El MOM es más rápido
    y produce respuestas más extremas porque descarta toda la información que
    no esté en el pico; el COG es más suave porque cada punto influye en
    proporción a su grado.
    """
    x = np.asarray(x, dtype=float)
    curva = np.asarray(curva, dtype=float)

    maximo = np.max(curva)
    if maximo == 0:
        return None

    return float(np.mean(x[curva == maximo]))


# ---------------------------------------------------------------------------
# 2. FUNCIONES DE PERTENENCIA SOBRE UN DOMINIO CONTINUO
# ---------------------------------------------------------------------------

def gaussiana(x, centro, sigma):
    """Campana de Gauss como función de membresía.

    A diferencia del triángulo de la sesión 3, la gaussiana es suave en todo su
    recorrido: no tiene vértices ni cambios bruscos de pendiente. En control
    automático eso importa, porque una salida que salta produce vibración en el
    actuador. Un sistema de frenado necesita una curva sin esquinas.

        μ(x) = exp( -(x - centro)^2 / (2 · sigma^2) )
    """
    x = np.asarray(x, dtype=float)
    return np.exp(-((x - centro) ** 2) / (2.0 * sigma ** 2))


def truncar(curva, altura):
    """Aplica la implicación de Mamdani: corta la curva a una altura máxima.

    Es el equivalente vectorial del recorte de la sesión 4, donde el conjunto
    de la conclusión se trunca a la fuerza de activación de su regla.
    """
    return np.fmin(np.asarray(curva, dtype=float), altura)


# ---------------------------------------------------------------------------
# 3. EJECUCIÓN
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print("\nDEFUZZIFICACIÓN POR CENTRO DE GRAVEDAD")
    print("=" * 72)

    # --- Punto 2: validación contra el taller analítico -------------------
    print("\nVALIDACIÓN CON LOS DATOS DEL TALLER ANALÍTICO")
    print("-" * 72)

    x_descuento = np.array([10, 20, 30, 40])
    mu_descuento = np.array([0.2, 0.8, 0.8, 0.0])

    numerador = float(np.sum(x_descuento * mu_descuento))
    denominador = float(np.sum(mu_descuento))
    resultado = centroide(x_descuento, mu_descuento)

    print("  x  = {}".format(x_descuento.tolist()))
    print("  mu = {}".format(mu_descuento.tolist()))
    print()
    print("  Numerador   Σ(x · μ) = {:.1f}".format(numerador))
    print("  Denominador Σ μ      = {:.1f}".format(denominador))
    print("  COG = {:.1f} / {:.1f} = {:.4f}".format(numerador, denominador, resultado))
    print()
    print("  Descuento recomendado: {:.2f} %".format(resultado))
    print("  Coincide con el cálculo a mano (23.33 %): {}".format(
        abs(resultado - 23.3333) < 0.001))
    print("  Coincide con la versión sin NumPy: {}".format(
        abs(resultado - centroide_paso_a_paso(x_descuento, mu_descuento)) < 1e-12))

    print("\n  Comparación con el método alternativo:")
    print("    Centroide (COG)        : {:.2f} %".format(resultado))
    print("    Media de máximos (MOM) : {:.2f} %".format(
        media_de_maximos(x_descuento, mu_descuento)))
    print("    El MOM promedia solo los picos (20 y 30) e ignora el aporte de")
    print("    x = 10, por eso da 25 % en lugar de 23.33 %.")

    # --- Puntos 3 y 4: sistema de frenado automático ----------------------
    print("\n" + "=" * 72)
    print("SISTEMA DE FRENADO AUTOMÁTICO")
    print("-" * 72)

    # Universo del discurso: la fuerza de frenado, de 0 a 100 Newtons.
    x_fuerza = np.linspace(0, 100, 100)

    # El motor de inferencia concluyó "frenado FUERTE", modelado como una
    # campana centrada en 70 N.
    curva_frenado = gaussiana(x_fuerza, centro=70, sigma=10)

    fuerza_exacta = centroide(x_fuerza, curva_frenado)
    print("  Universo    : 100 puntos entre 0 y 100 N")
    print("  Conclusión  : campana de Gauss centrada en 70 N (sigma = 10)")
    print("  FUERZA DE FRENADO EXACTA: {:.2f} N".format(fuerza_exacta))
    print()
    print("  El centroide de una curva simétrica cae en su centro. El valor no")
    print("  da exactamente 70 porque el dominio se corta en 100 N y recorta")
    print("  una fracción de la cola derecha.")

    # --- Demostración: truncar no mueve el centroide de una curva simétrica
    print("\n" + "-" * 72)
    print("EFECTO DE LA IMPLICACIÓN DE MAMDANI SOBRE EL CENTROIDE")
    print("-" * 72)
    for altura in (1.0, 0.6, 0.3):
        truncada = truncar(curva_frenado, altura)
        print("  truncada a {:.1f} -> centroide {:.2f} N   (área {:.2f})".format(
            altura, centroide(x_fuerza, truncada), float(np.sum(truncada))))
    print()
    print("  Truncar una curva simétrica NO mueve su centroide: reduce el área")
    print("  pero conserva el equilibrio. Por eso la fuerza de una sola regla no")
    print("  cambia la decisión por sí sola: lo que la mueve es la competencia")
    print("  entre conclusiones distintas, como se ve enseguida.")

    # --- Agregación de dos conclusiones en competencia --------------------
    print("\n" + "-" * 72)
    print("DOS REGLAS EN COMPETENCIA: AQUÍ SÍ SE MUEVE LA DECISIÓN")
    print("-" * 72)

    # R1: frenado FUERTE (centro 70) con activación alta.
    # R2: frenado SUAVE  (centro 25) con activación menor.
    fuerte = truncar(gaussiana(x_fuerza, centro=70, sigma=10), 0.8)
    suave = truncar(gaussiana(x_fuerza, centro=25, sigma=10), 0.4)

    # Agregación de Mamdani: se unifican con el máximo punto a punto, que es la
    # T-Conorma de la sesión 4 aplicada sobre todo el universo.
    agregada = np.fmax(fuerte, suave)

    print("  R1 frenado FUERTE (centro 70, activación 0.8) -> centroide {:.2f} N".format(
        centroide(x_fuerza, fuerte)))
    print("  R2 frenado SUAVE  (centro 25, activación 0.4) -> centroide {:.2f} N".format(
        centroide(x_fuerza, suave)))
    print("  Curva agregada con MAX punto a punto           -> centroide {:.2f} N".format(
        centroide(x_fuerza, agregada)))
    print()
    print("  La decisión final no es 70 ni 25: el sistema frena con una fuerza")
    print("  intermedia, inclinada hacia la conclusión que se activó con más")
    print("  fuerza. Ninguna regla dice ese número; sale del equilibrio entre")
    print("  todas, y eso es lo que un if/else nunca podría producir.")

    # --- Caso sin activación ----------------------------------------------
    print("\n" + "-" * 72)
    vacia = np.zeros_like(x_fuerza)
    print("  Curva sin ninguna activación -> centroide: {}".format(
        centroide(x_fuerza, vacia)))
    print("  No hay área que equilibrar: el sistema informa que no tiene una")
    print("  recomendación, en lugar de dividir por cero o inventar un valor.")
    print("=" * 72)
