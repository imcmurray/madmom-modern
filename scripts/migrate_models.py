#!/usr/bin/env python
"""
Script to migrate pickled model files to NumPy 2.x compatible format.

This re-saves all .pkl files in the models directory to update dtype definitions
that use align=0/1 (integers) to use align=False/True (booleans).

Usage (from the repository root, with venv activated):
    python scripts/migrate_models.py

This will eliminate the VisibleDeprecationWarning about dtype align parameter.
"""

import io
import pickle
import sys
import warnings
from pathlib import Path

# Add the parent directory to sys.path so madmom can be imported
script_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(script_dir.parent))


# Module redirections for NumPy 2.x compatibility
# NumPy 2.0 reorganized internal modules
NUMPY_MODULE_REDIRECTS = {
    'numpy.lib.shape_base': 'numpy.lib._shape_base_impl',
    'numpy.core.multiarray': 'numpy._core.multiarray',
    'numpy.core.numeric': 'numpy._core.numeric',
    'numpy.core.umath': 'numpy._core.umath',
    'numpy.core._multiarray_umath': 'numpy._core._multiarray_umath',
}


class NumpyBackwardsCompatUnpickler(pickle.Unpickler):
    """Custom unpickler that handles NumPy 2.x module reorganization."""

    def find_class(self, module, name):
        # Check if this module needs to be redirected
        if module in NUMPY_MODULE_REDIRECTS:
            module = NUMPY_MODULE_REDIRECTS[module]
        return super().find_class(module, name)


def migrate_model(filepath):
    """Load and re-save a single model file.

    Returns True if successful, False if skipped due to missing dependencies.
    """
    print(f"  Migrating: {filepath.name}...", end=" ", flush=True)

    # Load with latin1 encoding for Python 2 compatibility
    # Use custom unpickler to handle NumPy 2.x module changes
    with open(filepath, 'rb') as f:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            unpickler = NumpyBackwardsCompatUnpickler(f, encoding='latin1')
            obj = unpickler.load()

    # Re-save with current pickle protocol
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)

    print("done")
    return True


def main():
    # Find the models directory
    script_dir = Path(__file__).parent
    models_dir = script_dir.parent / "madmom" / "models"

    if not models_dir.exists():
        print(f"Error: Models directory not found at {models_dir}")
        return 1

    # Find all .pkl files
    pkl_files = list(models_dir.rglob("*.pkl"))

    if not pkl_files:
        print("No .pkl files found")
        return 0

    print(f"Found {len(pkl_files)} model files to migrate\n")

    # Track results
    migrated = 0
    skipped = []

    # Group by subdirectory for better output
    current_dir = None
    for filepath in sorted(pkl_files):
        parent = filepath.parent.relative_to(models_dir)
        if parent != current_dir:
            current_dir = parent
            print(f"\n{parent}/")

        try:
            if migrate_model(filepath):
                migrated += 1
        except AttributeError as e:
            # Missing class/attribute - model uses unimplemented features
            print(f"SKIPPED (missing: {e})")
            skipped.append((filepath.relative_to(models_dir), str(e)))
        except Exception as e:
            print(f"FAILED: {e}")
            return 1

    print(f"\n\nMigrated {migrated} model files")

    if skipped:
        print(f"Skipped {len(skipped)} model files (missing layer implementations):")
        for path, reason in skipped:
            print(f"  - {path}")

    return 0


if __name__ == "__main__":
    exit(main())
