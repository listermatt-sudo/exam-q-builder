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
    # ✅ PROCESS ALL QUESTIONS
    # =================
    for paper_name, q in entries:

        parts = paper_name.split(" ")
        month = parts[0]
        year = parts[1][-2:]
        paper = parts[2]

    # ✅ Fix month abbreviations
if month == "November":
    month = "Nov"

        paper_fixed = f"{month} {year} {paper}"
        filename_base = f"{paper_fixed}_Q{q}"

        # ✅ Build URLs
        urls = [f"{BASE_URL}/{urllib.parse.quote(filename_base + '.png')}"]

        for i in range(1, 6):
            urls.append(f"{BASE_URL}/{urllib.parse.quote(filename_base + '_' + str(i) + '.png')}")

        images = []

        for url in urls:
            res = requests.get(url)
            if res.status_code == 200:
                images.append(res.content)

        if not images:
            continue

        # =================
        # ✅ WORD (FLOW MODE)
        # =================
        if filetype == "word":

            header = f"{paper_fixed}   Question {q}"

            p = doc.add_paragraph(header)
            p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            p.runs[0].bold = True

            doc.add_paragraph("")

            for img in images:
                doc.add_picture(BytesIO(img), width=Inches(6))

            doc.add_paragraph("")  # spacing only (NO PAGE BREAK)

        # =================
        # ✅ STORE FOR PDF
        # =================
        if filetype == "pdf":
            pdf_data.append((paper_fixed, q, images))

    # =================
    # ✅ WORD OUTPUT
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
    # ✅ PDF OUTPUT (SMART PAGINATION)
    # =================
    if filetype == "pdf":

        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader

        pdf_stream = BytesIO()
        c = canvas.Canvas(pdf_stream, pagesize=A4)

        PAGE_WIDTH, PAGE_HEIGHT = A4

        y = PAGE_HEIGHT - 40  # start near top

        for paper_fixed, q, images in pdf_data:

            header = f"{paper_fixed}   Question {q}"

            c.setFont("Helvetica-Bold", 14)

            # ✅ Move to next page if header won't fit
            if y < 100:
                c.showPage()
                y = PAGE_HEIGHT - 40

            c.drawCentredString(PAGE_WIDTH / 2, y, header)
            y -= 30

            for img_bytes in images:

                img = ImageReader(BytesIO(img_bytes))

                img_width = 500
                img_height = 350  # adjustable

                # ✅ If image won't fit → new page
                if y - img_height < 50:
                    c.showPage()
                    y = PAGE_HEIGHT - 40

                c.drawImage(
                    img,
                    50,
                    y - img_height,
                    width=img_width,
                    height=img_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )

                y -= (img_height + 20)

            y -= 20  # spacing between questions

        c.save()
        pdf_stream.seek(0)

        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=generated.pdf"}
        )
