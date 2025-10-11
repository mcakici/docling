FROM ghcr.io/docling-project/docling-serve-cu128:latest
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-tur && \
    rm -rf /var/lib/apt/lists/*
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/
