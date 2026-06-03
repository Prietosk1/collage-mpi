import os
import subprocess

BASE = "/shared/proyecto"
SEG_DIR = os.path.join(BASE, "segmentos")
OUT_DIR = os.path.join(BASE, "collages")

# Listar videos (Estructura: [video1, video2, ...])
videos = sorted([f"video{i}" for i in range(1, 9)])

# Crear directorio de salida para collages (si ya existe, no hace nada)
os.makedirs(OUT_DIR, exist_ok=True)

# Generar collages para cada segmento (1 a 12)
for seg_idx in range(1, 13):

    # Lista de inputs para ffmpeg (Estructura: ["-i", "path/to/seg1.mp4", "-i", "path/to/seg2.mp4", ...])
    inputs = []

    for v in videos:
        # Ejemplo: /shared/proyecto/segmentos/video1/seg01.mp4
        path = os.path.join(SEG_DIR, v, f"seg{seg_idx:02d}.mp4")

        inputs += ["-i", path]  # Agregar input para ffmpeg

    # Ejemplo: /shared/proyecto/collages/collage01.mp4
    output = os.path.join(OUT_DIR, f"collage{seg_idx:02d}.mp4")

    # xstack 2x4 (8 videos por collage) con layout específico
    filter_complex = (
        "[0:v]scale=320:180[v0];"
        "[1:v]scale=320:180[v1];"
        "[2:v]scale=320:180[v2];"
        "[3:v]scale=320:180[v3];"
        "[4:v]scale=320:180[v4];"
        "[5:v]scale=320:180[v5];"
        "[6:v]scale=320:180[v6];"
        "[7:v]scale=320:180[v7];"
        "[v0][v1][v2][v3][v4][v5][v6][v7]"
        "xstack=inputs=8:"
        "layout=0_0|320_0|640_0|960_0|0_180|320_180|640_180|960_180"
    )

    # Comando completo para generar el collage con ffmpeg
    cmd = [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex",
        filter_complex,
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        output,
    ]

    print(f"Generando collage {seg_idx:02d}")

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

print("Collages listos 🚀")
