import os
import random
import sys
import subprocess
import ffmpeg

class Composer:
    def __init__(self):
        self.temp_dir = os.path.join(os.getcwd(), "assets", "temp")
        self.final_dir = os.path.join(os.getcwd(), "assets", "final")
        self.avatar_path = os.path.join(os.getcwd(), "assets", "avatar", "avatars.mp4")
        
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.final_dir, exist_ok=True)
        self.transitions = ['fade', 'diagbr', 'diagtl']

    def get_duration(self, filepath):
        try:
            probe = ffmpeg.probe(filepath)
            return float(probe['format']['duration'])
        except:
            return 0.0

    def process_scene(self, scene, video_pair, is_avatar=False):
        scene_id = scene['id']
        total_duration = scene.get('duration', 5)
        output_path = os.path.join(self.temp_dir, f"scene_{scene_id}.mp4")

        try:
            # Koska puheääni on poistettu, luodaan tilalle lyhyt hiljainen ääniraita tai käytetään videon omaa ääntä ilman erillistä audio-inputtia
            # Tehdään ffmpeg-virrasta pelkkä videovirta tälle kohtaukselle
            if is_avatar:
                print(f"   ⚙️ Processing Scene {scene_id}: 🤖 Avatar Mode (Cropped)")
                video_stream = (
                    ffmpeg.input(video_pair[0], stream_loop=-1)
                    .trim(duration=total_duration + 0.5)
                    .setpts('PTS-STARTPTS')
                    .filter('crop', 'iw', 'ih-150', 0, 0) 
                    .filter('scale', 1080, 1920, force_original_aspect_ratio='increase')
                    .filter('crop', 1080, 1920)
                    .filter('fps', fps=30, round='up')
                )
            else:
                print(f"   ⚙️ Processing Scene {scene_id}: 🎞️ A/B Split Mode")
                path_a, path_b = video_pair
                
                duration_a = total_duration / 2
                duration_b = (total_duration / 2) + 0.5 

                stream_a = (
                    ffmpeg.input(path_a, stream_loop=-1)
                    .trim(duration=duration_a)
                    .setpts('PTS-STARTPTS')
                    .filter('scale', 1080, 1920).filter('crop', 1080, 1920)
                    .filter('fps', fps=30, round='up')
                )

                stream_b = (
                    ffmpeg.input(path_b, stream_loop=-1)
                    .trim(duration=duration_b)
                    .setpts('PTS-STARTPTS')
                    .filter('scale', 1080, 1920).filter('crop', 1080, 1920)
                    .filter('fps', fps=30, round='up')
                )

                video_stream = ffmpeg.concat(stream_a, stream_b, v=1, a=0)

            # Tallennetaan kohtaus ilman erillistä puhetta (lisätään taustamusiikki vasta lopussa concatenate-vaiheessa)
            runner = ffmpeg.output(
                video_stream, 
                output_path, 
                vcodec='libx264', 
                pix_fmt='yuv420p',
                r=30
            )
            
            args = ffmpeg.compile(runner)
            args[0] = 'ffmpeg'
            subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return output_path

        except Exception as e:
            print(f"❌ Render Fail Scene {scene_id}: {str(e)}")
            return None

    def render_all_scenes(self, script_data, video_pairs):
        rendered_paths = []
        avatar_indices = []
        
        if len(script_data) >= 4 and os.path.exists(self.avatar_path):
            valid_range = list(range(1, len(script_data) - 1))
            count_to_pick = 2 if len(valid_range) >= 2 else 1
            avatar_indices = random.sample(valid_range, count_to_pick)
            avatar_indices.sort()
            human_readable_indices = [i + 1 for i in avatar_indices]
            print(f"🎲 Avatar set for Scenes: {human_readable_indices}")

        for i, scene in enumerate(script_data):
            current_pair = video_pairs[i]
            is_avatar = False

            if i in avatar_indices:
                current_pair = (self.avatar_path, None)
                is_avatar = True
            elif current_pair is None:
                continue 

            output_path = self.process_scene(scene, current_pair, is_avatar)
            if output_path:
                rendered_paths.append(output_path)
        
        return rendered_paths

    def concatenate_with_transitions(self, video_paths, output_filename="final_short.mp4", music_url=None):
        print("🎬 Stitching final video and adding music...")
        output_path = os.path.join(self.final_dir, output_filename)
        
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass

        if not video_paths:
            return None

        # Yhdistetään kohtaukset ja ladataan taustalle taustamusiikki (tai pelkkä videon yhdistely jos musaa ei haeta suoraan)
        input1 = ffmpeg.input(video_paths[0])
        v_stream = input1.video
        
        current_dur = self.get_duration(video_paths[0])

        for i in range(1, len(video_paths)):
            next_clip = ffmpeg.input(video_paths[i])
            next_dur = self.get_duration(video_paths[i])
            
            trans_dur = 0.5
            offset = current_dur - trans_dur
            
            effect = random.choice(self.transitions)
            print(f"   ✨ Transition {i}: '{effect}' at {offset:.2f}s")

            v_stream = ffmpeg.filter(
                [v_stream, next_clip.video], 
                'xfade', 
                transition=effect, 
                duration=trans_dur, 
                offset=offset
            )
            
            current_dur = (current_dur + next_dur) - trans_dur

        try:
            # Jos meillä on biisin url, ladataan se tai liitetään taustalle, tai tehdään perus shortsi ilman äänivirheen riskiä
            runner = ffmpeg.output(
                v_stream, 
                output_path, 
                vcodec='libx264',    
                pix_fmt='yuv420p',  
                movflags='faststart', 
                preset='medium' 
            )
            
            args = ffmpeg.compile(runner)
            args[0] = 'ffmpeg'
            subprocess.run(args, check=True)
            print(f"✅ FINAL VIDEO SAVED: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Stitching Error: {str(e)}")
            return None
