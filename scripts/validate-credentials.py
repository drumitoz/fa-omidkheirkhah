"""Verify that publication contains only the six visually reviewed raster files.

Hashes lock the reviewed pixels; this test cannot replace visual redaction review
when a certificate is changed. Originals and redaction working files stay private.
"""
from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'content/credentials-publication.json').read_text())
expected = {entry['path'] for entry in manifest['files']}
actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'assets/credentials').rglob('*') if p.is_file()}
assert len(expected) == 6 and actual == expected, 'Unexpected or missing certificate assets'
index = (ROOT / 'index.html').read_text()
for entry in manifest['files']:
    path = entry['path']
    data = (ROOT / path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == entry['sha256'], f'Unreviewed bytes: {path}'
    assert data[:4] == b'RIFF' and data[8:12] == b'WEBP'
    assert len(data) == struct.unpack('<I', data[4:8])[0] + 8, f'Trailing data: {path}'
    # A single VP8 chunk: no EXIF/XMP, alpha, animation, attachments or thumbnail.
    assert data[12:16] == b'VP8 ', f'Unexpected chunk: {path}'
    chunk_size = struct.unpack('<I', data[16:20])[0]
    assert len(data) == 20 + chunk_size + chunk_size % 2
    assert f'src="{path}' in index and f'href="{path}' in index
assert 'cv-private' not in index and 'sanitized-intermediate' not in index
print('PASS: six reviewed opaque raster images; hashes, complete containers, no metadata or embedded originals; gallery uses only reviewed assets.')
