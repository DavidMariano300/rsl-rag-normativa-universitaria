# -*- coding: utf-8 -*-
"""Rastreo de citas hacia atrás y hacia adelante sobre los estudios ya incluidos.

Es la técnica de bola de nieve que exige la guía de Kitchenham y que PRISMA 2020
pide reportar por separado de la búsqueda en bases. Se ejecuta sobre los estudios
que ya pasaron el filtro de plataforma indizada.

Hacia atrás: las referencias que citan esos estudios en su bibliografía.
Hacia adelante: los trabajos posteriores que los citan a ellos.

Todo lo recuperado pasa por los mismos filtros que la búsqueda principal, es
decir pertinencia por vocabulario y alojamiento en plataforma indizada.

Uso:
    python rastreo_de_citas.py
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

NIVEL_1 = {"10.1109": "IEEE Xplore", "10.1145": "ACM Digital Library",
           "10.1007": "SpringerLink", "10.1057": "SpringerLink", "10.1186": "SpringerLink",
           "10.1140": "SpringerLink", "10.1016": "ScienceDirect (Elsevier)"}
NIVEL_2 = {"10.1002": "Wiley Online Library", "10.3390": "MDPI",
           "10.1080": "Taylor & Francis", "10.1088": "IOP Publishing",
           "10.1177": "SAGE Journals", "10.1093": "Oxford Academic",
           "10.1017": "Cambridge Core", "10.1108": "Emerald Insight",
           "10.3389": "Frontiers", "10.1371": "PLOS", "10.18653": "ACL Anthology",
           "10.1609": "AAAI", "10.24963": "IJCAI", "10.5220": "SciTePress",
           "10.1049": "IET Digital Library", "10.1111": "Wiley Online Library"}
PLATAFORMAS = {**NIVEL_1, **NIVEL_2}
TIPOS_FUERA = {"preprint", "dataset", "dissertation", "peer-review", "editorial",
               "erratum", "paratext", "retraction", "grant"}


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
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception:
            if i == intentos - 1:
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


def a_registro(it, procedencia, semilla):
    loc = it.get("primary_location") or {}
    src = loc.get("source") or {}
    return {
        "fuente": procedencia, "semilla": semilla,
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
    }


def pertinente(r):
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
                r"tuition", r"tr[aá]mite", r"reglament", r"advising", r"handbook"])
    return tec and ctx and inst


def main():
    origen = sorted(SALIDA.glob("indizados_*.csv"))
    if not origen:
        print("Falta indizados_*.csv. Corre antes busqueda_ampliada.py")
        return
    semillas = list(csv.DictReader(origen[-1].open(encoding="utf-8-sig")))
    con_doi = [s for s in semillas if (s.get("doi") or "").strip()]
    print(f"Semillas: {len(semillas)} estudios incluidos, {len(con_doi)} con identificador\n")

    ya = {(s.get("doi") or "").strip().lower() for s in semillas}
    ids_atras, recuperados = set(), []

    print("Rastreo hacia atrás, bibliografías de las semillas")
    for i, s in enumerate(con_doi, 1):
        d = pedir(f"https://api.openalex.org/works/doi:{s['doi']}?mailto={CORREO}")
        if d:
            for ref in (d.get("referenced_works") or []):
                ids_atras.add(ref.rsplit("/", 1)[-1])
        if i % 12 == 0:
            print(f"   {i}/{len(con_doi)} semillas · {len(ids_atras)} referencias acumuladas")
        time.sleep(0.16)
    print(f"   referencias únicas por resolver: {len(ids_atras)}")

    ids = [x for x in ids_atras]
    for k in range(0, len(ids), 50):
        lote = "|".join(ids[k:k + 50])
        d = pedir(f"https://api.openalex.org/works?filter=openalex_id:{lote},"
                  f"publication_year:{ANIO_MIN}-{ANIO_MAX}&per-page=50&mailto={CORREO}")
        if d:
            for it in d.get("results", []):
                recuperados.append(a_registro(it, "rastreo hacia atrás", ""))
        time.sleep(0.3)
    print(f"   dentro de la ventana temporal: {len(recuperados)}")

    print("\nRastreo hacia adelante, trabajos que citan a las semillas")
    antes = len(recuperados)
    for i, s in enumerate(con_doi, 1):
        d = pedir(f"https://api.openalex.org/works/doi:{s['doi']}?select=id&mailto={CORREO}")
        if not d:
            continue
        oid = (d.get("id") or "").rsplit("/", 1)[-1]
        if not oid:
            continue
        c = pedir(f"https://api.openalex.org/works?filter=cites:{oid},"
                  f"publication_year:{ANIO_MIN}-{ANIO_MAX}&per-page=100&mailto={CORREO}")
        if c:
            for it in c.get("results", []):
                recuperados.append(a_registro(it, "rastreo hacia adelante", s.get("id", "")))
        if i % 12 == 0:
            print(f"   {i}/{len(con_doi)} semillas · {len(recuperados) - antes} citantes acumulados")
        time.sleep(0.22)
    print(f"   citantes recuperados: {len(recuperados) - antes}")

    vistos, unicos, dup = set(ya), [], 0
    for r in recuperados:
        doi = (r.get("doi") or "").strip().lower()
        if not doi or doi in vistos:
            dup += 1
            continue
        vistos.add(doi)
        unicos.append(r)
    print(f"\nRecuperado en bruto: {len(recuperados)} · repetidos o ya incluidos: {dup}")
    print(f"Nuevos únicos: {len(unicos)}")

    pert = [r for r in unicos if pertinente(r)]
    print(f"Pertinentes por vocabulario: {len(pert)}")

    dentro = []
    for r in pert:
        pref = r["doi"].split("/")[0] if "/" in r["doi"] else ""
        r["prefijo_doi"] = pref
        r["plataforma"] = PLATAFORMAS.get(pref, "")
        r["nivel"] = ("1 · base del protocolo" if pref in NIVEL_1
                      else "2 · editorial mayor" if pref in NIVEL_2 else "")
        r["en_scopus"] = "verificar manualmente"
        r["en_wos"] = "verificar manualmente"
        r["issn_para_consulta"] = (r.get("issn") or "").split(";")[0].strip()
        if r["plataforma"] and (r.get("tipo") or "").lower() not in TIPOS_FUERA:
            dentro.append(r)
    print(f"En plataforma indizada: {len(dentro)}")

    conteo = {}
    for r in dentro:
        conteo[r["plataforma"]] = conteo.get(r["plataforma"], 0) + 1
    for k, v in sorted(conteo.items(), key=lambda x: -x[1]):
        print(f"   {v:>4}  {k}")
    por_via = {}
    for r in dentro:
        por_via[r["fuente"]] = por_via.get(r["fuente"], 0) + 1
    print("   por vía:", por_via)

    hoy = date.today().isoformat()
    destino = SALIDA / f"rastreo_citas_{hoy}.csv"
    campos = ["id", "fuente", "nivel", "plataforma", "anio", "titulo", "autores", "medio",
              "tipo", "editorial", "doi", "prefijo_doi", "issn_para_consulta",
              "en_scopus", "en_wos", "citas", "semilla", "resumen"]
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for i, r in enumerate(sorted(dentro, key=lambda x: (x["nivel"],
                                                            -int(x.get("anio") or 0))), 1):
            r["id"] = f"R{i:03d}"
            w.writerow(r)
    print(f"\nGuardado en {destino.name}")
    if dentro:
        print("\nAnticipo:")
        for r in dentro[:15]:
            print(f"   {r['anio']} {r['plataforma'][:20]:<22} {r['titulo'][:64]}")


if __name__ == "__main__":
    main()
