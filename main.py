import os
os.environ["PATH"] += os.pathsep + "/usr/bin"

import asyncio
import shutil
import random
from modules.brain import ContentBrain
from modules.asset_manager import AssetManager
from modules.audio import AudioEngine
from modules.composer import Composer
from modules.upload import YouTubeUploader

# =====================================================================
# ARTISTIN KANAVA, SPOTIFY JA BIISILISTA + ALOITUSKOHDAT (sekunteina)
# =====================================================================
ARTIST_CHANNEL_URL = "https://www.youtube.com/channel/UC_yIS6wcTTaubHKBXHhFvYQ"
SPOTIFY_ARTIST_URL = "https://open.spotify.com/artist/2Dfd0WHvgWt2kRsxfbAkxl?si=lSD1kv3nTpeyram0drBKZg"
CHANNEL_HANDLE = "@FuturaBot1"

ARTIST_SONGS = [
    {
        "title": "nuori_elama", 
        "display_name": "Nuori elämä", 
        "url": "https://www.youtube.com/watch?v=W4XruKLK2-c",
        "start_time": 94  # 1:34
    },
    {
        "title": "isa", 
        "display_name": "Isä", 
        "url": "https://www.youtube.com/watch?v=gkpRCcQtSzo",
        "start_time": 60  # 1:00
    },
    {
        "title": "aiti", 
        "display_name": "Äiti", 
        "url": "https://www.youtube.com/watch?v=OxYVgqrJYD8",
        "start_time": 143 # 2:23
    },
    {
        "title": "jaljet_tunturissa", 
        "display_name": "Jäljet tunturissa", 
        "url": "https://www.youtube.com/watch?v=nMihlPyXs8U",
        "start_time": 170 # 2:50
    }
]

def get_unique_title_and_description(song):
    titles = [
        f"Fiilistelyä: {song['display_name']} #Shorts",
        f"Musafiiliksiä - {song['display_name']} #Music",
        f"Tänään kuuntelussa: {song['display_name']} #Shorts",
        f"{song['display_name']} - Ota mukava asento #Shorts"
    ]
    chosen_title = random.choice(titles)
    
    description = (
        f"🎵 Tällä videolla fiilistellään biisiä: {song['display_name']}\n"
        f"🎧 Kuuntele koko biisi ja artistiprofiili Spotifyssa: {SPOTIFY_ARTIST_URL}\n"
        f"👉 Tilaa kanava ja tsekkaa kaikki videot: {ARTIST_CHANNEL_URL}\n"
        f"Alkuperäinen kappale: {song['url']}\n\n"
        f"#Shorts #Music #{song['display_name'].replace(' ', '')}"
    )
    return chosen_title, description

def clean_cache():
    print("🧹 Cleaning up temporary files...")
    folders_to_clean = [
        os.path.join(os.getcwd(), "assets", "audio_clips"),
        os.path.join(os.getcwd(), "assets", "video_clips"),
        os.path.join(os.getcwd(), "assets", "temp")
    ]

    for folder in folders_to_clean:
        if not os.path.exists(folder) or "assets" not in folder:
            continue
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"❌ Failed to delete {file_path}. Reason: {e}")
    print("✨ Workspace clean!")

async def main():
    print("🚀 STARTING AUTOMATION (Smart Start-Time WAV Music Mode)...")
    
    current_song = random.choice(ARTIST_SONGS)
    video_title, video_desc = get_unique_title_and_description(current_song)
    print(f"🎶 Valittu biisi: {current_song['display_name']} (Aloituskohta: {current_song['start_time']}s)")
    print(f"📌 Generoitu otsikko: {video_title}")

    # 1. BRAIN: Get Script / Scenes structure
    brain = ContentBrain()
    try:
        topic = f"Musavideo kappaleelle {current_song['display_name']}"
        script = brain.generate_script(topic)
    except Exception as e:
        print(f"❌ Brain Error: {e}")
        return
    
    if not script:
        print("❌ Script generation failed.")
        return

    # 2. AUDIO: Map local WAV file and crop from start_time
    audio_engine = AudioEngine()
    try:
        script = await audio_engine.process_script(
            script, 
            song_title=current_song["title"], 
            start_time=current_song["start_time"]
        )
    except Exception as e:
        print(f"⚠️ Audio/Music Setup Warning: {e}")

    # 3. ASSETS: Get Stock Video
    asset_manager = AssetManager()
    assets_map = asset_manager.get_videos(script)

    # 4. COMPOSER: Merge Video + Music Track
    composer = Composer()
    final_scene_paths = composer.render_all_scenes(script, assets_map)

    # 5. STITCH WITH TRANSITIONS & ADD MUSIC
    if final_scene_paths:
        composer.concatenate_with_transitions(final_scene_paths, music_url=current_song["url"])
        
        # 6. YOUTUBE UPLOAD
        print("🚀 Siirrytään YouTubeen lataamiseen...")
        try:
            uploader = YouTubeUploader()
            uploader.upload_short("assets/final/final_short.mp4", title=video_title, description=video_desc)
            print("✅ Video ladattu onnistuneesti dynaamisella nimellä, kuvauksella ja kohdennetulla musiikilla!")
        except Exception as e:
            print(f"❌ YouTube Upload Error: {e}")

        clean_cache()
    else:
        print("❌ Failed to generate any scenes.")

if __name__ == "__main__":
    asyncio.run(main())
