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

# Regex pattern to extract pathology data (same as before)
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

def extract_pathologies_from_pdf(file_stream):
    # Reuse the previous extraction logic from extractor.py or implement here
    # For now, we can import and call the existing function from extractor.py
    from extractor import extract_pathologies_from_pdf as old_extract
    return old_extract(file_stream)

def generate_front_page_pdf(info):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add static elements like logo here if needed

    # Dynamic text
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "Reporte de Inspección de Propiedades")
    c.setFont("Helvetica", 12)
    c.drawString(72, height - 100, f"Dirección: {info.get('address', '')}")
    c.drawString(72, height - 120, f"Fecha: {info.get('date', '')}")
    c.drawString(72, height - 140, f"Inspector: {info.get('inspector', '')}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def generate_pathology_table_pdf(items):
    buffer = io.BytesIO()
    
    # Reduce the left and right margins to make table wider
    # Default margins are usually around 72 points (1 inch)
    left_margin = 30
    right_margin = 30
    top_margin = 72
    bottom_margin = 72
    
    # Create document with custom margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin
    )
    
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("Tabla de Patologías ROJO", styles['Heading1'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    data = [["Número", "Tipo", "Descripción Corta", "Habitación", "Página"]]
    for item in items:
        row = [
            Paragraph(str(item["code"]), styles['BodyText']),
            Paragraph(item["type"], styles['BodyText']),
            Paragraph(item["description"], styles['BodyText']),
            Paragraph(item["room"], styles['BodyText']),
            Paragraph(item["page"], styles['BodyText'])
        ]
        data.append(row)

    # Calculate column widths based on content length
    col_count = len(data[0])
    # Use the actual page width minus the reduced margins
    available_width = letter[0] - left_margin - right_margin
    min_col_width = 50
    col_widths = []

    # Define column width proportions (total should equal 1.0)
    col_proportions = [0.1, 0.15, 0.45, 0.2, 0.1]  # Adjust these as needed
    
    for col_idx in range(col_count):
        # Calculate width based on proportion
        col_widths.append(max(min_col_width, available_width * col_proportions[col_idx]))

    table = Table(data, colWidths=col_widths, rowHeights=None)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
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
    logo_width = 200  # Ajustar según el tamaño real de tu logo
    logo_height = 80
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
    
    # Calcular ancho total para centrar texto
    address_text = f"Dirección: {info.get('address', 'Formosa 157, CABA, Buenos Aires')}"
    date_text = f"Fecha: {info.get('date', '22 de Abril de 2025')}"
    inspector_text = f"Inspector: {info.get('inspector', 'Mendez Mariano Jeremias')}"
    
    address_width = c.stringWidth(address_text, "Helvetica", 10)
    date_width = c.stringWidth(date_text, "Helvetica", 10)
    inspector_width = c.stringWidth(inspector_text, "Helvetica", 10)
    
    c.drawString((width - address_width) / 2, y_position, address_text)
    c.drawString((width - date_width) / 2, y_position - 15, date_text)
    c.drawString((width - inspector_width) / 2, y_position - 30, inspector_text)
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def compose_final_report(original_pdf_path, front_page_info, pathology_items, output_path):
    import os
    # Generate pathology table PDF
    pathology_table_pdf = generate_pathology_table_pdf(pathology_items)
    
    # Generate the custom page with background color and images
    custom_page_pdf = generate_custom_page(front_page_info)
    
    # Load additional pages from PDF folder
    page2_path = os.path.join("pdf", "page2.pdf")
    page3_path = os.path.join("pdf", "page3.pdf")
    termspage1_path = os.path.join("pdf", "termspage1.pdf")
    termspage2_path = os.path.join("pdf", "termspage2.pdf")
    lastpage_path = os.path.join("pdf", "lastpage.pdf")
    
    reader_original = PdfReader(original_pdf_path)
    writer = PdfWriter()

    # Add our custom page as the first page
    custom_reader = PdfReader(custom_page_pdf)
    writer.add_page(custom_reader.pages[0])
    
    page4_path = os.path.join("pdf", "page4.pdf")  # Added definition for page4_path

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
    
    # Add page3 from pdf folder
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
