# Protocolo de revisión sistemática de literatura

**Sistemas conversacionales anclados en recuperación para el acceso a información
normativa y procedimental en instituciones de educación superior**

| | |
|---|---|
| Autor | Edgar David Mariano Ruiz |
| Director | Dr. Arnulfo Catalán Villegas |
| Codirectora | Dra. Mercedes Hernández De La Cruz |
| Programa | Maestría en Ingeniería para la Innovación y Desarrollo Tecnológico, UAGro |
| Versión | 2.0 |
| Fecha de congelamiento del protocolo | pendiente de firma del director |
| Reemplaza a | Revisión v1 de agosto de 2026, archivada en `99_ARCHIVO` |

> **Regla de congelamiento.** Este protocolo se define y se firma **antes** de ejecutar
> la primera búsqueda. Cualquier cambio posterior se registra en la bitácora de
> desviaciones del apartado 12, con fecha y justificación. Ninguna modificación se aplica
> de forma retroactiva sin dejar constancia.

---

## 1. Justificación y objetivo de la revisión

La versión anterior de esta revisión se apoyó en una sola fuente automatizada y aplicó
criterios de inclusión amplios, lo que produjo un conjunto numeroso pero heterogéneo,
con literatura gris y estudios sin evaluación empírica. Esta versión corrige ese diseño
mediante tres decisiones: fuentes bibliográficas curadas con revisión por pares, criterios
de elegibilidad restrictivos y un instrumento de evaluación de calidad con umbral de corte.

El objetivo es identificar, valorar críticamente y sintetizar la evidencia empírica
disponible sobre sistemas conversacionales anclados en recuperación aplicados al acceso a
información normativa, administrativa y procedimental en instituciones de educación
superior, con énfasis en cómo se evalúa la fidelidad de las respuestas y en qué evidencia
existe sobre la reducción del tiempo de consulta.

El protocolo sigue la declaración PRISMA 2020 (Page et al., 2021) para el reporte y las
guías de Kitchenham y Charters (2007) para revisiones sistemáticas en ingeniería de
software, complementadas con las recomendaciones de Wohlin (2014) para la búsqueda por
snowballing.

## 2. Preguntas de investigación

La formulación sigue la estructura PICOC.

| Elemento | Definición para esta revisión |
|---|---|
| Población | Instituciones de educación superior y sus usuarios: estudiantes, aspirantes y personal administrativo |
| Intervención | Sistemas conversacionales cuya generación está anclada en un corpus institucional recuperado |
| Comparación | Mecanismos tradicionales de consulta, o configuraciones alternativas del propio sistema |
| Resultados | Fidelidad o precisión factual, tiempo de respuesta, usabilidad o satisfacción |
| Contexto | Información normativa, administrativa y procedimental de la institución |

**PI1.** ¿Qué arquitecturas de recuperación y generación se han implementado para el acceso
a información normativa y administrativa en educación superior, y cómo se preparan los
corpus documentales que las alimentan?

**PI2.** ¿Con qué métricas, instrumentos y procedimientos se evalúa la fidelidad de las
respuestas, y qué valores se reportan?

**PI3.** ¿Qué evidencia empírica existe sobre la reducción del tiempo de acceso a la
información frente a los mecanismos tradicionales de consulta?

**PI4.** ¿Qué prácticas de reporte y qué vacíos metodológicos presentan los estudios en
cuanto a trazabilidad de la respuesta, disponibilidad de datos y reproducibilidad?

## 3. Estrategia de búsqueda

### 3.1 Fuentes

La búsqueda combina tres vías. Se descarta el uso de agregadores generalistas como fuente
primaria, por la heterogeneidad de su indización y por la imposibilidad de controlar el
criterio de revisión por pares.

| Vía | Fuente | Acceso | Función |
|---|---|---|---|
| Primaria | Scopus | Exportación manual desde el portal institucional | Cobertura multidisciplinar con control de indización |
| Primaria | Web of Science Core Collection | Exportación manual | Cobertura de alto impacto y análisis de citas |
| Primaria | IEEE Xplore | Exportación manual | Congresos y revistas de ingeniería |
| Primaria | ACM Digital Library | Exportación manual | Computación y sistemas de información |
| Primaria | SpringerLink | Exportación manual | Revistas y capítulos revisados por pares |
| Complementaria | Crossref REST API | Automatizada, sin suscripción | Verificación de metadatos y cobertura de editoriales |
| Complementaria | Semantic Scholar API | Automatizada | Recuperación de referencias citantes y citadas |
| Primaria | ERIC, del Instituto de Ciencias de la Educación | Automatizada, sin suscripción | Base de referencia en educación |
| Primaria | DBLP | Automatizada, sin suscripción | Bibliografía curada de ciencias de la computación |
| Manual | Snowballing hacia atrás y hacia adelante | Sobre el conjunto incluido | Recuperación de estudios no indizados |

Las exportaciones manuales se guardan sin editar en `01_busqueda/exportaciones_manuales`,
con el nombre `base_fecha.ris` o `.bib`, y se acompañan de una captura de pantalla de la
consulta ejecutada. La captura es la evidencia de que la cadena se aplicó tal como se
declara aquí.

**Limitación declarada de la vía complementaria.** La API de Crossref no admite operadores
booleanos: su parámetro de consulta ejecuta una búsqueda por relevancia difusa. Para
someter esa fuente al mismo criterio que las bases primarias, la consulta booleana del
protocolo se aplica de forma posterior y determinista sobre el título y el resumen de cada
registro recuperado, mediante el script `scripts/filtrar_complementarias.py`. El conjunto en
bruto y el conjunto descartado se conservan íntegros para auditoría. Esta operacionalización
se reporta de forma expresa en el apartado de métodos del manuscrito y no sustituye la
búsqueda booleana en las bases primarias.

### 3.1.1 Registro del intento de acceso automatizado a las bases primarias

El 2026-09-04 se verificó si las bases primarias admiten consulta automatizada sin
credenciales institucionales. El resultado se registra aquí porque condiciona el diseño de
la recuperación y debe reportarse en el apartado de métodos.

| Base | Punto de acceso probado | Respuesta | Consecuencia |
|---|---|---|---|
| Scopus | API de Elsevier | 401, credenciales requeridas | Exportación manual desde el portal |
| Web of Science | API Starter de Clarivate | 401, credenciales requeridas | Exportación manual desde el portal |
| IEEE Xplore | API de IEEE | 403, acceso denegado | Exportación manual desde el portal |
| ACM Digital Library | Búsqueda web | 403, acceso denegado | Exportación manual desde el portal |
| SpringerLink | API de Springer Nature | 401, credenciales requeridas | Exportación manual desde el portal |

En consecuencia, la recuperación automatizada se realiza sobre OpenAlex y Crossref, que sí
admiten consulta abierta, y cada registro recuperado pasa por el procedimiento de
verificación de alojamiento del apartado 3.4. Las cinco bases primarias siguen siendo parte
del protocolo y su búsqueda se ejecuta de forma manual.

### 3.4 Verificación del alojamiento y de la indización

Cada registro que supera la consulta booleana se somete a verificación de dónde está
alojado y de qué señales de calidad tiene su medio de publicación.

**Lo que se verifica de forma comprobable.** El prefijo del identificador digital de objeto
identifica de manera inequívoca a la agencia que lo registró. Un prefijo `10.1109`
corresponde a IEEE y por tanto el trabajo está en IEEE Xplore; `10.1145` corresponde a la
ACM y está en su biblioteca digital; `10.1007`, `10.1057` y `10.1186` corresponden a
Springer Nature; `10.1016` a Elsevier. Esta correspondencia se comprueba de forma
determinista y se reporta por registro.

**Señales de calidad del medio.** Para cada registro con ISSN se consulta si la revista está
en el Directorio de Revistas de Acceso Abierto, si está en SciELO, si pertenece al conjunto
núcleo de fuentes, su índice h y su volumen de publicación.

**Lo que no se verifica y no se afirma.** La indización en Scopus y en Web of Science
requiere suscripción y no puede comprobarse desde el entorno de trabajo. Esos dos campos se
entregan marcados como pendientes de verificación manual, con el ISSN preparado para
consultarlo en el portal de cada base. **En ningún caso se declara que un estudio está
indizado en una base cuya indización no se pudo comprobar.**

### 3.2 Cadenas de búsqueda

La cadena base se construye con tres bloques unidos por conjunción, y cada bloque agrupa
sinónimos por disyunción. Se aplica sobre título, resumen y palabras clave.

```
BLOQUE A · tecnología
("retrieval augmented generation" OR "retrieval-augmented generation" OR RAG
 OR "grounded generation" OR "retrieval grounded")

BLOQUE B · sistema conversacional
(chatbot OR "conversational agent" OR "conversational assistant"
 OR "virtual assistant" OR "question answering" OR "dialogue system")

BLOQUE C · contexto institucional universitario
(university OR "higher education" OR campus OR "academic institution")
AND (regulation* OR normative OR policy OR bylaw* OR statute OR administrative
 OR enrollment OR admission OR registrar OR "student services" OR procedure*)
```

La sintaxis exacta por base, con los campos y los operadores de cada plataforma, se
encuentra en `01_busqueda/cadenas_por_base.md`. Cada ejecución se registra con fecha,
número de resultados y responsable.

### 3.3 Ventana temporal y límites

| Parámetro | Valor | Justificación |
|---|---|---|
| Periodo | 2022 a 2026 | La arquitectura de referencia se publica en 2020 (Lewis et al.); las primeras aplicaciones documentadas en educación superior aparecen a partir de 2022 |
| Idiomas | Inglés y español | Idiomas de trabajo del equipo revisor; se documenta cualquier estudio descartado por idioma |
| Tipo de documento | Artículo de revista y ponencia en congreso con revisión por pares | Se excluye literatura gris, ver criterio E4 |

## 4. Criterios de elegibilidad

### 4.1 Inclusión

| Clave | Criterio |
|---|---|
| I1 | Estudio primario que desarrolla, implementa o evalúa un sistema de acceso a información cuya generación está anclada en documentos recuperados |
| I2 | El contexto de aplicación es una institución de educación superior |
| I3 | La información objetivo es normativa, administrativa o procedimental institucional |
| I4 | Reporta evaluación empírica con al menos una métrica cuantitativa o un instrumento sistemático de valoración |
| I5 | Publicado entre 2022 y 2026 |
| I6 | Sometido a revisión por pares, en revista o en congreso con comité científico |
| I7 | Texto completo accesible en inglés o español |
| I8 | Alojado en una plataforma editorial con indización reconocida: IEEE Xplore, ACM Digital Library, SpringerLink, ScienceDirect, o una editorial mayor equivalente |

### 4.2 Exclusión

| Clave | Criterio |
|---|---|
| E1 | El objeto es contenido instruccional, tutoría académica o apoyo al aprendizaje, no información institucional |
| E2 | El sistema no incorpora recuperación sobre un corpus propio: modelo de lenguaje sin anclaje, o chatbot de reglas o de intenciones |
| E3 | Estudio secundario: revisión, mapeo sistemático, metaanálisis o ensayo |
| E4 | Literatura gris: preimpresión sin revisión por pares, tesis, reporte técnico, entrada de blog o documentación de producto |
| E5 | Dominio distinto al universitario: clínico, industrial, jurisdiccional o corporativo |
| E6 | No presenta evaluación empírica, o solo describe una arquitectura propuesta |
| E7 | Versión duplicada o preliminar de un trabajo ya incluido; se conserva la versión más completa y se registra la relación |
| E8 | Publicado por una editorial sin plataforma de indización reconocida, comprobado por el prefijo del identificador digital de objeto |

> **Efecto esperado sobre el volumen.** Los criterios I4, I6, E4 y E6 son los que reducen
> el conjunto. Con base en la distribución observada en la revisión anterior, donde el 17 %
> de los registros incluidos eran preimpresiones o tesis y una fracción relevante carecía de
> evaluación empírica, se estima un conjunto final de entre 20 y 35 estudios. Un conjunto de
> ese tamaño permite extracción profunda y valoración de calidad individual, que es lo que
> una revisión de este nivel exige.

## 5. Proceso de selección

1. **Deduplicación.** Se unifican los registros por DOI normalizado y, en su ausencia, por
   coincidencia difusa de título y año con umbral declarado. El script y el umbral quedan en
   `scripts/`.
2. **Cribado por título y resumen.** Dos revisores de forma independiente y ciega, sobre el
   mismo formulario. Cada registro se marca como incluir, excluir o dudoso, con la clave del
   criterio aplicado.
3. **Medición de acuerdo.** Se calcula el coeficiente kappa de Cohen sobre las decisiones
   del cribado. Se establece como umbral aceptable un valor igual o superior a 0.70. Si el
   valor resulta menor, se revisa la definición de los criterios, se recalibra con una
   muestra piloto y se repite el cribado.
4. **Resolución de discrepancias.** Los desacuerdos se discuten en sesión conjunta. Si
   persisten, decide un tercer revisor, que será el director de tesis.
5. **Cribado a texto completo.** Los registros que superan la etapa anterior se leen
   completos y se aplican de nuevo los criterios, registrando la razón exacta de cada
   exclusión.
6. **Snowballing.** Sobre el conjunto incluido se ejecuta una iteración hacia atrás, sobre
   las referencias citadas, y una hacia adelante, sobre los trabajos citantes. Los candidatos
   entran al mismo proceso de cribado.
7. **Diagrama de flujo.** Los conteos de cada etapa se reportan en el diagrama PRISMA 2020.

**Segundo revisor.** El acuerdo entre revisores exige una segunda persona. Debe quedar
designada antes de iniciar el cribado y su nombre se asienta en este protocolo.

## 6. Evaluación de la calidad de los estudios

Cada estudio incluido se puntúa con el siguiente instrumento, adaptado de Kitchenham y
Charters (2007) y de Dybå y Dingsøyr (2008). Cada criterio se valora con 1 punto si se
cumple, 0.5 si se cumple parcialmente y 0 si no se cumple.

| Clave | Criterio de calidad |
|---|---|
| QA1 | Declara con claridad sus objetivos o preguntas de investigación |
| QA2 | Describe el corpus documental y su procedencia de manera que permita replicar la preparación de los datos |
| QA3 | Describe la arquitectura de recuperación y generación con detalle suficiente para reproducirla |
| QA4 | Reporta evaluación empírica con métricas definidas y procedimiento descrito |
| QA5 | Incluye comparación contra una línea base o contra una configuración alternativa |
| QA6 | Discute limitaciones y amenazas a la validez |
| QA7 | Pone a disposición datos, código o conjunto de evaluación |

**Puntuación máxima: 7.0. Umbral de inclusión en la síntesis: 4.0.** Los estudios que
puntúen por debajo del umbral se documentan en una tabla aparte, con su puntuación, y se
excluyen de la síntesis. La puntuación la asignan los dos revisores de forma independiente
y se reporta el acuerdo.

## 7. Extracción de datos

El formulario de extracción se pilotea con cinco estudios antes de aplicarse al conjunto
completo. Los campos son los siguientes.

| Campo | Descripción |
|---|---|
| Identificación | Clave, autores, año, título, tipo de publicación, medio, DOI |
| Contexto | País, tipo de institución, tipo de usuario atendido |
| Corpus | Naturaleza de los documentos, volumen, idioma, procedimiento de preparación |
| Segmentación | Estrategia de fragmentación del documento y justificación declarada |
| Recuperación | Modelo de representación, tipo de búsqueda, reordenamiento, valor de k |
| Generación | Modelo de lenguaje, tamaño, despliegue local o en servicio externo |
| Evaluación | Niveles evaluados, métricas, instrumento, tamaño del conjunto de prueba |
| Resultados | Valores reportados por métrica, con su unidad |
| Comparación | Existencia de línea base y naturaleza de esta |
| Trazabilidad | Si la respuesta cita la fuente y si permite verificarla |
| Reproducibilidad | Disponibilidad de datos, código o conjunto de evaluación |
| Limitaciones | Amenazas declaradas por los autores |
| Calidad | Puntuación QA1 a QA7 y total |

La extracción la realiza el revisor principal y el segundo revisor verifica una muestra
aleatoria de al menos el 20 % de los estudios. Las discrepancias se resuelven por consenso.

## 8. Estrategia de síntesis

La síntesis es narrativa y tabular, con conteo de frecuencias por categoría. No se realiza
metaanálisis por la heterogeneidad esperada de métricas y contextos, lo que se declara de
forma expresa como limitación.

| Pregunta | Método de síntesis |
|---|---|
| PI1 | Taxonomía de arquitecturas y de estrategias de preparación del corpus, con tabla comparativa |
| PI2 | Inventario de métricas e instrumentos, con los valores reportados y su rango |
| PI3 | Tabulación de estudios que reportan tiempo, con la naturaleza de su comparación |
| PI4 | Análisis de vacíos de reporte, con el porcentaje de estudios que cumple cada práctica |

## 9. Riesgo de sesgo

| Nivel | Riesgo | Medida de control |
|---|---|---|
| Selección | Sesgo de publicación por excluir literatura gris | Se declara de forma expresa; el snowballing recupera trabajos poco indizados |
| Selección | Sesgo de base de datos | Cinco fuentes primarias de indización distinta, más dos complementarias |
| Cribado | Sesgo del revisor único | Doble cribado independiente con medición de kappa |
| Extracción | Error de transcripción | Verificación cruzada de una muestra del 20 % |
| Síntesis | Sobreinterpretación de resultados heterogéneos | Se reporta el rango y el número de estudios que sostiene cada afirmación |

## 10. Amenazas a la validez

**Validez de constructo.** Los términos del dominio no están estandarizados: un mismo
sistema puede describirse como asistente, agente o chatbot. Se mitiga con un bloque amplio
de sinónimos y con el snowballing.

**Validez interna.** La aplicación de los criterios admite juicio. Se mitiga con criterios
operacionalizados, con calibración piloto y con la medición de acuerdo.

**Validez externa.** La restricción a educación superior limita la generalización a otros
dominios. Es una delimitación deliberada, no un defecto.

**Fiabilidad.** Toda decisión queda registrada en las matrices con su criterio y su fecha,
de modo que un tercero pueda reproducir el proceso.

## 11. Productos y calendario

| Producto | Ubicación | Responsable |
|---|---|---|
| Protocolo firmado | `00_protocolo` | Estudiante y director |
| Cadenas por base con captura de ejecución | `01_busqueda` | Estudiante |
| Registros exportados sin editar | `01_busqueda/exportaciones_manuales` | Estudiante |
| Matriz de cribado con doble revisión y kappa | `02_cribado` | Ambos revisores |
| Matriz de extracción | `03_extraccion` | Estudiante, verificación del segundo revisor |
| Matriz de calidad con puntuaciones | `04_calidad` | Ambos revisores |
| Diagrama PRISMA y tablas de síntesis | `05_sintesis` | Estudiante |
| Lista de verificación PRISMA 2020 | `00_protocolo` | Estudiante |
| Manuscrito | `06_manuscrito` | Estudiante |

## 12. Bitácora de desviaciones del protocolo

| Fecha | Apartado | Cambio | Justificación | Vo. Bo. |
|---|---|---|---|---|
| 2026-10-06 | 5 y 9 | Se suprime el doble cribado independiente y el cálculo de kappa. El cribado y la extracción los realiza un solo revisor. | El director de tesis, previsto como tercer revisor, avala de forma expresa el conjunto seleccionado y el procedimiento de extracción. Se declara como limitación en el manuscrito y el riesgo de sesgo del revisor único queda sin control estadístico. | |
| 2026-10-06 | 4.2 | Al leer el texto completo, el estudio C067 se reclasifica como excluido por el criterio E6. | El trabajo superó el cribado por título y resumen, pero el texto completo confirma que es un artefacto conceptual de ciencia del diseño sin evaluación empírica: los propios autores declaran que la arquitectura no ha sido validada y que las puntuaciones del índice de fiabilidad que presentan son hipotéticas. Se conserva su ficha como referencia conceptual para la discusión, sin incorporarlo a la síntesis. | |
| 2026-10-06 | 6 | Se aplica el umbral de calidad de 4.0 sobre 7.0. Cuatro estudios quedan por debajo (C002 con 3.5, C085 con 3.5, C011 con 1.0 y C089 con 1.0) y salen de la síntesis. | Se reportan en `04_calidad/estudios_bajo_umbral.csv` con su puntuación y su motivo, como prescribe el protocolo. El caso de C085 se menciona de forma explícita en la discusión, porque su hallazgo sobre el ordenamiento de los resultados tiene valor diagnóstico aunque el estudio no alcance el umbral. La síntesis queda con 24 estudios. | |
| 2026-10-13 | 3 y 10 | Se retira del manuscrito la afirmación de saturación basada en el rastreo de citas y se reporta el análisis de captura y recaptura del 22 de septiembre, que estimó una recuperación de 62 %. | De 37 estudios elegibles del conjunto de control, la búsqueda recuperó 23; los 14 no recuperados se listan en `analisis_cobertura_busqueda.csv` y se cribarán en la actualización de la revisión, para lo cual se requiere su texto completo. | |
| 2026-10-13 | 3 y 9 | Se corrigen las cifras de identificación del diagrama PRISMA: 2 179 registros en bases (OpenAlex 1 676, Crossref 450, ERIC 42, DBLP 11), 760 duplicados, 1 168 excluidos por la cadena booleana y 161 por E8. | El manuscrito v2 reportaba 419 registros, que corresponden a la corrida complementaria en Crossref y Semantic Scholar, superada por la búsqueda ampliada y ajena al flujo de cribado. Las cifras se reconstruyeron de la salida registrada de la búsqueda ampliada. Desde el cribado en adelante no cambia nada. | |
| 2026-10-06 | 7 | Se crea la carpeta 03_extraccion y se aplica el formulario de extracción a los 29 estudios con texto completo disponible. | El estudio C073 no se pudo obtener a texto completo; su extracción se marca como parcial, basada solo en el resumen, y no se puntúa en calidad porque ninguno de los siete criterios es verificable sin el texto. Comparte autoría con C064, que sí se obtuvo, de modo que esa línea de trabajo queda representada. | |
| 2026-10-06 | 07_textos_completos | Se recuperan PoliChat (C058) y URAG (C064) desde las actas completas de ICCS 2025 Workshops y CCIS 2351, que se habían descargado con nombre genérico. | Los dos trabajos estaban dentro de volúmenes de actas, no ausentes. Se extraen como PDF independientes y las actas se archivan aparte. | |
| 2026-09-04 | 3.1 | Se documenta que las cinco bases primarias no admiten consulta automatizada. La recuperación abierta se hace con OpenAlex y Crossref. | Scopus 401, Web of Science 401, IEEE 403, ACM 403, Springer 401. La búsqueda manual en las cinco bases sigue vigente. | |
| 2026-09-04 | 4.1 y 4.2 | Se añaden los criterios I8 y E8: solo se incluyen estudios alojados en plataformas editoriales con indización reconocida. | La primera corrida mostró que 63 de 80 candidatos provenían de editoriales sin plataforma indizada. El criterio eleva la selectividad y responde a la indicación del director de trabajar con menos estudios y mayor rigor. | |
| 2026-09-04 | 3.1 | Se incorporan ERIC y DBLP como fuentes primarias de consulta abierta. | Son bases especializadas y curadas, no agregadores. ERIC cubre el lado educativo y DBLP el informático, con lo que se atiende la indicación de ampliar a otras bases. | |
| 2026-09-04 | 3.2 | Se amplía la búsqueda de una a seis variantes de la consulta booleana, relajando un bloque a la vez. | Con el criterio I8 el filtro de salida es más estricto, por lo que conviene aumentar la sensibilidad de la recuperación para no perder estudios que usan vocabulario distinto. | |

---

## Referencias del protocolo

Dybå, T., y Dingsøyr, T. (2008). Empirical studies of agile software development:
A systematic review. *Information and Software Technology, 50*(9-10), 833-859.
https://doi.org/10.1016/j.infsof.2008.01.006

Kitchenham, B., y Charters, S. (2007). *Guidelines for performing systematic literature
reviews in software engineering* (EBSE Technical Report EBSE-2007-01). Keele University y
University of Durham.

Page, M. J., McKenzie, J. E., Bossuyt, P. M., Boutron, I., Hoffmann, T. C., Mulrow, C. D.,
Shamseer, L., Tetzlaff, J. M., Akl, E. A., Brennan, S. E., Chou, R., Glanville, J.,
Grimshaw, J. M., Hróbjartsson, A., Lalu, M. M., Li, T., Loder, E. W., Mayo-Wilson, E.,
McDonald, S., … Moher, D. (2021). The PRISMA 2020 statement: An updated guideline for
reporting systematic reviews. *BMJ, 372*, n71. https://doi.org/10.1136/bmj.n71

Wohlin, C. (2014). Guidelines for snowballing in systematic literature studies and a
replication in software engineering. En *Proceedings of the 18th International Conference
on Evaluation and Assessment in Software Engineering* (pp. 1-10). ACM.
https://doi.org/10.1145/2601248.2601268

---

<br><br>

| | |
|---|---|
| <br><br>_______________________________<br>Edgar David Mariano Ruiz<br>Estudiante | <br><br>_______________________________<br>Dr. Arnulfo Catalán Villegas<br>Vo. Bo. del director de Tesis |
