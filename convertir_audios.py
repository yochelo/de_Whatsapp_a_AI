import os
import subprocess

def convertir(lista_opus):
    carpeta_origen = os.path.join("output", "media")
    carpeta_salida = os.path.join("output", "audio_wav")
    os.makedirs(carpeta_salida, exist_ok=True)

    wavs_generados = []

    for archivo in lista_opus:
        nombre_wav = archivo.replace(".opus", ".wav")
        ruta_entrada = os.path.join(carpeta_origen, archivo)
        ruta_salida = os.path.join(carpeta_salida, nombre_wav)

        if os.path.exists(ruta_salida):
            continue  # ya convertido

        comando = [
            "C:/proyectos/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe",
            "-y", "-i", ruta_entrada, ruta_salida
        ]

        try:
            subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print(f"✅ Convertido: {archivo}")
            wavs_generados.append(nombre_wav)
        except subprocess.CalledProcessError:
            print(f"❌ Error al convertir {archivo}")

    return wavs_generados
