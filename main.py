import os
# Varmistetaan ffmpeg polku Ubuntussa / GitHub Actionsissa
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

def get_promo_description():
    """Luo valmiin mainostekstin ja linkit videon kuvaukseen."""
    song = random.choice(ARTIST_SONGS)
    promo = (
        f"\n\n🎵 Tällä videolla fiilistellään biisiä: {song['title']}\n"
        f"🎧 Kuuntele artistiprofiili Spotifyssa: {SPOTIFY_ARTIST_URL}\n"
        f"👉 Tilaa kanava ja tsekkaa kaikki videot: {ARTIST_CHANNEL_URL}\n"
        f"Alkuperäinen kappale: {song['url']}"
    )
    return promo

def clean_cache():
    """
    Safely deletes temporary files.
    Includes a Safety Lock to prevent deleting anything outside the project.
    """
    print("🧹 Cleaning up temporary files...")
    
    # 1. Define the specific target folders
    folders_to_clean = [
        os.path.join(os.getcwd(), "assets", "audio_clips"),
        os.path.join(os.getcwd(), "assets", "video_clips"),
        os.path.join(os.getcwd(), "assets", "temp")
    ]

    for folder in folders_to_clean:
        # SAFETY CHECK 1: Ensure folder actually exists
        if not os.path.exists(folder):
            continue
            
        # SAFETY CHECK 2: Double check we are inside our project "assets" folder
        if "assets" not in folder:
            print(f"   🚨 SECURITY ALERT: Skipping {folder} because it looks unsafe!")
            continue

        # Loop through files inside the folder
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path) # Delete the file
                    print(f"     Deleted: {filename}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path) # Delete subfolders if any
            except Exception as e:
                print(f"   ❌ Failed to delete {file_path}. Reason: {e}")
    
    print("✨ Workspace clean!")

async def main():
    print("🚀 STARTING AUTOMATION (Artist Promo Mode)...")
    
    # Valitaan satunnainen biisi pohjaksi tai teemaksi
    current_song = random.choice(ARTIST_SONGS)
    print(f"🎶 Valittu teemabiisi tälle kierrokselle: {current_song['title']}")

    # 1. BRAIN: Get Script
    brain = ContentBrain()
    try:
        topic = f"Musavideo ja tarina kappaleesta {current_song['title']}"
        script = brain.generate_script(topic)
    except Exception as e:
        print(f"❌ Brain Error: {e}")
        return
    
    if not script:
        print("❌ Script generation failed.")
        return

    # 2. AUDIO: Generate Voice
    audio_engine = AudioEngine() 
    try:
        script = await audio_engine.process_script(script)
    except Exception as e:
        print(f"❌ Audio Error: {e}")
        return

    # 3. ASSETS: Get Stock Video
    asset_manager = AssetManager()
    assets_map = asset_manager.get_videos(script)

    # 4. COMPOSER: Merge Video + Audio
    composer = Composer()

    final_scene_paths = composer.render_all_scenes(script, assets_map)

    # 5. STITCH WITH TRANSITIONS
    if final_scene_paths:
        composer.concatenate_with_transitions(final_scene_paths)
        
        # 6. YOUTUBE UPLOAD
        print("🚀 Siirrytään YouTubeen lataamiseen...")
        try:
            uploader = YouTubeUploader()
            uploader.upload_short("assets/final/final_short.mp4")
            print("✅ Mainostekstit ja linkit lisätty onnistuneesti!")
        except Exception as e:
            print(f"❌ YouTube Upload Error: {e}")

        clean_cache()
    else:
        print("❌ Failed to generate any scenes.")

if __name__ == "__main__":
    asyncio.run(main())
