
import os
from datetime import datetime

ruta_checkpoint = os.path.join("output", "ultimo_checkpoint.txt")
ruta_incremental = os.path.join("output", "chatRenderizado.md")
ruta_acumulado = os.path.join("output", "chatCompleto.md")
ruta_media = os.path.join("output", "media")

def contar_lineas(path):
    return sum(1 for _ in open(path, "r", encoding="utf-8")) if os.path.exists(path) else 0

def fecha_mod(path):
    if os.path.exists(path):
        ts = os.path.getmtime(path)
        return datetime.fromtimestamp(ts).strftime("%d/%m %H:%M")
    return "(no existe)"

def contar_multimedia():
    if not os.path.exists(ruta_media):
        return 0, 0
    archivos = os.listdir(ruta_media)
    imgs = [f for f in archivos if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    auds = [f for f in archivos if f.lower().endswith('.opus')]
    return len(imgs), len(auds)

print("📊 ESTADO ACTUAL DEL SISTEMA\n")

print(f"🔖 Último checkpoint registrado:")
if os.path.exists(ruta_checkpoint):
    with open(ruta_checkpoint, "r", encoding="utf-8") as f:
        print(f"   {f.read().strip()}")
else:
    print("   (sin checkpoint aún)")

print(f"\n🧾 Líneas en chatRenderizado.md: {contar_lineas(ruta_incremental)}")
print(f"📅 Última modificación: {fecha_mod(ruta_incremental)}")

print(f"\n📚 Líneas en chatCompleto.md:    {contar_lineas(ruta_acumulado)}")
print(f"📅 Última modificación: {fecha_mod(ruta_acumulado)}")

imgs, auds = contar_multimedia()
print(f"\n🖼️ Imágenes en media/: {imgs}")
print(f"🎧 Audios en media/:   {auds}")

