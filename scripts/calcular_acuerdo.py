# -*- coding: utf-8 -*-
"""Kappa de Cohen sobre las decisiones de cribado de los dos revisores.

Compara los dos formularios llenos, calcula el acuerdo observado, el acuerdo
esperado por azar y el coeficiente kappa, y produce la lista de discrepancias
que hay que resolver en sesión conjunta.

Uso:
    python calcular_acuerdo.py
    python calcular_acuerdo.py --r1 cribado_revisor1_2026-09-05.csv --r2 ...
"""
import argparse
import csv
from collections import Counter
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CRIBADO = RAIZ / "02_cribado"
UMBRAL = 0.70

# Landis y Koch (1977)
def interpretar(k):
    if k < 0.00: return "sin acuerdo"
    if k <= 0.20: return "leve"
    if k <= 0.40: return "aceptable"
    if k <= 0.60: return "moderado"
    if k <= 0.80: return "sustancial"
    return "casi perfecto"


def leer(ruta):
    with ruta.open(encoding="utf-8-sig") as f:
        return {fila["id"]: fila for fila in csv.DictReader(f)}


def kappa(pares):
    """Kappa de Cohen sobre una lista de pares (decision1, decision2)."""
    n = len(pares)
    if n == 0:
        return None, None, None
    acuerdos = sum(1 for a, b in pares if a == b)
    po = acuerdos / n
    c1, c2 = Counter(a for a, _ in pares), Counter(b for _, b in pares)
    pe = sum((c1[cat] / n) * (c2[cat] / n) for cat in set(c1) | set(c2))
    if pe == 1.0:
        return po, pe, 1.0
    return po, pe, (po - pe) / (1 - pe)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r1"); ap.add_argument("--r2")
    args = ap.parse_args()

    if args.r1 and args.r2:
        f1, f2 = CRIBADO / args.r1, CRIBADO / args.r2
    else:
        c1 = sorted(CRIBADO.glob("cribado_revisor1_*.csv"))
        c2 = sorted(CRIBADO.glob("cribado_revisor2_*.csv"))
        if not c1 or not c2:
            print("Faltan los formularios de cribado en 02_cribado.")
            return
        f1, f2 = c1[-1], c2[-1]

    r1, r2 = leer(f1), leer(f2)
    comunes = sorted(set(r1) & set(r2))
    pares, sin_llenar = [], 0
    for i in comunes:
        d1 = (r1[i].get("decision") or "").strip().lower()
        d2 = (r2[i].get("decision") or "").strip().lower()
        if not d1 or not d2:
            sin_llenar += 1
            continue
        pares.append((d1, d2))

    print(f"Formularios: {f1.name}  y  {f2.name}")
    print(f"Registros comunes: {len(comunes)} · sin decisión en algún revisor: {sin_llenar}")
    if not pares:
        print("\nAún no hay decisiones registradas. Llena la columna 'decision' en ambos.")
        return

    po, pe, k = kappa(pares)
    print(f"\nRegistros comparados:   {len(pares)}")
    print(f"Acuerdo observado (Po): {po:.4f}")
    print(f"Acuerdo esperado  (Pe): {pe:.4f}")
    print(f"Kappa de Cohen:         {k:.4f}   ({interpretar(k)})")
    print(f"Umbral del protocolo:   {UMBRAL:.2f}   ->  " +
          ("CUMPLE" if k >= UMBRAL else "NO CUMPLE, hay que recalibrar y repetir"))

    print("\nMatriz de confusión")
    cats = sorted({c for p in pares for c in p})
    print("           " + "".join(f"{c:>10}" for c in cats) + "     total R1")
    for a in cats:
        fila = [sum(1 for x, y in pares if x == a and y == b) for b in cats]
        print(f"{a:>10} " + "".join(f"{v:>10}" for v in fila) + f"{sum(fila):>13}")
    print("  total R2 " + "".join(
        f"{sum(1 for _, y in pares if y == b):>10}" for b in cats))

    discrepancias = [i for i in comunes
                     if (r1[i].get('decision') or '').strip().lower()
                     != (r2[i].get('decision') or '').strip().lower()
                     and r1[i].get('decision') and r2[i].get('decision')]
    print(f"\nDiscrepancias a resolver: {len(discrepancias)}")

    hoy = date.today().isoformat()
    destino = CRIBADO / f"discrepancias_{hoy}.csv"
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "titulo", "anio", "doi", "decision_r1", "criterio_r1",
                    "decision_r2", "criterio_r2", "decision_consenso", "justificacion"])
        for i in discrepancias:
            w.writerow([i, r1[i].get("titulo", ""), r1[i].get("anio", ""), r1[i].get("doi", ""),
                        r1[i].get("decision", ""), r1[i].get("criterio", ""),
                        r2[i].get("decision", ""), r2[i].get("criterio", ""), "", ""])
    print(f"Lista de discrepancias en {destino.name}")

    reporte = CRIBADO / f"acuerdo_{hoy}.txt"
    reporte.write_text(
        f"MEDICION DE ACUERDO ENTRE REVISORES\n"
        f"Fecha: {hoy}\n"
        f"Formularios: {f1.name} / {f2.name}\n"
        f"Registros comparados: {len(pares)}\n"
        f"Acuerdo observado: {po:.4f}\n"
        f"Acuerdo esperado por azar: {pe:.4f}\n"
        f"Kappa de Cohen: {k:.4f} ({interpretar(k)}, Landis y Koch 1977)\n"
        f"Umbral del protocolo: {UMBRAL:.2f} -> "
        f"{'cumple' if k >= UMBRAL else 'no cumple'}\n"
        f"Discrepancias: {len(discrepancias)}\n", encoding="utf-8")
    print(f"Reporte en {reporte.name}")


if __name__ == "__main__":
    main()
