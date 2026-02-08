# backend/main.py

from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import requests
import xml.etree.ElementTree as ET
import tempfile
import os
import uuid

from validator.google import validate_google_feed
from report import generate_pdf_report


# ---------------- APP ----------------

app = FastAPI(
    title="FeedFix API",
    description="Analiza feedów Google Shopping",
    version="1.0"
)


# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # MVP: pozwalamy wszystkim
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- HEALTH ----------------

@app.get("/")
def home():
    return {"status": "FeedFix API działa"}


# ---------------- ANALIZA JSON ----------------

@app.post("/validate/url")
def validate_feed(url: str = Form(...)):

    try:

        response = requests.get(url, timeout=20)

        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Nie można pobrać pliku XML"
            )

        root = ET.fromstring(response.content)

        result = validate_google_feed(root)

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- ANALIZA + PDF ----------------

@app.post("/validate/url/pdf")
def validate_feed_pdf(url: str = Form(...)):

    try:

        # Pobierz XML
        response = requests.get(url, timeout=20)

        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Nie można pobrać pliku XML"
            )

        # Parsuj XML
        root = ET.fromstring(response.content)

        # Waliduj
        result = validate_google_feed(root)

        # Nazwa pliku
        file_id = uuid.uuid4().hex
        filename = f"report_{file_id}.pdf"

        temp_path = os.path.join(
            tempfile.gettempdir(),
            filename
        )

        # Generuj PDF
        generate_pdf_report(result, temp_path)

        # Wyślij PDF
        with open(temp_path, "rb") as f:
            pdf_data = f.read()

        # Sprzątanie
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return pdf_data

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
