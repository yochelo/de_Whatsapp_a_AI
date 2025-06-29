import sys
import os
import zipfile
import re
import shutil

def procesar_chat(chat_name):

    # ======== CONFIG ========
    VALID_AUDIO = [".opus", ".mp3", ".m4a"]
    VALID_IMAGE = [".jpg", ".jpeg", ".png"]
    IGNORED_EXT = [".webp", ".gif"]
    ruta_checkpoint = os.path.join("output", "ultimo_checkpoint.txt")
    ruta_renderizado = os.path.join("output", "chatRenderizado.md")
    ruta_media_output = os.path.join("output", "media")
    os.makedirs(ruta_media_output, exist_ok=True)

    # ======== ARGUMENTO ========
    if __name__ == "__main__":
        if len(sys.argv) < 2:
            print("❌ Debés pasar el nombre del chat. Ej: python parser.py chat2")
            exit(1)

        procesar_chat(chat_name)

    ruta_zip = os.path.join("zips", f"{chat_name}.zip")
    carpeta_destino = os.path.join("data", f"{chat_name}_temp")

    if not os.path.exists(ruta_zip):
        print(f"❌ No se encontró el archivo: {ruta_zip}")
        exit(1)

    # ======== DESCOMPRIMIR ZIP ========
    os.makedirs(carpeta_destino, exist_ok=True)
    with zipfile.ZipFile(ruta_zip, 'r') as zip_ref:
        zip_ref.extractall(carpeta_destino)

    archivos_extraidos = os.listdir(carpeta_destino)
    chat_txt = next((f for f in archivos_extraidos if f.endswith(".txt")), None)

    if not chat_txt:
        print("❌ No se encontró ningún archivo .txt dentro del zip.")
        exit(1)

    ruta_txt = os.path.join(carpeta_destino, chat_txt)
    print(f"✅ ZIP descomprimido en: {carpeta_destino}")
    print(f"📄 Archivo de chat encontrado: {chat_txt}")

    # ======== CLASIFICAR LÍNEAS ========
    with open(ruta_txt, "r", encoding="utf-8") as f:
        lineas_txt = f.readlines()

    # ======== CARGAR CHECKPOINT ========
    if os.path.exists(ruta_checkpoint):
        with open(ruta_checkpoint, "r", encoding="utf-8") as f:
            ultima_linea_guardada = f.read().strip()
    else:
        ultima_linea_guardada = None

    idx_inicio = 0
    if ultima_linea_guardada:
        for i, linea in enumerate(lineas_txt):
            if linea.strip() == ultima_linea_guardada:
                idx_inicio = i + 1
                print(f"📍 Línea de checkpoint detectada en línea {i}, comenzando desde {idx_inicio}")
                break
        else:
            print("⚠️ Línea de checkpoint NO encontrada. Se procesará desde el inicio.")

    lineas_nuevas = lineas_txt[idx_inicio:]

    # === Detectar audios ===
    imagenes_detectadas = []
    audios_detectados = []
    lineas_de_texto = []

    archivos_extraidos = os.listdir(carpeta_destino)

    for linea in lineas_nuevas:
        # Audio
        match_audio = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4}), \d{1,2}:\d{2} - .*?: .*?(WA\d{4})\.opus", linea)
        if match_audio:
            fecha_original = match_audio.group(1)   # ej: 21/5/25
            wa_id = match_audio.group(2)            # ej: WA0044

            partes = fecha_original.split("/")
            if len(partes[2]) == 2:
                partes[2] = "20" + partes[2]        # año corto → largo
            fecha_formateada = f"{partes[2]}{partes[1].zfill(2)}{partes[0].zfill(2)}"  # yyyyMMdd

            nombre_esperado = f"PTT-{fecha_formateada}-{wa_id}.opus"
            if nombre_esperado in archivos_extraidos:
                audios_detectados.append(nombre_esperado)
            continue

        # Imagen
        match_img = re.search(r"(IMG-\d{8}-WA\d{4}\.(jpg|jpeg|png))", linea, re.IGNORECASE)
        if match_img:
            nombre_img = match_img.group(1)
            if nombre_img in archivos_extraidos:
                imagenes_detectadas.append(nombre_img)
            continue

        # Texto
        lineas_de_texto.append(linea)


    def clasificar_linea(linea):
        # Audio de WhatsApp
        match_audio = re.search(r"(PTT-\d{8}-WA\d{4})\.opus", linea)
        if match_audio:
            return {"tipo": "audio", "wa_id": match_audio.group(1)}

        # Imagen (formato IMG con fecha y código)
        # Imagen (formato IMG con fecha y código)
        match_img = re.search(r"(IMG-\d{8}-WA\d{4})\.(jpg|jpeg|png)", linea, re.IGNORECASE)
        if match_img:
            return {"tipo": "imagen", "wa_id": match_img.group(1)}


        # Línea vacía o sin valor
        if not linea.strip() or linea.strip() == "":
            return {"tipo": "descartable"}

        # Texto común
        return {"tipo": "texto", "linea": linea}


    # ======== PARSEAR Y EXPORTAR ========
    audios_detectados = []
    imagenes_detectadas = []
    archivos_extraidos = os.listdir(carpeta_destino)  # ZIP descomprimido

    with open(ruta_renderizado, "w", encoding="utf-8") as f_out:
        for linea in lineas_nuevas:
            linea = linea.strip()
            if not linea:
                continue

            clasif = clasificar_linea(linea)
            tipo = clasif["tipo"]

            if tipo == "descartable":
                continue

            if tipo == "audio":
                wa_id = clasif["wa_id"]
                nombre_opus = f"{clasif['wa_id']}.opus"
                if nombre_opus in archivos_extraidos:
                    f_out.write(f"##AUDIO_{wa_id}##\n")
                    audios_detectados.append(nombre_opus)
                else:
                    f_out.write(f"[Audio {clasif['wa_id']} no encontrado]\n")


            elif tipo == "imagen":
                autor = clasif.get("autor", "Desconocido")
                archivo_real = next(
                    (x for x in archivos_extraidos if clasif['wa_id'] in x and x.lower().endswith(tuple(VALID_IMAGE))),
                    None
                )
                if archivo_real:
                    markdown_img = f"![Imagen enviada por {autor}](media/{archivo_real})"
                    f_out.write(markdown_img + "\n")
                    imagenes_detectadas.append(archivo_real)
                else:
                    f_out.write(f"[Imagen WA{clasif['wa_id']} no encontrada]\n")

            elif tipo == "texto":
                f_out.write(clasif["linea"] + "\n")
    # Guardar checkpoint con la última línea útil (no vacía ni descartada)
    if lineas_nuevas:
        for linea in reversed(lineas_nuevas):
            linea = linea.strip()
            if linea:
                with open(ruta_checkpoint, "w", encoding="utf-8") as f:
                    f.write(linea)
                break


    # ======== COPIAR ARCHIVOS A /output/media ========
    for archivo in imagenes_detectadas + audios_detectados:
        origen = os.path.join(carpeta_destino, archivo)
        destino = os.path.join(ruta_media_output, archivo)
        if os.path.exists(origen):
            shutil.copy2(origen, destino)

    # ======== RESUMEN ========
    print("\n📈 Resultados:")
    print(f"🧾 Último checkpoint: {ultima_linea_guardada or '(ninguno - primera vez)'}")
    print(f"📥 Nuevas líneas encontradas: {len(lineas_nuevas)}")
    print(f"🎧 Audios detectados: {len(audios_detectados)}")
    print(f"🖼️ Imágenes detectadas: {len(imagenes_detectadas)}")
    print(f"💬 Líneas de texto: {len(lineas_nuevas) - len(audios_detectados) - len(imagenes_detectadas)}")
    print("✅ Chat incremental exportado en output/chatRenderizado.md")

    return audios_detectados, imagenes_detectadas
