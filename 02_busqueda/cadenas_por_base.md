# Cadenas de búsqueda por base de datos

Cada cadena se ejecuta tal como aparece aquí. Al ejecutarla se registra la fecha, el número
de resultados y se guarda la exportación sin editar en `exportaciones_manuales`, junto con
una captura de pantalla de la pantalla de resultados.

**No modificar una cadena sin registrarlo en la bitácora de desviaciones del protocolo.**

---

## 1. Scopus

Campo: `TITLE-ABS-KEY`. Acceso por el portal de la biblioteca UAGro.

```
TITLE-ABS-KEY (
  ( "retrieval augmented generation" OR "retrieval-augmented generation" OR "grounded generation" )
  AND
  ( chatbot OR "conversational agent" OR "conversational assistant" OR "virtual assistant"
    OR "question answering" OR "dialogue system" )
  AND
  ( university OR "higher education" OR campus OR "academic institution" )
  AND
  ( regulation OR regulations OR normative OR policy OR bylaw OR bylaws OR statute
    OR administrative OR enrollment OR enrolment OR admission OR registrar
    OR "student services" OR procedure OR procedures )
)
AND PUBYEAR > 2021
AND ( LIMIT-TO ( DOCTYPE , "ar" ) OR LIMIT-TO ( DOCTYPE , "cp" ) )
AND ( LIMIT-TO ( LANGUAGE , "English" ) OR LIMIT-TO ( LANGUAGE , "Spanish" ) )
```

## 2. Web of Science Core Collection

Campo: `TS` (tema: título, resumen, palabras clave de autor y Keywords Plus).

```
TS = (
  ( "retrieval augmented generation" OR "retrieval-augmented generation" OR "grounded generation" )
  AND
  ( chatbot OR "conversational agent" OR "conversational assistant" OR "virtual assistant"
    OR "question answering" OR "dialogue system" )
  AND
  ( university OR "higher education" OR campus OR "academic institution" )
  AND
  ( regulation* OR normative OR policy OR bylaw* OR statute OR administrative
    OR enrol*ment OR admission OR registrar OR "student services" OR procedure* )
)
```

Refinar por: **Años** 2022-2026 · **Tipos de documento** Article, Proceedings Paper ·
**Idiomas** English, Spanish.

## 3. IEEE Xplore

Búsqueda avanzada, campo *All Metadata*.

```
( "All Metadata":"retrieval augmented generation" OR "All Metadata":"retrieval-augmented generation" )
AND
( "All Metadata":chatbot OR "All Metadata":"conversational agent"
  OR "All Metadata":"virtual assistant" OR "All Metadata":"question answering" )
AND
( "All Metadata":university OR "All Metadata":"higher education" OR "All Metadata":campus )
AND
( "All Metadata":regulation OR "All Metadata":administrative OR "All Metadata":admission
  OR "All Metadata":"student services" OR "All Metadata":procedure )
```

Filtros: **Year** 2022-2026 · **Content type** Conferences, Journals.

## 4. ACM Digital Library

Búsqueda avanzada, campo *Abstract*. La plataforma limita el anidamiento, por lo que la
consulta se ejecuta en dos partes y se unen los resultados en la deduplicación.

```
Parte 1
Abstract:( "retrieval augmented generation" AND ( university OR "higher education" )
           AND ( administrative OR regulation OR admission OR "student services" ) )

Parte 2
Abstract:( "retrieval-augmented generation" AND ( chatbot OR "conversational agent" )
           AND ( university OR campus OR "higher education" ) )
```

Filtros: **Publication date** 2022-2026 · **Content type** Research Article, Conference Paper.

## 5. SpringerLink

Búsqueda avanzada.

```
( "retrieval augmented generation" OR "retrieval-augmented generation" )
AND ( chatbot OR "conversational agent" OR "virtual assistant" )
AND ( university OR "higher education" )
AND ( administrative OR regulation OR admission OR "student services" )
```

Filtros: **Date published** 2022-2026 · **Content type** Article, Conference Paper ·
**Discipline** Computer Science, Education.

---

## 6. Fuentes complementarias automatizadas

Se ejecutan con el script `scripts/buscar_complementarias.py`, que consulta la API de
Crossref y la de Semantic Scholar. Su función no es sustituir a las bases primarias, sino
verificar metadatos y detectar estudios de editoriales poco indizadas. Los resultados se
marcan con su fuente de origen en la matriz de cribado.

## 7. Snowballing

Se ejecuta sobre el conjunto que supera el cribado a texto completo, conforme a Wohlin
(2014).

- **Hacia atrás.** Revisión de las referencias citadas por cada estudio incluido.
- **Hacia adelante.** Revisión de los trabajos que citan cada estudio incluido, obtenidos de
  Semantic Scholar y de Web of Science.

Cada candidato entra al mismo proceso de cribado y se registra el estudio semilla del que
proviene.

---

## Bitácora de ejecución

| Base | Fecha | Resultados | Archivo exportado | Captura | Ejecutó |
|---|---|---|---|---|---|
| Scopus | | | | | |
| Web of Science | | | | | |
| IEEE Xplore | | | | | |
| ACM Digital Library | | | | | |
| SpringerLink | | | | | |
| Crossref (automatizada) | | | | | |
| Semantic Scholar (automatizada) | | | | | |
