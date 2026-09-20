# Image Handling

The deck must be self-contained — local images must be embedded as base64 data URIs, not referenced by file path. A file path `src` breaks as soon as the HTML is moved or shared.

## Encoding local images

Use the host's authorized file/image capabilities to read the provided local image, preserve its actual MIME type and encode its bytes as a base64 data URI. Do not reconstruct an installed executable from instructions. If the host cannot read or encode the file, retain an explicit missing-image state.

Then use the output as the `src` value:

```html
<img src="data:image/jpeg;base64,/9j/4AAQ..." alt="Description" />
```

## Using /as:resize-images output

If the user ran `/as:resize-images` before this skill, the `resized-slides/` folder contains images already sized for the slide canvas:

- `*-slides-wide.jpg` — 1920×1080 (16:9) — use for full-bleed and image-grid slides
- `*-slides-standard.jpg` — 1024×768 (4:3) — use only if the user asked for a 4:3 deck

Prefer `slides-wide` images. Embed them as base64 (see above) so the deck stays portable.

## When no local images are provided

Use `src=""` with a descriptive `alt` attribute as a placeholder. Note the placeholder in the output so the user knows which slides need images:

```html
<img src="" alt="[Insert: project exterior view]" />
```

## File size note

Base64-encoding large images increases HTML file size. If the user provides many high-res images, warn them: "Embedding N images will produce a large HTML file (~X MB). Consider running `/as:resize-images` first (choose the slides output when it asks which sizes you need) to reduce file size before embedding."
