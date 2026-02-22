#!/usr/bin/env python3
"""
TTS Voice Generator
- Splits script into paragraphs and generates a separate .wav per paragraph
- Adjusts speed so total duration matches your target
- Outputs to voice/ folder (DaVinci Resolve compatible)
- Male voice by default
"""

import os
import sys
import wave
import contextlib
import re
from TTS.api import TTS

# ============================================================
# EDIT THIS CONFIG FOR EACH SCRIPT
# ============================================================
SCRIPT_FILE = "scripts10.md"        # <-- change this to your script file
OUTPUT_NAME = "scripts10"           # <-- output prefix (saved as voice/scripts8_01.wav, etc.)
TARGET_DURATION = 90               # <-- total target duration in seconds
SPEAKER = "p226"                   # <-- default male voice (try: p259, p247, p260, p245, p226)
MODEL = "tts_models/en/vctk/vits" # <-- TTS model
# ============================================================

VOICE_DIR = "voice"


def get_wav_duration(filepath):
    """Get duration of a WAV file in seconds."""
    with contextlib.closing(wave.open(filepath, "r")) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)


def generate_voice():
    os.makedirs(VOICE_DIR, exist_ok=True)

    # Read the script
    try:
        with open(SCRIPT_FILE, "r") as f:
            text = f.read().strip()
    except FileNotFoundError:
        print(f"Error: '{SCRIPT_FILE}' not found.")
        sys.exit(1)

    if not text:
        print(f"Error: '{SCRIPT_FILE}' is empty.")
        sys.exit(1)

    # Split into paragraphs (non-empty lines separated by blank lines)
    raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    print(f"Script file : {SCRIPT_FILE}")
    print(f"Paragraphs  : {len(raw_paragraphs)}")
    print(f"Target time : {TARGET_DURATION}s")
    print(f"Default Spkr: {SPEAKER}")
    print("-" * 50)

    # Initialize TTS
    tts = TTS(model_name=MODEL)

    # Parse paragraphs for voice tags
    parsed_paragraphs = []
    # format: {'text': "...", 'speaker': "..."}

    current_speaker = SPEAKER
    
    for p in raw_paragraphs:
        # Check for [Voice: pXXX] tag
        match = re.match(r'^\[Voice:\s*(\w+)\]\s*(.*)', p, re.DOTALL)
        if match:
            s_tag = match.group(1)
            content = match.group(2)
            parsed_paragraphs.append({'text': content, 'speaker': s_tag})
            current_speaker = s_tag # Update current speaker context if you wanted sticky, but here we just use what's found or default
        else:
            parsed_paragraphs.append({'text': p, 'speaker': SPEAKER}) # Use default if not specified

    # Pass 1: Generate all paragraphs at normal speed to measure durations
    print("Pass 1: Generating at normal speed to measure durations...")
    natural_durations = []
    temp_paths = []

    for i, item in enumerate(parsed_paragraphs):
        para_text = item['text']
        para_speaker = item['speaker']
        
        path = os.path.join(VOICE_DIR, f"{OUTPUT_NAME}_{i+1:02d}.wav")
        temp_paths.append(path)
        
        # Determine actual speaker to use
        # If the tag is invalid for the model, it might crash, but we assume valid VCTK IDs
        print(f"  Part {i+1:02d} | Speaker: {para_speaker} | Text start: {para_text[:30]}...")
        
        tts.tts_to_file(text=para_text, file_path=path, speaker=para_speaker, speed=1.0)
        dur = get_wav_duration(path)
        natural_durations.append(dur)
        print(f"        -> Duration: {dur:.1f}s")

    total_natural = sum(natural_durations)
    print(f"  Total natural duration: {total_natural:.1f}s")

    # Pass 2: Calculate speed and regenerate
    if TARGET_DURATION > 0:
        speed = total_natural / TARGET_DURATION
        speed = max(0.5, min(speed, 2.0))
        print(f"  Calculated speed: {speed:.2f}x")
        print(f"Pass 2: Regenerating all parts at {speed:.2f}x speed...")

        total_final = 0
        for i, item in enumerate(parsed_paragraphs):
            para_text = item['text']
            para_speaker = item['speaker']
            path = temp_paths[i]
            
            tts.tts_to_file(text=para_text, file_path=path, speaker=para_speaker, speed=speed)
            dur = get_wav_duration(path)
            total_final += dur
            print(f"  Part {i+1:02d}: {dur:.1f}s -> {path}")
    else:
        print("Target duration is 0, skipping speed adjustment.")
        speed = 1.0
        total_final = total_natural

    print("-" * 50)
    print(f"Done! {len(parsed_paragraphs)} audio files saved to {VOICE_DIR}/")
    print(f"Total duration: {total_final:.1f}s (target was {TARGET_DURATION}s)")
    print()

if __name__ == "__main__":
    generate_voice()
