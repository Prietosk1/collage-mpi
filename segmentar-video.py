import os
import sys
import subprocess

VIDEO_DIR = "/shared/proyecto/videos_originales"
SEGMENTOS_DIR = "/shared/proyecto/segmentos"

if len(sys.argv) != 2:
    print("Uso: python3 segmentar_video.py video1.mp4")
    sys.exit(1)

video = sys.argv[1]

video_path = os.path.join(VIDEO_DIR, video)

nombre_video = os.path.splitext(video)[0]

salida_dir = os.path.join(SEGMENTOS_DIR, nombre_video)

os.makedirs(salida_dir, exist_ok=True)

for i in range(12):
    inicio = i * 10

    salida = os.path.join(salida_dir, f"seg{i+1:02d}.mp4")

    comando = [
        "ffmpeg",
        "-y",
        "-ss",
        str(inicio),
        "-i",
        video_path,
        "-t",
        "10",
        "-c",
        "copy",
        salida,
    ]

    print(f"Generando {salida}...")

    subprocess.run(comando, check=True)

print("Segmentación completada.")
