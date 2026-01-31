# madmom-modern

A modernized fork of the [madmom](https://github.com/CPJKU/madmom) audio signal processing library, updated for **Python 3.11+** and **NumPy 2.x+**.

## About

madmom is an audio signal processing library written in Python with a strong focus on music information retrieval (MIR) tasks. This modernized version maintains full compatibility with the original madmom API while ensuring compatibility with current Python and NumPy versions.

### Key Features

- Beat and downbeat detection using recurrent neural networks
- Onset detection with multiple algorithms
- Tempo estimation
- Chord recognition
- Note transcription
- Pre-trained models included

## Changes from Original madmom

This fork includes the following modernization updates:

- **Python 3.11+ compatibility**: Updated all deprecated syntax and imports
- **NumPy 2.x+ compatibility**: Replaced deprecated NumPy type aliases (`np.float` -> `np.float64`, `np.int` -> `np.int64`, `np.bool` -> `np.bool_`)
- **collections.abc imports**: Migrated abstract base class imports from `collections` to `collections.abc`
- **Modern build system**: Added `pyproject.toml` for PEP 517/518 compliance
- **Updated Cython**: Compatible with Cython 3.x
- **Updated dependencies**: Uses latest secure versions of NumPy, SciPy, and other dependencies

## Installation

### From Source

```bash
git clone https://github.com/imcmurray/madmom-modern.git
cd madmom-modern
pip install .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Requirements

- Python >= 3.11
- NumPy >= 2.0
- SciPy >= 1.13
- Cython >= 3.0
- mido >= 1.2.8

## Quick Start

### Beat Detection

```python
import madmom

# Create a beat processor
proc = madmom.features.beats.RNNBeatProcessor()

# Process an audio file
activations = proc('audio_file.wav')

# Track beats using a DBN
dbn = madmom.features.beats.DBNBeatTrackingProcessor(fps=100)
beats = dbn(activations)

print(f"Detected beats at: {beats}")
```

### Downbeat Detection

```python
import madmom

# Create a downbeat processor
proc = madmom.features.downbeats.RNNDownBeatProcessor()

# Process an audio file
activations = proc('audio_file.wav')

# Track downbeats
dbn = madmom.features.downbeats.DBNDownBeatTrackingProcessor(
    beats_per_bar=[3, 4], fps=100
)
downbeats = dbn(activations)

print(f"Detected downbeats: {downbeats}")
```

### Onset Detection

```python
import madmom

# Create an onset processor
proc = madmom.features.onsets.RNNOnsetProcessor()

# Process an audio file
activations = proc('audio_file.wav')

# Peak picking to get onset times
onsets = madmom.features.onsets.OnsetPeakPickingProcessor(fps=100)(activations)

print(f"Detected onsets at: {onsets}")
```

## Documentation

For detailed documentation, please refer to:
- [Original madmom documentation](https://madmom.readthedocs.io/)
- [Original madmom paper](https://arxiv.org/abs/1706.00074)

## License

This project is licensed under the BSD-3-Clause License. See [LICENSE](LICENSE) for details.

The pre-trained models are licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.

## Credits

The original madmom library was developed by the Department of Computational Perception at Johannes Kepler University Linz, Austria, and the Austrian Research Institute for Artificial Intelligence (OFAI), Vienna, Austria.

### Original Authors

- Sebastian Bock
- Filip Korzeniowski
- Jan Schluter
- Florian Krebs
- Gerhard Widmer

### Citation

If you use this library in academic work, please cite the original paper:

```bibtex
@inproceedings{madmom,
   title = {{madmom: a new Python Audio and Music Signal Processing Library}},
   author = {B{\"o}ck, Sebastian and Korzeniowski, Filip and Schl{\"u}ter, Jan and Krebs, Florian and Widmer, Gerhard},
   booktitle = {Proceedings of the 24th ACM International Conference on Multimedia},
   pages = {1174--1178},
   year = {2016},
   address = {Amsterdam, The Netherlands},
   doi = {10.1145/2964284.2973795}
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
