# Professional profile and public certificates — 2026-09-16

Added the `#credentials` route with CV-based experience, education, skills,
languages, six certificate cards, full-image links and a contact invitation.
Navigation and About link to the new section. Existing articles are unchanged.

The gallery describes the chamber certificate as historical temporary membership,
not current membership. YÖK is described as academic equivalency; the course is
described as training. No new clinical licence or specialist qualification is claimed.

## Privacy review

- Reviewed all six document scans and all six final exported images visually.
- Removed portrait, parent name, birth information, nationality, student/identity
  numbers, GPA, address, registration/serial identifiers, barcode and QR code
  where present. Degree titles, holder name and issuer details remain.
- Redaction was applied to the PDF image pixels before raster export. Fresh RGB
  image encoding contains only the sanitized view, not a hidden original layer.
- The site receives only six WebP files. No source CV, PDF, unredacted scan,
  redaction working file, OCR output or private coordinates are committed.
- Containers have exactly one opaque VP8 image chunk, without EXIF, XMP,
  thumbnails, animation, attachments or trailing payloads.
- The manifest records reviewed asset hashes. Replacing an image requires a new
  visual privacy review before updating that manifest.

## Checks

- `python scripts/validate-content.py`
- `node scripts/validate-navigation.mjs` (including direct `#credentials` route)
- `python scripts/validate-credentials.py`

The checks validate file identity and structure; they do not independently detect
unredacted personal text in a new image. The originals remain unchanged privately.
