from flask import Flask, request, render_template, send_file, make_response
import io
import csv
import os
import tempfile
from extractorv2 import extract_pathologies_from_pdf, extract_front_page_info, compose_final_report
from datetime import datetime

app = Flask(__name__)

def items_to_csv(items):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Número", "Tipo de Patología", "Descripción Corta", "Habitación", "Página"])
    for item in items:
        writer.writerow([item["code"], item["type"], item["description"], item["room"], item["page"]])
    return output.getvalue()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/process_pdf", methods=["POST"])
def process_pdf():
    file = request.files.get("pdf_file")
    if not file:
        return render_template("index.html", error="No file uploaded")

    # Recopilar todos los datos del formulario
    form_data = {
        # Datos del inspector
        "inspector": request.form.get("inspector", ""),
        "inspector_phone": request.form.get("inspector_phone", ""),
        "inspector_email": request.form.get("inspector_email", ""),
        
        # Datos del cliente
        "client_name": request.form.get("client_name", ""),
        "client_address": request.form.get("client_address", ""),
        "client_locality": request.form.get("client_locality", ""),
        "client_province": request.form.get("client_province", ""),
        "client_postalcode": request.form.get("client_postalcode", ""),
        "client_phone": request.form.get("client_phone", ""),
        "client_email": request.form.get("client_email", ""),
        "client_cuit": request.form.get("client_cuit", ""),
        
        # Datos del inmueble
        "property_address": request.form.get("property_address", ""),
        "property_locality": request.form.get("property_locality", ""),
        "property_province": request.form.get("property_province", ""),
        "client_present": "Sí" if request.form.get("client_present") else "No",
        "property_opened_by": request.form.get("property_opened_by", ""),
        "property_ficha": request.form.get("property_ficha", "")
    }

    # Extract front page info
    front_page_info = extract_front_page_info(file)

    # Reset file stream position to start for next read
    file.seek(0)

    # Extract pathology items
    pathology_items = extract_pathologies_from_pdf(file)

    # Reset file stream position to start for composing final report
    file.seek(0)

    # Create a temporary file for the output PDF
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_output.close()

    # Compose final report PDF
    # Save uploaded file to a temporary file to get a valid file path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_input:
        file.seek(0)
        temp_input.write(file.read())
        temp_input_path = temp_input.name

    from pdf_summary import get_pdf_summary, generate_summary_page
    summary_text = get_pdf_summary(temp_input_path)
    summary_pdf = generate_summary_page(summary_text)

    compose_final_report(temp_input_path, front_page_info, pathology_items, temp_output.name, form_data, summary_pdf=summary_pdf)

    # Read the generated PDF to send as response
    with open(temp_output.name, "rb") as f:
        pdf_data = f.read()

    # Remove the temporary file
    os.unlink(temp_output.name)

    # Generate pathology table CSV for display
    csv_data = items_to_csv(pathology_items)

    response = make_response(pdf_data)
    response.headers.set('Content-Type', 'application/pdf')
    response.headers.set('Content-Disposition', 'attachment', filename='reporte_final.pdf')

    # Render the page with pathology table and download link
    return response

if __name__ == "__main__":
    app.run(debug=True)