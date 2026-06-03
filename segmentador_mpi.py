from mpi4py import MPI
import os
import subprocess

# Comunicador predefinido de MPI (Message Passing Interface), he incluye todos los proceso de un programa MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

VIDEO_DIR = "/shared/proyecto/videos_originales"
SEG_DIR = "/shared/proyecto/segmentos"

# -------------------------
# MASTER (rank 0)
# -------------------------
if rank == 0:

    # listar videos. (Estructura: [video1.mp4, video2.mp4, ...])
    videos = sorted([f for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")])

    print("Videos encontrados:", videos)

    # repartir videos en chunks (Estructura: [[], [], ...])
    chunks = [[] for _ in range(size)]

    # Asignar videos a workers (Resultado: worker 1 -> video1, video2; worker 2 -> video3, video4; ...)
    for i, video in enumerate(videos):
        worker_id = (i % (size - 1)) + 1  # Distribuir entre workers (ignorar rank 0)
        if worker_id < size:
            chunks[worker_id].append(video)

    # enviar SOLO a workers.
    for i in range(1, size):
        comm.send(chunks[i], dest=i)

    print("[MASTER] distribución enviada")

# -------------------------
# WORKERS
# -------------------------
else:
    my_videos = comm.recv(source=0)  # Recuperar videos asignados por el master

    if not my_videos:
        print(f"[Rank {rank}] sin trabajo asignado")
    else:
        print(f"[Rank {rank}] Videos asignados: {my_videos}")

    for video in my_videos:

        # Preparar paths y directorios
        video_path = os.path.join(VIDEO_DIR, video)
        name = os.path.splitext(video)[0]
        out_dir = os.path.join(SEG_DIR, name)

        # Crear directorio de salida para el video (si ya existe, no hace nada)
        os.makedirs(out_dir, exist_ok=True)

        print(f"[Rank {rank}] Procesando {video}")

        # Segmentar el video en 12 partes de 10 segundos cada una
        for i in range(12):
            start = i * 10
            output = os.path.join(out_dir, f"seg{i+1:02d}.mp4")  # nombre del segmento

            # comando para segmentar con ffmpeg
            cmd = [
                "ffmpeg",
                "-y",
                "-ss",
                str(start),
                "-i",
                video_path,
                "-t",
                "10",
                "-c",
                "copy",
                output,
            ]

            # Ejecutar el comando (sin mostrar salida)
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"[Rank {rank}] terminado")
