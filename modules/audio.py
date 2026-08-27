import os
import asyncio
import subprocess
import sys
from mutagen.mp3 import MP3

class AudioEngine:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "assets", "audio_clips")
        os.makedirs(self.output_dir, exist_ok=True)

    def get_audio_duration(self, file_path):
        try:
            audio = MP3(file_path)
            return audio.info.length
        except Exception as e:
            print(f"❌ Error reading audio length: {e}")
            return 5.0 # Oletuskesto jos lukeminen epäonnistuu

    async def download_artist_song(self, song_url, output_filename="background_music.mp3"):
        """
        Lataa artistin biisin suoraan YouTubesta mp3-muotoon taustamusiikiksi Pythonin yt_dlp-modulilla.
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Jos biisi on jo ladattu, ei ladata turhaan uudestaan
        if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            print(f"🎵 Biisi löytyy valmiina: {output_path}")
            return output_path

        print(f"📥 Ladataan artistin biisi YouTubesta: {song_url}...")
        
        # Käytetään sys.executable jotta komento käyttää varmasti oikeaa Python-ympäristöä ja yt-dlp modulia
        command = [
            sys.executable, "-m", "yt_dlp",
            "-x", "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", output_path.replace(".mp3", ".%(ext)s"),
            song_url
        ]

        try:
            process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if process.returncode != 0:
                print(f"⚠️ yt-dlp varoitus/virhe: {process.stderr}")
            
            # Varmistetaan tiedoston olemassaolo
            if os.path.exists(output_path):
                print(f"✅ Biisi ladattu onnistuneesti: {output_path}")
                return output_path
            else:
                # Jos tiedostopääte on eri, etsitään kansiosta
                for file in os.listdir(self.output_dir):
                    if file.startswith("background_music"):
                        found_path = os.path.join(self.output_dir, file)
                        return found_path
                        
                raise RuntimeError("Äänitiedoston lataus epäonnistui, tiedostoa ei löytynyt.")
        except Exception as e:
            print(f"❌ Virhe biisin latauksessa: {e}")
            raise e

    async def process_script(self, script_data, song_url=None):
        """
        Valmistelee kohtaukset ja lataa taustamusiikin biisin urlista.
        """
        print(f"🎙️ Valmistellaan musiikki ja kohtaukset ({len(script_data)} kohtausta)...")
        
        if song_url:
            try:
                music_path = await self.download_artist_song(song_url)
            except Exception as e:
                print(f"⚠️ Musiikin lataus epäonnistui, jatketaan ilman erillistä biisiä: {e}")

        for scene in script_data:
            scene_id = scene['id']
            scene['audio_path'] = None 
            scene['duration'] = 5.0 
            print(f"   ✅ Scene {scene_id}: Kesto asetettu (5.00s)")

        return script_data
