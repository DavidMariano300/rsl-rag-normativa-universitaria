# -*- coding: utf-8 -*-
"""Aplica la consulta booleana del protocolo sobre los registros de Crossref.

Por qué existe este script. La API de Crossref no admite operadores booleanos:
su parámetro de consulta es una búsqueda por relevancia difusa. Para que la
fuente complementaria quede sujeta al mismo criterio que las bases primarias,
la consulta booleana del protocolo se aplica aquí de forma posterior y
determinista sobre el título y el resumen de cada registro recuperado.

Esto es una operacionalización declarada, no un atajo: el conjunto en bruto se
conserva íntegro para auditoría y el script es reproducible. Debe citarse en el
apartado de métodos del manuscrito.

Uso:
    python filtrar_complementarias.py
"""
import csv
import re
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "01_busqueda" / "automatizada"

# Los tres bloques replican la cadena del protocolo. Un registro pasa el filtro
# solo si los tres aparecen en el título o en el resumen.
BLOQUE_A = [r"retrieval[\s\-]?augmented\s+generation", r"\bRAG\b",
            r"grounded\s+generation", r"retrieval[\s\-]?grounded"]
BLOQUE_B = [r"chatbot", r"conversational\s+(agent|assistant|ai|system)",
            r"virtual\s+assistant", r"question[\s\-]answering", r"dialogue\s+system",
            r"asistente\s+conversacional", r"agente\s+conversacional"]
BLOQUE_C = [r"universit(y|ies|ario|aria)", r"higher\s+education", r"\bcampus\b",
            r"academic\s+institution", r"educaci[oó]n\s+superior",
            r"\bstudent(s)?\b", r"estudiante"]
# El bloque D acota al dominio institucional: sin esto entran los sistemas de
# tutoría y de contenido instruccional, que el criterio E1 excluye.
BLOQUE_D = [r"regulat(ion|ory|ions)", r"normativ", r"\bpolic(y|ies)\b", r"bylaw",
            r"statute", r"administrativ", r"enrol", r"admission", r"registrar",
            r"student\s+services", r"procedure", r"tr[aá]mite", r"reglament"]


def coincide(texto, patrones):
    return next((p for p in patrones if re.search(p, texto, re.I)), None)


def main():
    fuentes = sorted(ENTRADA.glob("complementarias_*.csv"))
    if not fuentes:
        print("No hay archivo de búsqueda complementaria. Ejecuta buscar_complementarias.py")
        return
    origen = fuentes[-1]
    filas = list(csv.DictReader(origen.open(encoding="utf-8-sig")))
    print(f"Archivo: {origen.name}  ({len(filas)} registros en bruto)\n")

    pasan, descartados = [], []
    for r in filas:
        texto = f"{r.get('titulo','')} {r.get('resumen','')}"
        a, b = coincide(texto, BLOQUE_A), coincide(texto, BLOQUE_B)
        c, d = coincide(texto, BLOQUE_C), coincide(texto, BLOQUE_D)
        bloques = [x is not None for x in (a, b, c, d)]
        r["bloques_cumplidos"] = sum(bloques)
        r["bloque_A"], r["bloque_B"] = a or "", b or ""
        r["bloque_C"], r["bloque_D"] = c or "", d or ""
        (pasan if all(bloques) else descartados).append(r)

    print(f"Cumplen los cuatro bloques:  {len(pasan)}")
    print(f"No cumplen:                  {len(descartados)}")
    reparto = {}
    for r in descartados:
        reparto[r["bloques_cumplidos"]] = reparto.get(r["bloques_cumplidos"], 0) + 1
    for k in sorted(reparto, reverse=True):
        print(f"    con {k} de 4 bloques: {reparto[k]}")

    hoy = date.today().isoformat()
    campos = list(filas[0].keys()) + ["bloques_cumplidos", "bloque_A", "bloque_B",
                                      "bloque_C", "bloque_D"]
    campos = list(dict.fromkeys(campos))

    destino = ENTRADA / f"candidatos_filtrados_{hoy}.csv"
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in sorted(pasan, key=lambda x: (-int(x.get("anio") or 0), x.get("titulo", ""))):
            w.writerow(r)

    excluidos = ENTRADA / f"descartados_por_filtro_{hoy}.csv"
    with excluidos.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in descartados:
            w.writerow(r)

    bitacora = ENTRADA / f"filtro_booleano_{hoy}.txt"
    bitacora.write_text(
        "APLICACION POSTERIOR DE LA CONSULTA BOOLEANA SOBRE CROSSREF\n"
        f"Fecha: {hoy}\n"
        f"Archivo de entrada: {origen.name}\n\n"
        "Motivo: la API de Crossref no admite operadores booleanos. La consulta del\n"
        "protocolo se aplica de forma posterior y determinista sobre titulo y resumen.\n\n"
        f"Registros en bruto: {len(filas)}\n"
        f"Cumplen los cuatro bloques: {len(pasan)}\n"
        f"Descartados por el filtro: {len(descartados)}\n\n"
        "Bloques exigidos (deben aparecer los cuatro):\n"
        f"  A tecnologia:   {' | '.join(BLOQUE_A)}\n"
        f"  B conversacion: {' | '.join(BLOQUE_B)}\n"
        f"  C universidad:  {' | '.join(BLOQUE_C)}\n"
        f"  D institucion:  {' | '.join(BLOQUE_D)}\n\n"
        "El conjunto en bruto y el de descartados se conservan para auditoria.\n",
        encoding="utf-8")

    print(f"\nCandidatos:  {destino.name}")
    print(f"Descartados: {excluidos.name}")
    print(f"Bitácora:    {bitacora.name}")

    if pasan:
        print("\nAnticipo de los candidatos:")
        for r in sorted(pasan, key=lambda x: -int(x.get("anio") or 0))[:12]:
            print(f"  {r.get('anio')} · {(r.get('titulo') or '')[:82]}")


if __name__ == "__main__":
    main()
