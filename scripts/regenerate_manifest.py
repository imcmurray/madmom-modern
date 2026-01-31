#!/usr/bin/env python
"""
Regenerate the model manifest with updated SHA256 hashes.

Usage (from the repository root):
    python scripts/regenerate_manifest.py

This updates madmom/models/model_manifest.json with fresh hashes
for all .pkl model files.
"""

import hashlib
import json
from datetime import date
from pathlib import Path


def compute_file_hash(filepath: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def main():
    # Find the models directory
    script_dir = Path(__file__).parent
    models_dir = script_dir.parent / "madmom" / "models"
    manifest_path = models_dir / "model_manifest.json"

    if not models_dir.exists():
        print(f"Error: Models directory not found at {models_dir}")
        return 1

    # Load existing manifest to preserve version info
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        version = manifest.get('version', '0.17.0')
    else:
        version = '0.17.0'

    # Find all .pkl files and compute hashes
    pkl_files = sorted(models_dir.rglob("*.pkl"))

    if not pkl_files:
        print("No .pkl files found")
        return 0

    print(f"Computing hashes for {len(pkl_files)} model files...\n")

    models = {}
    for filepath in pkl_files:
        rel_path = filepath.relative_to(models_dir)
        rel_path_str = str(rel_path).replace('\\', '/')  # Normalize for cross-platform
        file_hash = compute_file_hash(filepath)
        models[rel_path_str] = file_hash
        print(f"  {rel_path_str}: {file_hash[:16]}...")

    # Create new manifest
    new_manifest = {
        "version": version,
        "description": "SHA256 hashes for madmom model files - verify before loading to prevent pickle attacks",
        "generated": str(date.today()),
        "models": models
    }

    # Write manifest
    with open(manifest_path, 'w') as f:
        json.dump(new_manifest, f, indent=4)
        f.write('\n')

    print(f"\nUpdated {manifest_path}")
    print(f"Total models: {len(models)}")
    return 0


if __name__ == "__main__":
    exit(main())
