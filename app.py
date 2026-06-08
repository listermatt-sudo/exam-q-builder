from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from docx import Document
from docx.shared import Inches
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

import requests
from io import BytesIO

# ✅ FastAPI app
app = FastAPI()

# ✅ Enable CORS (required for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Supabase config
SUPABASE_URL = "https://gdcwjpkgffqmatsmuqra.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdkY3dqcGtnZmZxbWF0c211cXJhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA4ODMxMzksImV4cCI6MjA5NjQ1OTEzOX0.bpjgWe1ydbiIK2e9yOwESvMRLoK5c_lHljCpOM8q-3o"
BUCKET = "question-images"

BASE_URL = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}"


# ✅ Request format
class RequestData(BaseModel):
    entries: list
    filetype: str


# ✅ Build image filename
def find_image(paper, q):
    return f"{paper}_Q{q}.png"


# ✅ Fetch file list from Supabase
def get_all_files():

    url = f"{SUPABASE_URL}/storage/v1/object/list/{BUCKET}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return []

    return response.json()


# ✅ Endpoint: get months + papers dynamically
@app.get("/papers")
def get_papers():

    files = get_all_files()
    return {"raw": files}


# ✅ Create Word file
def create_word(entries, filename):

    doc = Document()
    doc.add_heading("Worksheet", 0)

    for paper, q in entries:

        doc.add_heading(f"{paper} — Q{q}", level=1)

        img = find_image(paper, q)
        url = f"{BASE_URL}/{img}"

        response = requests.get(url)

        if response.status_code == 200:
            doc.add_picture(BytesIO(response.content), width=Inches(5))

        doc.add_page_break()

    doc.save(filename)


# ✅ Create PDF file
def create_pdf(entries, filename):

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 40

    for paper, q in entries:

        img = find_image(paper, q)
        url = f"{BASE_URL}/{img}"

        response = requests.get(url)
        if response.status_code != 200:
            continue

        img_obj = ImageReader(BytesIO(response.content))
        img_w, img_h = img_obj.getSize()

        scale = (width - 80) / img_w
        new_h = img_h * scale

        if y - new_h < 50:
            c.showPage()
            y = height - 40

        c.drawImage(
            img_obj,
            40,
            y - new_h,
            width=width - 80,
            height=new_h
        )

        y -= new_h + 20

    c.save()


# ✅ Main generate endpoint
@app.post("/generate")
def generate(data: RequestData):

    if data.filetype == "word":
        filename = "worksheet.docx"
        create_word(data.entries, filename)
    else:
        filename = "worksheet.pdf"
        create_pdf(data.entries, filename)

    return FileResponse(filename, filename=filename)


# ✅ Basic homepage (avoids 404)
@app.get("/")
def home():
    return {"message": "Worksheet Builder API is running"}
