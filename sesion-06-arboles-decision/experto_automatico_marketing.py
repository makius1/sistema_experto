# -*- coding: utf-8 -*-
"""
Taller de Laboratorio Final: El Experto Automático
==================================================
Asignatura : Sistemas Expertos e Inteligencia Artificial - VIII Semestre
Sesión 6   : Árboles de Decisión y Machine Learning
Docente    : Amaury Giovanni Méndez Aguirre

Proyecto integrador del módulo.

Problema
--------
El mayor obstáculo histórico de los sistemas expertos es la ADQUISICIÓN DEL
CONOCIMIENTO: sentar a un experto durante semanas para extraerle sus reglas es
caro, lento, y queda a merced de lo que recuerde y de sus sesgos.

El árbol de decisión invierte el proceso. En lugar de escribir las reglas a
mano, se le entrega el histórico y el algoritmo las deduce midiendo el desorden
de los datos. Y lo hace produciendo reglas SI-ENTONCES legibles, no una caja
negra: por eso es la unión natural entre el enfoque estadístico y el simbólico
que se trabajó en las sesiones 1 y 2.

Caso: un departamento de marketing quiere saber qué clientes hacen clic en su
anuncio, a partir de la edad, las horas que pasan en línea y sus compras
previas.
"""

import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split


# ---------------------------------------------------------------------------
# 1. ENTROPÍA: LA MATEMÁTICA QUE EL ÁRBOL USA POR DENTRO
# ---------------------------------------------------------------------------
# Se implementa a mano antes de usar la librería. El objetivo no es competir
# con scikit-learn sino comprobar que se entiende qué hace .fit() por debajo:
# sin esto, el árbol sería magia.

def entropia(etiquetas):
    """Mide el desorden de un conjunto de etiquetas, en bits.

        H(S) = - Σ p(i) · log2( p(i) )

    Vale 1.0 cuando el conjunto está mitad y mitad (desorden máximo, no se
    puede predecir nada) y 0.0 cuando es puro (todos de la misma clase).

    El caso p = 0 se omite de la suma porque log2(0) no está definido, y su
    aporte al límite es cero: una clase que no aparece no añade desorden.
    """
    etiquetas = np.asarray(etiquetas)
    if len(etiquetas) == 0:
        return 0.0

    _, conteos = np.unique(etiquetas, return_counts=True)
    proporciones = conteos / len(etiquetas)
    proporciones = proporciones[proporciones > 0]

    return float(-np.sum(proporciones * np.log2(proporciones)))


def ganancia_informacion(etiquetas, grupos):
    """Calcula cuánto desorden elimina una pregunta.

        Ganancia = H(antes) - Σ ( |Si| / |S| ) · H(Si)

    La entropía de cada grupo se pondera por su TAMAÑO, y esa ponderación no es
    un detalle: separar un elemento puro de otros noventa y nueve mezclados casi
    no ordena el conjunto, aunque ese grupo de uno tenga entropía cero. Sin
    ponderar, el algoritmo se entusiasmaría con divisiones inútiles.
    """
    total = len(etiquetas)
    h_antes = entropia(etiquetas)
    h_despues = sum((len(g) / total) * entropia(g) for g in grupos)
    return h_antes - h_despues


# ---------------------------------------------------------------------------
# 2. DATASET SIMULADO: DEPARTAMENTO DE MARKETING
# ---------------------------------------------------------------------------
# Los datos se construyen con un patrón deliberado para poder verificar que el
# árbol lo descubre:
#
#     Hace clic  <=>  Horas_Online >= 4  Y  Compras_Previas >= 2
#
# La edad se reparte de forma amplia en ambas clases, o sea que NO influye. Es
# a propósito: sirve para comprobar que el algoritmo descarta las variables
# irrelevantes en lugar de inventarles importancia.

nombres_variables = ["Edad", "Horas_Online", "Compras_Previas"]

X = np.array([
    # Edad, Horas_Online, Compras_Previas
    [22,  6, 3],
    [45,  5, 4],
    [31,  7, 2],
    [58,  4, 5],
    [27,  8, 2],
    [39,  5, 3],
    [63,  6, 6],
    [24,  4, 2],
    [35,  2, 4],
    [48,  1, 5],
    [29,  3, 3],
    [52,  0, 2],
    [26,  6, 0],
    [41,  7, 1],
    [33,  5, 0],
    [60,  8, 1],
])

# 1 = hizo clic en el anuncio, 0 = lo ignoró
Y = np.array([1, 1, 1, 1, 1, 1, 1, 1,
              0, 0, 0, 0, 0, 0, 0, 0])


# ---------------------------------------------------------------------------
# 3. TRADUCCIÓN DEL ÁRBOL A REGLAS DE PRODUCCIÓN
# ---------------------------------------------------------------------------

def extraer_reglas(arbol, nombres, clases=("NO_CLIC", "CLIC")):
    """Recorre el árbol entrenado y devuelve sus caminos como reglas SI-ENTONCES.

    Es el puente entre las dos mitades del curso. `export_text` imprime el árbol
    con la sangría de la librería; esta función lo convierte al mismo formato de
    reglas de producción que usaron los motores de las sesiones 1 y 2, de modo
    que el conocimiento aprendido por la máquina pueda alimentar directamente un
    motor de inferencia simbólico.
    """
    estructura = arbol.tree_
    reglas = []

    def recorrer(nodo, condiciones):
        # Una hoja tiene -1 como hijo izquierdo: ahí termina el camino.
        if estructura.children_left[nodo] == -1:
            muestras = estructura.value[nodo][0]
            clase = clases[int(np.argmax(muestras))]
            reglas.append({
                "condiciones": list(condiciones),
                "conclusion": clase,
                "muestras": int(estructura.n_node_samples[nodo]),
                "pureza": float(np.max(muestras) / np.sum(muestras)),
            })
            return

        variable = nombres[estructura.feature[nodo]]
        umbral = estructura.threshold[nodo]

        # scikit-learn siempre divide con la condición "variable <= umbral":
        # el hijo izquierdo la cumple y el derecho no.
        recorrer(estructura.children_left[nodo],
                 condiciones + ["{} <= {:.1f}".format(variable, umbral)])
        recorrer(estructura.children_right[nodo],
                 condiciones + ["{} > {:.1f}".format(variable, umbral)])

    recorrer(0, [])
    return reglas


# ---------------------------------------------------------------------------
# 4. EJECUCIÓN
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print("\nEL EXPERTO AUTOMÁTICO - ÁRBOLES DE DECISIÓN")
    print("=" * 74)

    # --- Verificación del taller analítico --------------------------------
    # Se reproduce el caso de los 6 clientes con las funciones propias, antes
    # de tocar la librería.
    print("\nVERIFICACIÓN DEL TALLER ANALÍTICO (6 clientes, 3 compraron)")
    print("-" * 74)

    compraron = [1, 1, 1, 0, 0, 0]
    print("  Entropía inicial: {:.4f}".format(entropia(compraron)))

    # Pregunta A: mayor de 30 -> [2 compraron, 2 no] y [1 compró, 1 no]
    grupos_a = [[1, 1, 0, 0], [1, 0]]
    # Pregunta B: tiene auto -> [3 compraron, 0 no] y [0 compraron, 3 no]
    grupos_b = [[1, 1, 1], [0, 0, 0]]

    ganancia_a = ganancia_informacion(compraron, grupos_a)
    ganancia_b = ganancia_informacion(compraron, grupos_b)

    print("  Pregunta A (¿mayor de 30?) -> ganancia {:.4f}".format(ganancia_a))
    print("  Pregunta B (¿tiene auto?)  -> ganancia {:.4f}".format(ganancia_b))
    print()
    print("  Gana la Pregunta {}, coincide con el cálculo a mano: {}".format(
        "B" if ganancia_b > ganancia_a else "A",
        abs(ganancia_b - 1.0) < 1e-9 and abs(ganancia_a) < 1e-9))
    print("  La Pregunta A tiene ganancia exactamente cero: no aporta nada.")

    # --- Entrenamiento del modelo -----------------------------------------
    print("\n" + "=" * 74)
    print("ENTRENAMIENTO DEL ÁRBOL DE DECISIÓN")
    print("-" * 74)
    print("  Registros: {} | Variables: {}".format(len(X), ", ".join(nombres_variables)))
    print("  Clientes que hicieron clic: {} de {}".format(Y.sum(), len(Y)))
    print("  Entropía del conjunto de entrenamiento: {:.4f}".format(entropia(Y)))

    # Se usa criterion="entropy" y no el "gini" que trae scikit-learn por
    # defecto, para que el algoritmo aplique exactamente la métrica estudiada
    # en clase. Ambos suelen dar árboles parecidos, pero solo la entropía
    # corresponde a la ganancia de información del taller analítico.
    arbol = DecisionTreeClassifier(criterion="entropy", max_depth=3, random_state=42)
    arbol.fit(X, Y)

    # --- Punto 4: el árbol impreso ----------------------------------------
    print("\n" + "-" * 74)
    print("BASE DE REGLAS GENERADA AUTOMÁTICAMENTE (export_text)")
    print("-" * 74)
    print(export_text(arbol, feature_names=nombres_variables))

    # --- Traducción a reglas de producción --------------------------------
    print("-" * 74)
    print("LAS MISMAS REGLAS EN FORMATO DE SISTEMA EXPERTO")
    print("-" * 74)
    for i, regla in enumerate(extraer_reglas(arbol, nombres_variables), start=1):
        premisas = " Y ".join(regla["condiciones"])
        print("  R{}: SI {}".format(i, premisas))
        print("      ENTONCES {}   ({} muestras, pureza {:.0%})".format(
            regla["conclusion"], regla["muestras"], regla["pureza"]))

    # --- Qué variables importaron -----------------------------------------
    print("\n" + "-" * 74)
    print("IMPORTANCIA DE CADA VARIABLE")
    print("-" * 74)
    for nombre, peso in sorted(zip(nombres_variables, arbol.feature_importances_),
                               key=lambda p: p[1], reverse=True):
        barra = "#" * int(round(peso * 40))
        print("  {:<18} {:.3f}  {}".format(nombre, peso, barra))
    print()
    print("  El árbol descartó la EDAD por sí solo: su importancia es cero.")
    print("  Nadie se lo dijo; lo dedujo al ver que preguntar por la edad no")
    print("  reducía el desorden, igual que la Pregunta A del taller analítico.")

    # --- El riesgo del sobreajuste ----------------------------------------
    print("\n" + "=" * 74)
    print("EL RIESGO DEL SOBREAJUSTE")
    print("-" * 74)

    # Con los datos anteriores el árbol no se sobreajusta, porque el patrón es
    # perfecto y sin excepciones. La realidad nunca es así: siempre hay clientes
    # que se comportan al revés de lo esperado. Se agregan cuatro casos que
    # CONTRADICEN la regla, que es exactamente lo que ocurre con datos reales.

    X_ruido = np.vstack([X, np.array([
        [30, 6, 3],   # cumple el patrón pero NO hizo clic
        [44, 5, 4],   # cumple el patrón pero NO hizo clic
        [36, 2, 0],   # no cumple el patrón pero SÍ hizo clic
        [50, 1, 1],   # no cumple el patrón pero SÍ hizo clic
    ])])
    Y_ruido = np.concatenate([Y, np.array([0, 0, 1, 1])])

    print("  Se agregan 4 clientes que contradicen el patrón ({} registros).".format(
        len(X_ruido)))
    print()

    X_ent, X_prueba, Y_ent, Y_prueba = train_test_split(
        X_ruido, Y_ruido, test_size=0.35, random_state=7, stratify=Y_ruido)

    for profundidad, etiqueta in [(None, "sin límite"), (2, "limitado a 2")]:
        modelo = DecisionTreeClassifier(criterion="entropy",
                                        max_depth=profundidad, random_state=42)
        modelo.fit(X_ent, Y_ent)
        print("  Árbol {:<14} entrenamiento {:>4.0%} | prueba {:>4.0%} | hojas {}".format(
            etiqueta,
            modelo.score(X_ent, Y_ent),
            modelo.score(X_prueba, Y_prueba),
            modelo.get_n_leaves()))

    print()
    print("  El árbol sin límite acierta más sobre los datos que vio, porque")
    print("  abre ramas nuevas hasta memorizar incluso a los clientes atípicos.")
    print("  El limitado no puede hacerlo y se queda con el patrón general.")
    print()
    print("  Lo que importa es la columna de PRUEBA: son clientes que el modelo")
    print("  nunca vio. Ahí se distingue haber aprendido de haber memorizado, y")
    print("  por eso una regla aprendida por un algoritmo debe validarse con")
    print("  datos nuevos antes de convertirse en política del negocio.")
    print()
    print("  Con 20 registros el conjunto de prueba es de apenas 7 clientes, así")
    print("  que sus porcentajes son inestables. La evidencia sólida aquí es el")
    print("  número de hojas: 8 contra 3 para el mismo problema. Ese exceso de")
    print("  ramas ES el sobreajuste, y se ve sin depender del azar del muestreo.")
    print("=" * 74)
