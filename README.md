# Servicio Local de Transcripción Multimedia (ASR)

Servicio dockerizado y privado de transcripción automática de audio y video basado en **faster-whisper** (modelo por defecto `large-v3-turbo`) y **Streamlit**.

---

## uía de Inicio Rápido

### 1. Construir la Imagen Docker

Asegúrate de estar en la raíz del proyecto (`~/Descargas/Github/Transcribe`) y ejecuta:

```bash
docker build -t local-whisper .
```

### 2. Iniciar el Contenedor

Lanza el contenedor en segundo plano exponiendo la interfaz en el puerto `8502` y montando el directorio local `./media`:

```bash
docker run -d --name whisper-app -p 8502:8501 -v $(pwd)/media:/media local-whisper
```

---

## Formas de Uso

### Opción A: Desde la Línea de Comandos (CLI)

Ejecuta la transcripción directa sobre archivos `.mp3` o `.mp4` guardados en tu carpeta local `./media`:

* **Transcripción estándar:**
  ```bash
  docker exec whisper-app transcribir /media/tu_archivo.mp4
  ```

* **Forzar sobrescritura del archivo `.sub` (`-f` / `--force`):**
  ```bash
  docker exec whisper-app transcribir -f /media/tu_archivo.mp4
  ```

---

### Opción B: Desde la Interfaz Web (Streamlit UI)

1. Abre tu navegador web e ingresa a: **`http://localhost:8502`**
2. Carga un archivo de audio o video.
3. Haz clic en **🚀 Iniciar Transcripción**.
4. Descarga directamente el archivo `.sub` generado.
