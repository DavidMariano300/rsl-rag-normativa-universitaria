# -*- coding: utf-8 -*-
"""Importa las exportaciones manuales de Scopus, Web of Science, IEEE, ACM y Springer.

Acepta los tres formatos que entregan esas plataformas y los normaliza al mismo
esquema que usan los demás archivos de la revisión, de modo que todo se pueda
deduplicar y cribar junto.

Formatos reconocidos
    .ris  .txt   Scopus, Web of Science, IEEE Xplore
    .bib         ACM Digital Library, SpringerLink, DBLP
    .csv         Scopus, IEEE Xplore, Web of Science

El nombre del archivo indica la base de origen, que se guarda en cada registro
para poder reportar cuántos aportó cada fuente en el diagrama PRISMA. Nombra los
archivos así:  scopus_2026-09-10.ris,  wos_2026-09-10.txt,  ieee_2026-09-10.csv

Uso:
    python importar_exportaciones.py
"""
import csv
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "01_busqueda" / "exportaciones_manuales"
SALIDA = RAIZ / "01_busqueda"

BASES = {
    "scopus": "Scopus", "wos": "Web of Science", "webofscience": "Web of Science",
    "ieee": "IEEE Xplore", "acm": "ACM Digital Library", "springer": "SpringerLink",
    "sciencedirect": "ScienceDirect", "eric": "ERIC", "dblp": "DBLP",
}

# Etiquetas RIS que interesan
RIS = {"TI": "titulo", "T1": "titulo", "AU": "autor", "PY": "anio", "Y1": "anio",
       "JO": "medio", "JF": "medio", "T2": "medio", "DO": "doi", "AB": "resumen",
       "SN": "issn", "TY": "tipo", "PB": "editorial"}

# Encabezados CSV de cada plataforma, en minúsculas
CSV_MAPA = {
    "titulo": ["title", "document title", "article title", "ti"],
    "autores": ["authors", "author full names", "author(s)", "au"],
    "anio": ["year", "publication year", "py"],
    "medio": ["source title", "publication title", "journal", "so"],
    "doi": ["doi", "di"],
    "resumen": ["abstract", "ab"],
    "issn": ["issn", "sn"],
    "tipo": ["document type", "content type", "dt"],
    "editorial": ["publisher", "pu"],
}


def base_de(nombre):
    n = nombre.lower()
    for clave, valor in BASES.items():
        if clave in n:
            return valor
    return "no identificada"


def normalizar(t):
    if not t:
        return ""
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", t.lower()).strip()


def limpiar(v):
    return re.sub(r"\s+", " ", (v or "")).strip()


def leer_ris(texto, origen):
    registros, actual, autores = [], {}, []
    for linea in texto.splitlines():
        m = re.match(r"^([A-Z][A-Z0-9])\s+-\s?(.*)$", linea)
        if not m:
            if actual and linea.strip() and "resumen" in actual:
                actual["resumen"] += " " + linea.strip()
            continue
        etiqueta, valor = m.group(1), m.group(2).strip()
        if etiqueta == "ER":
            if actual.get("titulo"):
                actual["autores"] = "; ".join(autores[:6])
                registros.append(actual)
            actual, autores = {}, []
            continue
        campo = RIS.get(etiqueta)
        if not campo:
            continue
        if campo == "autor":
            autores.append(valor)
        elif campo in actual:
            actual[campo] += " " + valor
        else:
            actual[campo] = valor
    if actual.get("titulo"):
        actual["autores"] = "; ".join(autores[:6])
        registros.append(actual)
    for r in registros:
        r["fuente"] = origen
    return registros


def leer_bibtex(texto, origen):
    registros = []
    for bloque in re.split(r"\n@", texto)[0:]:
        if "{" not in bloque:
            continue
        campos = dict(re.findall(r"(\w+)\s*=\s*[{\"]((?:[^{}]|\{[^{}]*\})*)[}\"]", bloque))
        titulo = limpiar(re.sub(r"[{}]", "", campos.get("title", "")))
        if not titulo:
            continue
        registros.append({
            "titulo": titulo,
            "autores": "; ".join(a.strip() for a in
                                 re.split(r"\s+and\s+", campos.get("author", ""))[:6]),
            "anio": limpiar(campos.get("year", "")),
            "medio": limpiar(re.sub(r"[{}]", "", campos.get("journal") or
                                    campos.get("booktitle", ""))),
            "doi": limpiar(campos.get("doi", "")).lower(),
            "resumen": limpiar(re.sub(r"[{}]", "", campos.get("abstract", ""))),
            "issn": limpiar(campos.get("issn", "")),
            "editorial": limpiar(campos.get("publisher", "")),
            "tipo": "", "fuente": origen,
        })
    return registros


def leer_csv(ruta, origen):
    for cod in ("utf-8-sig", "latin-1"):
        try:
            filas = list(csv.DictReader(ruta.open(encoding=cod)))
            break
        except UnicodeDecodeError:
            continue
    else:
        return []
    if not filas:
        return []
    cabeceras = {k.lower().strip(): k for k in filas[0].keys() if k}
    def col(campo):
        for cand in CSV_MAPA[campo]:
            if cand in cabeceras:
                return cabeceras[cand]
        return None
    mapa = {c: col(c) for c in CSV_MAPA}
    registros = []
    for f in filas:
        titulo = limpiar(f.get(mapa["titulo"] or "", ""))
        if not titulo:
            continue
        registros.append({
            "titulo": titulo,
            "autores": limpiar(f.get(mapa["autores"] or "", "")),
            "anio": limpiar(f.get(mapa["anio"] or "", "")),
            "medio": limpiar(f.get(mapa["medio"] or "", "")),
            "doi": limpiar(f.get(mapa["doi"] or "", "")).lower(),
            "resumen": limpiar(f.get(mapa["resumen"] or "", "")),
            "issn": limpiar(f.get(mapa["issn"] or "", "")),
            "tipo": limpiar(f.get(mapa["tipo"] or "", "")),
            "editorial": limpiar(f.get(mapa["editorial"] or "", "")),
            "fuente": origen,
        })
    return registros


def main():
    if not ENTRADA.exists() or not any(ENTRADA.iterdir()):
        print(f"No hay exportaciones en {ENTRADA}")
        print("\nCómo nombrarlas para que se reconozca la base de origen:")
        for k, v in sorted(set(BASES.items()), key=lambda x: x[1]):
            print(f"   {k}_AAAA-MM-DD.ris   ->  {v}")
        return

    todos, por_archivo = [], []
    for archivo in sorted(ENTRADA.iterdir()):
        if archivo.suffix.lower() not in (".ris", ".txt", ".bib", ".csv"):
            continue
        origen = base_de(archivo.name)
        if archivo.suffix.lower() == ".csv":
            regs = leer_csv(archivo, origen)
        else:
            texto = archivo.read_text(encoding="utf-8", errors="replace")
            regs = (leer_bibtex(texto, origen) if archivo.suffix.lower() == ".bib"
                    else leer_ris(texto, origen))
        por_archivo.append((archivo.name, origen, len(regs)))
        todos += regs

    print("Archivos leídos")
    for nombre, origen, n in por_archivo:
        print(f"   {n:>5} registros · {origen:<20} {nombre}")
    print(f"\nTotal importado: {len(todos)}")

    if not todos:
        print("Ningún registro reconocido. Revisa el formato de los archivos.")
        return

    doi_v, tit_v, unicos, dup = set(), set(), [], 0
    for r in todos:
        doi = (r.get("doi") or "").replace("https://doi.org/", "").strip().lower()
        r["doi"] = doi
        clave = (normalizar(r.get("titulo", ""))[:90], str(r.get("anio", "")))
        if doi and doi in doi_v:
            dup += 1; continue
        if not doi and clave[0] and clave in tit_v:
            dup += 1; continue
        if doi: doi_v.add(doi)
        if clave[0]: tit_v.add(clave)
        unicos.append(r)

    print(f"Duplicados entre bases: {dup}")
    print(f"Únicos: {len(unicos)}")
    aporte = {}
    for r in unicos:
        aporte[r["fuente"]] = aporte.get(r["fuente"], 0) + 1
    print("\nAporte único por base, para el diagrama PRISMA")
    for k, v in sorted(aporte.items(), key=lambda x: -x[1]):
        print(f"   {v:>5}  {k}")

    hoy = date.today().isoformat()
    destino = SALIDA / f"exportaciones_normalizadas_{hoy}.csv"
    campos = ["id", "fuente", "doi", "titulo", "autores", "anio", "medio", "tipo",
              "editorial", "issn", "resumen"]
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for i, r in enumerate(sorted(unicos, key=lambda x: (x["fuente"],
                                                            str(x.get("anio") or ""))), 1):
            r["id"] = f"M{i:04d}"
            w.writerow(r)
    print(f"\nGuardado en {destino.relative_to(RAIZ)}")
    print("Siguiente paso: python busqueda_ampliada.py para unir todo y aplicar el filtro,")
    print("o usa este archivo tal cual si prefieres cribar solo lo de las bases primarias.")


if __name__ == "__main__":
    main()
