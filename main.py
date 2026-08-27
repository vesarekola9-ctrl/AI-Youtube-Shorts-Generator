import os
os.environ["PATH"] += os.pathsep + "/usr/bin"

import asyncio
import shutil
import random
from modules.brain import ContentBrain
from modules.asset_manager import AssetManager
from modules.composer import Composer
from modules.upload import YouTubeUploader

# =====================================================================
# ARTISTIN KANAVA, SPOTIFY JA BIISILISTA
# =====================================================================
ARTIST_CHANNEL_URL = "https://www.youtube.com/channel/UC_yIS6wcTTaubHKBXHhFvYQ"
SPOTIFY_ARTIST_URL = "https://open.spotify.com/artist/2Dfd0WHvgWt2kRsxfbAkxl?si=lSD1kv3nTpeyram0drBKZg"
CHANNEL_HANDLE = "@FuturaBot1"

ARTIST_SONGS = [
    {"title": "Nuori elämä", "url": "https://www.youtube.com/watch?v=W4XruKLK2-c"},
    {"title": "Isä", "url": "https://www.youtube.com/watch?v=gkpRCcQtSzo"},
    {"title": "Äiti", "url": "https://www.youtube.com/watch?v=OxYVgqrJYD8"},
    {"title": "Jäljet tunturissa", "url": "https://www.youtube.com/watch?v=nMihlPyXs8U"}
]

def get_unique_title_and_description(song):
    titles = [
        f"Fiilistelyä: {song['title']} #Shorts",
        f"Musafiiliksiä - {song['title']} #Music",
        f"Tänään kuuntelussa: {song['title']} #Shorts",
        f"{song['title']} - Ota mukava asento #Shorts"
    ]
    chosen_title = random.choice(titles)
    
    description = (
        f"🎵 Tällä videolla fiilistellään biisiä: {song['title']}\n"
        f"🎧 Kuuntele artistiprofiili Spotifyssa: {SPOTIFY_ARTIST_URL}\n"
        f"👉 Tilaa kanava ja tsekkaa kaikki videot: {ARTIST_CHANNEL_URL}\n"
        f"Alkuperäinen kappale: {song['url']}\n\n"
        f"#Shorts #Music #{song['title'].replace(' ', '')}"
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
    print("🚀 STARTING AUTOMATION (Dynamic Title & Music-Only Mode)...")
    
    current_song = random.choice(ARTIST_SONGS)
    video_title, video_desc = get_unique_title_and_description(current_song)
    print(f"🎶 Valittu biisi: {current_song['title']}")
    print(f"📌 Generoitu otsikko: {video_title}")

    # 1. BRAIN: Get Script / Scenes structure
    brain = ContentBrain()
    try:
        topic = f"Musavideo kappaleelle {current_song['title']}"
        script = brain.generate_script(topic)
    except Exception as e:
        print(f"❌ Brain Error: {e}")
        return
    
    if not script:
        print("❌ Script generation failed.")
        return

    # Varmistetaan että skripti on oikeassa muodossa ja lisätään tarvittavat kentät (duration & audio_path)
    if isinstance(script, list):
        scenes = script
    elif isinstance(script, dict) and "scenes" in script:
        scenes = script["scenes"]
    else:
        scenes = [{"text": "Musavideo"}]

    for scene in scenes:
        if isinstance(scene, dict):
            scene['audio_path'] = None
            scene['duration'] = 5  # Asetetaan jokaiselle kohtaukselle 5 sekunnin kesto, ettei tule KeyError

    # 2. ASSETS: Get Stock Video
    asset_manager = AssetManager()
    assets_map = asset_manager.get_videos(script)

    # 3. COMPOSER: Merge Video + Music Track
    composer = Composer()
    final_scene_paths = composer.render_all_scenes(script, assets_map)

    # 4. STITCH WITH TRANSITIONS & ADD MUSIC
    if final_scene_paths:
        composer.concatenate_with_transitions(final_scene_paths, music_url=current_song["url"])
        
        # 5. YOUTUBE UPLOAD
        print("🚀 Siirrytään YouTubeen lataamiseen...")
        try:
            uploader = YouTubeUploader()
            uploader.upload_short("assets/final/final_short.mp4", title=video_title, description=video_desc)
            print("✅ Video ladattu onnistuneesti uudella nimellä ja kuvauksella!")
        except Exception as e:
            print(f"❌ YouTube Upload Error: {e}")

        clean_cache()
    else:
        print("❌ Failed to generate any scenes.")

if __name__ == "__main__":
    asyncio.run(main())
