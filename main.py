from fastapi import Request
from fastapi.responses import StreamingResponse
from docx import Document
from docx.shared import Inches
from io import BytesIO
import requests
import urllib.parse


BASE_URL = "https://gdcwjpkgffqmatsmuqra.supabase.co/storage/v1/object/public/question-images"


@app.post("/generate")
async def generate(request: Request):

    data = await request.json()
    entries = data["entries"]
    filetype = data["filetype"]

    doc = Document()

    for paper_name, q in entries:

        # paper_name example: "June 17 1F"
        filename_base = f"{paper_name}_Q{q}"

        images = []

        # ✅ try single image first
        urls = [f"{BASE_URL}/{urllib.parse.quote(filename_base + '.png')}"]

        # ✅ then try multi-part versions
        for i in range(1, 5):
            multi = f"{filename_base}_{i}.png"
            urls.append(f"{BASE_URL}/{urllib.parse.quote(multi)}")

        # ✅ download images
        for url in urls:
            res = requests.get(url)
            if res.status_code == 200:
                images.append(res.content)

        # ✅ add to doc
        for img_bytes in images:
            image_stream = BytesIO(img_bytes)
            doc.add_picture(image_stream, width=Inches(6))

        doc.add_paragraph("")  # spacing between questions

    # ✅ save to memory
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)

    filename = "generated.docx" if filetype == "word" else "generated.docx"

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
