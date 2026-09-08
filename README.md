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
│   ├── diagnostico_servidor.py
│   └── Taller-1-Logica-Proposicional.docx
├── sesion-02-motor-inferencia/ Motor de inferencia y Modus Ponens
│   ├── motor_fraude.py
│   └── Taller-2-Traza-Inferencia.docx
├── .gitattributes              Normalización de finales de línea y binarios
├── .gitignore
├── CHANGELOG.md                Registro de cambios por sesión
├── README.md
└── requirements.txt            Dependencias (ninguna: solo librería estándar)
```

---

## Cómo ejecutar

No hay dependencias externas. Con Python 3.8 o superior:

```bash
python sesion-01-introduccion/diagnostico_servidor.py
python sesion-02-motor-inferencia/motor_fraude.py
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
para el HelpDesk de una empresa tecnológica.

| Módulo | Ubicación | Función |
|---|---|---|
| Base de Hechos | `servidor_estado` | Memoria de trabajo: 6 métricas del servidor |
| Base de Reglas + Motor | `diagnosticar_servidor()` | Reglas anidadas en dos niveles: el externo decide la gravedad, el interno la causa |
| Explicación | `imprimir_diagnostico()` | Retorna el ID de la regla disparada: trazabilidad de la decisión |

Ejecuta 11 casos que cubren todas las ramas del motor.

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
