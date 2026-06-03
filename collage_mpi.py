from mpi4py import MPI
import os
import subprocess

# MPI setup
comm = MPI.COMM_WORLD  # Comunicación entre procesos
rank = comm.Get_rank()
size = comm.Get_size()

BASE = "/shared/proyecto"
SEG_DIR = os.path.join(BASE, "segmentos")
OUT_DIR = os.path.join(BASE, "collages")

# Listar videos (Estructura: [video1, video2, ...])
videos = [f"video{i}" for i in range(1, 9)]
os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------
# MASTER
# -------------------------
if rank == 0:

    tasks = list(range(1, 13))  # collages 1–12. Estrctura: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    # Estructura: [[], [], ...] para asignar tareas a cada worker
    chunks = [[] for _ in range(size)]

    # Asignar tareas a workers (Resultado: worker 1 -> collages 1, 5, 9; worker 2 -> collages 2, 6, 10; ...)
    for i, t in enumerate(tasks):
        worker = (i % (size - 1)) + 1
        chunks[worker].append(t)

    print("[MASTER] tareas distribuidas:", chunks)

    # Enviar SOLO a workers (ignorar rank 0)
    for i in range(1, size):
        comm.send(chunks[i], dest=i)

# -------------------------
# WORKERS
# -------------------------
else:

    # Recuperar tareas asignadas por el master (Estructura: worker 1 -> collages 1, 5, 9; worker 2 -> collages 2, 6, 10; ...)
    my_tasks = comm.recv(source=0)

    print(f"[Rank {rank}] collages asignados: {my_tasks}")

    # Generar collages para cada segmento asignado a este worker
    for seg_idx in my_tasks:

        # Preparar inputs para ffmpeg (Estructura: ["-i", "path/to/seg1.mp4", "-i", "path/to/seg2.mp4", ...])
        inputs = []

        for v in videos:
            # Ejemplo: /shared/proyecto/segmentos/video1/seg01.mp4
            path = os.path.join(SEG_DIR, v, f"seg{seg_idx:02d}.mp4")

            inputs += ["-i", path]

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
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            output,
        ]

        print(f"[Rank {rank}] generando collage {seg_idx:02d}")
        subprocess.run(
            cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )

    print(f"[Rank {rank}] terminado")
