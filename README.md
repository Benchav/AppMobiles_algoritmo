# Concurso Multidisciplinario de Aplicaciones Moviles 2026 - Algoritmo de Equipos

meter 2 de sistemas y 2 ingenieros mas por cada equipo + uno de ciencias economicas y 1 de humanidades


Este proyecto automatiza la conformacion de equipos de trabajo multidisciplinarios garantizando un balance equitativo de conocimientos y areas de especialidad academica. El algoritmo ingiere un archivo CSV con las inscripciones, limpia y normaliza los datos, y distribuye a los estudiantes en equipos de hasta 5 integrantes bajo reglas de negocio estrictas.

--- del numero 90 en adelante son datos sinteticos para completar el archivo---

## Guia de Inicio Rapido

### 1. Instalacion de Dependencias
Asegurate de tener Python instalado en tu sistema. Luego, instala las librerias necesarias ejecutando el siguiente comando en la raiz del proyecto:

```bash
pip install -r requirements.txt
```

*(Esto instalara pandas, openpyxl y matplotlib)*.

### 2. Preparacion de Datos
Verifica que el archivo de inscripciones en formato .csv se encuentre dentro de la carpeta data/.

## Nota importante: Si vas a actualizar o agregar un nuevo archivo de inscripciones, este debe ir obligatoriamente dentro de la carpeta `data/`. Debes **reemplazar el archivo existente** y asegurarte de que el nuevo archivo tenga exactamente el **mismo nombre** que el original para que el algoritmo pueda encontrarlo.

### 3. Ejecucion del Algoritmo
Para iniciar el pipeline completo de limpieza, agrupacion y exportacion, ejecuta:

```bash
python main.py
```

---

## Estructura del Proyecto

```text
algoritmo_app/
│
├── data/                  # Datos de Entrada
│   ├── Inscripción...csv  # CSV crudo descargado del formulario
│   └── datos_limpios.csv  # CSV resultante tras la limpieza automatica
│
├── datos/                 # Resultados de Salida (Output)
│   ├── equipos_conformados.xlsx
│   ├── conteo_estudiantes.csv
│   ├── grafico_areas.png
│   ├── grafico_area_año.png
│   └── grafico_carreras.png
│
├── src/                   # Codigo Fuente (Logica de Negocio)
│   ├── config.py
│   ├── data_cleaner.py
│   ├── data_loader.py
│   ├── team_builder.py
│   └── exporter.py
│
├── main.py                # Archivo ejecutable central
└── requirements.txt       # Lista de dependencias del proyecto
```

---

## Explicacion de Cada Archivo (src/)

- **main.py**: Es el orquestador principal. Invoca secuencialmente cada etapa del pipeline (limpiar -> cargar -> graficar -> conformar equipos -> exportar Excel).
- **config.py**: Almacena variables globales, rutas de directorios, nombres de archivos y el diccionario base de mapeo para que el resto del sistema lo pueda consultar de forma unificada.
- **data_cleaner.py**: Se encarga de la limpieza bruta. Transforma mas de 35 maneras diferentes en las que los estudiantes escribieron sus carreras y las reduce a un estandar canonico unico. Elimina tildes, caracteres matematicos especiales y descarta inscripciones nulas.
- **data_loader.py**: Aplica la limpieza logica. Filtra estudiantes duplicados (por nombre o carnet), descarta a los inscritos en el año "Otro" (ya que no cumplen el requisito universitario) y clasifica a cada estudiante en una de las 4 areas requeridas.
- **team_builder.py**: Es el cerebro matematico. Recibe el pool de estudiantes limpios y, usando semillas aleatorias dependientes del reloj, agrupa a los estudiantes en conjuntos que no se repiten garantizando la distribucion requerida.
- **exporter.py**: Es la capa de presentacion visual. Utiliza matplotlib para dibujar graficas analiticas estilizadas en paleta oscura y openpyxl para inyectar los datos tabulares en un reporte Excel con diseño profesional (colores, bordes y agrupacion).

---

## Flujo y Migracion de Datos

El algoritmo esta diseñado para tratar la informacion de manera inmutable, pasando de un estado "crudo" a un resultado "pulido" a traves del siguiente flujo de vida:

1. **Ingesta (Crudo):** Se lee el archivo CSV exportado del formulario ubicado en la carpeta data/.
2. **Normalizacion y Sanitizacion:** data_cleaner detecta caracteres basura, normaliza mayusculas y reduce variantes de texto (ej. Ingeneria Industrial e Ing. industrial pasan a ser Ingenieria Industrial). 
3. **Persistencia Intermedia:** Los datos pre-procesados se guardan inmediatamente como data/datos_limpios.csv garantizando trazabilidad.
4. **Validacion de Negocio y Deduplicacion:** Se cargan los datos_limpios.csv. Aqui se eliminan registros duplicados de un mismo alumno (filtrando por carnet y nombre identico) y se excluyen años universitarios irrelevantes ("Otro").
5. **Categorizacion de Areas:** Cada carrera normalizada se vincula a su Macrozona Academica (Sistemas, Ingenieria, Economicas o Humanidades).
6. **Aleatorizacion y Formacion:** Los candidatos entran a pools separados por areas. Se construyen los equipos extrayendo integrantes aleatoriamente bajo la regla de los 5 roles, vaciando progresivamente los pools.
7. **Exportacion Final:** El resultado numerico y los DataFrames se compilan en graficos analiticos .png y un multi-hoja de calculo en la carpeta datos/.

---

## Reglas de Formacion de Equipos

El algoritmo obliga a la siguiente distribucion base para un equipo optimo de **5 integrantes**:
- **2 Estudiantes:** Ingenieria en Sistemas de Informacion (Exclusivamente de 4to o 5to año).
- **1 Estudiante:** Otra disciplina ingenieril (ej. Industrial o Telematica).
- **1 Estudiante:** Ciencias Economicas.
- **1 Estudiante:** Ciencias de Humanidades y Educacion (ej. Psicologia o Fisica-Matematica).

*Nota: El algoritmo garantiza combinaciones unicas entre corridas gracias a su factorizacion de aleatoriedad por tiempo. Si hay escasez en alguna area, el sistema prioriza a los integrantes base (Sistemas y Otras Ingenierias) antes de abortar un equipo.*

---

## Interpretacion de los Graficos Analiticos

Al finalizar la ejecucion, en la carpeta datos/ se habran generado automaticamente 3 infografias cruciales para el analisis de los inscritos:

### 1. grafico_areas.png (Grafico de Pastel)
- **Que muestra:** Proporcion total del pool de inscritos dividido entre las cuatro grandes areas profesionales.
- **Utilidad:** Permite ver rapidamente de un solo vistazo que macrozona del conocimiento domina la competencia. Incluye el porcentaje y el total numerico.

### 2. grafico_area_año.png (Grafico de Barras Agrupadas)
- **Que muestra:** Segmentacion profunda que cruza las Areas versus el Año Universitario (3ro, 4to, 5to).
- **Utilidad:** Fundamental para identificar si el area de "Sistemas de Informacion" cuenta con la cantidad requerida y especifica de alumnos de 4to y 5to año exigida por las reglas de la competencia.

### 3. grafico_carreras.png (Grafico de Barras Horizontales)
- **Que muestra:** El conteo individual y especifico de cuantos inscritos validos y sin duplicar pertenecen a cada carrera particular (Psicologia, Informatica Educativa, Ingenieria Industrial, etc).
- **Utilidad:** Proporciona granularidad exacta con codigo de colores segun su macro-area, identificando las carreras de mayor popularidad.
