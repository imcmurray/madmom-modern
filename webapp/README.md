# Madmom Modern Web Interface

A browser-based interface for visualizing beat and downbeat detection using the madmom-modern library.

## Features

- Upload audio files (WAV, MP3, FLAC, OGG, M4A, AAC)
- Interactive waveform visualization with beat markers
- Visual distinction between regular beats (green) and downbeats (orange)
- Audio playback with progress tracking
- Adjustable detection parameters:
  - Detection mode (beats only or beats + downbeats)
  - BPM range (min/max)
  - Time signatures (3/4, 4/4, custom)
  - Advanced: transition lambda, FPS
- Click on beat timestamps to jump to that position
- Real-time results display (estimated BPM, beat count, bar count)

## Prerequisites

1. Python 3.11 or higher
2. madmom-modern installed (from the parent directory)

## Installation

1. First, install madmom-modern from the parent directory:

```bash
cd /path/to/madmom-modern
pip install -e .
```

2. Install webapp dependencies:

```bash
cd webapp
pip install -r requirements.txt
```

## Running the Application

```bash
cd webapp
python app.py
```

The application will start on `http://localhost:5000`

## Usage

1. **Upload a Song**: Drag and drop an audio file onto the upload area, or click to browse files.

2. **Adjust Parameters**:
   - **Detection Mode**: Choose between "Beats + Downbeats" for full bar detection, or "Beats Only" for just beat times.
   - **Min/Max BPM**: Set the tempo range to search within. Narrowing this can improve accuracy for songs with known tempo.
   - **Time Signatures**: Select which time signatures to detect. Use "Custom" for unusual meters like 5/4 or 7/8.
   - **Advanced Settings**: Click "Show Advanced" to access:
     - **Transition Lambda**: Controls how strict the beat tracking is (higher = more strict)
     - **FPS**: Frames per second for analysis (higher = more precise but slower)

3. **Analyze**: Click "Analyze Beats" to process the song. Processing time depends on song length.

4. **View Results**:
   - Beat markers appear on the waveform (green = beat, orange = downbeat)
   - Results show estimated BPM, total beats, and bar count
   - Click "Show List" to see all beat timestamps
   - Click any row in the list to jump to that beat

5. **Playback**: Use the play button to hear the song with visual beat tracking.

## Tips for Better Results

- **Known Tempo**: If you know the song's BPM, set min/max BPM close to that value (e.g., for 120 BPM, try 115-125).
- **Time Signature**: If you know the meter, select only that time signature.
- **Electronic Music**: Often works best with higher transition lambda values.
- **Live Recordings**: May need lower transition lambda to handle tempo variations.
- **Complex Rhythms**: Try adjusting FPS higher for more precise detection.

## Troubleshooting

- **Processing takes too long**: Try reducing FPS or using a shorter audio file.
- **Beats are off**: Adjust BPM range to match the actual tempo better.
- **Missing downbeats**: Make sure the correct time signature is selected.
- **File won't load**: Ensure the file is a supported format and under 50MB.

## Architecture

```
webapp/
├── app.py              # Flask backend with madmom integration
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── templates/
│   └── index.html     # Frontend HTML/CSS/JS
├── static/            # Static assets (if needed)
└── uploads/           # Temporary file storage
```

## API Endpoints

- `GET /` - Main page
- `POST /upload` - Upload audio file
- `GET /uploads/<filename>` - Serve uploaded file
- `POST /process` - Process audio for beat detection
- `POST /cleanup` - Delete uploaded file

## License

Same as madmom-modern (BSD-3-Clause for code, CC BY-NC-SA 4.0 for models).
