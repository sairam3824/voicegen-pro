import os
import wave
import contextlib
import re
import uuid
import shutil
from TTS.api import TTS


# Get absolute path to this file's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOICE_DIR = os.path.join(BASE_DIR, "generated_voices")
if not os.path.exists(VOICE_DIR):
    os.makedirs(VOICE_DIR)


def get_wav_duration(filepath):
    """Get duration of a WAV file in seconds."""
    with contextlib.closing(wave.open(filepath, "r")) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)

def combine_wavs(input_files, output_file):
    if not input_files:
        return

    data = []
    params = None
    
    for file in input_files:
        try:
            w = wave.open(file, 'rb')
            if params is None:
                params = w.getparams()
            data.append(w.readframes(w.getnframes()))
            w.close()
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if params and data:
        output = wave.open(output_file, 'wb')
        output.setparams(params)
        for d in data:
            output.writeframes(d)
        output.close()

class VoiceGenerator:
    def __init__(self):
        # We initialize the model here. This will download/load the model.
        # It might take a while on first run.
        self.model_name = "tts_models/en/vctk/vits"
        print(f"Loading TTS model: {self.model_name}...")
        # gpu=False for compatibility, but user might have GPU. Let's stick to False for safety unless requested.
        self.tts = TTS(model_name=self.model_name, progress_bar=False, gpu=False)
        print("TTS model loaded.")

    def generate(self, text, target_duration=0.0, speaker="p226"):
        request_id = str(uuid.uuid4())
        
        # Split into paragraphs (non-empty lines separated by blank lines)
        raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        
        if not raw_paragraphs:
            raw_paragraphs = [text] if text.strip() else []

        if not raw_paragraphs:
            return None

        # Parse paragraphs for voice tags
        parsed_paragraphs = []
        
        for p in raw_paragraphs:
            # Check for [Voice: pXXX] tag
            match = re.match(r'^\[Voice:\s*(\w+)\]\s*(.*)', p, re.DOTALL)
            if match:
                s_tag = match.group(1)
                content = match.group(2)
                parsed_paragraphs.append({'text': content, 'speaker': s_tag})
            else:
                parsed_paragraphs.append({'text': p, 'speaker': speaker}) 

        # Create temp directory for this request
        temp_dir = os.path.join(VOICE_DIR, f"temp_{request_id}")
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_paths = []
        natural_durations = []

        # Pass 1: Generate all paragraphs at normal speed
        print(f"[{request_id}] Pass 1: Generating at normal speed...")
        for i, item in enumerate(parsed_paragraphs):
            para_text = item['text']
            para_speaker = item['speaker']
            
            path = os.path.join(temp_dir, f"part_{i:03d}.wav")
            temp_paths.append(path)
            
            try:
                self.tts.tts_to_file(text=para_text, file_path=path, speaker=para_speaker, speed=1.0)
                dur = get_wav_duration(path)
                natural_durations.append(dur)
            except Exception as e:
                print(f"Error generating part {i}: {e}")
                # Create a silent file or skip? Better to fail or skip.
                # creating empty wave might break concatenation if params differ.
                # For now, let's just proceed.

        total_natural = sum(natural_durations)
        print(f"[{request_id}] Total natural duration: {total_natural:.2f}s")
        
        speed = 1.0
        if target_duration > 0:
            speed = total_natural / target_duration
            # Clamp speed between 0.5 and 2.0
            speed = max(0.5, min(speed, 2.0))
            print(f"[{request_id}] Calculated speed: {speed:.2f}x (Target: {target_duration}s)")

        # Pass 2: Regenerate if speed is significantly different from 1.0
        if abs(speed - 1.0) > 0.01:
             print(f"[{request_id}] Pass 2: Regenerating at {speed:.2f}x speed...")
             for i, item in enumerate(parsed_paragraphs):
                para_text = item['text']
                para_speaker = item['speaker']
                path = temp_paths[i]
                # Overwrite existing file
                self.tts.tts_to_file(text=para_text, file_path=path, speaker=para_speaker, speed=speed)
        
        # Combine files
        output_filename = f"{request_id}.wav"
        output_path = os.path.join(VOICE_DIR, output_filename)
        
        combine_wavs(temp_paths, output_path)
        
        # Cleanup temp directory
        try:
            shutil.rmtree(temp_dir)
        except OSError as e:
            print(f"Error removing temp dir {temp_dir}: {e}")
        
        return output_filename
