# -*- coding: utf-8 -*-
"""Búsqueda ampliada, restringida a estudios alojados en las bases del protocolo.

Estrategia. Se ejecutan seis variantes de la consulta booleana en lugar de una
sola: la más específica exige los cuatro bloques, y las demás relajan un bloque
a la vez para recuperar trabajos que usan vocabulario distinto. El aumento de
ruido no importa, porque el filtro posterior por plataforma lo elimina.

Filtro de salida. Solo se conservan los registros cuyo prefijo de identificador
digital de objeto corresponde a una editorial con plataforma indizada. Los
registros de editoriales pequeñas o regionales se descartan y se conservan
aparte para auditoría.

Uso:
    python busqueda_ampliada.py
    python busqueda_ampliada.py --tope 800
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

# --------------------------------------------------------------- bloques léxicos
A = ('"retrieval augmented generation" OR "retrieval-augmented generation" OR '
     '"grounded generation" OR "retrieval augmented" OR "knowledge grounded" OR '
     '"retrieval based generation"')
B = ('chatbot OR "conversational agent" OR "conversational assistant" OR '
     '"virtual assistant" OR "question answering" OR "dialogue system" OR '
     '"chat assistant" OR "AI assistant" OR "conversational AI"')
C = ('university OR "higher education" OR campus OR "academic institution" OR '
     'college OR "educational institution"')
D = ('regulation OR regulations OR normative OR policy OR policies OR bylaw OR '
     'statute OR administrative OR enrollment OR enrolment OR admission OR '
     'registrar OR "student services" OR "academic services" OR "student affairs" OR '
     'procedure OR procedures OR scholarship OR tuition OR "academic regulations"')

# Cada variante relaja un bloque distinto. La clave se guarda en cada registro
# para poder rastrear qué consulta lo trajo.
VARIANTES = [
    ("V1_ABCD", f"({A}) AND ({B}) AND ({C}) AND ({D})"),
    ("V2_ABC",  f"({A}) AND ({B}) AND ({C})"),
    ("V3_ACD",  f"({A}) AND ({C}) AND ({D})"),
    ("V4_ABD",  f"({A}) AND ({B}) AND ({D})"),
    ("V5_AC_politica", f"({A}) AND ({C}) AND (policy OR regulation OR normative OR compliance)"),
    ("V6_AC_tramite",  f"({A}) AND ({C}) AND (admission OR enrollment OR registrar OR "
                       f'"student services" OR "academic advising")'),
]

# --------------------------------------------- plataformas con indización reconocida
NIVEL_1 = {   # bases nombradas en el protocolo
    "10.1109": "IEEE Xplore",
    "10.1145": "ACM Digital Library",
    "10.1007": "SpringerLink", "10.1057": "SpringerLink", "10.1186": "SpringerLink",
    "10.1140": "SpringerLink",
    "10.1016": "ScienceDirect (Elsevier)",
}
NIVEL_2 = {   # editoriales mayores, habitualmente indizadas en Scopus y WoS
    "10.1002": "Wiley Online Library",
    "10.3390": "MDPI",
    "10.1080": "Taylor & Francis",
    "10.1088": "IOP Publishing",
    "10.1177": "SAGE Journals",
    "10.1093": "Oxford Academic",
    "10.1017": "Cambridge Core",
    "10.1108": "Emerald Insight",
    "10.3389": "Frontiers",
    "10.1371": "PLOS",
    "10.18653": "ACL Anthology",
    "10.1609": "AAAI",
    "10.24963": "IJCAI",
    "10.5220": "SciTePress",
    "10.1049": "IET Digital Library",
    "10.1111": "Wiley Online Library",
}
PLATAFORMAS = {**NIVEL_1, **NIVEL_2}

TIPOS_EXCLUIDOS = {"preprint", "dataset", "dissertation", "peer-review", "grant",
                   "retraction", "editorial", "erratum", "paratext", "libro"}


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
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == intentos - 1:
                print(f"      fallo: {e}")
                return None
            time.sleep(espera * (i + 1))
    return None


def resumen_de(inv):
    if not inv:
        return ""
    pos = {}
    for palabra, idxs in inv.items():
        for i in idxs:
            pos[i] = palabra
    return " ".join(pos[k] for k in sorted(pos))[:1600]


def openalex(clave, consulta, tope):
    filtro = (f"title_and_abstract.search:{consulta},"
              f"publication_year:{ANIO_MIN}-{ANIO_MAX}")
    salida, cursor = [], "*"
    while cursor and len(salida) < tope:
        url = ("https://api.openalex.org/works?"
               f"filter={urllib.parse.quote(filtro, safe=':,')}"
               f"&per-page=200&cursor={cursor}&mailto={CORREO}")
        d = pedir(url)
        if not d:
            break
        for it in d.get("results", []):
            loc = it.get("primary_location") or {}
            src = loc.get("source") or {}
            salida.append({
                "fuente": "OpenAlex",
                "variante": clave,
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
                "resumen": resumen_de(it.get("abstract_inverted_index")),
            })
        cursor = (d.get("meta") or {}).get("next_cursor")
        time.sleep(0.35)
    return salida[:tope]


def crossref(consulta, filas=150):
    params = {
        "query.bibliographic": consulta,
        "rows": filas,
        "filter": f"from-pub-date:{ANIO_MIN}-01-01,until-pub-date:{ANIO_MAX}-12-31",
        "select": "DOI,title,author,issued,container-title,type,abstract,publisher,ISSN",
        "mailto": CORREO,
    }
    d = pedir("https://api.crossref.org/works?" + urllib.parse.urlencode(params))
    if not d:
        return []
    salida = []
    for it in d.get("message", {}).get("items", []):
        partes = it.get("issued", {}).get("date-parts", [[None]])[0]
        anio = partes[0] if partes and partes[0] else None
        if not anio or not (ANIO_MIN <= anio <= ANIO_MAX):
            continue
        salida.append({
            "fuente": "Crossref", "variante": "CR",
            "doi": (it.get("DOI") or "").lower(),
            "titulo": (it.get("title") or [""])[0],
            "autores": "; ".join(f"{a.get('family','')} {a.get('given','')}".strip()
                                 for a in it.get("author", [])[:6] if a.get("family")),
            "anio": anio, "medio": (it.get("container-title") or [""])[0],
            "tipo": it.get("type", ""), "editorial": it.get("publisher", ""),
            "issn": ";".join(it.get("ISSN") or []), "citas": "",
            "resumen": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ",
                                                  it.get("abstract", "") or "")).strip()[:1600],
        })
    return salida


def pertinente(r):
    """Exige el bloque de tecnología y el de contexto universitario o institucional."""
    t = f"{r.get('titulo','')} {r.get('resumen','')}"
    tec = any(re.search(p, t, re.I) for p in
              [r"retrieval[\s\-]?augmented", r"\bRAG\b", r"grounded\s+generation",
               r"knowledge[\s\-]grounded"])
    ctx = any(re.search(p, t, re.I) for p in
              [r"universit", r"higher\s+education", r"\bcampus\b", r"academic\s+institution",
               r"\bcollege\b", r"educaci[oó]n\s+superior", r"\bstudent"])
    inst = any(re.search(p, t, re.I) for p in
               [r"regulat", r"normativ", r"\bpolic(y|ies)\b", r"bylaw", r"statute",
                r"administrativ", r"enrol", r"admission", r"registrar", r"student\s+services",
                r"academic\s+services", r"student\s+affairs", r"procedure", r"scholarship",
                r"tuition", r"tr[aá]mite", r"reglament", r"advising"])
    return tec and ctx and inst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tope", type=int, default=600)
    args = ap.parse_args()

    crudos = []
    print(f"Ventana {ANIO_MIN}-{ANIO_MAX} · {len(VARIANTES)} variantes de consulta\n")
    for clave, consulta in VARIANTES:
        r = openalex(clave, consulta, args.tope)
        print(f"  {clave:<18} OpenAlex: {len(r):>4} registros")
        crudos += r
    for txt in ["retrieval augmented generation university policy chatbot evaluation",
                "retrieval augmented generation student services assistant higher education",
                "retrieval augmented generation academic regulations question answering"]:
        r = crossref(txt)
        print(f"  {'CR':<18} Crossref: {len(r):>4} · {txt[:44]}")
        crudos += r
        time.sleep(1.2)

    # deduplicación
    doi_v, tit_v, unicos, dup = set(), set(), [], 0
    for r in crudos:
        doi = (r.get("doi") or "").strip().lower()
        clave = (normalizar(r.get("titulo", ""))[:90], str(r.get("anio", "")))
        if doi and doi in doi_v:
            dup += 1; continue
        if not doi and clave[0] and clave in tit_v:
            dup += 1; continue
        if doi: doi_v.add(doi)
        if clave[0]: tit_v.add(clave)
        unicos.append(r)
    print(f"\nEn bruto: {len(crudos)} · duplicados: {dup} · únicos: {len(unicos)}")

    pertinentes = [r for r in unicos if pertinente(r)]
    print(f"Pertinentes por vocabulario: {len(pertinentes)}")

    dentro, fuera = [], []
    for r in pertinentes:
        doi = (r.get("doi") or "").strip().lower()
        pref = doi.split("/")[0] if "/" in doi else ""
        r["prefijo_doi"] = pref
        r["plataforma"] = PLATAFORMAS.get(pref, "")
        r["nivel"] = "1 · base del protocolo" if pref in NIVEL_1 else (
                     "2 · editorial mayor" if pref in NIVEL_2 else "")
        r["en_ieee"] = "sí" if pref == "10.1109" else "no"
        r["en_acm"] = "sí" if pref == "10.1145" else "no"
        r["en_springer"] = "sí" if pref in ("10.1007", "10.1057", "10.1186", "10.1140") else "no"
        r["en_sciencedirect"] = "sí" if pref == "10.1016" else "no"
        r["en_scopus"] = "verificar manualmente"
        r["en_wos"] = "verificar manualmente"
        r["issn_para_consulta"] = (r.get("issn") or "").split(";")[0].strip()
        tipo = (r.get("tipo") or "").lower()
        if r["plataforma"] and not any(x in tipo for x in TIPOS_EXCLUIDOS):
            dentro.append(r)
        else:
            r["motivo_descarte"] = ("tipo de documento: " + tipo) if r["plataforma"] \
                                   else "editorial sin plataforma indizada"
            fuera.append(r)

    print(f"\nAlojados en plataforma indizada: {len(dentro)}")
    print(f"Descartados: {len(fuera)}")
    conteo = {}
    for r in dentro:
        conteo[r["plataforma"]] = conteo.get(r["plataforma"], 0) + 1
    for k, v in sorted(conteo.items(), key=lambda x: -x[1]):
        n = "1" if any(p in NIVEL_1.values() for p in [k]) else "2"
        print(f"  {v:>4}  [nivel {n}]  {k}")

    hoy = date.today().isoformat()
    SALIDA.mkdir(parents=True, exist_ok=True)
    campos = ["id", "nivel", "plataforma", "anio", "titulo", "autores", "medio", "tipo",
              "editorial", "doi", "prefijo_doi", "issn_para_consulta", "en_ieee", "en_acm",
              "en_springer", "en_sciencedirect", "en_scopus", "en_wos", "citas",
              "fuente", "variante", "resumen"]
    destino = SALIDA / f"indizados_{hoy}.csv"
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for i, r in enumerate(sorted(dentro, key=lambda x: (x["nivel"], -int(x.get("anio") or 0),
                                                            x.get("titulo", ""))), 1):
            r["id"] = f"P{i:03d}"
            w.writerow(r)

    desc = SALIDA / f"descartados_no_indizados_{hoy}.csv"
    with desc.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos + ["motivo_descarte"], extrasaction="ignore")
        w.writeheader()
        for r in fuera:
            w.writerow(r)

    print(f"\nIncluidos:   {destino.name}")
    print(f"Descartados: {desc.name}")


if __name__ == "__main__":
    main()
