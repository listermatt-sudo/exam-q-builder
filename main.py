from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse
import json
import requests
from docx import Document
from docx.shared import Inches
from io import BytesIO
import urllib.parse

# ✅ CREATE APP FIRST (CRITICAL)
app = FastAPI()

SUPABASE_URL = "https://gdcwjpkgffqmatsmuqra.supabase.co"

BASE_URL = f"{SUPABASE_URL}/storage/v1/object/public/question-images"


# ✅ HOME PAGE
@app.get("/")
def serve_home():
    return FileResponse("index.html")


# ✅ STRUCTURE (USED BY DROPDOWN)
@app.get("/structure")
def get_structure():
    try:
        with open("structure.json") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


@app.post("/generate")
async def generate(request: Request):

    data = await request.json()
    entries = data["entries"]

    doc = Document()

    for paper_name, q in entries:

        @app.post("/generate")
async def generate(request: Request):

    data = await request.json()
    entries = data["entries"]

    doc = Document()

    for paper_name, q in entries:

        filename_base = f"{paper_name}_Q{q}"

        images = []

        urls = [f"{BASE_URL}/{urllib.parse.quote(filename_base + '.png')}"]

        for i in range(1, 5):
            multi = f"{filename_base}_{i}.png"
            urls.append(f"{BASE_URL}/{urllib.parse.quote(multi)}")

        for url in urls:
            res = requests.get(url)
            if res.status_code == 200:
                images.append(res.content)

        for img_bytes in images:
            image_stream = BytesIO(img_bytes)
            doc.add_picture(image_stream, width=Inches(6))

        doc.add_paragraph("")

    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)

    # ✅ THIS MUST BE INSIDE THE FUNCTION
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=generated.docx"}
    )

        images = []

        urls = [f"{BASE_URL}/{urllib.parse.quote(filename_base + '.png')}"]

        for i in range(1, 5):
            multi = f"{filename_base}_{i}.png"
            urls.append(f"{BASE_URL}/{urllib.parse.quote(multi)}")

        for url in urls:
            res = requests.get(url)
            if res.status_code == 200:
                images.append(res.content)

        for img_bytes in images:
            image_stream = BytesIO(img_bytes)
            doc.add_picture(image_stream, width=Inches(6))

        doc.add_paragraph("")

    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)

    # ✅ THIS MUST BE INSIDE THE FUNCTION
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=generated.docx"}
    )
