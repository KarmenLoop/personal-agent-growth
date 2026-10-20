#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Check an offline skill ZIP against its supplied manifest using only stdlib.

Exit 0: consistent; 1: completed inspection found an inconsistent archive;
2: invocation, manifest, read or resource-limit error prevented full inspection.
This verifies consistency, not publisher authenticity or host compatibility.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import platform
import re
import sys
import zipfile

MAX_BYTES = 16 * 1024 * 1024
MAX_MANIFEST = 1024 * 1024
MAX_FILES = 128
HASH = re.compile(r"[0-9a-f]{64}")
RULE = "SHA256 of sorted compact JSON for the files object"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_bounded(path, limit):
    with path.open("rb") as source:
        data = source.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Input exceeds byte limit: " + str(path))
    return data


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate manifest key: " + key)
        value[key] = item
    return value


def safe_relative(name):
    return (isinstance(name, str) and bool(name) and
            "\\" not in name and "\x00" not in name and
            all(part not in ("", ".", "..") for part in name.split("/")) and
            ":" not in name)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_manifest(manifest):
    require(isinstance(manifest, dict), "Manifest must be an object")
    name = manifest.get("name")
    require(safe_relative(name) and "/" not in name, "Invalid package root")
    require(isinstance(manifest.get("declared_version"), str) and
            bool(manifest["declared_version"]), "Missing declared version")
    require(manifest.get("content_hash_rule") == RULE, "Unsupported content hash rule")
    files = manifest.get("files")
    require(isinstance(files, dict) and 0 < len(files) <= MAX_FILES,
            "Invalid file map or file count")
    total = 0
    for path, record in files.items():
        require(safe_relative(path), "Unsafe manifest path: " + str(path))
        require(isinstance(record, dict), "Invalid file record")
        size = record.get("bytes")
        require(type(size) is int and 0 <= size <= MAX_BYTES, "Invalid file size")
        require(isinstance(record.get("sha256"), str) and
                HASH.fullmatch(record["sha256"]), "Invalid file digest")
        total += size
    require(total <= MAX_BYTES, "Uncompressed package exceeds limit")
    archive = manifest.get("archive")
    require(isinstance(archive, dict), "Missing archive record")
    require(safe_relative(archive.get("name")) and "/" not in archive["name"],
            "Invalid archive name")
    require(isinstance(archive.get("sha256"), str) and
            HASH.fullmatch(archive["sha256"]), "Invalid archive digest")
    require(isinstance(manifest.get("content_sha256"), str) and
            HASH.fullmatch(manifest["content_sha256"]), "Invalid content digest")
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    require(digest(canonical) == manifest["content_sha256"],
            "Manifest content_sha256 does not match its file map")


def verify(archive_path, manifest_path):
    result = {
        "verifier_version": "1.0.0",
        "status": "INCOMPLETE",
        "stage": "read_inputs",
        "scope": "Supplied manifest and archive identity/content consistency only",
        "publisher_authenticated": False,
        "environment": {"python": sys.version, "executable": sys.executable,
                        "platform": platform.platform()},
        "verifier_sha256": digest(Path(__file__).read_bytes()),
        "inputs": {},
        "checks": [],
    }
    try:
        raw_manifest = read_bounded(manifest_path, MAX_MANIFEST)
        result["inputs"]["manifest"] = {
            "path": str(manifest_path), "bytes": len(raw_manifest),
            "sha256": digest(raw_manifest)}
        result["stage"] = "validate_manifest"
        manifest = json.loads(raw_manifest, object_pairs_hook=unique_object)
        validate_manifest(manifest)
        result["declared_package"] = {
            "name": manifest["name"], "version": manifest["declared_version"],
            "content_sha256": manifest["content_sha256"]}
        result["stage"] = "read_archive"
        archive_bytes = read_bounded(archive_path, MAX_BYTES)
        result["inputs"]["archive"] = {
            "path": str(archive_path), "bytes": len(archive_bytes),
            "sha256": digest(archive_bytes)}
        result["stage"] = "inspect_archive"

        def check(name, expected, actual):
            result["checks"].append({
                "name": name, "passed": expected == actual,
                "expected": expected, "actual": actual})

        check("archive_name", manifest["archive"]["name"], archive_path.name)
        check("archive_sha256", manifest["archive"]["sha256"], digest(archive_bytes))
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            members = archive.infolist()
            require(len(members) <= MAX_FILES, "Archive member limit exceeded")
            require(sum(i.file_size for i in members) <= MAX_BYTES,
                    "Uncompressed archive limit exceeded")
            names = [i.filename for i in members]
            expected = {manifest["name"] + "/" + path: record
                        for path, record in manifest["files"].items()}
            check("unique_members", len(names), len(set(names)))
            check("exact_member_list", sorted(expected), sorted(names))
            check("safe_member_paths", True, all(safe_relative(n) for n in names))
            total_read = 0
            for index, member in enumerate(members):
                # Inspect expected entries only. No archive member is extracted.
                if member.filename not in expected:
                    continue
                with archive.open(member) as stream:
                    data = stream.read(MAX_BYTES - total_read + 1)
                total_read += len(data)
                require(total_read <= MAX_BYTES, "Actual uncompressed byte limit exceeded")
                record = expected[member.filename]
                prefix = "member[{}]:{}".format(index, member.filename)
                check(prefix + ":bytes", record["bytes"], len(data))
                check(prefix + ":sha256", record["sha256"], digest(data))
        result["stage"] = "completed_inspection"
        failed = [c["name"] for c in result["checks"] if not c["passed"]]
        result["failed_checks"] = failed
        result["status"] = "REJECT" if failed else "PASS"
        return result, 1 if failed else 0
    except zipfile.BadZipFile as error:
        result.update(status="REJECT", error_type=type(error).__name__, error=str(error))
        result["failed_checks"] = ["zip_structure_or_crc"]
        return result, 1
    except (OSError, ValueError, RuntimeError, NotImplementedError) as error:
        result.update(status="INCOMPLETE", error_type=type(error).__name__, error=str(error))
        return result, 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    result, code = verify(args.archive.resolve(), args.manifest.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
