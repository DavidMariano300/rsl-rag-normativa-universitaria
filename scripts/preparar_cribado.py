# -*- coding: utf-8 -*-
"""Prepara los formularios de cribado ciego para los dos revisores.

Lee todos los registros recuperados, los deduplica entre fuentes y genera un
formulario por revisor con el mismo orden aleatorio pero sin la decisión del
otro. El orden es aleatorio con semilla fija, para que sea reproducible.

Uso:
    python preparar_cribado.py --revisores "E. Mariano" "Segundo revisor"
"""
import argparse
import csv
import random
import re
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADAS = [RAIZ / "01_busqueda" / "automatizada",
            RAIZ / "01_busqueda" / "exportaciones_manuales"]
SALIDA = RAIZ / "02_cribado"
SEMILLA = 20260901

CRITERIOS = [
    ("I1", "Sistema de acceso a información anclado en recuperación"),
    ("I2", "Contexto de educación superior"),
    ("I3", "Información normativa, administrativa o procedimental"),
    ("I4", "Evaluación empírica con al menos una métrica"),
    ("I5", "Publicado entre 2022 y 2026"),
    ("I6", "Revisión por pares"),
    ("I7", "Texto completo en inglés o español"),
    ("E1", "Contenido instruccional o tutoría, no información institucional"),
    ("E2", "Sin componente de recuperación sobre corpus propio"),
    ("E3", "Estudio secundario"),
    ("E4", "Literatura gris"),
    ("E5", "Dominio distinto al universitario"),
    ("E6", "Sin evaluación empírica"),
    ("E7", "Duplicado o versión preliminar de un trabajo incluido"),
]


def normalizar(t):
    if not t:
        return ""
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", t.lower()).strip()


def cargar():
    registros = []
    for carpeta in ENTRADAS:
        if not carpeta.exists():
            continue
        for archivo in sorted(carpeta.glob("*.csv")):
            with archivo.open(encoding="utf-8-sig") as f:
                for fila in csv.DictReader(f):
                    fila["archivo_origen"] = archivo.name
                    registros.append(fila)
    return registros


def deduplicar(regs):
    doi_vistos, tit_vistos, unicos, dup = set(), set(), [], []
    for r in regs:
        doi = (r.get("doi") or "").strip().lower()
        clave = (normalizar(r.get("titulo", ""))[:90], str(r.get("anio", "")))
        if doi and doi in doi_vistos:
            dup.append(r); continue
        if not doi and clave[0] and clave in tit_vistos:
            dup.append(r); continue
        if doi:
            doi_vistos.add(doi)
        if clave[0]:
            tit_vistos.add(clave)
        unicos.append(r)
    return unicos, dup


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--revisores", nargs=2, default=["Revisor A", "Revisor B"])
    args = ap.parse_args()

    regs = cargar()
    if not regs:
        print("No hay registros. Ejecuta primero buscar_complementarias.py y coloca")
        print("las exportaciones de Scopus, WoS, IEEE, ACM y Springer convertidas a CSV")
        print(f"en {ENTRADAS[1]}")
        return

    unicos, dup = deduplicar(regs)
    random.Random(SEMILLA).shuffle(unicos)
    SALIDA.mkdir(parents=True, exist_ok=True)
    hoy = date.today().isoformat()

    campos = ["orden", "id", "titulo", "autores", "anio", "medio", "fuente", "doi",
              "resumen", "decision", "criterio", "nota"]
    for n, revisor in enumerate(args.revisores, 1):
        destino = SALIDA / f"cribado_revisor{n}_{hoy}.csv"
        with destino.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            for i, r in enumerate(unicos, 1):
                w.writerow({
                    "orden": i,
                    "id": r.get("id") or f"R{i:04d}",
                    "titulo": r.get("titulo", ""),
                    "autores": r.get("autores", ""),
                    "anio": r.get("anio", ""),
                    "medio": r.get("medio", ""),
                    "fuente": r.get("fuente", ""),
                    "doi": r.get("doi", ""),
                    "resumen": r.get("resumen", "")[:1200],
                    "decision": "",       # incluir / excluir / dudoso
                    "criterio": "",       # clave del criterio aplicado
                    "nota": "",
                })
        print(f"Formulario de {revisor}: {destino.name}  ({len(unicos)} registros)")

    guia = SALIDA / "GUIA_de_cribado.md"
    lineas = ["# Guía de cribado por título y resumen", "",
              f"Registros a cribar: **{len(unicos)}** · Duplicados eliminados: **{len(dup)}**",
              f"Semilla de aleatorización: `{SEMILLA}` (el orden es reproducible)", "",
              "## Cómo llenar el formulario", "",
              "En la columna `decision` escribe `incluir`, `excluir` o `dudoso`.",
              "En la columna `criterio` escribe la clave del criterio que sostiene la decisión.",
              "Ante la duda, marca `dudoso` y pasa al siguiente. La duda se resuelve a texto completo.",
              "", "**No consultes el formulario del otro revisor hasta calcular el acuerdo.**",
              "", "## Criterios", "", "| Clave | Criterio |", "|---|---|"]
    lineas += [f"| {c} | {d} |" for c, d in CRITERIOS]
    lineas += ["", "## Después del cribado", "",
               "Ejecuta `python calcular_acuerdo.py` para obtener el kappa de Cohen.",
               "Si el valor queda por debajo de 0.70, recalibren los criterios sobre una",
               "muestra piloto y repitan el cribado antes de continuar.", ""]
    guia.write_text("\n".join(lineas), encoding="utf-8")
    print(f"Guía: {guia.name}")

    if dup:
        d = SALIDA / f"duplicados_eliminados_{hoy}.csv"
        with d.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["titulo", "anio", "doi", "fuente", "archivo_origen"])
            w.writeheader()
            for r in dup:
                w.writerow({k: r.get(k, "") for k in
                            ["titulo", "anio", "doi", "fuente", "archivo_origen"]})
        print(f"Duplicados registrados en {d.name}: {len(dup)}")


if __name__ == "__main__":
    main()
