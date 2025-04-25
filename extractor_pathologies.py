import pdfplumber
import re
from collections import defaultdict

# Regex pattern para detectar inicios de patologías ROJO
pattern = re.compile(
    r"(?m)^\s*(\d{1,3})\s+([A-ZÁÉÍÓÚÜÑ ]+)\s+ROJO(?:\s+Foto)?",
    re.MULTILINE
)

def extract_pathologies_from_pdf(file_stream):
    pathology_dict = defaultdict(lambda: {"pages": [], "type": "", "description": "", "room": ""})

    full_text = ""
    page_positions = []
    page_texts = []

    with pdfplumber.open(file_stream) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                marker = f"\n<<PAGE {i+1}>>\n"
                page_positions.append((len(full_text), i + 1))
                full_text += marker + text
                page_texts.append((i + 1, text))

    matches = list(pattern.finditer(full_text))

    for i, match in enumerate(matches):
        code = match.group(1).strip()
        type_path = match.group(2).strip()

        start_pos = match.end()
        end_pos = matches[i+1].start() if i + 1 < len(matches) else len(full_text)
        block_text = full_text[start_pos:end_pos].strip()

        match_start = match.start()
        page_number = next((p for pos, p in reversed(page_positions) if match_start >= pos), "?")

        # Verificar si se repite el código y tipo en la siguiente página y usar solo ese contenido si existe
        if i + 1 < len(matches):
            next_code = matches[i + 1].group(1).strip()
            next_type = matches[i + 1].group(2).strip()
            if next_code == code and next_type == type_path:
                start_pos = matches[i + 1].end()
                end_pos = matches[i + 2].start() if i + 2 < len(matches) else len(full_text)
                block_text = full_text[start_pos:end_pos].strip()

        description_lines = []
        room = ""
        lines = block_text.splitlines()

        for line in lines:
            line_strip = line.strip()
            if not line_strip or line_strip.lower() == "foto":
                continue
            if "-Identificación" in line_strip:
                break
            if re.match(r"^(Page\s+\d+/\d+|<<PAGE \d+>>)", line_strip):
                break
            description_lines.append(line_strip)
            if len(description_lines) >= 3:
                break

        description = " ".join(description_lines).strip()

        type_phrase = type_path.lower()
        if description.lower().startswith(type_phrase):
            description = description[len(type_phrase):].strip()
        if description.lower().startswith("rojo"):
            description = description[4:].strip()

        # Eliminar prefijos erróneos como "s " y caracteres no alfabéticos antes del texto real
        description = re.sub(r"^[^a-zA-Z]*(?:s\s+)?", "", description)

        # Nuevo enfoque: detectar habitación según línea con símbolo "▼" (triángulo negro hacia abajo)
        if not room:
            page_text = next((text for pg, text in page_texts if str(pg) == str(page_number)), "")
            lines_page = page_text.splitlines()
            match_header = f"{code} {type_path} ROJO"
            match_line_idx = next((idx for idx, l in enumerate(lines_page) if match_header in l), None)
            if match_line_idx is not None:
                for prev_line in reversed(lines_page[:match_line_idx]):
                    if "▼" in prev_line:
                        room = prev_line.strip("\u25bc ").strip()
                        break

        if code in pathology_dict:
            if page_number not in pathology_dict[code]["pages"]:
                pathology_dict[code]["pages"].append(page_number)
        else:
            pathology_dict[code]["type"] = type_path
            pathology_dict[code]["description"] = description
            pathology_dict[code]["room"] = room
            pathology_dict[code]["pages"] = [page_number]

    items = []
    for code, info in pathology_dict.items():
        items.append({
            "code": code,
            "type": info["type"],
            "description": info["description"],
            "room": info["room"],
            "page": ", ".join(map(str, info["pages"]))
        })

    items.sort(key=lambda x: int(x["code"]))
    return items