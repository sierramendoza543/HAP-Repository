#!/usr/bin/env python3
"""Walks every town JSON, finds pdf-kind sources, computes a sha256 of the
mirrored local file, and stamps it as content_hash so the /api/check route
has a baseline to compare a fresh download against."""
import json, os, hashlib, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOWNS_DIR = os.path.join(ROOT, "data", "towns")
PUBLIC_DIR = os.path.join(ROOT, "public")

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def stamp_source(src):
    if src.get("kind") == "pdf" and src.get("file"):
        local_path = os.path.join(PUBLIC_DIR, src["file"].lstrip("/"))
        if os.path.exists(local_path):
            src["content_hash"] = sha256_of(local_path)
            src["mirrored_size_bytes"] = os.path.getsize(local_path)
    return src

count = 0
for fp in glob.glob(os.path.join(TOWNS_DIR, "*.json")):
    with open(fp) as f:
        town = json.load(f)
    town["primary_source"] = stamp_source(town["primary_source"])
    for var in town["variables"]:
        var["source"] = stamp_source(var["source"])
    for m in town["nza_metrics"]:
        m["source"] = stamp_source(m["source"])
    with open(fp, "w") as f:
        json.dump(town, f, indent=2, ensure_ascii=False)
    count += 1

print(f"Stamped content_hash on pdf sources in {count} town files")
