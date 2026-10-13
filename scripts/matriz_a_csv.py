# -*- coding: utf-8 -*-
"""Convierte las fichas de extracción (JSON) en la matriz CSV y en el
formulario de calidad QA.

Las fichas se llenan a mano leyendo el texto completo de cada estudio. Este
guion solo las ordena y las vuelca en los dos archivos que acompañan al
manuscrito.

Uso:
    python scripts/matriz_a_csv.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FICHAS = RAIZ / "03_extraccion" / "fichas_extraccion.json"
MATRIZ = RAIZ / "03_extraccion" / "matriz_extraccion.csv"
CALIDAD = RAIZ / "04_calidad" / "formulario_calidad_QA.csv"
BAJO_UMBRAL = RAIZ / "04_calidad" / "estudios_bajo_umbral.csv"

UMBRAL = 4.0

COLUMNAS = [
    # Identificación
    "id", "autores", "anio", "titulo", "tipo_publicacion", "medio", "doi",
    # Contexto
    "pais", "tipo_institucion", "tipo_usuario",
    # Corpus
    "corpus_naturaleza", "corpus_volumen", "corpus_idioma", "corpus_preparacion",
    # Segmentación
    "segmentacion_estrategia", "segmentacion_justificacion",
    # Recuperación
    "recuperacion_representacion", "recuperacion_tipo_busqueda",
    "recuperacion_reordenamiento", "recuperacion_k",
    # Generación
    "generacion_modelo", "generacion_tamano", "generacion_despliegue",
    # Evaluación
    "evaluacion_niveles", "evaluacion_metricas", "evaluacion_instrumento",
    "evaluacion_tamano_prueba",
    # Resultados
    "resultados",
    # Comparación
    "comparacion_linea_base",
    # Trazabilidad
    "trazabilidad_cita_fuente", "trazabilidad_verificable",
    # Reproducibilidad
    "reproducibilidad",
    # Limitaciones
    "limitaciones_declaradas",
    # Control
    "estado_extraccion",
]

QA = ["QA1", "QA2", "QA3", "QA4", "QA5", "QA6", "QA7"]

COLUMNAS_QA = (["id", "titulo", "autores", "anio", "medio", "doi"] +
               [f"{c}_{n}" for c, n in zip(QA, [
                   "objetivos", "corpus_replicable", "arquitectura_reproducible",
                   "evaluacion_con_metricas", "linea_base", "limitaciones",
                   "datos_o_codigo"])] +
               ["total", "supera_umbral", "observaciones_calidad"])


EXCLUIDOS = RAIZ / "03_extraccion" / "excluidos_en_texto_completo.csv"


def main() -> None:
    todas = json.loads(FICHAS.read_text(encoding="utf-8"))

    # Estudios que superaron el cribado por título y resumen pero que al leer el
    # texto completo resultaron no cumplir un criterio. Salen de la síntesis y se
    # reportan aparte, como exige PRISMA.
    fuera = {k: v for k, v in todas.items() if v.get("excluido_texto_completo")}
    fichas = {k: v for k, v in todas.items() if k not in fuera}
    claves = sorted(fichas, key=lambda k: int(k[1:]))

    with EXCLUIDOS.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "autores", "anio", "titulo", "medio", "doi",
                    "criterio", "motivo"])
        for k in sorted(fuera, key=lambda k: int(k[1:])):
            d = fuera[k]
            w.writerow([k, d["autores"], d["anio"], d["titulo"], d["medio"],
                        d["doi"], d["excluido_texto_completo"],
                        d["motivo_exclusion"]])

    with MATRIZ.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS, extrasaction="ignore")
        w.writeheader()
        for k in claves:
            w.writerow({**{c: "" for c in COLUMNAS}, "id": k, **fichas[k]})

    bajo = []
    with CALIDAD.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(COLUMNAS_QA)
        for k in claves:
            d = fichas[k]
            notas = [float(d["calidad"][c]) for c in QA]
            total = round(sum(notas), 1)
            supera = "si" if total >= UMBRAL else "no"
            fila = ([k, d["titulo"], d["autores"], d["anio"], d["medio"], d["doi"]] +
                    notas + [total, supera, d.get("observaciones_calidad", "")])
            w.writerow(fila)
            if total < UMBRAL:
                bajo.append([k, d["autores"], d["anio"], total,
                             d.get("observaciones_calidad", "")])

    with BAJO_UMBRAL.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "autores", "anio", "total_QA", "motivo"])
        w.writerows(bajo)

    print(f"Fichas en sintesis: {len(claves)}")
    print(f"Excluidos al leer texto completo: {len(fuera)} -> {sorted(fuera)}")
    print(f"Por debajo del umbral ({UMBRAL}): {len(bajo)} -> {[b[0] for b in bajo]}")
    print(f"  {MATRIZ.relative_to(RAIZ)}")
    print(f"  {CALIDAD.relative_to(RAIZ)}")
    print(f"  {BAJO_UMBRAL.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
