import os
import time
import whisper

modelo = whisper.load_model("medium")  # Cambiá por "base", "small", etc. si querés

def transcribir(chat_name, lista_wav):
    carpeta_wav = os.path.join("output", "audio_wav")
    carpeta_transcripciones = os.path.join("data", chat_name, "transcripciones")
    os.makedirs(carpeta_transcripciones, exist_ok=True)

    audios_procesados = 0
    audios_omitidos = 0

    for archivo in lista_wav:
        ruta_wav = os.path.join(carpeta_wav, archivo)
        nombre_txt = archivo.replace(".wav", ".txt")
        ruta_txt = os.path.join(carpeta_transcripciones, nombre_txt)

        if os.path.exists(ruta_txt):
            audios_omitidos += 1
            continue  # silencioso

        print(f"🎧 Transcribiendo {archivo}...")
        start = time.time()

        resultado = modelo.transcribe(ruta_wav)
        texto = resultado["text"].strip()

        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write(texto)

        print(f"✅ Guardado: {nombre_txt}")
        print(f"⏱️ Tiempo de transcripción: {time.time() - start:.2f} segundos")
        audios_procesados += 1

    # 🧾 Resumen final
    if audios_procesados == 0:
        print(f"⏩ Todos los audios ya estaban transcritos. Nada que hacer.")
    else:
        print(f"📝 Transcripciones nuevas generadas: {audios_procesados}")
