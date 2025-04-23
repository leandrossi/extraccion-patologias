# Plan for PDF Pathology Extraction Web App (Python + HTML)

## Overview
This project involves creating a Python script with a simple HTML page to upload PDF inspection reports of properties. The goal is to extract "patologías caratulares" marked as "ROJO" from the PDF, parse the relevant data, and display it as an HTML table on the page. The user will also have the option to download the results as a CSV file.

## Process Flow

```mermaid
flowchart TD
  A[User uploads PDF via HTML form] --> B[Python backend receives PDF]
  B --> C[Extract text from PDF page-by-page]
  C --> D[Reset pathology items array]
  D --> E[Parse text with regex for "ROJO" pathologies]
  E --> F[Extract fields: code, type, description, room, page]
  F --> G[Add items to array]
  G --> H[Sort array by code ascending]
  H --> I[Render HTML table with results]
  I --> J[Display table on webpage]
  I --> K[Provide CSV download option]
```

## Technical Details

- **Backend:** Python Flask app
- **PDF Extraction:** Use `pdfplumber` or `PyMuPDF` to extract text page-by-page preserving line breaks
- **Regex Pattern:**
  ```
  (?m)^\s*(\d{1,3})\s+([A-ZÁÉÍÓÚÜÑ ]+)\s+ROJO(?:\s+Foto)?\s*([\s\S]*?)(?=^\s*\d{1,3}\s+[A-ZÁÉÍÓÚÜÑ ]+\s+(?:ROJO|AMARILLO|VERDE)|\Z)
  ```
- **Parsing Logic:**
  - Extract:
    - Code (group 1)
    - Type of pathology (group 2)
    - Short description (first line after "Foto" and before "-Identificación")
    - Room (to be extracted from the block if available)
    - Page number (from the text "Page X" after the block)
- **Data Handling:**
  - Store extracted items in an array
  - Sort array by code ascending
- **Frontend:**
  - Simple HTML form for PDF upload
  - Display results as an HTML table with columns:
    - Number of pathology
    - Type of pathology
    - Short description
    - Room
    - Page
  - Provide a button to download results as CSV

## Notes
- The script will process one PDF at a time.
- The output will be displayed on the webpage and optionally downloadable as CSV.

Please confirm if you want me to proceed with implementing this solution.