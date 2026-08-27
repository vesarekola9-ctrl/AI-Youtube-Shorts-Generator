import os
import random
import subprocess
import ffmpeg

class Composer:
    def __init__(self):
        self.temp_dir = os.path.join(os.getcwd(), "assets", "temp")
        self.final_dir = os.path.join(os.getcwd(), "assets", "final")
        self.audio_dir = os.path.join(os.getcwd(), "assets", "audio_clips")
        
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.final_dir, exist_ok=True)
        self.transitions = ['fade', 'diagbr', 'diagtl']

    def get_duration(self, filepath):
        try:
            probe = ffmpeg.probe(filepath)
            return float(probe['format']['duration'])
        except:
            return 0.0

    def process_scene(self, scene, video_pair):
        scene_id = scene['id']
        total_duration = scene.get('duration', 5)
        output_path = os.path.join(self.temp_dir, f"scene_{scene_id}.mp4")

        try:
            print(f"   ⚙️ Processing Scene {scene_id}: 🎞️ A/B Split Mode (Nature & Memories)")
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
        print("🎬 Luodaan kohtaukset pelkillä rauhallisilla maisema- ja muistovideoilla...")

        for i, scene in enumerate(script_data):
            current_pair = video_pairs[i]
            if current_pair is None:
                continue 

            output_path = self.process_scene(scene, current_pair)
            if output_path:
                rendered_paths.append(output_path)
        
        return rendered_paths

    def concatenate_with_transitions(self, video_paths, output_filename="final_short.mp4", music_url=None):
        print("🎬 Stitching final video and adding music from local wav...")
        output_path = os.path.join(self.final_dir, output_filename)
        
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass

        if not video_paths:
            return None

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

        bg_audio_path = os.path.join(self.audio_dir, "background_music.wav")
        has_audio = os.path.exists(bg_audio_path)

        try:
            if has_audio:
                print(f"🎵 Löydettiin paikallinen ääniraita: {bg_audio_path}, liitetään videoon...")
                audio_input = ffmpeg.input(bg_audio_path)
                
                runner = ffmpeg.output(
                    v_stream,
                    audio_input,
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    pix_fmt='yuv420p',
                    movflags='faststart',
                    shortest=None,
                    preset='medium'
                )
            else:
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
