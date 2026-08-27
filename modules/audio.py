import os
import asyncio
import shutil
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

    async def process_script(self, script_data, song_title=None):
        print(f"🎙️ Valmistellaan taustamusiikki ja kohtaukset ({len(script_data)} kohtausta)...")
        
        target_audio_path = os.path.join(self.output_dir, "background_music.wav")
        found = False
        
        if song_title:
            safe_name = song_title.lower().replace("ä", "a").replace("ö", "o").replace("å", "a").replace(" ", "_")
            for file in os.listdir(self.songs_dir):
                file_lower = file.lower().replace("ä", "a").replace("ö", "o").replace("å", "a")
                if safe_name in file_lower or file_lower.startswith(safe_name):
                    source_path = os.path.join(self.songs_dir, file)
                    shutil.copyfile(source_path, target_audio_path)
                    print(f"🎵 Löydetty paikallinen biisi: {file} -> Asetettu taustamusiikiksi.")
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
