# Registro de cambios

Historial del proyecto por sesión de clase. Cada entrega al docente queda
marcada además con una etiqueta de Git (`git tag`).

---

## [entrega-sesion-06] — Sesión 6: Árboles de decisión y machine learning

### Agregado
- `experto_automatico_marketing.py`: entropía de Shannon y ganancia de
  información implementadas a mano, entrenamiento de un árbol de decisión y
  extracción automática de la base de reglas.
- Función que traduce el árbol entrenado al formato de reglas de producción de
  las sesiones 1 y 2, cerrando el puente entre el enfoque estadístico y el
  simbólico.
- Demostración del sobreajuste mediante registros que contradicen el patrón.
- `06_Taller_Analitico_Ganancia_Informacion.txt`: cálculo de la entropía y de la
  ganancia de las dos preguntas candidatas, y la regla aprendida.

### Decisiones de diseño
- Se entrena con `criterion="entropy"` en lugar del `gini` que scikit-learn trae
  por defecto, para que el algoritmo aplique la misma métrica del taller.
- Las métricas se implementan a mano antes de usar la librería: sin eso el
  entrenamiento sería una caja negra.
- El conjunto de datos se construye con un patrón conocido, de modo que se pueda
  verificar que el árbol lo descubre y que descarta la variable irrelevante.

---

## [entrega-sesion-05] — Sesión 5: Defuzzificación

### Agregado
- `defuzzificacion_frenado.py`: implementación del centro de gravedad con
  operaciones matriciales de NumPy, con una segunda versión sin NumPy que sirve
  de verificación cruzada.
- Método de la media de los máximos, para comparar criterios de defuzzificación.
- Funciones de membresía gaussiana y truncamiento de Mamdani sobre dominios
  continuos, aplicadas a un sistema de frenado automático.
- `05_Taller_Analitico_Centro_de_Masa.txt`: cálculo paso a paso del centroide
  sobre el dominio discreto del descuento comercial.

### Decisiones de diseño
- Se implementa el centroide propio en lugar de usar scikit-fuzzy, como permite
  el enunciado: escribir la fórmula obliga a entenderla y evita una dependencia
  pesada.
- La función retorna `None` cuando el área total es cero, en lugar de fallar por
  división o devolver un número arbitrario: significa que ninguna regla se
  disparó y el sistema no tiene recomendación.
- NumPy se declara como primera dependencia del proyecto, porque el enunciado
  pide operaciones matriciales sobre dominios de cientos de puntos.

---

## [entrega-sesion-04] — Sesión 4: Inferencia difusa (modelo Mamdani)

### Agregado
- `motor_mamdani_rrhh.py`: motor de inferencia difusa con los operadores de
  Mamdani implementados como funciones con nombre propio (T-Norma, T-Conorma y
  complemento), las tres reglas del bono anual y la agregación por máximo.
- Motor genérico que evalúa premisas anidadas de forma recursiva, capaz de
  resolver estructuras como `(A O B) Y C` sin escribir una función por regla.
- Verificación computacional de los grados calculados a mano en el taller.
- `04_Taller_Analitico_Propagacion_Fuerza.txt`: cálculo paso a paso de la
  fuerza de activación y de la altura de truncamiento de la conclusión.

### Decisiones de diseño
- Los operadores se encapsulan en funciones en lugar de escribir `min` y `max`
  sueltos dentro de las reglas: existen otras T-Normas, como el producto
  algebraico, y cambiar de criterio debe ser modificar una función.
- La premisa se modela como un árbol y no como una lista plana, porque el orden
  de precedencia entre AND y OR altera el resultado y debe quedar explícito.

---

## [entrega-sesion-03] — Sesión 3: Incertidumbre y lógica difusa

### Agregado
- `fuzzificacion_conductores.py`: implementación de la función de membresía
  triangular y fuzzificación de la experiencia de conductores en tres conjuntos
  difusos, con selección de la categoría dominante mediante `max()`.
- Verificación computacional de los grados calculados a mano en el taller
  analítico (conjunto "Temperatura Agradable").
- `03_Taller_Analitico_Grados_de_Verdad.txt`: cálculo paso a paso de μ(20) y
  μ(25) e interpretación del grado de verdad para el motor de inferencia.

### Mejorado
- Se agrega la variable de incidentes como segunda entrada, lo que permite
  mostrar la conjunción difusa.
- Se agrega la base de 9 reglas difusas y el cálculo de la fuerza de disparo
  mediante el mínimo de los grados.
- Se agregan la agregación por máximo y la defuzzificación por promedio
  ponderado, con lo que el sistema pasa de informar grados a decidir la
  bonificación del conductor.

### Corregido
- La función de membresía devolvía 0.0 en el vértice de los conjuntos hombro
  (a == b), de modo que un conductor con cero incidentes quedaba sin
  bonificación siendo el mejor evaluado. Se verifica primero el vértice.

### Decisiones de diseño
- Los conjuntos difusos y las reglas se declaran como datos en diccionarios,
  siguiendo la misma separación entre conocimiento y algoritmo adoptada en la
  sesión 2.
- El script reporta también las pertenencias parciales a otros conjuntos, que es
  justamente la información que la lógica booleana descarta.
- Se usa el promedio ponderado en lugar del centroide de Mamdani porque produce
  el mismo orden de resultados con una fracción del cálculo.

---

## [entrega-sesion-02] — Sesión 2: Motor de inferencia y Modus Ponens

### Agregado
- `motor_fraude.py`: motor de inferencia genérico con encadenamiento hacia
  adelante, que lee las reglas como datos en lugar de tenerlas escritas en el
  código.
- Implementación explícita del ciclo de vida del motor: equiparación
  (construcción del conjunto de conflicto), resolución de conflictos por
  prioridad y ejecución de una regla por ciclo.
- Base de conocimientos de detección de fraude bancario con 8 reglas.
- Base de conocimientos de vehículos, resuelta por el mismo motor sin
  modificarlo, que verifica computacionalmente la traza del taller analítico.
- `Taller-2-Traza-Inferencia.docx`: traza manual ciclo por ciclo, con análisis
  de la refractariedad y de la granularidad de los ciclos.

### Mejorado
- Se agrega el motor de encadenamiento hacia atrás, que parte de una meta y
  pregunta únicamente los hechos que necesita para demostrarla, con árbol de
  objetivos, backtracking y protección contra reglas circulares.
- La fuente de los hechos se pasa como parámetro, de modo que el mismo motor
  sirve para un expediente cargado o para un interrogatorio interactivo.

### Decisiones de diseño
- El evaluador de condiciones se amplió para soportar operadores relacionales
  (`{"monto": (">", 5000)}`), porque el motor de referencia solo comparaba por
  igualdad y el enunciado exige la premisa `monto > 5000`.
- La disyunción (OR) se modela como dos reglas con la misma conclusión, dado
  que `all()` solo implementa la conjunción.
- Se dispara una sola regla por ciclo para que la resolución de conflictos por
  prioridad tenga efecto real y la traza sea legible.

---

## [entrega-sesion-01] — Sesión 1: Introducción a los sistemas expertos

### Agregado
- `diagnostico_servidor.py`: prototipo de sistema experto para el HelpDesk de
  una empresa tecnológica, con la memoria de trabajo modelada como diccionario
  y las reglas organizadas en dos niveles de anidamiento.
- Módulo de explicación: cada diagnóstico retorna el identificador de la regla
  disparada y la acción recomendada.
- Once casos de prueba que cubren la totalidad de las ramas del motor.
- `Taller-1-Logica-Proposicional.docx`: formalización del manual de créditos en
  reglas de producción, con tabla de decisión y análisis de la ambigüedad de la
  cláusula de excepción.

### Mejorado
- Se agrega la captura de hechos con validación en tres pasos, que completa el
  módulo de interfaz de usuario que exigía la arquitectura.
- Se agrega el menú de operación, con el que el técnico decide qué hacer y
  cuántas veces en lugar de ejecutar siempre la misma demostración.
- Se agrega el historial de la sesión, que conserva cada diagnóstico con su
  hora, sus hechos y la regla disparada, con un resumen por nivel.

### Corregido
- Los casos de prueba modificaban el diccionario de hechos, de modo que una
  segunda ejecución partía de los valores que dejó la primera. Se restaura el
  estado inicial al comienzo de cada corrida.

---

## [inicial] — Configuración del repositorio

### Agregado
- Entorno de desarrollo reproducible en `.devcontainer/` para GitHub Codespaces
  (Python 3.11, extensiones de VS Code, codificación UTF-8).
- `.gitattributes` para normalizar finales de línea entre Windows y Linux.
- `.gitignore` con exclusión de artefactos de Python, temporales de Word y
  material de consulta del docente.
- `requirements.txt` documentando la ausencia de dependencias externas.
