import os
from pathlib import Path
import streamlit as st
from services.db import init_db, add_image, list_images, get_image, add_version, list_versions, update_caption
from services.storage import save_upload, save_version
from services.gemini_service import caption_image, edit_image
from services.search import search_images

ROOT = Path(__file__).parent
st.set_page_config(page_title="PixelAI Studio", page_icon="✨", layout="wide")
init_db()
st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#0b1020,#111827 55%,#17152c);color:#f8fafc}
[data-testid="stSidebar"]{background:#0b1020}
.hero{padding:1.4rem 1.8rem;border:1px solid #35415b;border-radius:20px;background:linear-gradient(120deg,#30275a,#16294a);margin-bottom:1rem}
.muted{color:#b5c1d5}
</style>""", unsafe_allow_html=True)

st.sidebar.title("✨ PixelAI")
st.sidebar.caption("Natural-language image editing studio")
page = st.sidebar.radio("Workspace", ["My Library", "AI Studio", "Version History", "About"])

def has_key():
    key = os.getenv("GEMINI_API_KEY")
    try:
        key = key or st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass
    if not key:
        st.error("GEMINI_API_KEY is missing. Add it to .env or Streamlit Secrets.")
        return False
    return True

if page == "My Library":
    st.markdown('<div class="hero"><h1>🖼️ Your visual library</h1><p class="muted">Upload, organize and find images using natural language.</p></div>', unsafe_allow_html=True)
    c1,c2=st.columns([1,1.5])
    with c1:
        up=st.file_uploader("Upload an image",type=["png","jpg","jpeg","webp"])
        if up and st.button("Add to library",type="primary",use_container_width=True):
            if has_key():
                try:
                    path=save_upload(up.getvalue(),up.name)
                    image_id=add_image(up.name,str(path),"",up.type or "image/jpeg")
                    with st.spinner("Gemini is describing your image..."):
                        cap=caption_image(up.getvalue(),up.type or "image/jpeg")
                    update_caption(image_id,cap)
                    st.success("Image uploaded and captioned.")
                    st.rerun()
                except Exception as e: st.error(f"Upload/analysis failed: {e}")
    with c2:
        q=st.text_input("🔎 Search your images",placeholder="e.g. show me images with a beach")
        records=list_images()
        found=search_images(q,records) if q else records
        st.caption(f"{len(found)} image(s)")
        if not found: st.info("No matching images. Upload an image first.")
        cols=st.columns(3)
        for i,item in enumerate(found):
            with cols[i%3]:
                st.image(item["path"],use_container_width=True)
                st.markdown(f"**{item['filename']}**")
                st.caption((item["caption"] or "No caption")[:160])
                if st.button("Edit this image",key=f"edit_{item['id']}",use_container_width=True):
                    st.session_state["selected_id"]=item["id"]
                    st.session_state["page"]="AI Studio"
                    st.rerun()

elif page == "AI Studio":
    st.markdown('<div class="hero"><h1>🎨 AI Studio</h1><p class="muted">Describe the change. Gemini receives the image and your instruction.</p></div>',unsafe_allow_html=True)
    records=list_images()
    if not records: st.info("Upload an image in My Library first.")
    else:
        ids=[x["id"] for x in records]
        selected=st.session_state.get("selected_id",ids[0])
        if selected not in ids: selected=ids[0]
        selected=st.selectbox("Choose an image",ids,index=ids.index(selected),
            format_func=lambda x: next((f"{r['filename']} · #{r['id']}" for r in records if r["id"]==x),str(x)))
        st.session_state["selected_id"]=selected
        item=get_image(selected)
        left,right=st.columns(2)
        with left:
            st.subheader("Original")
            st.image(item["path"],use_container_width=True)
            st.caption(item["caption"])
        with right:
            st.subheader("Edit instruction")
            preset=st.selectbox("Quick edit",["Custom instruction","Enhance image","Change background","Remove background","Change colours","Remove an object"])
            templates={
              "Enhance image":"Improve lighting, sharpness and visual quality while preserving the subject and composition.",
              "Change background":"Replace the background with a beautiful realistic beach at golden hour. Keep the main subject unchanged.",
              "Remove background":"Remove the background and place the subject on a clean neutral background.",
              "Change colours":"Make the colours more vibrant and balanced without changing the objects.",
              "Remove an object":"Remove the unwanted object described below and naturally reconstruct the area behind it."
            }
            prompt=st.text_area("What should change?",value=templates.get(preset,""),height=120,
                placeholder="Example: Remove the person on the left and fill the background naturally.")
            if st.button("✨ Generate edit",type="primary",use_container_width=True):
                if not prompt.strip(): st.warning("Enter an edit instruction.")
                elif has_key():
                    try:
                        with st.spinner("Generating image edit... this can take a little while."):
                            result=edit_image(Path(item["path"]).read_bytes(),item["mime_type"],prompt)
                            path=save_version(result,selected)
                            number=add_version(selected,str(path),prompt)
                        st.session_state["latest_edit"]=str(path)
                        st.success(f"Saved as version {number}.")
                        st.rerun()
                    except Exception as e: st.error(f"Image editing failed: {e}")
        latest=st.session_state.get("latest_edit")
        if latest and Path(latest).exists():
            st.divider(); st.subheader("Latest result")
            a,b=st.columns(2)
            with a: st.image(item["path"],caption="Original",use_container_width=True)
            with b:
                st.image(latest,caption="AI edited",use_container_width=True)
                st.download_button("Download edited image",Path(latest).read_bytes(),file_name=Path(latest).name,mime="image/png")

elif page == "Version History":
    st.markdown('<div class="hero"><h1>🕘 Version history</h1><p class="muted">Originals are preserved; each edit is saved separately.</p></div>',unsafe_allow_html=True)
    records=list_images()
    if records:
        selected=st.selectbox("Choose image",[x["id"] for x in records],format_func=lambda x: next(r["filename"] for r in records if r["id"]==x))
        item=get_image(selected)
        st.subheader("Original"); st.image(item["path"],use_container_width=True); st.caption(item["created_at"])
        versions=list_versions(selected)
        if versions:
            cols=st.columns(3)
            for i,v in enumerate(versions):
                with cols[i%3]:
                    st.image(v["path"],use_container_width=True)
                    st.caption(f"Version {v['version_no']} · {v['created_at']}")
                    st.write(v["prompt"])
                    st.download_button("Download",Path(v["path"]).read_bytes(),file_name=Path(v["path"]).name,mime="image/png",key=f"v_{v['id']}")
        else: st.info("No edits yet. Create one in AI Studio.")
    else: st.info("Your library is empty.")

else:
    st.markdown('<div class="hero"><h1>About PixelAI</h1><p class="muted">An AI-first image library and natural-language editing MVP.</p></div>',unsafe_allow_html=True)
    st.write("PixelAI combines Gemini image understanding and image editing with a Streamlit interface, SQLite metadata, local file storage and edit history.")
    st.markdown("""
    **MVP features**
    - Upload JPG, PNG and WebP images.
    - Generate searchable image captions using Gemini Vision.
    - Search image captions using natural-language-style text queries.
    - Edit selected images through natural-language prompts.
    - Preserve originals and browse edit versions.

    **Deployment note:** This is a single-user local MVP. For production, add authentication and cloud object storage.
    """)
