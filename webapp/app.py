"""
Madmom Modern Web Interface

A Flask-based web application for visualizing beat and downbeat detection
using the madmom-modern library.
"""

import os
import json
import uuid
import tempfile
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

import numpy as np

# Import madmom components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import madmom
from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor
from madmom.features.downbeats import RNNDownBeatProcessor, DBNDownBeatTrackingProcessor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'ogg', 'm4a', 'aac'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_beats(filepath, fps=100, min_bpm=55, max_bpm=215, transition_lambda=100):
    """
    Process audio file to detect beats.

    Parameters
    ----------
    filepath : str
        Path to the audio file.
    fps : int
        Frames per second for processing.
    min_bpm : float
        Minimum BPM for beat tracking.
    max_bpm : float
        Maximum BPM for beat tracking.
    transition_lambda : float
        Lambda parameter for DBN transitions.

    Returns
    -------
    numpy.ndarray
        Array of beat times in seconds.
    """
    # Create beat processor
    beat_processor = RNNBeatProcessor()

    # Process audio to get activations
    activations = beat_processor(filepath)

    # Create DBN beat tracker with parameters
    beat_tracker = DBNBeatTrackingProcessor(
        fps=fps,
        min_bpm=min_bpm,
        max_bpm=max_bpm,
        transition_lambda=transition_lambda
    )

    # Get beat positions
    beats = beat_tracker(activations)

    return beats


def process_downbeats(filepath, fps=100, beats_per_bar=None, min_bpm=55, max_bpm=215,
                      transition_lambda=100):
    """
    Process audio file to detect downbeats.

    Parameters
    ----------
    filepath : str
        Path to the audio file.
    fps : int
        Frames per second for processing.
    beats_per_bar : list or None
        List of possible beats per bar (e.g., [3, 4] for 3/4 and 4/4 time).
    min_bpm : float
        Minimum BPM for beat tracking.
    max_bpm : float
        Maximum BPM for beat tracking.
    transition_lambda : float
        Lambda parameter for DBN transitions.

    Returns
    -------
    tuple
        (beats, downbeats) - Arrays of beat and downbeat times.
    """
    if beats_per_bar is None:
        beats_per_bar = [3, 4]

    # Create downbeat processor
    downbeat_processor = RNNDownBeatProcessor()

    # Process audio to get activations
    activations = downbeat_processor(filepath)

    # Create DBN downbeat tracker with parameters
    downbeat_tracker = DBNDownBeatTrackingProcessor(
        beats_per_bar=beats_per_bar,
        fps=fps,
        min_bpm=min_bpm,
        max_bpm=max_bpm,
        transition_lambda=transition_lambda
    )

    # Get beat positions with bar positions
    # Returns array of [time, beat_position] where beat_position 1 = downbeat
    results = downbeat_tracker(activations)

    # Separate beats and downbeats
    all_beats = results[:, 0].tolist()
    downbeats = results[results[:, 1] == 1, 0].tolist()

    return all_beats, downbeats, results.tolist()


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = app.config['UPLOAD_FOLDER'] / unique_filename

    file.save(filepath)

    return jsonify({
        'success': True,
        'filename': unique_filename,
        'original_name': file.filename
    })


@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/process', methods=['POST'])
def process_audio():
    """Process audio file for beat/downbeat detection."""
    data = request.get_json()

    if not data or 'filename' not in data:
        return jsonify({'error': 'No filename provided'}), 400

    filename = secure_filename(data['filename'])
    filepath = app.config['UPLOAD_FOLDER'] / filename

    if not filepath.exists():
        return jsonify({'error': 'File not found'}), 404

    # Get processing parameters
    mode = data.get('mode', 'downbeats')  # 'beats' or 'downbeats'
    fps = int(data.get('fps', 100))
    min_bpm = float(data.get('min_bpm', 55))
    max_bpm = float(data.get('max_bpm', 215))
    transition_lambda = float(data.get('transition_lambda', 100))
    beats_per_bar = data.get('beats_per_bar', [3, 4])

    # Ensure beats_per_bar is a list of integers
    if isinstance(beats_per_bar, str):
        beats_per_bar = [int(x.strip()) for x in beats_per_bar.split(',')]
    elif isinstance(beats_per_bar, list):
        beats_per_bar = [int(x) for x in beats_per_bar]

    try:
        if mode == 'beats':
            beats = process_beats(
                str(filepath),
                fps=fps,
                min_bpm=min_bpm,
                max_bpm=max_bpm,
                transition_lambda=transition_lambda
            )

            result = {
                'success': True,
                'mode': 'beats',
                'beats': beats.tolist(),
                'downbeats': [],
                'beat_data': [[b, 1] for b in beats.tolist()],
                'num_beats': len(beats),
                'estimated_bpm': estimate_bpm(beats) if len(beats) > 1 else 0
            }
        else:
            all_beats, downbeats, beat_data = process_downbeats(
                str(filepath),
                fps=fps,
                beats_per_bar=beats_per_bar,
                min_bpm=min_bpm,
                max_bpm=max_bpm,
                transition_lambda=transition_lambda
            )

            result = {
                'success': True,
                'mode': 'downbeats',
                'beats': all_beats,
                'downbeats': downbeats,
                'beat_data': beat_data,
                'num_beats': len(all_beats),
                'num_downbeats': len(downbeats),
                'estimated_bpm': estimate_bpm(all_beats) if len(all_beats) > 1 else 0
            }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def estimate_bpm(beats):
    """Estimate BPM from beat times."""
    if len(beats) < 2:
        return 0
    intervals = np.diff(beats)
    median_interval = np.median(intervals)
    if median_interval > 0:
        return round(60.0 / median_interval, 1)
    return 0


@app.route('/cleanup', methods=['POST'])
def cleanup_file():
    """Delete uploaded file."""
    data = request.get_json()

    if not data or 'filename' not in data:
        return jsonify({'error': 'No filename provided'}), 400

    filename = secure_filename(data['filename'])
    filepath = app.config['UPLOAD_FOLDER'] / filename

    if filepath.exists():
        filepath.unlink()
        return jsonify({'success': True})

    return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
