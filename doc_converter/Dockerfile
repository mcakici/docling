FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

# LibreOffice + temel bağımlılıklar
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice \
        fonts-dejavu \
        locales \
        curl \
        && rm -rf /var/lib/apt/lists/*

# TR locale (opsiyonel ama güzel olur)
RUN sed -i 's/^# *tr_TR.UTF-8 UTF-8/tr_TR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen tr_TR.UTF-8
ENV LANG=tr_TR.UTF-8
ENV LC_ALL=tr_TR.UTF-8

# FastAPI + Uvicorn + python-multipart (UploadFile için gerekli)
RUN pip install --no-cache-dir fastapi uvicorn[standard] python-multipart

WORKDIR /app

COPY doc_to_docx_api.py /app/doc_to_docx_api.py

EXPOSE 8000

CMD ["uvicorn", "doc_to_docx_api:app", "--host", "0.0.0.0", "--port", "8000"]
