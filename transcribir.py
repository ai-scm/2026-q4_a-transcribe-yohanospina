#!/usr/bin/env python3
"""Servicio local de transcripción ASR basado en faster-whisper.

Procesamiento incremental con consumo de memoria constante O(1).
"""

import argparse
import os
from pathlib import Path
import sys

from faster_whisper import WhisperModel

# Extensiones multimedia permitidas por alcance
ALLOWED_EXTENSIONS = {".mp4", ".mp3"}


def format_timestamp(seconds: float) -> str:
    """Formatea un tiempo en segundos flotantes al formato HH:MM:SS.mmm.

    Ejemplo: 3661.5 -> '01:01:01.500'
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    milliseconds = int((secs - int(secs)) * 1000)
    secs = int(secs)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"


def main():
    parser = argparse.ArgumentParser(
        description="Herramienta local dockerizada de transcripción ASR mediante Whisper."
    )
    parser.add_argument(
        "archivo", type=str, help="Ruta al archivo multimedia (.mp4 o .mp3)."
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Fuerza la sobrescritura del archivo .sub si ya existe sin solicitar confirmación.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("WHISPER_MODEL", "large-v3-turbo"),
        help="Modelo de Whisper a utilizar large-v3-turbo.",
    )
    parser.add_argument(
        "--language",
        type=str,
        default=os.getenv("WHISPER_LANGUAGE", "es"),
        help="Código del idioma de transcripción (default: es).",
    )
    parser.add_argument(
        "--compute-type",
        type=str,
        default=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
        help="Tipo de cuantización: int8, float16, float32 (default: int8).",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=os.getenv("WHISPER_DEVICE", "cpu"),
        help="Dispositivo de cómputo: cpu o cuda (default: cpu).",
    )
    args = parser.parse_args()

    input_path = Path(args.archivo).resolve()

    # Validar existencia del archivo
    if not input_path.is_file():
        print(
            f"Error: El archivo de entrada '{input_path}' no existe.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validar formato de extensión
    if input_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        print(
            f"Error: Formato '{input_path.suffix}' no soportado. "
            f"Formatos permitidos: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Determinar ruta del archivo .sub de salida
    output_path = input_path.with_suffix(".sub")

    # Verificar existencia previa de archivo .sub
    if output_path.exists() and not args.force:
        print(f"Aviso: El archivo de salida '{output_path}' ya existe.")
        try:
            confirmacion = (
                input("¿Desea sobrescribirlo? [s/N]: ").strip().lower()
            )
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada.")
            sys.exit(0)

        if confirmacion not in ["s", "si", "sí", "y", "yes"]:
            print(
                "Operación cancelada por el usuario. El archivo existente no fue modificado."
            )
            sys.exit(0)

    print(f"Iniciando procesamiento: {input_path.name}")
    print(
        f"Parámetros: Modelo='{args.model}', Idioma='{args.language}', Dispositivo='{args.device}', Cuantización='{args.compute_type}'"
    )

    # Cargar el modelo en CTranslate2
    try:
        model = WhisperModel(
            args.model,
            device=args.device,
            compute_type=args.compute_type,
            download_root="/root/.cache/huggingface/hub",
        )
    except Exception as e:
        print(f"Error al inicializar el modelo Whisper: {e}", file=sys.stderr)
        sys.exit(1)

    # Ejecutar transcripción mediante generadores (streaming)
    try:
        segments, info = model.transcribe(
            str(input_path),
            language=args.language,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        print(
            f"Audio verificado: Idioma='{info.language}' (Confianza: {info.language_probability:.2f}), Duración: {info.duration:.2f}s"
        )
        print("Escribiendo subtítulos en disco...")

        # Escritura streaming segmento a segmento
        with open(output_path, "w", encoding="utf-8") as sub_file:
            count = 0
            for segment in segments:
                count += 1
                t_start = format_timestamp(segment.start)
                t_end = format_timestamp(segment.end)
                text = segment.text.strip()
                sub_file.write(f"[{t_start} -> {t_end}] {text}\n")
                sub_file.flush()

        print(
            f"Transcripción completada. Se escribieron {count} segmentos en '{output_path}'."
        )
    except Exception as e:
        print(f"Error durante la transcripción: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()