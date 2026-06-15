from fastapi import FastAPI, UploadFile, File
import shutil

app = FastAPI()


@app.get("/")
def home():
    return {"status": "API running ✅"}


@app.post("/process")
async def process_pdf(file: UploadFile = File(...)):

    # save uploaded file
    with open("input.pdf", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # TODO: call your existing processing function here
    # e.g. process_markscheme("input.pdf")

    return {"message": "Processing complete ✅"}
