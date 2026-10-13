# Registro de la búsqueda ampliada, 4 de septiembre de 2026

Salida de `scripts/busqueda_ampliada.py` y `scripts/buscar_eric_dblp.py`, transcrita de la
consola de ejecución. Ventana de publicación: 2022 a 2026.

## OpenAlex y Crossref

| Fuente | Consulta | Registros |
|---|---|---:|
| OpenAlex | V1_ABCD, los cuatro bloques de la cadena | 149 |
| OpenAlex | V2_ABC, sin el bloque de información institucional | 434 |
| OpenAlex | V3_ACD, sin el bloque de sistema conversacional | 256 |
| OpenAlex | V4_ABD, sin el bloque de contexto universitario | 600 |
| OpenAlex | V5_AC_politica | 147 |
| OpenAlex | V6_AC_tramite | 90 |
| Crossref | retrieval augmented generation university policy chatbot evaluation | 150 |
| Crossref | retrieval augmented generation student services assistant higher education | 150 |
| Crossref | retrieval augmented generation academic regulations question answering | 150 |
| **Total** | | **2 126** |

- Duplicados: 754. Registros únicos: 1 372.
- Cumplen los bloques de la cadena en título y resumen: 217.
- Alojados en plataforma editorial indizada, según prefijo DOI: 56 (IEEE Xplore 33, ACM 8,
  MDPI 6, SpringerLink 4, ScienceDirect 3, Frontiers 1, Oxford Academic 1).
- Descartados por el criterio E8: 161 (`registros/descartados_no_indizados_2026-09-04.csv`).

## ERIC y DBLP

- En bruto: 53 (ERIC 42, DBLP 11). Duplicados: 6. Únicos: 47.
- Pertinentes por la cadena: 34 (ERIC 24, DBLP 10).

## Corrida complementaria superada

`bitacoras/bitacora_complementaria_2026-09-04.txt` documenta una corrida previa en Crossref
y Semantic Scholar (419 registros en bruto, 378 únicos). Quedó superada por la búsqueda
ampliada y no alimenta el flujo de cribado. Se conserva para trazabilidad.
