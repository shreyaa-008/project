# Week 3 — Image Search + Backend Enhancements

## Delivered in this build

- Caption embeddings generated with Gemini `gemini-embedding-001` when a new image is uploaded and captioned.
- Existing captioned records can be indexed using **Build / repair search index** in My Library.
- Search queries are embedded with `RETRIEVAL_QUERY`; image captions use `RETRIEVAL_DOCUMENT`.
- A persistent JSON index (`data/caption_vectors.json`) stores vectors, source text and update timestamps.
- Retrieval uses cosine similarity and ranks the closest image captions.
- The original image and all edit versions remain separately stored; version numbers are sequential per source image.
- Upload processing now stores a normalized JPEG MIME type matching the actual normalized JPEG file.
- A Mermaid system architecture diagram is included in README.md.

## Data flow

1. Upload -> normalized local image file.
2. Gemini Vision -> caption.
3. SQLite -> image metadata and caption.
4. Gemini Embeddings -> dense caption vector.
5. JSON vector index -> persist vector by image ID.
6. Search text -> query embedding.
7. Cosine similarity -> ranked caption/image results.
8. Edit prompt + original image -> Gemini image model -> new image version + SQLite version row.

## Validation checklist

- [ ] Upload at least three different images and confirm each gets a caption.
- [ ] Confirm `data/caption_vectors.json` is created and contains one vector per captioned image.
- [ ] Search with a phrase that does not exactly match the filename, such as “warm evening sky” or “snow-covered peaks”.
- [ ] Confirm semantically related images rank above unrelated images.
- [ ] Use **Build / repair search index** to backfill pre-existing records.
- [ ] Generate an edit and confirm the original file is unchanged and a new version is added.
- [ ] Restart the app and confirm search and version history still work.

## Important implementation note

This implementation embeds the Gemini-generated text captions, as requested by the Week 3 deliverable “search interface using embedded captions.” It does not create image-pixel embeddings. The JSON index is a lightweight vector store suitable for a small local demo; FAISS or Chroma would be a sensible next step for larger collections.

## API and deployment notes

The embedding endpoint and image-editing endpoint require valid Gemini API access, quota and model availability. Test using your own API key. The JSON index and SQLite database are local files; standard ephemeral hosting may discard them after a restart/redeploy. For persistent public deployment, migrate images to object storage and metadata/vector data to durable managed services. Never commit API keys.
