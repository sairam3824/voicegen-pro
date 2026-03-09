# VoiceGen SaaS Application

This project converts a script-to-voice Python script into a full-stack web application.

## Structure

- **backend/**: FastAPI application for changing text to speech.
  - `main.py`: The API server.
  - `service.py`: The core logic using Coqui TTS.
  - `generated_voices/`: Directory where audio files are saved.
- **frontend/**: React + Vite application for the user interface.
  - Modern, glassmorphism design.
  - Real-time interaction with the backend.

## Setup Instructions

### 1. Backend Setup

You need to install the required Python packages.

```bash
pip install -r requirements.txt
```

Start the backend server:

```bash
python backend/main.py
```
The server will start at `http://localhost:8000`.
*Note: The first run will download the TTS model, which may take a few minutes.*

### 2. Frontend Setup

Open a new terminal window and navigate to the frontend directory:

```bash
cd frontend
npm install
npm run dev
```

The frontend will start at `http://localhost:5173`.

## Usage

1. Open `http://localhost:5173` in your browser.
2. Enter your script in the text area. You can use `[Voice: pXXX]` tags to switch speakers.
3. Select a default speaker.
4. (Optional) Set a target duration in seconds.
5. Click **Generate Voice**.
6. Listen to the result or download the WAV file.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
