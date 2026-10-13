# Sistemas conversacionales anclados en recuperación para el acceso a información normativa universitaria: revisión sistemática

**Autores:** Edgar David Mariano Ruiz, Arnulfo Catalán Villegas y Mercedes Hernández De La Cruz
Facultad de Ingeniería, Universidad Autónoma de Guerrero. Maestría en Ingeniería para la Innovación y el Desarrollo Tecnológico.

Este repositorio contiene los materiales de auditoría y reproducción de una revisión sistemática
(PRISMA 2020) sobre sistemas de generación anclada en recuperación (RAG) aplicados al acceso a
información normativa, administrativa y procedimental en instituciones de educación superior.
De 2 179 registros identificados en OpenAlex, Crossref, ERIC y DBLP, 90 pasaron a cribado, 30 a
texto completo, 28 a extracción y 24 superaron el umbral de calidad de 4.0 sobre 7.0.

Con estos archivos un tercero puede repetir la búsqueda y revisar cada decisión de cribado,
de elegibilidad, de calidad y de extracción.

## Contenido

| Carpeta | Qué contiene |
|---|---|
| `01_protocolo/` | Protocolo congelado con su bitácora de desviaciones (apartado 12), lista de verificación PRISMA 2020 e informe de la búsqueda |
| `02_busqueda/` | Cadenas por base, guía de ejecución manual, registro de la búsqueda ampliada con conteos por consulta, registros recuperados y bitácoras |
| `03_cribado/` | Registro del cribado por título y resumen con decisión, criterio y motivo de cada uno de los 90 registros; conteos del diagrama PRISMA; análisis de cobertura por captura y recaptura |
| `04_texto_completo/` | Decisión y motivo de cada uno de los 30 estudios evaluados a texto completo |
| `05_calidad/` | Puntuación QA1 a QA7 de cada estudio, justificación por criterio con la regla aplicada y la evidencia extraída, y estudios por debajo del umbral |
| `06_extraccion/` | Matriz de extracción (28 estudios por 34 campos), fichas completas en JSON y estudios excluidos a texto completo |
| `07_sintesis/` | Catálogo de los estudios incluidos |
| `08_manuscrito/` | Manuscrito en LaTeX, referencias en BibTeX, diagrama PRISMA y PDF compilado |
| `scripts/` | Programas de búsqueda, verificación, consolidación, cribado y extracción |

Los criterios de elegibilidad (I1 a I8 y E1 a E8) están en el apartado 4 del protocolo y en la
Tabla 1 del manuscrito. El instrumento de calidad está en el apartado 6 del protocolo; el
formulario de extracción, en el apartado 7.

## Qué no se incluye

- **Textos completos de los estudios.** Son obras de terceros protegidas por derechos de autor.
  Cada estudio se identifica por su DOI.
- **Resúmenes (abstracts) de los registros.** Se eliminaron de todos los archivos por la misma
  razón. Se recuperan con el DOI desde Crossref u OpenAlex.

Los archivos no contienen datos personales de participantes de los estudios primarios ni
credenciales de acceso.

## Cómo reproducir la búsqueda

Los programas usan solo la biblioteca estándar de Python 3.10 o posterior.

```bash
# Crossref y OpenAlex piden un correo de contacto para el acceso cortés
export CORREO_CONTACTO="su_correo@ejemplo.org"

python scripts/busqueda_ampliada.py      # OpenAlex (6 variantes) y Crossref (3 consultas)
python scripts/buscar_eric_dblp.py       # ERIC y DBLP
python scripts/rastreo_de_citas.py       # rastreo de citas sobre los incluidos
python scripts/consolidar_para_cribado.py
```

Los programas escriben en la estructura de trabajo original (`01_busqueda/automatizada/` y
`02_cribado/`); los resultados de la ejecución del 4 de septiembre de 2026 están archivados
en las carpetas numeradas de este repositorio. Los conteos de una nueva ejecución pueden
variar, porque OpenAlex y Crossref se actualizan de forma continua.

Las cinco bases de suscripción previstas en el protocolo (Scopus, Web of Science, IEEE Xplore,
ACM Digital Library y SpringerLink) no admiten consulta automatizada sin credenciales. Sus
cadenas, con la sintaxis de cada plataforma, están en `02_busqueda/cadenas_por_base.md`.

## Actualización pendiente

El análisis de captura y recaptura (`03_cribado/analisis_cobertura_captura_recaptura.csv`)
contrastó la búsqueda contra el conjunto de una exploración previa y estimó una recuperación
de 62 %. Los 14 estudios elegibles no recuperados están listados en ese archivo y se cribarán
en la actualización de la revisión.

## Licencia

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es). Ver `LICENSE`.

## Cómo citar

Mariano Ruiz, E. D., Catalán Villegas, A., y Hernández De La Cruz, M. (2026). *Sistemas
conversacionales anclados en recuperación para el acceso a información normativa y
procedimental en instituciones de educación superior: Una revisión sistemática. Materiales de
auditoría y reproducción* (Versión 4.0) [Conjunto de datos]. GitHub.
https://github.com/DavidMariano300/rsl-rag-normativa-universitaria
