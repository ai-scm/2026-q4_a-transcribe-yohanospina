# Imagen base oficial de Python liviana (Debian slim)
FROM python:3.11-slim

# Evitar la creación de archivos .pyc y forzar salida continua en consola
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Instalar el gestor de paquetes uv desde la imagen oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Directorio de trabajo
WORKDIR /app

# Copiar configuración de dependencias e instalarlas en el entorno global
COPY pyproject.toml /app/
RUN uv pip install --system "faster-whisper>=1.1.0" "av>=12.0.0" "ctranslate2>=4.0.0" "streamlit>=1.30.0"

# Copiar los scripts de transcripción y la interfaz web
COPY transcribir.py /app/transcribir.py
COPY app_web.py /app/app_web.py

# Crear ejecutable global 'transcribir'
RUN echo '#!/bin/sh\nexec python3 /app/transcribir.py "$@"' > /usr/local/bin/transcribir && \
    chmod +x /usr/local/bin/transcribir /app/transcribir.py

# Crear punto de montaje para los archivos multimedia
RUN mkdir -p /media

# Exponer el puerto de la interfaz web
EXPOSE 8501

# Iniciar la aplicación web de Streamlit
CMD ["streamlit", "run", "/app/app_web.py", "--server.address=0.0.0.0", "--server.port=8501"]