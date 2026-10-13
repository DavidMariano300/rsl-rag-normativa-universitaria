# -*- coding: utf-8 -*-
"""Búsqueda en las fuentes complementarias de la revisión sistemática v2.

Consulta Crossref y Semantic Scholar. No sustituye a las bases primarias: sirve
para verificar metadatos y para detectar estudios de editoriales poco indizadas.

Cada registro guarda su fuente y la consulta que lo recuperó, de modo que la
procedencia de cualquier estudio sea rastreable hasta la cadena que lo trajo.

Uso:
    python buscar_complementarias.py                 # ejecuta y guarda CSV
    python buscar_complementarias.py --solo-conteo   # solo reporta cuántos hay
"""
import os
import argparse
import csv
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

CORREO = os.environ.get("CORREO_CONTACTO", "tu_correo@ejemplo.org")          # Crossref pide un contacto para el pool cortés
SALIDA = Path(__file__).resolve().parent.parent / "01_busqueda" / "automatizada"
ANIO_MIN, ANIO_MAX = 2022, 2026

# Las consultas replican los tres bloques del protocolo. Crossref no admite
# booleanos anidados, así que cada combinación se lanza por separado y la
# deduplicación posterior las une.
CONSULTAS = [
    "retrieval augmented generation university administrative information",
    "retrieval augmented generation higher education student services chatbot",
    "retrieval augmented generation university regulations policy question answering",
    "retrieval augmented generation campus virtual assistant admission",
    "retrieval augmented generation academic institution procedures conversational agent",
    "grounded generation higher education institutional information chatbot",
]

TIPOS_VALIDOS = {"journal-article", "proceedings-article", "book-chapter"}


def normalizar(texto):
    """Título en minúsculas, sin acentos ni puntuación, para cotejo difuso."""
    if not texto:
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", texto.lower()).strip()


def pedir(url, intentos=3, espera=2.0):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"RSL-UAGro ({CORREO})"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == intentos - 1:
                print(f"    fallo definitivo: {e}")
                return None
            time.sleep(espera * (i + 1))
    return None


def buscar_crossref(consulta, filas=100):
    """Registros de Crossref para una consulta, filtrados por año y tipo."""
    base = "https://api.crossref.org/works"
    params = {
        "query.bibliographic": consulta,
        "rows": filas,
        "filter": f"from-pub-date:{ANIO_MIN}-01-01,until-pub-date:{ANIO_MAX}-12-31",
        "select": "DOI,title,author,issued,container-title,type,abstract,subject,publisher",
        "mailto": CORREO,
    }
    datos = pedir(f"{base}?{urllib.parse.urlencode(params)}")
    if not datos:
        return []
    salida = []
    for it in datos.get("message", {}).get("items", []):
        if it.get("type") not in TIPOS_VALIDOS:
            continue
        partes = it.get("issued", {}).get("date-parts", [[None]])[0]
        anio = partes[0] if partes and partes[0] else None
        if not anio or not (ANIO_MIN <= anio <= ANIO_MAX):
            continue
        autores = "; ".join(
            f"{a.get('family','')} {a.get('given','')}".strip()
            for a in it.get("author", [])[:6] if a.get("family"))
        resumen = re.sub(r"<[^>]+>", " ", it.get("abstract", "") or "")
        salida.append({
            "fuente": "Crossref",
            "consulta": consulta,
            "doi": (it.get("DOI") or "").lower(),
            "titulo": (it.get("title") or [""])[0],
            "autores": autores,
            "anio": anio,
            "medio": (it.get("container-title") or [""])[0],
            "tipo": it.get("type", ""),
            "editorial": it.get("publisher", ""),
            "resumen": re.sub(r"\s+", " ", resumen).strip()[:1500],
        })
    return salida


def buscar_semantic(consulta, limite=100):
    """Registros de Semantic Scholar. Tolera el límite de tasa sin abortar."""
    base = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": consulta,
        "limit": limite,
        "year": f"{ANIO_MIN}-{ANIO_MAX}",
        "fields": "title,abstract,year,authors,venue,publicationTypes,externalIds",
    }
    datos = pedir(f"{base}?{urllib.parse.urlencode(params)}", intentos=4, espera=5.0)
    if not datos:
        return []
    salida = []
    for it in datos.get("data", []):
        doi = ((it.get("externalIds") or {}).get("DOI") or "").lower()
        salida.append({
            "fuente": "Semantic Scholar",
            "consulta": consulta,
            "doi": doi,
            "titulo": it.get("title") or "",
            "autores": "; ".join(a.get("name", "") for a in (it.get("authors") or [])[:6]),
            "anio": it.get("year") or "",
            "medio": it.get("venue") or "",
            "tipo": "; ".join(it.get("publicationTypes") or []),
            "editorial": "",
            "resumen": re.sub(r"\s+", " ", it.get("abstract") or "").strip()[:1500],
        })
    return salida


def deduplicar(registros):
    """Une por DOI y, en su ausencia, por título normalizado y año."""
    vistos_doi, vistos_titulo, unicos, duplicados = {}, {}, [], 0
    for r in registros:
        clave_doi = r["doi"] or None
        clave_tit = (normalizar(r["titulo"])[:90], str(r["anio"]))
        if clave_doi and clave_doi in vistos_doi:
            duplicados += 1
            continue
        if not clave_doi and clave_tit[0] and clave_tit in vistos_titulo:
            duplicados += 1
            continue
        if clave_doi:
            vistos_doi[clave_doi] = True
        if clave_tit[0]:
            vistos_titulo[clave_tit] = True
        unicos.append(r)
    return unicos, duplicados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-conteo", action="store_true")
    args = ap.parse_args()

    crudos = []
    print(f"Ventana temporal: {ANIO_MIN} a {ANIO_MAX}\n")
    for i, c in enumerate(CONSULTAS, 1):
        print(f"[{i}/{len(CONSULTAS)}] {c[:66]}")
        cr = buscar_crossref(c)
        print(f"    Crossref: {len(cr)} registros")
        crudos += cr
        time.sleep(1.2)
        ss = buscar_semantic(c)
        print(f"    Semantic Scholar: {len(ss)} registros")
        crudos += ss
        time.sleep(3.5)

    unicos, dup = deduplicar(crudos)
    print(f"\nRecuperados en bruto: {len(crudos)}")
    print(f"Duplicados eliminados: {dup}")
    print(f"Únicos para cribado:   {len(unicos)}")
    por_fuente = {}
    for r in unicos:
        por_fuente[r["fuente"]] = por_fuente.get(r["fuente"], 0) + 1
    for k, v in sorted(por_fuente.items()):
        print(f"    {k}: {v}")

    if args.solo_conteo:
        return

    SALIDA.mkdir(parents=True, exist_ok=True)
    hoy = date.today().isoformat()
    destino = SALIDA / f"complementarias_{hoy}.csv"
    campos = ["id", "fuente", "consulta", "doi", "titulo", "autores", "anio",
              "medio", "tipo", "editorial", "resumen"]
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for i, r in enumerate(sorted(unicos, key=lambda x: (-int(x["anio"] or 0), x["titulo"])), 1):
            r["id"] = f"C{i:04d}"
            w.writerow(r)
    print(f"\nGuardado en {destino}")

    bitacora = SALIDA / f"bitacora_{hoy}.txt"
    bitacora.write_text(
        f"BITACORA DE BUSQUEDA COMPLEMENTARIA\n"
        f"Fecha de ejecucion: {hoy}\n"
        f"Ventana: {ANIO_MIN}-{ANIO_MAX}\n"
        f"Fuentes: Crossref REST API, Semantic Scholar Graph API\n"
        f"Consultas ejecutadas: {len(CONSULTAS)}\n"
        f"Tipos aceptados: {', '.join(sorted(TIPOS_VALIDOS))}\n"
        f"Registros en bruto: {len(crudos)}\n"
        f"Duplicados eliminados: {dup}\n"
        f"Unicos para cribado: {len(unicos)}\n\n"
        + "\n".join(f"  {i}. {c}" for i, c in enumerate(CONSULTAS, 1)) + "\n",
        encoding="utf-8")
    print(f"Bitácora en {bitacora}")


if __name__ == "__main__":
    main()
