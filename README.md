# Parser de Conversaciones de WhatsApp con Audios y Multimedia

Este proyecto automatiza el procesamiento de una conversación exportada desde **WhatsApp** (con sus archivos multimedia) para convertirla en un formato óptimo que pueda ser analizado por una **IA**, incorporando texto, imágenes y audios **transcritos**. 

---

## 🧠 ¿Qué problema resuelve?

Muchas conversaciones de WhatsApp incluyen **audios** y **fotos** que no son fácilmente interpretables por un modelo de IA al exportar el chat. Este programa:
- **Convierte los audios en texto** y los inyecta directamente en la conversación, respetando la referencia original.
- **Extrae las imágenes** y las renombra según su referencia, para que puedan ser leídas en contexto.
- **Separa el resultado final en dos versiones**:
  - **Global**: toda la conversación procesada.
  - **Incremental**: solo el nuevo contenido desde la última actualización.

---

## 🔁 Flujo de trabajo

1. **Exportás el chat de WhatsApp** con multimedia incluido.
2. El sistema:
   - **Elimina archivos irrelevantes** como `.webp` (stickers, gifs).
   - **Convierte los audios `.opus` a `.wav`** de forma temporal.
   - **Transcribe los audios** usando [`Whisper`](https://github.com/openai/whisper) de OpenAI (por defecto se usa el modelo `medium`, que ofrece excelente rendimiento).
   - **Inyecta la transcripción** directamente en el lugar correspondiente de la conversación.
   - **Extrae las imágenes relevantes** según las referencias en el texto.
   - **Crea dos salidas**:
     - `chatIncremental.md` (solo lo nuevo desde la última vez)
     - `chatGlobal.md` (toda la conversación)
     - Carpeta `/imagenes/` con las imágenes referenciadas.
3. **Zipea automáticamente** todo lo que debe entregarse a la IA:
   - Una estructura ordenada con texto + imágenes en carpetas separadas.

---

## 📦 Estructura final del ZIP para la IA

```
/chatIncremental.md
/imagenes/
    IMG-20230622-WA0001.jpg
    IMG-20230622-WA0005.png
```

> En caso de ser la primera ejecución, `chatGlobal.md` y `chatIncremental.md` son iguales.

---

## 💬 Casos de uso

- Entrenamiento de modelos que interpretan conversaciones.
- Análisis de contenido emocional o comercial en chats.
- Monitorización de evolución de una conversación sin reanalizar todo.
- Validación automatizada de feedback en negocios o grupos de trabajo.

---

## 🧰 Requisitos técnicos

- Python 3.10+
- [`Whisper`](https://github.com/openai/whisper) instalado localmente
- FFmpeg disponible en el PATH (para convertir `.opus` → `.wav`)

---

## 🗂️ Extras

Este sistema fue pensado para facilitar análisis progresivo sin repetir carga. Ideal para usar junto con modelos de lenguaje que no aceptan input multimodal nativo pero necesitan contexto enriquecido.
