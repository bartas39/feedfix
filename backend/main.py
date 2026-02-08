# backend/main.py

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse

import requests
from lxml import etree
import uuid
import os

from validator.google import validate_google_feed
from report import generate_pdf_report


app = FastAPI()


# -------------------------
# Utils
# -------------------------

def parse_xml(content: bytes):
    try:
        parser = etree.XMLParser(recover=False)
        return etree.fromstring(content, parser=parser)
    except Exception:
        return None


# -------------------------
# API Endpoints
# -------------------------

@app.post("/validate/url")
def validate_from_url(url: str = Form(...)):

    r = requests.get(url, timeout=20)

    if r.status_code != 200:
        return {"error": "Nie można pobrać pliku"}

    root = parse_xml(r.content)

    if root is None:
        return {"error": "Niepoprawny XML"}

    result = validate_google_feed(root)

    return result


@app.post("/validate/file")
def validate_from_file(file: UploadFile = File(...)):

    content = file.file.read()

    root = parse_xml(content)

    if root is None:
        return {"error": "Niepoprawny XML"}

    result = validate_google_feed(root)

    return result


@app.post("/validate/url/pdf")
def validate_and_generate_pdf(url: str = Form(...)):

    r = requests.get(url, timeout=20)

    if r.status_code != 200:
        return {"error": "Nie można pobrać pliku"}

    root = parse_xml(r.content)

    if root is None:
        return {"error": "Niepoprawny XML"}

    result = validate_google_feed(root)

    filename = f"report_{uuid.uuid4().hex}.pdf"
    filepath = os.path.join("/tmp", filename)

    generate_pdf_report(result, filepath)

    return {
        "status": "ok",
        "file": filename,
        "download_url": f"/download/{filename}"
    }


@app.get("/download/{filename}")
def download_report(filename: str):

    filepath = os.path.join("/tmp", filename)

    if not os.path.exists(filepath):
        return {"error": "Plik nie istnieje"}

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=filename
    )
