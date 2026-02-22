import os
from service import VoiceGenerator

# Define the voices matches backend/main.py
VOICES = [
    {"id": "p226", "name": "Male 1 (p226)"},
    {"id": "p259", "name": "Male 2 (p259)"},
    {"id": "p247", "name": "Male 3 (p247)"},
    {"id": "p260", "name": "Male 4 (p260)"},
    {"id": "p245", "name": "Male 5 (p245)"},
    {"id": "p230", "name": "Female 1 (p230)"}, 
    {"id": "p236", "name": "Female 2 (p236)"},
    {"id": "p225", "name": "Speaker 8 (p225)"},
    {"id": "p227", "name": "Speaker 9 (p227)"},
    {"id": "p228", "name": "Speaker 10 (p228)"},
    {"id": "p229", "name": "Speaker 11 (p229)"},
    {"id": "p231", "name": "Speaker 12 (p231)"},
    {"id": "p232", "name": "Speaker 13 (p232)"},
    {"id": "p233", "name": "Speaker 14 (p233)"},
    {"id": "p234", "name": "Speaker 15 (p234)"},
    {"id": "p237", "name": "Speaker 16 (p237)"},
    {"id": "p238", "name": "Speaker 17 (p238)"},
    {"id": "p239", "name": "Speaker 18 (p239)"},
    {"id": "p240", "name": "Speaker 19 (p240)"},
    {"id": "p241", "name": "Speaker 20 (p241)"},
    {"id": "p243", "name": "Speaker 21 (p243)"},
    {"id": "p244", "name": "Speaker 22 (p244)"},
    {"id": "p246", "name": "Speaker 23 (p246)"},
    {"id": "p248", "name": "Speaker 24 (p248)"},
    {"id": "p249", "name": "Speaker 25 (p249)"}
]

# Ensure demos directory exists
DEMO_DIR = os.path.join("generated_voices", "demos")
os.makedirs(DEMO_DIR, exist_ok=True)

def generate_demos():
    print("Initializing VoiceGenerator...")
    gen = VoiceGenerator()
    
    print(f"Generating {len(VOICES)} demo files...")
    
    for voice in VOICES:
        voice_id = voice["id"]
        # Creating a specific text for each speaker or generic
        text = f"Hello. I am {voice['name']}. This is a demo of my voice."
        
        output_path = os.path.join(DEMO_DIR, f"{voice_id}.wav")
        
        if os.path.exists(output_path):
            print(f"Skipping {voice_id}, already exists.")
            continue
            
        print(f"Generating demo for {voice_id}...")
        # We use the internal tts_to_file directly or the generate method. 
        # Using tts.tts_to_file directly to avoid the uuid/temp logic of the service class for simple single file
        try:
            gen.tts.tts_to_file(
                text=text, 
                file_path=output_path, 
                speaker=voice_id, 
                speed=1.0
            )
            print(f"Saved to {output_path}")
        except Exception as e:
            print(f"Failed to generate {voice_id}: {e}")

if __name__ == "__main__":
    generate_demos()
