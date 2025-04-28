import io
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm, inch
from reportlab.lib.utils import ImageReader
from datetime import datetime

def generate_page3_pdf(form_data):
    buffer = io.BytesIO()
    doc = BaseDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Custom styles for cards and footer
    card_paragraph_style = ParagraphStyle(
        'CardParagraph',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#233D4C"),
        spaceAfter=4,
    )
    card_title_style = ParagraphStyle(
        'CardTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor("#233D4C"),
        spaceAfter=8,
    )
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        alignment=2,  # right
        textColor=colors.HexColor("#233D4C"),
    )

    # Título
    title_style = styles['Heading1']
    title_style.textColor = HexColor("#233D4C")
    title = Paragraph("Datos del Informe", title_style)
    elements.append(title)
    elements.append(Spacer(1, 5))

    # Card-like Inspector Section
    elements.append(Paragraph("Información del Inspector", card_title_style))
    elements.append(Spacer(1, 6))
    inspector_data = [
        ["Nombre:", form_data.get("inspector", "")],
        ["Teléfono:", form_data.get("inspector_phone", "")],
        ["Email:", form_data.get("inspector_email", "")]
    ]
    inspector_table = Table(inspector_data, colWidths=[100, 400])
    inspector_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cccccc")),
        ('ROUNDED', (0, 0), (-1, -1), 8),
        ('INNERPADDING', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#233D4C")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SHADOW', (0, 0), (-1, -1), 2, 2, colors.HexColor("#e0e0e0")),
    ]))
    elements.append(KeepTogether([inspector_table]))
    elements.append(Spacer(1, 16))

    # Card-like Client Section
    elements.append(Paragraph("Datos del Cliente", card_title_style))
    elements.append(Spacer(1, 6))
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
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cccccc")),
        ('ROUNDED', (0, 0), (-1, -1), 8),
        ('INNERPADDING', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#233D4C")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SHADOW', (0, 0), (-1, -1), 2, 2, colors.HexColor("#e0e0e0")),
    ]))
    elements.append(KeepTogether([client_table]))
    elements.append(Spacer(1, 16))

    # Card-like Property Section
    elements.append(Paragraph("Datos del Inmueble", card_title_style))
    elements.append(Spacer(1, 6))
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
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cccccc")),
        ('ROUNDED', (0, 0), (-1, -1), 8),
        ('INNERPADDING', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#233D4C")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SHADOW', (0, 0), (-1, -1), 2, 2, colors.HexColor("#e0e0e0")),
    ]))
    elements.append(KeepTogether([property_table]))
    elements.append(Spacer(1, 18))

    # Fecha actual al pie de página (above footer)
    #date_paragraph = Paragraph(f"Fecha del informe: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal'])
    #elements.append(date_paragraph)
    #elements.append(Spacer(1, 10))

    # Define frame and onPage callback for header/footer
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 1*inch, id='normal')

    def on_page(canvas, doc):
        width, height = letter
        # Draw header image (logoheader.png) with specified width (138px) and proportional height
        header_img = ImageReader("images/Logoheader.png")
        header_width = 138
        orig_width, orig_height = 708, 90  # Actual image size
        header_height = int(orig_height * (header_width / orig_width))  # ≈ 17.54 px, rounded to 18
        margin_top = 15  # Reduced to 1/8 of previous value for compact spacing
        margin_right = 50
        canvas.drawImage(
            header_img,
            width - header_width - margin_right,
            height - header_height - margin_top,
            header_width,
            header_height,
            mask='auto'
        )

        # Draw a dashed horizontal line as a separator
        line_y = 54  # y position for the dashed line
        canvas.setStrokeColorRGB(0, 0, 0)
        canvas.setDash(3, 3)
        canvas.setLineWidth(1)
        canvas.line(doc.leftMargin, line_y, width - doc.rightMargin, line_y)
        canvas.setDash()  # reset dash

        # Footer content positions
        footer_y = 32  # y position for the footer text

        # Left section: Company name (bold) and email (regular)
        left_x = doc.leftMargin
        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColorRGB(0, 0, 0)
        canvas.drawString(left_x, footer_y + 10, "Check Home")
        canvas.setFont("Helvetica", 10)
        canvas.drawString(left_x, footer_y, "info@checkhome.com.ar")

        # Center section: Website URL (centered)
        center_text = "https://checkhome.com.ar"
        canvas.setFont("Helvetica", 10)
        center_text_width = canvas.stringWidth(center_text, "Helvetica", 10)
        center_x = (width - center_text_width) / 2
        canvas.drawString(center_x, footer_y + 5, center_text)

        # Right section: Phone icon and number (right-aligned)
        phone_text = u"\u260E +(549) 1128330040"  # ☎ Unicode
        canvas.setFont("Helvetica", 10)
        phone_text_width = canvas.stringWidth(phone_text, "Helvetica", 10)
        right_x = width - doc.rightMargin - phone_text_width
        canvas.drawString(right_x, footer_y + 5, phone_text)

    doc.addPageTemplates([PageTemplate(id='PageWithHeaderFooter', frames=[frame], onPage=on_page)])

    # Build PDF with elements
    doc.build(elements)
    buffer.seek(0)
    return buffer