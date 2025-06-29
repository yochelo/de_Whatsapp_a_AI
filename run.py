import os
from parser import procesar_chat
from convertir_audios import convertir
from transcribir_audios import transcribir


def elegir_zip():
    carpeta_zips = "zips"
    zips_disponibles = [f for f in os.listdir(carpeta_zips) if f.endswith(".zip")]

    if not zips_disponibles:
        print("❌ No hay archivos .zip en la carpeta 'zips'.")
        return None

    print("\n📦 ZIPs disponibles para procesar:")
    for i, zipfile in enumerate(zips_disponibles, 1):
        print(f"[{i}] {zipfile}")

    while True:
        seleccion = input("🧠 Elegí un ZIP por número: ").strip()
        if seleccion.isdigit() and 1 <= int(seleccion) <= len(zips_disponibles):
            zip_elegido = zips_disponibles[int(seleccion) - 1]
            return os.path.splitext(zip_elegido)[0]
        else:
            print("❌ Opción inválida. Intentá de nuevo.")

def ejecutar_flujo(comandos):
    for cmd in comandos:
        print(f"\n▶️ Ejecutando: {cmd}")
        resultado = os.system(cmd)
        if resultado != 0:
            print(f"❌ Error al ejecutar: {cmd}. Deteniendo ejecución.")
            break
        else:
            print(f"✅ Completado: {cmd}")

def menu():
    print("\n🎛️ MENÚ DE PROCESAMIENTO:")
    print("[1] Procesamiento del chat")
    print("[2] Ver estado actual del sistema")
    print("[0] Salir")

    opcion = input("Seleccioná una opción: ").strip()
    return opcion

while True:
    opcion = menu()

    if opcion == "0":
        print("👋 Cerrando el sistema. ¡Hasta luego!")
        break

    elif opcion == "1":
        chat_name = elegir_zip()
        if not chat_name:
            continue

        from parser import procesar_chat
        audios_detectados, imagenes_detectadas = procesar_chat(chat_name)

        # 🧼 Limpiar carpeta de imágenes incrementales
        import shutil
        carpeta_incremental = os.path.join("output", "imagenes_incrementales")
        if os.path.exists(carpeta_incremental):
            shutil.rmtree(carpeta_incremental)
        os.makedirs(carpeta_incremental, exist_ok=True)

        cantidad_imagenes = len(imagenes_detectadas)
        print(f"🖼️ Imágenes nuevas guardadas: {cantidad_imagenes}")

        from shutil import copy2
        for img in imagenes_detectadas:
            origen = os.path.join("output", "media", img)
            destino = os.path.join(carpeta_incremental, img)
            if os.path.exists(origen):
                copy2(origen, destino)

        if not audios_detectados:
            print("📭 No hay audios nuevos. Flujo finalizado.")
            continue

        # 🧼 Limpiar carpeta de WAVs
        carpeta_wav = os.path.join("output", "audio_wav")
        if os.path.exists(carpeta_wav):
            shutil.rmtree(carpeta_wav)
        os.makedirs(carpeta_wav, exist_ok=True)

        # 2. Convertir: convierte sólo esos audios
        from convertir_audios import convertir
        convertir(audios_detectados)

        # 3. Transcribir: convierte esos .wav en texto
        from transcribir_audios import transcribir
        wavs = [a.replace(".opus", ".wav") for a in audios_detectados]
        transcribir(chat_name, wavs)

        # 4. Integrar transcripciones en el md final
       
        from integrar_transcripciones import integrar
        integrar(chat_name)

        # 5. Generar ZIP para ChatGPT
        from datetime import datetime
        import zipfile

        fecha_actual = datetime.now().strftime("%d-%m-%Y")
        nombre_zip = f"incremental_{chat_name}_{fecha_actual}.zip"

        carpeta_para_chaty = os.path.join("output", "PARA_CHATY")
        os.makedirs(carpeta_para_chaty, exist_ok=True)

        ruta_zip = os.path.join(carpeta_para_chaty, nombre_zip)

        with zipfile.ZipFile(ruta_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            ruta_md = os.path.join("output", "chatIncremental.md")
            if os.path.exists(ruta_md):
                zipf.write(ruta_md, arcname="chatIncremental.md")

            carpeta_imgs = os.path.join("output", "imagenes_incrementales")
            if os.path.exists(carpeta_imgs):
                for nombre_archivo in os.listdir(carpeta_imgs):
                    ruta_archivo = os.path.join(carpeta_imgs, nombre_archivo)
                    if os.path.isfile(ruta_archivo):
                        zipf.write(ruta_archivo, arcname=f"imagenes_incrementales/{nombre_archivo}")

        print(f"📦 ZIP generado para ChatGPT: {nombre_zip}")



    elif opcion == "2":
        os.system("python ver_estado.py")

    else:
        print("❌ Opción inválida.")


