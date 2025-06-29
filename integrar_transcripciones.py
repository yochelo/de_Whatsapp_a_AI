import re
import glob
import os
from datetime import datetime
import shutil

def integrar(chat_name):
    ruta_md_original = "output/chatRenderizado.md"
    ruta_md_nuevo = "output/chatIncremental.md"
    
    # 🚫 Cortar si el archivo base está vacío
    if not os.path.exists(ruta_md_original) or os.path.getsize(ruta_md_original) == 0:
        print("⏩ chatRenderizado.md está vacío. No se generó chatIncremental.md ni se tocó el acumulado.")
        return

    carpeta_transcripciones = os.path.join("data", chat_name, "transcripciones")

    with open(ruta_md_original, "r", encoding="utf-8") as f:
        contenido = f.read()

    patron_audio = r"##AUDIO_(PTT-\d{8}-WA\d{4})##"
    coincidencias = re.findall(patron_audio, contenido)

    print(f"🔎 Encontrados {len(coincidencias)} audios para reemplazar...")

    for nombre_audio in coincidencias:
        patron = os.path.join(carpeta_transcripciones, f"{nombre_audio}.txt").replace("\\", "/")
        coincidencias_txt = glob.glob(patron)

        if coincidencias_txt:
            with open(coincidencias_txt[0], "r", encoding="utf-8") as f:
                texto_transcripto = f.read().strip()

            contenido = contenido.replace(
                f"##AUDIO_{nombre_audio}##",
                f"🎤 *{texto_transcripto}*"
            )
            print(f"✅ Reemplazado: {nombre_audio}")
        else:
            print(f"⚠️ No se encontró la transcripción de: {nombre_audio}")

    if not coincidencias:
        print("⏩ No hay audios para reemplazar. No se generó nuevo chatIncremental.md")
        return

    with open(ruta_md_nuevo, "w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"\n📝 Archivo final generado: {ruta_md_nuevo}")

    # ========== VERIFICAR Y ACTUALIZAR chatCompleto.md ==========
    ruta_acumulado = "output/chatCompleto.md"
    ruta_checkpoint = "output/ultimo_checkpoint.txt"

    with open(ruta_md_nuevo, "r", encoding="utf-8") as f:
        lineas_incrementales = f.readlines()

    # No hace falta filtrar por checkpoint: el incremental ya parte desde él.
    nuevas_lineas = lineas_incrementales


    if nuevas_lineas:
        if os.path.exists(ruta_acumulado):
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            ruta_backup = os.path.join("output", f"backup_chatCompleto_{timestamp}.md")
            shutil.copy2(ruta_acumulado, ruta_backup)
            print(f"🛡️ Backup generado: {ruta_backup}")

        with open(ruta_acumulado, "a", encoding="utf-8") as f:
            f.writelines(nuevas_lineas)

        with open(ruta_checkpoint, "w", encoding="utf-8") as f:
            f.write(nuevas_lineas[-1].strip())

        print("📚 Incremental agregado a chatCompleto.md y checkpoint actualizado.")
    else:
        print("⏩ No se agregaron líneas nuevas. Acumulado intacto.")
