# Offline manifest format

The release builder writes an installable ZIP and a separate `manifest.json`. All archive entries are files under the `personal-agent-growth/` root. Directory entries are omitted.

The manifest contains:

| Field | Meaning |
|---|---|
| `name` | Package root, `personal-agent-growth`. |
| `declared_version` | Version declared by the builder. |
| `files` | Map from each package-relative path to its `bytes` and lowercase SHA-256. |
| `content_hash_rule` | Literal value `SHA256 of sorted compact JSON for the files object`. |
| `content_sha256` | Hash of the UTF-8 JSON serialization of `files`, with sorted keys, compact separators, and Python's default ASCII escaping. |
| `archive.name` | Expected ZIP filename. |
| `archive.sha256` | SHA-256 of the entire ZIP. |

The content hash is calculated as:

```python
hashlib.sha256(
    json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
```

The verifier checks the archive filename and hash, exact member list, duplicate names, path form, and each expected file's size and content hash. It reads members without extracting them.

Limits: 128 files, a 1 MiB manifest, a 16 MiB ZIP, and 16 MiB total uncompressed content. Invalid inputs or exceeded limits produce `INCOMPLETE`, not a successful inspection.

The declared version is supplied metadata; the verifier does not independently parse a version from each contained file. It also does not validate Markdown references, certify safe extraction, authenticate the publisher, or check host compatibility. Someone who can replace both the archive and manifest can produce a new consistent pair. Use the project's trusted release channel to obtain the intended pair.
