FROM ghcr.io/docling-project/docling-serve-cu128:latest

RUN apt-get update && \
    apt-get install -y tesseract-ocr-tur && \
    rm -rf /var/lib/apt/lists/*

RUN tesseract --list-langs | grep tur