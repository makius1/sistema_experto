# Registro de cambios

Historial del proyecto por sesión de clase. Cada entrega al docente queda
marcada además con una etiqueta de Git (`git tag`).

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

---

## [inicial] — Configuración del repositorio

### Agregado
- Entorno de desarrollo reproducible en `.devcontainer/` para GitHub Codespaces
  (Python 3.11, extensiones de VS Code, codificación UTF-8).
- `.gitattributes` para normalizar finales de línea entre Windows y Linux.
- `.gitignore` con exclusión de artefactos de Python, temporales de Word y
  material de consulta del docente.
- `requirements.txt` documentando la ausencia de dependencias externas.
