import os, base64
from google import genai

VISION_MODEL=os.getenv("GEMINI_VISION_MODEL","gemini-2.5-flash")
IMAGE_MODEL=os.getenv("GEMINI_IMAGE_MODEL","gemini-3.1-flash-image")

def client():
    key=os.getenv("GEMINI_API_KEY")
    if not key:
        try:
            import streamlit as st
            key=st.secrets.get("GEMINI_API_KEY")
        except Exception: pass
    if not key: raise RuntimeError("GEMINI_API_KEY is missing. Add it to .env or Streamlit Secrets.")
    return genai.Client(api_key=key)

def caption_image(image_bytes,mime_type):
    response=client().models.generate_content(
      model=VISION_MODEL,
      contents=[
        {"inline_data":{"mime_type":mime_type,"data":base64.b64encode(image_bytes).decode("utf-8")}},
        "Describe visible contents in 2-4 factual sentences. Mention objects, people, setting and colours. Do not guess identities or unsupported facts."
      ])
    text=(getattr(response,"text",None) or "").strip()
    if not text: raise RuntimeError("Gemini returned an empty caption.")
    return text

def edit_image(image_bytes,mime_type,instruction):
    interaction=client().interactions.create(
      model=IMAGE_MODEL,
      input=[
        {"type":"image","data":base64.b64encode(image_bytes).decode("utf-8"),"mime_type":mime_type},
        {"type":"text","text":(
          "Edit the supplied image according to this instruction: "+instruction+
          ". Preserve unrelated parts of the original as closely as possible. Return the edited image."
        )}
      ])
    output=getattr(interaction,"output_image",None)
    if output is not None and getattr(output,"data",None):
        return base64.b64decode(output.data)
    for step in (getattr(interaction,"steps",None) or []):
        for block in (getattr(step,"content",None) or []):
            if getattr(block,"type",None)=="image" and getattr(block,"data",None):
                return base64.b64decode(block.data)
    raise RuntimeError("The model did not return image bytes. Verify image-model access and GEMINI_IMAGE_MODEL.")


def embed_text(text, task_type="RETRIEVAL_DOCUMENT"):
    """Create a dense vector for a caption or search query using Gemini Embeddings."""
    from google.genai import types
    response = client().models.embed_content(
        model=os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"),
        contents=text,
        config=types.EmbedContentConfig(task_type=task_type, output_dimensionality=768),
    )
    embeddings = getattr(response, "embeddings", None) or []
    if not embeddings or not getattr(embeddings[0], "values", None):
        raise RuntimeError("Gemini returned an empty text embedding.")
    return [float(x) for x in embeddings[0].values]
