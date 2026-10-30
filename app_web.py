from pathlib import Path
import subprocess
import streamlit as st

st.set_page_config(
    page_title="Transcripción ASR con Whisper",
    page_icon="🎙️",
    layout="centered",
)

st.title("🎙️ Transcripción Local de Audio y Video")
st.write(
    "Sube tu archivo de audio o video (`.mp3` o `.mp4`) para generar los subtítulos con marcas de tiempo."
)

# Componente para subir archivos
uploaded_file = st.file_uploader(
    "Carga tu archivo multimedia", type=["mp3", "mp4"]
)

if uploaded_file is not None:
    # Guardar el archivo cargado en el volumen /media
    file_path = Path("/media") / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.info(f"Archivo preparado en el servidor: `{uploaded_file.name}`")

    # Botón para iniciar el proceso
    if st.button("🚀 Iniciar Transcripción", type="primary"):
        with st.spinner(
            "Procesando transcripción con faster-whisper... Esto puede tomar unos minutos."
        ):
            # Invocar transcribir.py forzando la sobrescritura
            cmd = ["python3", "/app/transcribir.py", "-f", str(file_path)]
            process = subprocess.run(cmd, capture_output=True, text=True)
            sub_path = file_path.with_suffix(".sub")

            if process.returncode == 0 and sub_path.exists():
                st.success("¡Transcripción completada con éxito!")

                # Leer y mostrar los subtítulos generados
                sub_content = sub_path.read_text(encoding="utf-8")
                st.text_area(
                    "Subtítulos Generados (`.sub`):", sub_content, height=250
                )

                # Botón para descargar el archivo .sub
                st.download_button(
                    label="Descargar Subtítulos (.sub)",
                    data=sub_content,
                    file_name=sub_path.name,
                    mime="text/plain",
                )
            else:
                st.error("Ocurrió un error al procesar la transcripción:")
                st.code(process.stderr)