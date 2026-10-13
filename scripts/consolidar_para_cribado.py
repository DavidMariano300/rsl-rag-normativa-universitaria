#!/usr/bin/env python3
"""
Consolida las salidas de la búsqueda automatizada en un único conjunto para
cribado, conforme al apartado 5.1 del protocolo v2: deduplicación por DOI
normalizado y, en su ausencia, por coincidencia de título y año.

Salida: 02_cribado/conjunto_para_cribado.csv
"""
import csv
import os
import re
import unicodedata
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUT = os.path.join(BASE, "01_busqueda", "automatizada")
OUT = os.path.join(BASE, "02_cribado")
os.makedirs(OUT, exist_ok=True)

FUENTES = [
    ("indizados_2026-09-04.csv", "busqueda automatizada, verificado en plataforma indizada"),
    ("eric_dblp_2026-09-04.csv", "ERIC y DBLP"),
    ("rastreo_citas_2026-09-08.csv", "snowballing hacia adelante y hacia atras"),
]

UMBRAL_TITULO = 0.93   # coincidencia difusa declarada en el protocolo


def norm_doi(d):
    d = (d or "").strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d


def norm_tit(t):
    t = unicodedata.normalize("NFKD", (t or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"[^a-z0-9]", "", t)


def similar(a, b):
    """Coincidencia difusa simple sobre cadenas ya normalizadas."""
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    corto, largo = (a, b) if len(a) <= len(b) else (b, a)
    if corto in largo:
        return len(corto) / len(largo)
    # coeficiente de Dice sobre bigramas
    bg = lambda s: Counter(s[i:i + 2] for i in range(len(s) - 1))
    A, B = bg(corto), bg(largo)
    inter = sum((A & B).values())
    tot = sum(A.values()) + sum(B.values())
    return 2 * inter / tot if tot else 0.0


registros, contados = [], Counter()
for archivo, etiqueta in FUENTES:
    ruta = os.path.join(AUT, archivo)
    if not os.path.exists(ruta):
        print(f"  aviso: no se encontro {archivo}")
        continue
    filas = list(csv.DictReader(open(ruta, encoding="utf-8-sig")))
    contados[etiqueta] = len(filas)
    for f in filas:
        registros.append({
            "origen": etiqueta,
            "archivo_origen": archivo,
            "id_origen": f.get("id", ""),
            "doi": norm_doi(f.get("doi")),
            "titulo": (f.get("titulo") or "").strip(),
            "autores": (f.get("autores") or "").strip(),
            "anio": (f.get("anio") or "").strip(),
            "medio": (f.get("medio") or "").strip(),
            "tipo": (f.get("tipo") or "").strip(),
            "editorial": (f.get("editorial") or "").strip(),
            "plataforma": (f.get("plataforma") or f.get("plataforma_verificada") or "").strip(),
            "nivel": (f.get("nivel") or "").strip(),
            "citas": (f.get("citas") or "").strip(),
            "sugerencia_previa": (f.get("sugerencia_cribado") or "").strip(),
            "resumen": re.sub(r"\s+", " ", (f.get("resumen") or "")).strip(),
        })

print("Registros por fuente:")
for k, v in contados.items():
    print(f"  {v:>4}  {k}")
print(f"  {'-'*4}")
print(f"  {len(registros):>4}  total en bruto\n")

# ------------------------------------------------------------------ dedup
unicos, por_doi, sin_doi = [], {}, []
dups = 0
for r in registros:
    if r["doi"]:
        if r["doi"] in por_doi:
            dups += 1
            prev = por_doi[r["doi"]]
            prev["origen"] = prev["origen"] + " + " + r["origen"] \
                if r["origen"] not in prev["origen"] else prev["origen"]
            if len(r["resumen"]) > len(prev["resumen"]):
                prev["resumen"] = r["resumen"]
            if not prev["plataforma"] and r["plataforma"]:
                prev["plataforma"] = r["plataforma"]
            continue
        por_doi[r["doi"]] = r
        unicos.append(r)
    else:
        sin_doi.append(r)

# los que no traen DOI se comparan por titulo y anio contra todo lo aceptado
for r in sin_doi:
    nt = norm_tit(r["titulo"])
    dup = None
    for u in unicos:
        if r["anio"] and u["anio"] and r["anio"] != u["anio"]:
            continue
        if similar(nt, norm_tit(u["titulo"])) >= UMBRAL_TITULO:
            dup = u
            break
    if dup:
        dups += 1
        if len(r["resumen"]) > len(dup["resumen"]):
            dup["resumen"] = r["resumen"]
    else:
        unicos.append(r)

print(f"Duplicados eliminados: {dups}")
print(f"Registros unicos para cribado: {len(unicos)}\n")

for i, r in enumerate(sorted(unicos, key=lambda x: (x["anio"], x["titulo"])), 1):
    r["id"] = f"C{i:03d}"

campos = ["id", "origen", "archivo_origen", "id_origen", "doi", "titulo", "autores",
          "anio", "medio", "tipo", "editorial", "plataforma", "nivel", "citas",
          "sugerencia_previa", "resumen"]
salida = os.path.join(OUT, "conjunto_para_cribado.csv")
with open(salida, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=campos)
    w.writeheader()
    for r in sorted(unicos, key=lambda x: x["id"]):
        w.writerow({k: r.get(k, "") for k in campos})

with open(os.path.join(OUT, "bitacora_consolidacion.txt"), "w", encoding="utf-8") as f:
    f.write("CONSOLIDACION PARA CRIBADO - protocolo v2, apartado 5.1\n")
    f.write(f"Umbral de coincidencia difusa de titulo: {UMBRAL_TITULO}\n\n")
    for k, v in contados.items():
        f.write(f"{v:>4}  {k}\n")
    f.write(f"{len(registros):>4}  total en bruto\n")
    f.write(f"{dups:>4}  duplicados eliminados\n")
    f.write(f"{len(unicos):>4}  unicos para cribado\n\n")
    f.write("PENDIENTE: exportaciones manuales de Scopus, WoS, IEEE Xplore, ACM y\n")
    f.write("SpringerLink, bloqueadas por credenciales institucionales. Las cifras\n")
    f.write("de este conjunto son PROVISIONALES hasta incorporarlas.\n")

print(f"Escrito: {salida}")
print(Counter(r["anio"] for r in unicos).most_common())
print(Counter(r["plataforma"] for r in unicos).most_common(8))
