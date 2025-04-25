import pdfplumber
import re
from datetime import datetime
from collections import defaultdict
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os

# Importar la función de extractor_pathologies.py
from extractor_pathologies import extract_pathologies_from_pdf

# Regex pattern para referencias internas
pattern = re.compile(
    r"(?m)^\s*(\d{1,3})\s+([A-ZÁÉÍÓÚÜÑ ]+)\s+ROJO(?:\s+Foto)?",
    re.MULTILINE
)

def extract_front_page_info(file_stream):
    with pdfplumber.open(file_stream) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text() or ""

        # Extract address (heuristic: look for lines with address-like content)
        address = ""
        inspector = ""

        lines = text.splitlines()
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if "formosa" in line_lower or "buenos aires" in line_lower or "ciudad autónoma" in line_lower:
                address = line.strip()
            if "inspector" in line_lower or "firmado por" in line_lower:
                # Next line likely contains inspector name
                if i + 1 < len(lines):
                    inspector = lines[i + 1].strip()
                break

        # Use current date
        date_str = datetime.now().strftime("%Y-%m-%d")
        return {
            "address": address,
            "inspector": inspector,
            "date": date_str
        }

def generate_page3_pdf(form_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Título
    title = Paragraph("Datos del Informe", styles['Heading1'])
    elements.append(title)
    elements.append(Spacer(1, 20))

    # Sección del Inspector
    elements.append(Paragraph("Información del Inspector", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    inspector_data = [
        ["Nombre:", form_data.get("inspector", "")],
        ["Teléfono:", form_data.get("inspector_phone", "")],
        ["Email:", form_data.get("inspector_email", "")]
    ]
    
    inspector_table = Table(inspector_data, colWidths=[100, 400])
    inspector_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    elements.append(inspector_table)
    elements.append(Spacer(1, 20))
    
    # Sección del Cliente
    elements.append(Paragraph("Datos del Cliente", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    client_data = [
        ["Nombre:", form_data.get("client_name", "")],
        ["Dirección:", form_data.get("client_address", "")],
        ["Localidad:", form_data.get("client_locality", "")],
        ["Provincia:", form_data.get("client_province", "")],
        ["Código Postal:", form_data.get("client_postalcode", "")],
        ["Teléfono:", form_data.get("client_phone", "")],
        ["Email:", form_data.get("client_email", "")],
        ["CUIT:", form_data.get("client_cuit", "")]
    ]
    
    client_table = Table(client_data, colWidths=[100, 400])
    client_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 20))
    
    # Sección del Inmueble
    elements.append(Paragraph("Datos del Inmueble", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    property_data = [
        ["Dirección:", form_data.get("property_address", "")],
        ["Localidad:", form_data.get("property_locality", "")],
        ["Provincia:", form_data.get("property_province", "")],
        ["Cliente presente:", form_data.get("client_present", "No")],
        ["Abierta por:", form_data.get("property_opened_by", "")],
        ["Ficha:", form_data.get("property_ficha", "")]
    ]
    
    property_table = Table(property_data, colWidths=[100, 400])
    property_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    elements.append(property_table)
    
    # Fecha actual al pie de página
    elements.append(Spacer(1, 40))
    date_paragraph = Paragraph(f"Fecha del informe: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal'])
    elements.append(date_paragraph)
    
    # Construir el PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_pathology_table_pdf(items):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Añadir título a la tabla
    styles = getSampleStyleSheet()
    title = Paragraph("Tabla de Patologías", styles['Heading1'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    data = [["Código", "Tipo", "Descripción", "Habitación", "Página"]]
    for item in items:
        data.append([
            item.get("code", ""),
            item.get("type", ""),
            item.get("description", ""),
            item.get("room", ""),
            item.get("page", "")
        ])
    table = Table(data)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_custom_page(info):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Fondo de color #233D4C (azul oscuro)
    c.setFillColor(colors.HexColor("#233D4C"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Ajustar el gráfico de líneas para que ocupe desde margen izquierdo a derecho
    lineas_image_width = width  # full width, zero margin
    lineas_image_height = 200
    c.drawImage("images/lineas_check_front.png",
                0,  # left edge
                (height - lineas_image_height) / 2,  # vertically centered
                lineas_image_width,
                lineas_image_height,
                mask='auto')  # Mantener transparencia

    # Colocar el logo encima de las líneas y centrado verticalmente
    logo_width = 400  # Ajustar según el tamaño real de tu logo
    logo_height = 160
    c.drawImage("images/Logo_check_front.png",
                (width - logo_width) / 2,  # horizontally centered
                (height - logo_height) / 2,  # vertically centered
                logo_width,
                logo_height,
                mask='auto')  # Mantener transparencia

    # Información centrada en la parte inferior
    c.setFillColor(colors.white)  # Texto en blanco para que resalte sobre el fondo azul
    c.setFont("Helvetica", 10)
    y_position = 100  # Ajustar según necesites

    c.save()
    buffer.seek(0)
    return buffer

def generate_front_page_pdf(info):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add static elements like logo here if needed
    c.save()
    buffer.seek(0)
    return buffer

def compose_final_report(original_pdf_path, front_page_info, pathology_items, output_path, form_data=None):
    # Generate pathology table PDF
    pathology_table_pdf = generate_pathology_table_pdf(pathology_items)
    
    # Generate the custom page with background color and images
    custom_page_pdf = generate_custom_page(front_page_info)
    
    # Load additional pages from PDF folder
    page2_path = os.path.join("pdf", "page2.pdf")
    page4_path = os.path.join("pdf", "page4.pdf")
    termspage1_path = os.path.join("pdf", "termspage1.pdf")
    termspage2_path = os.path.join("pdf", "termspage2.pdf")
    lastpage_path = os.path.join("pdf", "lastpage.pdf")
    
    # Generate page3 dynamically from form data if provided
    page3_pdf = None
    if form_data:
        page3_pdf = generate_page3_pdf(form_data)
    
    reader_original = PdfReader(original_pdf_path)
    writer = PdfWriter()

    # Add our custom page as the first page
    custom_reader = PdfReader(custom_page_pdf)
    writer.add_page(custom_reader.pages[0])
    
    # Add page2 from pdf folder
    if os.path.exists(page2_path):
        page2_reader = PdfReader(page2_path)
        for page in page2_reader.pages:
            writer.add_page(page)
    
    # Add page4 from pdf folder (added as per user request)
    if os.path.exists(page4_path):
        page4_reader = PdfReader(page4_path)
        for page in page4_reader.pages:
            writer.add_page(page)
    
    # Add dynamically generated page3 or try to load it from pdf folder
    if page3_pdf:
        page3_reader = PdfReader(page3_pdf)
        for page in page3_reader.pages:
            writer.add_page(page)
    else:
        # Fallback to static file if form_data not provided
        page3_path = os.path.join("pdf", "page3.pdf")
        if os.path.exists(page3_path):
            page3_reader = PdfReader(page3_path)
            for page in page3_reader.pages:
                writer.add_page(page)
    
    # Keep original front page as the next page
    if len(reader_original.pages) > 0:
        writer.add_page(reader_original.pages[0])

    # Add index page
    if len(reader_original.pages) > 1:
        writer.add_page(reader_original.pages[1])

    # Add pathology table pages
    pathology_reader = PdfReader(pathology_table_pdf)
    for page in pathology_reader.pages:
        writer.add_page(page)

    # Add remaining pages from original report starting from page 3
    for i in range(2, len(reader_original.pages)):
        writer.add_page(reader_original.pages[i])

    # Add terms pages in order
    for path in [termspage1_path, termspage2_path, lastpage_path]:
        if os.path.exists(path):
            term_reader = PdfReader(path)
            for page in term_reader.pages:
                writer.add_page(page)

    # Save final composed PDF
    with open(output_path, "wb") as f_out:
        writer.write(f_out)