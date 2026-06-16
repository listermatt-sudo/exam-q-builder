from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse
import json
import requests
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from io import BytesIO
import urllib.parse

app = FastAPI()

SUPABASE_URL = "https://gdcwjpkgffqmatsmuqra.supabase.co"
BASE_URL = f"{SUPABASE_URL}/storage/v1/object/public/question-images"


# ✅ HOME
@app.get("/")
def serve_home():
    return FileResponse("index.html")


# ✅ STRUCTURE
@app.get("/structure")
def get_structure():
    with open("structure.json") as f:
        return json.load(f)


# ✅ GENERATE
@app.post("/generate")
async def generate(request: Request):

    data = await request.json()
    entries = data["entries"]
    filetype = data["filetype"]

    doc = Document()
    pdf_data = []

    # =================
    # PROCESS QUESTIONS
    # =================
    for paper_name, q in entries:

        parts = paper_name.split(" ")
        month = parts[0]

        # ✅ Fix month naming
        if month == "November":
            month = "Nov"

        year = parts[1][-2:]
        paper = parts[2]

        paper_fixed = f"{month} {year} {paper}"
        filename_base = f"{paper_fixed}_Q{q}"

        images = []

        # ✅ Try main image
        base_url = f"{BASE_URL}/{urllib.parse.quote(filename_base + '.png')}"
        res = requests.get(base_url)

        if res.status_code == 200:
            images.append(res.content)
        else:
            # ✅ Try multi-part images
            for i in range(1, 6):
                part_url = f"{BASE_URL}/{urllib.parse.quote(filename_base + '_' + str(i) + '.png')}"
                res = requests.get(part_url)
                if res.status_code == 200:
                    images.append(res.content)

        # ✅ Handle missing
        if not images:
            if filetype == "word":
                doc.add_paragraph(f"MISSING: {paper_fixed} Q{q}")
            continue

        # =================
        # ✅ WORD OUTPUT (FIXED)
        # =================
        if filetype == "word":

            # ✅ Table groups header + images
            table = doc.add_table(rows=1, cols=1)
            cell = table.rows[0].cells[0]

            # ✅ Header
            p = cell.paragraphs[0]
            run = p.add_run(f"{paper_fixed}   Question {q}")
            p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            run.bold = True

            # ✅ Images (CORRECT METHOD)
            for img in images:
                paragraph = cell.add_paragraph()
                run = paragraph.add_run()
                run.add_picture(BytesIO(img), width=Inches(6))

            # ✅ spacing after question
            doc.add_paragraph("")

        # =================
        # ✅ STORE FOR PDF
        # =================
        if filetype == "pdf":
            pdf_data.append((paper_fixed, q, images))

    # =================
    # ✅ WORD RETURN
    # =================
    if filetype == "word":

        stream = BytesIO()
        doc.save(stream)
        stream.seek(0)

        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=generated.docx"}
        )

    # =================
    # ✅ PDF RETURN (FIXED)
    # =================
    if filetype == "pdf":

        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader

        pdf_stream = BytesIO()
        c = canvas.Canvas(pdf_stream, pagesize=A4)

        PAGE_WIDTH, PAGE_HEIGHT = A4
        y = PAGE_HEIGHT - 40

        for paper_fixed, q, images in pdf_data:

            header = f"{paper_fixed}   Question {q}"
            header_height = 30

            # ✅ Ensure header + first image together
            if y < 120:
                c.showPage()
                y = PAGE_HEIGHT - 40

            # ✅ Header
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(PAGE_WIDTH / 2, y, header)
            y -= header_height

            for img_bytes in images:

                img_reader = ImageReader(BytesIO(img_bytes))
                orig_width, orig_height = img_reader.getSize()

                # ✅ Scale to full width
                max_width = PAGE_WIDTH - 80
                scale = max_width / orig_width

                img_width = max_width
                img_height = orig_height * scale

                # ✅ Page break if needed
                if y - img_height < 50:
                    c.showPage()
                    y = PAGE_HEIGHT - 40

                c.drawImage(
                    img_reader,
                    (PAGE_WIDTH - img_width) / 2,
                    y - img_height,
                    width=img_width,
                    height=img_height
                )

                y -= (img_height + 20)

            y -= 30

        # ✅ FINALISE PDF
        c.save()
        pdf_stream.seek(0)

        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=generated.pdf"}
        )
