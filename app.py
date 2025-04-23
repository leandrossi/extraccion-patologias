from flask import Flask, request, render_template, send_file
import io
import csv
from extractor import extract_pathologies_from_pdf

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
    items = []
    csv_data = ""
    file = request.files.get("pdf_file")
    if file:
        items = extract_pathologies_from_pdf(file)
        csv_data = items_to_csv(items).replace("\n", "\\n").replace("\"", "\\\"")
    return render_template("index.html", items=items, csv_data=csv_data)

@app.route("/download_csv", methods=["POST"])
def download_csv():
    csv_data = request.form.get("csv_data", "")
    csv_data = csv_data.replace("\\n", "\n").replace("\\\"", "\"")
    buffer = io.BytesIO()
    buffer.write(csv_data.encode("utf-8"))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="patologias_rojo.csv", mimetype="text/csv")

if __name__ == "__main__":
    app.run(debug=True)