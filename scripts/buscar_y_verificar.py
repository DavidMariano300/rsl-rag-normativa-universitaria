# -*- coding: utf-8 -*-
"""Búsqueda booleana en OpenAlex y Crossref, con verificación de indización.

Contexto. Scopus, Web of Science, IEEE Xplore, ACM Digital Library y SpringerLink
exigen credenciales institucionales y no admiten consulta automatizada desde aquí
(devuelven 401 o 403). La recuperación se hace por dos vías abiertas y, para cada
registro, se verifica en qué plataformas está alojado.

Qué se verifica y qué no. El prefijo del DOI identifica de forma inequívoca a la
agencia que lo registró, de modo que un DOI 10.1109 está en IEEE Xplore y uno
10.1145 está en la ACM Digital Library. Eso es comprobable. La indización en
Scopus y en Web of Science NO es comprobable sin suscripción, por lo que esos
campos quedan marcados para verificación manual, con el ISSN listo para pegar en
el portal. Nunca se afirma una indización que no se pudo comprobar.

Uso:
    python buscar_y_verificar.py
    python buscar_y_verificar.py --max-por-consulta 200
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

CORREO = os.environ.get("CORREO_CONTACTO", "tu_correo@ejemplo.org")
RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "01_busqueda" / "automatizada"
ANIO_MIN, ANIO_MAX = 2022, 2026

BLOQUE_A = '"retrieval augmented generation" OR "retrieval-augmented generation" OR "grounded generation"'
BLOQUE_B = 'chatbot OR "conversational agent" OR "conversational assistant" OR "virtual assistant" OR "question answering" OR "dialogue system"'
BLOQUE_C = 'university OR "higher education" OR campus OR "academic institution"'
BLOQUE_D = ('regulation OR regulations OR normative OR policy OR bylaw OR statute OR '
            'administrative OR enrollment OR admission OR registrar OR "student services" OR procedure')

# Prefijo de DOI a plataforma. La agencia registradora del DOI es verificable.
PLATAFORMAS = {
    "10.1109": "IEEE Xplore",
    "10.1145": "ACM Digital Library",
    "10.1007": "SpringerLink", "10.1057": "SpringerLink", "10.1186": "SpringerLink",
    "10.1016": "ScienceDirect (Elsevier)",
    "10.1002": "Wiley Online Library",
    "10.3390": "MDPI",
    "10.1080": "Taylor & Francis",
    "10.1088": "IOP Publishing",
    "10.1177": "SAGE Journals",
    "10.1371": "PLOS",
    "10.1093": "Oxford Academic",
}


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
            with urllib.request.urlopen(req, timeout=50) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == intentos - 1:
                print(f"      fallo: {e}")
                return None
            time.sleep(espera * (i + 1))
    return None


def buscar_openalex(maximo):
    """Consulta booleana anidada sobre título y resumen."""
    filtro = (f"title_and_abstract.search:({BLOQUE_A}) AND ({BLOQUE_B}) AND "
              f"({BLOQUE_C}) AND ({BLOQUE_D}),"
              f"publication_year:{ANIO_MIN}-{ANIO_MAX}")
    salida, cursor = [], "*"
    while cursor and len(salida) < maximo:
        url = ("https://api.openalex.org/works?"
               f"filter={urllib.parse.quote(filtro, safe=':,')}"
               f"&per-page=200&cursor={cursor}&mailto={CORREO}")
        d = pedir(url)
        if not d:
            break
        for it in d.get("results", []):
            loc = it.get("primary_location") or {}
            src = loc.get("source") or {}
            inv = it.get("abstract_inverted_index") or {}
            resumen = ""
            if inv:
                pos = {}
                for palabra, idxs in inv.items():
                    for i in idxs:
                        pos[i] = palabra
                resumen = " ".join(pos[k] for k in sorted(pos))[:1500]
            salida.append({
                "fuente": "OpenAlex",
                "doi": (it.get("doi") or "").replace("https://doi.org/", "").lower(),
                "titulo": it.get("display_name") or "",
                "autores": "; ".join(a["author"]["display_name"]
                                     for a in (it.get("authorships") or [])[:6]),
                "anio": it.get("publication_year") or "",
                "medio": src.get("display_name") or "",
                "tipo": it.get("type") or "",
                "editorial": src.get("host_organization_name") or "",
                "issn": ";".join(src.get("issn") or []),
                "citas": it.get("cited_by_count", 0),
                "resumen": resumen,
            })
        cursor = (d.get("meta") or {}).get("next_cursor")
        time.sleep(0.4)
    return salida[:maximo]


def cargar_crossref_previo():
    """Reutiliza la corrida de Crossref ya ejecutada, si existe."""
    prev = sorted(SALIDA.glob("complementarias_*.csv"))
    if not prev:
        return []
    filas = list(csv.DictReader(prev[-1].open(encoding="utf-8-sig")))
    for f in filas:
        f.setdefault("issn", "")
        f.setdefault("citas", "")
    return filas


def cumple_bloques(r):
    """Aplica los cuatro bloques sobre título y resumen."""
    t = f"{r.get('titulo','')} {r.get('resumen','')}"
    pats = [
        [r"retrieval[\s\-]?augmented\s+generation", r"\bRAG\b", r"grounded\s+generation"],
        [r"chatbot", r"conversational\s+(agent|assistant|ai|system)", r"virtual\s+assistant",
         r"question[\s\-]answering", r"dialogue\s+system", r"asistente\s+conversacional"],
        [r"universit", r"higher\s+education", r"\bcampus\b", r"academic\s+institution",
         r"educaci[oó]n\s+superior", r"\bstudent", r"estudiante"],
        [r"regulat", r"normativ", r"\bpolic(y|ies)\b", r"bylaw", r"statute", r"administrativ",
         r"enrol", r"admission", r"registrar", r"student\s+services", r"procedure",
         r"tr[aá]mite", r"reglament"],
    ]
    return all(any(re.search(p, t, re.I) for p in grupo) for grupo in pats)


def verificar_indizacion(reg):
    """Determina en qué plataformas está alojado el registro."""
    doi = (reg.get("doi") or "").strip().lower()
    prefijo = doi.split("/")[0] if "/" in doi else ""
    reg["plataforma_verificada"] = PLATAFORMAS.get(prefijo, "")
    reg["prefijo_doi"] = prefijo
    reg["en_ieee"] = "sí" if prefijo == "10.1109" else "no"
    reg["en_acm"] = "sí" if prefijo == "10.1145" else "no"
    reg["en_springer"] = "sí" if prefijo in ("10.1007", "10.1057", "10.1186") else "no"
    reg["en_sciencedirect"] = "sí" if prefijo == "10.1016" else "no"
    # Scopus y Web of Science no son verificables sin suscripción.
    reg["en_scopus"] = "verificar manualmente"
    reg["en_wos"] = "verificar manualmente"

    issn = (reg.get("issn") or "").split(";")[0].strip()
    reg["issn_para_consulta"] = issn
    if issn:
        d = pedir(f"https://api.openalex.org/sources/issn:{issn}?mailto={CORREO}", intentos=2)
        if d:
            reg["revista_en_doaj"] = "sí" if d.get("is_in_doaj") else "no"
            reg["revista_en_scielo"] = "sí" if d.get("is_in_scielo") else "no"
            reg["revista_es_nucleo"] = "sí" if d.get("is_core") else "no"
            st = d.get("summary_stats") or {}
            reg["revista_indice_h"] = st.get("h_index", "")
            reg["revista_trabajos"] = d.get("works_count", "")
        time.sleep(0.25)
    return reg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-por-consulta", type=int, default=600)
    args = ap.parse_args()

    print("Bases con credenciales: Scopus 401, Web of Science 401, IEEE 403, ACM 403,")
    print("Springer 401. No es posible consultarlas de forma automatizada.\n")

    print("Buscando en OpenAlex con la consulta booleana de los cuatro bloques...")
    oa = buscar_openalex(args.max_por_consulta)
    print(f"  OpenAlex: {len(oa)} registros")

    cr = cargar_crossref_previo()
    print(f"  Crossref (corrida previa reutilizada): {len(cr)} registros")

    todos = oa + cr
    doi_vistos, tit_vistos, unicos, dup = set(), set(), [], 0
    for r in todos:
        doi = (r.get("doi") or "").strip().lower()
        clave = (normalizar(r.get("titulo", ""))[:90], str(r.get("anio", "")))
        if doi and doi in doi_vistos:
            dup += 1; continue
        if not doi and clave[0] and clave in tit_vistos:
            dup += 1; continue
        if doi: doi_vistos.add(doi)
        if clave[0]: tit_vistos.add(clave)
        unicos.append(r)
    print(f"\nTotal en bruto: {len(todos)} · duplicados: {dup} · únicos: {len(unicos)}")

    candidatos = [r for r in unicos if cumple_bloques(r)]
    print(f"Cumplen los cuatro bloques: {len(candidatos)}")

    print("\nVerificando indización de cada candidato...")
    for i, r in enumerate(candidatos, 1):
        verificar_indizacion(r)
        if i % 10 == 0:
            print(f"  {i}/{len(candidatos)}")

    hoy = date.today().isoformat()
    campos = ["id", "fuente", "doi", "prefijo_doi", "titulo", "autores", "anio", "medio",
              "tipo", "editorial", "issn_para_consulta", "plataforma_verificada",
              "en_ieee", "en_acm", "en_springer", "en_sciencedirect",
              "en_scopus", "en_wos", "revista_en_doaj", "revista_en_scielo",
              "revista_es_nucleo", "revista_indice_h", "revista_trabajos", "citas", "resumen"]
    destino = SALIDA / f"candidatos_verificados_{hoy}.csv"
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for i, r in enumerate(sorted(candidatos, key=lambda x: (-int(x.get("anio") or 0),
                                                               x.get("titulo", ""))), 1):
            r["id"] = f"V{i:03d}"
            w.writerow(r)

    conteo = {}
    for r in candidatos:
        p = r.get("plataforma_verificada") or "editorial sin plataforma mayor"
        conteo[p] = conteo.get(p, 0) + 1
    print("\nAlojamiento verificado por prefijo de DOI:")
    for k, v in sorted(conteo.items(), key=lambda x: -x[1]):
        print(f"  {v:>4}  {k}")

    print(f"\nGuardado en {destino.name}")
    print("Las columnas en_scopus y en_wos quedan marcadas para verificación manual:")
    print("hay que pegar el ISSN de la columna issn_para_consulta en el portal de cada base.")


if __name__ == "__main__":
    main()
