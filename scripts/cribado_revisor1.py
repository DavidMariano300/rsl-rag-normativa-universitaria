#!/usr/bin/env python3
"""
Cribado por título y resumen, revisor 1, conforme al apartado 5.2 del protocolo v2.

Cada registro se marca como incluir o excluir con la clave del criterio aplicado.
Se usan claves I* cuando el registro incumple un criterio de inclusión y claves E*
cuando incurre en un criterio de exclusión explícito.

IMPORTANTE: el protocolo exige DOS revisores independientes y kappa de Cohen >= 0.70.
Este script produce únicamente las decisiones del revisor 1 y genera el formulario
ciego para el revisor 2. El kappa NO puede calcularse hasta que exista la segunda
evaluación; el script calcular_acuerdo.py queda listo para ejecutarse entonces.
"""
import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRIB = os.path.join(BASE, "02_cribado")

# decision, clave de criterio, nota
D = {
 "C001": ("incluir", "I1-I8", "Admisión, corpus institucional, evaluación reportada"),
 "C002": ("incluir", "I1-I8", "Servicios de apoyo universitario sobre documentos institucionales"),
 "C003": ("incluir", "I1-I8", "Admisión con filtro de intención más recuperación"),
 "C004": ("excluir", "E1", "MoodleBot en aula: apoyo al aprendizaje, no información institucional"),
 "C005": ("excluir", "E4", "DBLP Informal and Other Publications: literatura gris"),
 "C006": ("incluir", "I1-I8", "Políticas, procedimientos y lineamientos de la universidad"),
 "C007": ("excluir", "E1", "Educación en anatomía: contenido instruccional"),
 "C008": ("excluir", "I3", "Corpus curado de Reddit, no documentación institucional"),
 "C009": ("excluir", "E6", "Estudio de percepción docente, no evalúa un sistema"),
 "C010": ("incluir", "I1-I8", "Preguntas de admisión sobre datos institucionales"),
 "C011": ("incluir", "I1-I8", "Admisión y consultas generales con base vectorial institucional"),
 "C012": ("excluir", "E1", "Apoyo al razonamiento del estudiante: instruccional"),
 "C013": ("excluir", "E4", "DBLP Informal: preimpresión sin revisión por pares"),
 "C014": ("excluir", "E1", "Tutoría de matemáticas en secundaria: instruccional y fuera de ES"),
 "C015": ("excluir", "I3", "Participación en TREC: recuperación genérica, no información institucional"),
 "C016": ("incluir", "I1-I8", "Programas, colegiaturas y condiciones de egreso"),
 "C017": ("incluir", "I1-I8", "Preguntas sobre políticas con RAG y LangChain"),
 "C018": ("excluir", "E1", "Resolución del examen de admisión ENEM: instruccional"),
 "C019": ("excluir", "E1", "Aprendizaje colaborativo: instruccional"),
 "C020": ("excluir", "E3", "Revisión de literatura, estudio secundario"),
 "C021": ("excluir", "E6", "Análisis teórico sin sistema ni evaluación empírica"),
 "C022": ("excluir", "E1", "Corpus de materiales de curso: instruccional"),
 "C023": ("excluir", "I2", "Población de deserción escolar básica, no educación superior"),
 "C024": ("incluir", "I1-I8", "Consultas de admisión con experimento controlado"),
 "C025": ("excluir", "E1", "Curso en línea de R: instruccional"),
 "C026": ("incluir", "I1-I8", "Orientación de admisión con beneficio medible"),
 "C027": ("excluir", "E2", "Ajuste fino sin recuperación; el propio texto se contrasta con RAG"),
 "C028": ("incluir", "I1-I8", "Tutoría académica sobre planes de estudio institucionales"),
 "C029": ("excluir", "E5", "Dominio clínico: cardio-oncología"),
 "C030": ("excluir", "E1", "Recursos educativos abiertos: instruccional"),
 "C031": ("excluir", "E5", "Dominio jurisdiccional: legislación argelina"),
 "C032": ("excluir", "E7", "Versión en ERIC del registro C004"),
 "C033": ("incluir", "I1-I8", "Reglamento de disciplina estudiantil, normativa institucional"),
 "C034": ("excluir", "E3", "Síntesis de paradigmas, estudio secundario"),
 "C035": ("incluir", "I1-I8", "Documentos de política institucional con grafo de conocimiento"),
 "C036": ("excluir", "E1", "Historia en educación básica: instruccional y fuera de ES"),
 "C037": ("excluir", "E1", "Sistema de enseñanza multiagente; el componente de política es accesorio"),
 "C038": ("excluir", "E1", "Compañero de aprendizaje: instruccional"),
 "C039": ("incluir", "I1-I8", "Compara configuraciones de pipeline para admisión internacional"),
 "C040": ("incluir", "I1-I8", "Planeación curricular contra lineamientos institucionales"),
 "C041": ("excluir", "E1", "Tutor de estadística: instruccional"),
 "C042": ("excluir", "E1", "Evaluación formativa con retroalimentación: instruccional"),
 "C043": ("incluir", "I1-I8", "Horarios, inscripción y reglamentos académicos"),
 "C044": ("excluir", "E1", "Calificación de respuestas cortas: instruccional"),
 "C045": ("excluir", "I3", "Análisis cuantitativo para investigación, no información institucional"),
 "C046": ("excluir", "E1", "Autorregulación del aprendizaje: instruccional"),
 "C047": ("excluir", "E1", "Apoyo a la docencia: instruccional"),
 "C048": ("excluir", "E1", "Retroalimentación a estudiantes: instruccional"),
 "C049": ("excluir", "E1", "Aprendizaje electrónico: instruccional"),
 "C050": ("excluir", "E1", "Asistentes de enseñanza en aula invertida: instruccional"),
 "C051": ("incluir", "I1-I8", "Soporte informativo universitario con RAG"),
 "C052": ("excluir", "E1", "Chatbot de curso en línea: instruccional"),
 "C053": ("excluir", "E1", "Generación de objetos de aprendizaje: instruccional"),
 "C054": ("excluir", "E1", "Tutoría inteligente adaptativa: instruccional"),
 "C055": ("incluir", "I1-I8", "Temas administrativos, legislativos y de interés público"),
 "C056": ("incluir", "I1-I8", "Planes, becas y procedimientos; despliegue local"),
 "C057": ("excluir", "E1", "Agente pedagógico en STEM+C: instruccional"),
 "C058": ("incluir", "I1-I8", "Documentos y reglamentos universitarios; verificar en texto completo"),
 "C059": ("excluir", "E1", "Formación en relaciones públicas: instruccional"),
 "C060": ("excluir", "I3", "Portal nacional de becas, corpus no institucional"),
 "C061": ("excluir", "E5", "Simulador de logística marítima: dominio industrial"),
 "C062": ("excluir", "E3", "Revisión sistemática, estudio secundario"),
 "C063": ("incluir", "I1-I8", "Asistente multimodal para comunidad universitaria"),
 "C064": ("incluir", "I1-I8", "RAG híbrido unificado para admisión, caso HCMUT"),
 "C065": ("excluir", "E1", "Automatización de pruebas de conocimiento: instruccional"),
 "C066": ("excluir", "E1", "Generación de problemas de matemáticas: instruccional"),
 "C067": ("incluir", "I1-I8", "Interpretación de políticas, comportamiento de rechazo y gobernanza"),
 "C068": ("incluir", "I1-I8", "Asistente de admisión con enrutamiento por grafo"),
 "C069": ("excluir", "E5", "Consultoría en cálculo de resistencia: dominio de ingeniería aplicada"),
 "C070": ("excluir", "I3", "Mentoría y orientación profesional, no información normativa"),
 "C071": ("excluir", "E1", "Asistente de curso en aula: instruccional"),
 "C072": ("excluir", "E1", "Evaluación de respuestas en secundaria: instruccional y fuera de ES"),
 "C073": ("incluir", "I1-I8", "Despliegue real de RAG multiagente en admisión"),
 "C074": ("excluir", "E4", "DBLP Informal: literatura gris"),
 "C075": ("excluir", "E6", "Patrones arquitectónicos sin evaluación empírica reportada"),
 "C076": ("incluir", "I1-I8", "Tutoría académica con datos curriculares normalizados"),
 "C077": ("excluir", "E5", "Apoyo a personas autistas: dominio de salud"),
 "C078": ("incluir", "I1-I8", "Información académica distribuida en portales departamentales"),
 "C079": ("excluir", "E1", "Curso de cultura emprendedora: instruccional"),
 "C080": ("excluir", "E1", "Aprendizaje autodirigido de Python: instruccional"),
 "C081": ("excluir", "I3", "Acceso a datos de evaluación a gran escala, no información institucional"),
 "C082": ("excluir", "E1", "Chatbot específico de curso: instruccional"),
 "C083": ("excluir", "I3", "Tarea compartida de recuperación, no información institucional"),
 "C084": ("excluir", "E1", "Diseño didáctico en primaria: instruccional y fuera de ES"),
 "C085": ("incluir", "I1-I8", "Evaluación sin etiquetas de un chatbot de política universitaria"),
 "C086": ("excluir", "I3", "Optimización de modelos para acceso educativo, no información institucional"),
 "C087": ("excluir", "E8", "Sin plataforma de indización verificable en el registro"),
 "C088": ("incluir", "I1-I8", "Comparación contra LLM comercial en administración universitaria"),
 "C089": ("incluir", "I1-I8", "Admisión, plan de estudios, cuotas e instalaciones"),
 "C090": ("excluir", "I3", "Colocación laboral y reclutamiento, no información normativa"),
}

rows = list(csv.DictReader(open(os.path.join(CRIB, "conjunto_para_cribado.csv"),
                                encoding="utf-8-sig")))
faltan = [r["id"] for r in rows if r["id"] not in D]
if faltan:
    raise SystemExit(f"Registros sin adjudicar: {faltan}")

for r in rows:
    dec, clave, nota = D[r["id"]]
    r["decision_revisor1"] = dec
    r["criterio_revisor1"] = clave
    r["nota_revisor1"] = nota

campos = list(rows[0].keys())
with open(os.path.join(CRIB, "decisiones_revisor1.csv"), "w", newline="",
          encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=campos)
    w.writeheader()
    w.writerows(rows)

# formulario ciego para el segundo revisor: sin la decisión del revisor 1
ciego = ["id", "titulo", "autores", "anio", "medio", "tipo", "plataforma", "doi",
         "resumen", "decision_revisor2", "criterio_revisor2", "nota_revisor2"]
with open(os.path.join(CRIB, "formulario_revisor2_ciego.csv"), "w", newline="",
          encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=ciego)
    w.writeheader()
    for r in rows:
        fila = {k: r.get(k, "") for k in ciego}
        fila["decision_revisor2"] = ""
        fila["criterio_revisor2"] = ""
        fila["nota_revisor2"] = ""
        w.writerow(fila)

incluidos = [r for r in rows if r["decision_revisor1"] == "incluir"]
with open(os.path.join(CRIB, "incluidos_tras_cribado.csv"), "w", newline="",
          encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=campos)
    w.writeheader()
    w.writerows(incluidos)

from collections import Counter
motivos = Counter(r["criterio_revisor1"] for r in rows if r["decision_revisor1"] == "excluir")
print(f"Registros cribados : {len(rows)}")
print(f"Incluidos          : {len(incluidos)}")
print(f"Excluidos          : {len(rows)-len(incluidos)}\n")
print("Motivos de exclusion:")
ETIQ = {
 "E1": "E1 contenido instruccional, no informacion institucional",
 "E2": "E2 sin recuperacion sobre corpus propio",
 "E3": "E3 estudio secundario",
 "E4": "E4 literatura gris",
 "E5": "E5 dominio distinto al universitario",
 "E6": "E6 sin evaluacion empirica",
 "E7": "E7 version duplicada",
 "E8": "E8 sin plataforma de indizacion reconocida",
 "I2": "I2 no es educacion superior",
 "I3": "I3 la informacion objetivo no es institucional",
}
for k, v in motivos.most_common():
    print(f"  {v:>3}  {ETIQ.get(k,k)}")
print(f"\nPor anio (incluidos): {dict(sorted(Counter(r['anio'] for r in incluidos).items()))}")
print(f"Por plataforma      : {dict(Counter(r['plataforma'] for r in incluidos).most_common())}")
