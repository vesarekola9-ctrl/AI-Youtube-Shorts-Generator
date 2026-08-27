import os
import asyncio
import shutil
import subprocess
from mutagen.wave import WAVE

class AudioEngine:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "assets", "audio_clips")
        self.songs_dir = os.path.join(os.getcwd(), "assets", "songs")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.songs_dir, exist_ok=True)

    def get_audio_duration(self, file_path):
        try:
            audio = WAVE(file_path)
            return audio.info.length
        except Exception as e:
            print(f"❌ Error reading audio length: {e}")
            return 5.0

    async def process_script(self, script_data, song_title=None, start_time=0):
        print(f"🎙️ Valmistellaan taustamusiikki (aloituskohta: {start_time}s)...")
        
        target_audio_path = os.path.join(self.output_dir, "background_music.wav")
        found = False
        
        if song_title:
            safe_name = song_title.lower().replace("ä", "a").replace("ö", "o").replace("å", "a").replace(" ", "_")
            for file in os.listdir(self.songs_dir):
                file_lower = file.lower().replace("ä", "a").replace("ö", "o").replace("å", "a")
                if safe_name in file_lower or file_lower.startswith(safe_name):
                    source_path = os.path.join(self.songs_dir, file)
                    
                    # Leikataan FFmegin avulla halutusta kohdasta tarkka pätkä taustamusiikiksi
                    print(f"🎵 Leikataan biisistä '{file}' kertosäe kohdasta {start_time}s...")
                    cut_cmd = [
                        "ffmpeg", "-y",
                        "-ss", str(start_time),
                        "-i", source_path,
                        "-t", "30",  # Shortsien mittainen pätkä (30 sekuntia)
                        "-c", "copy",
                        target_audio_path
                    ]
                    result = subprocess.run(cut_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    if result.returncode != 0:
                        cut_cmd_reencode = [
                            "ffmpeg", "-y",
                            "-ss", str(start_time),
                            "-i", source_path,
                            "-t", "30",
                            target_audio_path
                        ]
                        subprocess.run(cut_cmd_reencode, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    print(f"✅ Taustamusiikki rajattu onnistuneesti!")
                    found = True
                    break

        if not found:
            print(f"⚠️ Biisiä '{song_title}' ei löytynyt kansiosta {self.songs_dir}.")

        for scene in script_data:
            scene_id = scene['id']
            scene['audio_path'] = None 
            scene['duration'] = 5.0 
            print(f"   ✅ Scene {scene_id}: Kesto asetettu (5.00s)")

        return script_data
