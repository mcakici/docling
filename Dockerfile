FROM ghcr.io/docling-project/docling-serve:latest

USER root

# CentOS Stream 9 tabanlı olduğu için dnf kullanıyoruz
# curl-minimal zaten yüklü, curl yerine onu kullanıyoruz
RUN dnf install -y --setopt=install_weak_deps=False \
        gcc gcc-c++ make automake autoconf libtool pkgconfig \
        leptonica-devel libpng-devel libtiff-devel libjpeg-turbo-devel \
        zlib-devel libarchive-devel \
        wget git which && \
    dnf clean all

# Tesseract 5.5.0 source'dan build
RUN cd /tmp && \
    wget https://github.com/tesseract-ocr/tesseract/archive/refs/tags/5.5.0.tar.gz && \
    tar -xzf 5.5.0.tar.gz && \
    cd tesseract-5.5.0 && \
    ./autogen.sh && \
    ./configure --prefix=/usr && \
    make -j"$(nproc)" && \
    make install && \
    ldconfig && \
    cd / && rm -rf /tmp/tesseract-5.5.0 /tmp/5.5.0.tar.gz

# Tesseract dil dosyaları için dizin ve TR/ENG/OSD modelleri
# Tesseract 5.5.0 için tessdata dizini
ENV TESSDATA_PREFIX=/usr/share/tesseract/tessdata/
RUN mkdir -p "$TESSDATA_PREFIX" && \
    curl -fsSL -o "$TESSDATA_PREFIX/tur.traineddata" \
      https://github.com/tesseract-ocr/tessdata_best/raw/main/tur.traineddata && \
    curl -fsSL -o "$TESSDATA_PREFIX/eng.traineddata" \
      https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata && \
    curl -fsSL -o "$TESSDATA_PREFIX/osd.traineddata" \
      https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata && \
    chmod 0644 "$TESSDATA_PREFIX"/*.traineddata

# Kurulumu doğrula (build zamanı check)
RUN tesseract --version && \
    tesseract --list-langs && \
    echo "Tesseract 5.5.0 kurulumu tamamlandı"

# Docling-serve zaten 5001 portunu kullanıyor
EXPOSE 5001

# Varsayılan entrypoint/cmd'i (docling-serve) bozmuyoruz
WORKDIR /app
