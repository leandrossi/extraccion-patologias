import openai
import os
from openai_config import OPENAI_API_KEY
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

openai.api_key = OPENAI_API_KEY

def get_pdf_summary(file_path):
    """
    Reads the PDF file content and sends a prompt to OpenAI ChatCompletion API to get the summary text.
    """
    # For simplicity, extract text from the PDF file (could be improved)
    from pdfplumber import open as pdfplumber_open
    with pdfplumber_open(file_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

    system_prompt = (
        "Eres un inspector profesional de propiedades trabajando para una empresa de inspección. "
        "Tu tarea es procesar documentos de inspección de propiedades (informes técnicos) y generar resúmenes formales, claros, detallados y estructurados. "
        "Tu estilo debe ser siempre: Formal, técnico y neutro. Claro y profesional, como un informe que podría ser entregado a un cliente. "
        "No alarmista, pero sí indicando prioridades de reparación si corresponde. "
        "Objetivo de cada respuesta: Generar un Resumen de Inspección organizado en secciones: Condiciones Generales, Estado Eléctrico, Estado de Plomería, Estado del Sistema de Gas, Humedad, Aislaciones, Aberturas, Estructura (terminaciones), Recomendaciones Finales. "
        "Cuando se detecten patologías críticas (color rojo) o fallas relevantes, indicarlo en cada sección de forma respetuosa, proponiendo acciones de mantenimiento o reparación, pero sin ser alarmista. "
        "Dar conclusiones finales indicando qué sistemas son prioritarios para intervenir. "
        "Utiliza siempre viñetas o guiones para listar observaciones dentro de cada sección. "
        "Utiliza recomendaciones específicas al final de cada grupo de observaciones. "
        "Cada informe debe estar referido exclusivamente al estado al día de la inspección. "
        "Si se requiere hacer un anexo (sobre humedades, filtraciones, terrazas verdes, piletas, etc.) debe escribirse como anexo formal adicional, especificando que se refiere al día de inspección. "
        "IMPORTANTE: No inventes datos técnicos si no están en el texto proporcionado. No exageres conclusiones si el informe base no las marca como críticas. "
        "Todo tu análisis debe ser coherente, profesional, y orientado a la preservación y mejora de la propiedad inspeccionada."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Resumen de inspección del archivo cargado:\n{full_text}"}
    ]

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    summary = response.choices[0].message.content.strip()
    return summary

def generate_summary_page(summary_text):
    """
    Generates a PDF page with the summary text.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("Resumen del Informe", styles['Heading1'])
    elements.append(title)
    elements.append(Spacer(1, 20))

    # Split summary into paragraphs if needed
    for paragraph in summary_text.split('\n\n'):
        elements.append(Paragraph(paragraph.strip(), styles['Normal']))
        elements.append(Spacer(1, 12))

    # Add date at the bottom
    elements.append(Spacer(1, 40))
    date_paragraph = Paragraph(f"Fecha del resumen: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal'])
    elements.append(date_paragraph)

    doc.build(elements)
    buffer.seek(0)
    return buffer