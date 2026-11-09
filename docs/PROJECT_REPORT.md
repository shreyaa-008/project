# PixelAI Project Report

## Problem
Traditional image-editing applications can require users to learn many manual tools. PixelAI demonstrates a prompt-based interface where a user uploads an image, describes a desired edit, and receives an AI-generated result.

## Objectives
1. Upload and organize a personal image collection.
2. Automatically describe images with a multimodal vision API.
3. Search images using their descriptions.
4. Edit images through natural-language instructions.
5. Preserve originals and track edited versions.

## Technologies
Streamlit for the UI; Gemini Vision for captioning; Gemini image generation/editing for image-to-image transformations; SQLite for metadata and version records; local filesystem for image files; Pillow for image conversion.

## Workflow
Upload -> store original -> caption with Gemini -> store caption -> search library -> select image -> send image and instruction to Gemini image model -> save result as a new version -> browse history.

## Manual evaluation checklist
- Upload a JPG and verify its caption appears.
- Search for an object/scene mentioned in the caption.
- Generate an edit with a specific prompt.
- Confirm the edited image appears and can be downloaded.
- Confirm original remains unchanged and a version is listed in History.

## Limitations
Local single-user storage; token-overlap search rather than vector embeddings; API availability and image quality depend on model access and quotas. The model may alter more than the requested region.

## Future work
Authentication, cloud object storage, vector embeddings, multilingual search, before/after slider, undo/restore, batch edits, moderation, quotas and deployment.
