from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
import tempfile
import subprocess
import shutil
import os
import time

app = FastAPI(title="DOC → DOCX Converter")

@app.post("/doc-to-docx")
async def doc_to_docx(file: UploadFile = File(...)):
    # Sadece .doc kabul edelim (istersen gevşetebilirsin)
    if not file.filename.lower().endswith(".doc"):
        raise HTTPException(status_code=400, detail="Lütfen .doc uzantılı bir dosya gönderin.")

    # Her istek için ayrı bir geçici klasör (otomatik temizlenecek)
    with tempfile.TemporaryDirectory() as tmpdir:
        # Orijinal dosya adını kullan (uzantı olmadan)
        original_base_name = os.path.splitext(file.filename)[0] or "document"
        input_path = os.path.join(tmpdir, f"{original_base_name}.doc")
        output_dir = tmpdir

        # Upload edilen dosyayı temp dizinine yaz
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Dosyanın yazıldığından emin ol
        if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
            raise HTTPException(status_code=400, detail="Dosya yüklenemedi veya boş.")

        # LibreOffice ile doc -> docx dönüştür
        # LibreOffice'in çalışma dizinini değiştir (bazı durumlarda sorun çıkabiliyor)
        result = subprocess.run(
            [
                "soffice",
                "--headless",
                "--invisible",
                "--nodefault",
                "--nolockcheck",
                '--convert-to', 'docx',
                "--outdir", output_dir,
                input_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=tmpdir,
            timeout=120,  # 2 dakika timeout
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Bilinmeyen hata"
            raise HTTPException(
                status_code=500,
                detail=f"LibreOffice dönüşüm başarısız: {error_msg}",
            )

        # LibreOffice'in dosyayı oluşturması için kısa bir bekleme (bazen dosya sistemi gecikmeli olabilir)
        max_wait = 10  # Maksimum 10 saniye bekle
        wait_interval = 0.5  # Her 0.5 saniyede bir kontrol et
        output_path = None
        
        # Beklenen çıktı dosyası yolu
        expected_output = os.path.join(output_dir, f"{original_base_name}.docx")
        
        for _ in range(int(max_wait / wait_interval)):
            # Önce beklenen yolu kontrol et
            if os.path.exists(expected_output):
                output_path = expected_output
                break
            
            # Eğer beklenen yerde yoksa, klasördeki tüm .docx dosyalarını kontrol et
            try:
                files_in_dir = os.listdir(output_dir)
                docx_files = [
                    os.path.join(output_dir, f)
                    for f in files_in_dir
                    if f.lower().endswith(".docx") and os.path.isfile(os.path.join(output_dir, f))
                ]
                
                if docx_files:
                    # En yeni dosyayı al (eğer birden fazla varsa)
                    output_path = max(docx_files, key=os.path.getmtime)
                    break
            except Exception:
                pass
            
            time.sleep(wait_interval)
        
        # Çıktı dosyasını kontrol et
        if output_path is None or not os.path.exists(output_path):
            # Son bir kez daha dene
            try:
                files_in_dir = os.listdir(output_dir)
                docx_files = [
                    os.path.join(output_dir, f)
                    for f in files_in_dir
                    if f.lower().endswith(".docx") and os.path.isfile(os.path.join(output_dir, f))
                ]
                
                if docx_files:
                    output_path = max(docx_files, key=os.path.getmtime)
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"DOCX çıktısı bulunamadı. Klasör içeriği: {os.listdir(output_dir)}"
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"DOCX çıktısı bulunamadı: {str(e)}"
                )
        
        # Dosyanın geçerli olduğunu kontrol et
        if os.path.getsize(output_path) == 0:
            raise HTTPException(status_code=500, detail="Dönüştürülmüş dosya boş.")
        
        # Dosyayı oku
        try:
            with open(output_path, "rb") as f:
                data = f.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Dosya okunamadı: {str(e)}")

        out_name = (file.filename.rsplit(".", 1)[0] or "document") + ".docx"

        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{out_name}"'
            },
        )
