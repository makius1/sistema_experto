# Sistemas Expertos e Inteligencia Artificial

Talleres y prototipos de la asignatura **Sistemas Expertos e Inteligencia Artificial**
(VIII Semestre, Ingeniería de Sistemas — Institución Universitaria de Colombia).

Cada sesión incluye un **taller analítico** (documento de análisis) y un
**taller de laboratorio** (prototipo funcional en Python).

---

## Estructura del repositorio

```
.
├── .devcontainer/              Definición del entorno de desarrollo (Codespaces)
│   └── devcontainer.json
├── consulta/                   Material de referencia (no versionado)
├── sesion-01-introduccion/     Arquitectura de un sistema experto
│   ├── 01_Taller_Analitico_Logica_Proposicional.txt
│   ├── diagnostico_servidor.py
│   └── Taller-1-Logica-Proposicional.docx
├── sesion-02-motor-inferencia/ Motor de inferencia y Modus Ponens
│   ├── 02_Taller_Analitico_Traza_Inferencia.txt
│   ├── motor_fraude.py
│   └── Taller-2-Traza-Inferencia.docx
├── sesion-03-logica-difusa/    Incertidumbre y lógica difusa
│   ├── 03_Taller_Analitico_Grados_de_Verdad.txt
│   └── fuzzificacion_conductores.py
├── sesion-04-inferencia-difusa/ Inferencia difusa (modelo Mamdani)
│   ├── 04_Taller_Analitico_Propagacion_Fuerza.txt
│   └── motor_mamdani_rrhh.py
├── sesion-05-defuzzificacion/  Defuzzificación por centro de gravedad
│   ├── 05_Taller_Analitico_Centro_de_Masa.txt
│   └── defuzzificacion_frenado.py
├── .gitattributes              Normalización de finales de línea y binarios
├── .gitignore
├── CHANGELOG.md                Registro de cambios por sesión
├── README.md
└── requirements.txt            Dependencias (NumPy, desde la sesión 5)
```

---

## Cómo ejecutar

Las sesiones 1 a 4 usan solo la librería estándar. Desde la sesión 5 se
requiere NumPy:

```bash
pip install -r requirements.txt
```


```bash
python sesion-01-introduccion/diagnostico_servidor.py
python sesion-02-motor-inferencia/motor_fraude.py
python sesion-03-logica-difusa/fuzzificacion_conductores.py
python sesion-04-inferencia-difusa/motor_mamdani_rrhh.py
python sesion-05-defuzzificacion/defuzzificacion_frenado.py
```

### En GitHub Codespaces

El repositorio incluye un **devcontainer**, así que el entorno se construye solo:
al crear el Codespace se levanta un contenedor con Python 3.11, las extensiones
de Python para VS Code y la codificación UTF-8 ya configurada. No hay que
instalar nada manualmente.

`Code → Codespaces → Create codespace on main`

---

## Contenido por sesión

### Sesión 1 — Arquitectura de un sistema experto

Un sistema experto pertenece a la **IA simbólica**: emula la decisión de un
experto humano en un dominio específico y, a diferencia de una red neuronal,
puede **explicar** el camino lógico que siguió. Su arquitectura separa tres
módulos: la Base de Conocimientos (reglas + hechos), el Motor de Inferencia y la
Interfaz con su Módulo de Explicación.

**Taller analítico.** Formalización de un fragmento de un manual de otorgamiento
de créditos en reglas de producción `SI premisa ENTONCES conclusión`,
identificando los hechos que el sistema debe solicitar y resolviendo la
ambigüedad de la cláusula de excepción.

**Taller de laboratorio.** `diagnostico_servidor.py` — sistema de diagnóstico
para el HelpDesk de una empresa tecnológica, con los tres módulos de la
arquitectura implementados:

| Módulo | Ubicación | Función |
|---|---|---|
| Base de Hechos | `servidor_estado` | Memoria de trabajo: 6 métricas del servidor |
| Base de Reglas + Motor | `diagnosticar_servidor()` | Reglas anidadas en dos niveles: el externo decide la gravedad, el interno la causa |
| Interfaz de Usuario | `capturar_estado_servidor()`, `menu_principal()` | Solicita las métricas al técnico validando cada dato, y ofrece un menú de operación |
| Explicación | `imprimir_diagnostico()`, `mostrar_historial()` | Retorna el ID de la regla disparada y conserva el registro de la sesión |

Ejecuta 11 casos que cubren todas las ramas del motor. Con terminal muestra el
menú; sin terminal ejecuta los casos de prueba.

### Sesión 2 — Motor de inferencia y Modus Ponens

El motor deja de ser un bloque de condicionales y pasa a ser un **algoritmo que
lee las reglas como datos**. Su base es el **Modus Ponens** (si P → Q y P es
verdadero, entonces Q), aplicado iterativamente mediante **encadenamiento hacia
adelante**.

**Taller analítico.** Traza de inferencia ciclo por ciclo de una base de tres
reglas, hasta que el motor alcanza la quiescencia.

**Taller de laboratorio.** `motor_fraude.py` — motor de detección de fraude
bancario. El archivo separa físicamente tres partes:

| Parte | Contenido | Qué demuestra |
|---|---|---|
| 1. Motor genérico | `evaluar_condicion()`, `premisas_satisfechas()`, `aporta_hechos_nuevos()`, `motor_inferencia()` | Lógica de control: Equiparación → Resolución de conflictos → Ejecución |
| 2. Base de fraude | `reglas_fraude` (8 reglas) | El conocimiento son datos, no código |
| 3. Base de vehículos | `reglas_motocicleta` | El mismo motor resuelve otro dominio sin cambiar una línea |
| 4. Motor hacia atrás | `demostrar()`, `consultar_meta()` | Estrategia dirigida por objetivos: parte de una meta y pregunta solo los hechos que necesita |

Las dos estrategias sobre la misma base de reglas: el encadenamiento hacia
adelante recibe las seis variables de la transacción y deduce todo lo posible;
el encadenamiento hacia atrás responde la misma pregunta consultando tres.

### Sesión 3 — Incertidumbre y lógica difusa

Las sesiones anteriores usaban **lógica booleana**: una premisa es verdadera o
falsa. Eso produce el problema de los límites estrictos — con la regla
"SI ingresos > 4000 ENTONCES crédito VIP", quien gana 3.999 queda rechazado por
un dólar. La **lógica difusa** de Lotfi Zadeh sustituye el valor booleano por un
**grado de membresía** continuo en el intervalo [0, 1], de modo que un valor
puede pertenecer a dos conjuntos a la vez.

**Taller analítico.** Cálculo manual de los grados de verdad del conjunto
"Temperatura Agradable" (función triangular con vértices 18, 22 y 26 °C) e
interpretación de lo que ese decimal significa para el motor de inferencia.

**Taller de laboratorio.** `fuzzificacion_conductores.py` — sistema difuso
completo que decide la bonificación mensual de un conductor a partir de sus
años de experiencia y sus incidentes del último año. Implementa las cuatro
etapas de un sistema experto difuso:

| Etapa | Ubicación | Función |
|---|---|---|
| 1. Fuzzificación | `membresia_triangular()`, `fuzzificar()` | Convierte un valor real en grados de verdad [0, 1] |
| 2. Base de reglas | `reglas_difusas` | Matriz de 9 reglas declaradas como datos |
| 3. Inferencia | `fuerza_de_disparo()`, `evaluar_reglas()` | AND difuso como mínimo de los grados; varias reglas disparan a la vez |
| 4. Defuzzificación | `agregar_conclusiones()`, `defuzzificar()` | OR difuso como máximo, y promedio ponderado para volver a un número concreto |

Evalúa a tres conductores (3, 6 y 12 años) y verifica computacionalmente los
grados calculados a mano en el taller analítico.

### Sesión 4 — Inferencia difusa (modelo Mamdani)

La sesión anterior convirtió valores reales en grados de verdad. Falta el paso
siguiente: **cómo evaluar una regla cuyas premisas no son ni completamente
verdaderas ni completamente falsas.** Ebrahim Mamdani lo resolvió en 1975
propagando la incertidumbre con operadores matemáticos en lugar de lógica
booleana: la **T-Norma** `MIN` para el AND, la **T-Conorma** `MAX` para el OR y
el complemento `1 - a` para el NOT. El paso ENTONCES, la **implicación**, no
traslada la conclusión completa: la trunca a la altura de la fuerza de la premisa.

**Taller analítico.** Cálculo de la fuerza de activación de una premisa anidada
`(A O B) Y C` y determinación de la altura de truncamiento de la conclusión.

**Taller de laboratorio.** `motor_mamdani_rrhh.py` — motor que decide el nivel
de bono anual de un empleado a partir de su desempeño y antigüedad.

| Componente | Ubicación | Función |
|---|---|---|
| Operadores difusos | `t_norma_and()`, `t_conorma_or()`, `complemento_not()` | Los operadores con nombre propio, no `min`/`max` sueltos en las reglas |
| Reglas del negocio | `evaluar_reglas_bono()` | Las tres reglas en la forma directa que pide el taller |
| Motor genérico | `evaluar_premisa()`, `inferir()` | Evalúa premisas anidadas de forma recursiva: resuelve `(A O B) Y C` |
| Agregación | dentro de `inferir()` | Reglas con la misma conclusión se unifican con el máximo |

Verifica computacionalmente los grados calculados a mano en el taller analítico.

### Sesión 5 — Defuzzificación

El motor de Mamdani produce respuestas como "el bono debería ser un 70 % Alto y
un 40 % Medio". Correcto dentro del sistema, inservible fuera: nómina no puede
pagar un salario "70 % Alto". La **defuzzificación** cierra el ciclo tomando la
geometría del área bajo la curva y encontrando el punto que la representa. El
estándar de la industria es el **centro de gravedad**:

    COG = Σ (x · μ(x)) / Σ μ(x)

**Taller analítico.** Cálculo del centroide sobre un dominio discreto de cuatro
puntos para determinar el porcentaje exacto de un descuento comercial.

**Taller de laboratorio.** `defuzzificacion_frenado.py` — sistema de frenado
automático que calcula la fuerza exacta en Newtons.

| Componente | Ubicación | Función |
|---|---|---|
| Centroide | `centroide()` | COG con operaciones matriciales de NumPy; retorna `None` si no hay área |
| Verificación | `centroide_paso_a_paso()` | La misma fórmula sin NumPy, para validación cruzada |
| Método alterno | `media_de_maximos()` | Promedia solo los picos: permite comparar criterios |
| Membresía continua | `gaussiana()`, `truncar()` | Campana de Gauss e implicación de Mamdani sobre el dominio |

Valida contra el resultado calculado a mano (23.33 %) y demuestra que truncar
una curva simétrica no desplaza su centroide: lo que mueve la decisión es la
competencia entre conclusiones distintas.

---

## Convenciones de control de versiones

- **Rama única `main`.** El proyecto es individual; las ramas se reservan para
  cambios experimentales que puedan romper lo entregado.
- **Un commit por unidad de trabajo**, con mensaje descriptivo en imperativo y
  prefijo de sesión. Ejemplo:
  `Sesión 2: agregar resolución de conflictos por prioridad`.
- **Una etiqueta por entrega.** Cada entrega al docente queda marcada con un tag
  anotado (`entrega-sesion-01`, `entrega-sesion-02`), de modo que siempre se
  puede recuperar el estado exacto de lo entregado.
- **`CHANGELOG.md`** documenta en lenguaje natural qué se agregó en cada sesión.
- Antes de empezar a trabajar: `git pull`. Al terminar: `git push`. Es lo que
  evita que la copia local y el Codespace diverjan.

---

## Autor

David Miller Aguilar Bayona — VIII Semestre
Docente: Amaury Giovanni Méndez Aguirre
