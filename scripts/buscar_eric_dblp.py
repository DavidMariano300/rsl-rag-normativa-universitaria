# -*- coding: utf-8 -*-
"""Búsqueda en ERIC y DBLP, las dos bases especializadas de consulta abierta.

ERIC es la base de referencia en educación, del Instituto de Ciencias de la
Educación de Estados Unidos. DBLP es la bibliografía curada de ciencias de la
computación. Ambas admiten consulta sin credenciales, y las dos son bases
propiamente dichas, no agregadores, de modo que amplían la cobertura del
protocolo por el lado educativo y por el lado informático.

Uso:
    python buscar_eric_dblp.py
"""
import os
import csv
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

CORREO = os.environ.get("CORREO_CONTACTO", "tu_correo@ejemplo.org")
RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "01_busqueda" / "automatizada"
ANIO_MIN, ANIO_MAX = 2022, 2026

CONSULTAS_ERIC = [
    '(title:"retrieval augmented generation" OR description:"retrieval augmented generation")',
    '(description:"retrieval-augmented" AND description:chatbot)',
    '(description:chatbot AND description:"higher education" AND description:"large language model")',
    '(description:"conversational agent" AND description:university AND description:"artificial intelligence")',
]
CONSULTAS_DBLP = [
    "retrieval augmented generation university",
    "retrieval augmented generation higher education",
    "retrieval augmented generation campus chatbot",
    "RAG chatbot university administrative",
    "retrieval augmented generation student services",
    "retrieval augmented generation academic regulations",
]


def normalizar(t):
    if not t:
        return ""
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", t.lower()).strip()


def pedir(url, intentos=3, espera=2.0):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"RSL-UAGro ({CORREO})"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            if i == intentos - 1:
                print(f"      fallo: {e}")
                return None
            time.sleep(espera * (i + 1))
    return None


def buscar_eric(consulta):
    campos = "id,title,author,publicationdateyear,source,description,publicationtype,issn"
    url = ("https://api.ies.ed.gov/eric/?search=" + urllib.parse.quote(consulta) +
           f"&format=json&rows=200&fields={campos}")
    d = pedir(url)
    if not d:
        return []
    salida = []
    for x in (d.get("response") or {}).get("docs", []):
        anio = x.get("publicationdateyear")
        if not anio or not (ANIO_MIN <= int(anio) <= ANIO_MAX):
            continue
        autores = x.get("author") or []
        salida.append({
            "fuente": "ERIC", "variante": "ERIC",
            "doi": "", "titulo": x.get("title") or "",
            "autores": "; ".join(autores[:6]) if isinstance(autores, list) else str(autores),
            "anio": anio, "medio": x.get("source") or "",
            "tipo": "; ".join(x.get("publicationtype") or [])
                    if isinstance(x.get("publicationtype"), list) else (x.get("publicationtype") or ""),
            "editorial": "", "issn": "; ".join(x.get("issn") or [])
                    if isinstance(x.get("issn"), list) else (x.get("issn") or ""),
            "citas": "", "eric_id": x.get("id") or "",
            "resumen": re.sub(r"\s+", " ", x.get("description") or "")[:1600],
        })
    return salida


def buscar_dblp(consulta):
    url = ("https://dblp.org/search/publ/api?q=" + urllib.parse.quote(consulta) +
           "&format=json&h=200")
    d = pedir(url)
    if not d:
        return []
    hits = ((d.get("result") or {}).get("hits") or {}).get("hit") or []
    salida = []
    for h in hits:
        i = h.get("info") or {}
        anio = i.get("year")
        if not anio or not (ANIO_MIN <= int(anio) <= ANIO_MAX):
            continue
        aut = (i.get("authors") or {}).get("author") or []
        if isinstance(aut, dict):
            aut = [aut]
        salida.append({
            "fuente": "DBLP", "variante": "DBLP",
            "doi": (i.get("doi") or "").lower(),
            "titulo": i.get("title") or "",
            "autores": "; ".join(a.get("text", "") for a in aut[:6]),
            "anio": anio, "medio": i.get("venue") or "",
            "tipo": i.get("type") or "", "editorial": i.get("publisher") or "",
            "issn": "", "citas": "", "eric_id": "",
            "resumen": "",
        })
    return salida


def pertinente(r):
    """DBLP no entrega resumen, por lo que sobre esa fuente se juzga por título."""
    t = f"{r.get('titulo','')} {r.get('resumen','')}"
    tec = any(re.search(p, t, re.I) for p in
              [r"retrieval[\s\-]?augmented", r"\bRAG\b", r"grounded\s+generation"])
    ctx = any(re.search(p, t, re.I) for p in
              [r"universit", r"higher\s+education", r"\bcampus\b", r"academic",
               r"\bcollege\b", r"\bstudent", r"education"])
    return tec and ctx


def main():
    crudos = []
    print("ERIC, base de referencia en educación")
    for c in CONSULTAS_ERIC:
        r = buscar_eric(c)
        print(f"   {len(r):>4} registros · {c[:62]}")
        crudos += r
        time.sleep(1.0)

    print("\nDBLP, bibliografía de ciencias de la computación")
    for c in CONSULTAS_DBLP:
        r = buscar_dblp(c)
        print(f"   {len(r):>4} registros · {c[:62]}")
        crudos += r
        time.sleep(1.0)

    doi_v, tit_v, unicos, dup = set(), set(), [], 0
    for r in crudos:
        doi = (r.get("doi") or "").strip().lower()
        clave = (normalizar(r.get("titulo", ""))[:90], str(r.get("anio", "")))
        if doi and doi in doi_v:
            dup += 1; continue
        if clave[0] and clave in tit_v:
            dup += 1; continue
        if doi: doi_v.add(doi)
        if clave[0]: tit_v.add(clave)
        unicos.append(r)

    pertinentes = [r for r in unicos if pertinente(r)]
    print(f"\nEn bruto: {len(crudos)} · duplicados: {dup} · únicos: {len(unicos)}")
    print(f"Pertinentes: {len(pertinentes)}")
    por_base = {}
    for r in pertinentes:
        por_base[r["fuente"]] = por_base.get(r["fuente"], 0) + 1
    for k, v in sorted(por_base.items()):
        print(f"   {v:>4}  {k}")

    hoy = date.today().isoformat()
    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / f"eric_dblp_{hoy}.csv"
    campos = ["id", "fuente", "doi", "titulo", "autores", "anio", "medio", "tipo",
              "editorial", "issn", "eric_id", "citas", "variante", "resumen"]
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for i, r in enumerate(sorted(pertinentes,
                                     key=lambda x: (x["fuente"], -int(x.get("anio") or 0))), 1):
            r["id"] = f"E{i:03d}"
            w.writerow(r)
    print(f"\nGuardado en {destino.name}")

    if pertinentes:
        print("\nAnticipo:")
        for r in pertinentes[:14]:
            print(f"   {r['fuente']:<6} {r['anio']} · {r['titulo'][:70]}")


if __name__ == "__main__":
    main()
