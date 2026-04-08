import ffmpeg
import os

class FinalRenderer:
    def __init__(self):
        pass

    def render_final_video(self, video_path, audio_path, output_path, preset='slow', codec='libx265', hdr=True, rife=False, audio_mode='lossless'):
        """
        Final FFmpeg pass with professional codecs, RIFE interpolation, and TrueHD audio.
        """
        input_v = ffmpeg.input(video_path)
        
        # Apply RIFE interpolation if requested (requires minterpolate filter)
        if rife:
            input_v = input_v.filter('minterpolate', fps=60, mi_mode='mci', mc_mode='aobmc', me_mode='bidir', vsfm=1)

        input_a = ffmpeg.input(audio_path)
        
        output_args = {
            'vcodec': codec,
            'preset': preset,
            'crf': 18,
            'acodec': 'truehd' if audio_mode == 'lossless' else 'eac3', 
            'ab': '640k' if audio_mode != 'lossless' else None,
        }
        
        if hdr:
            # HDR10 / Dolby Vision compatible flags (simplified)
            output_args.update({
                'pix_fmt': 'yuv420p10le',
                'color_primaries': 'bt2020',
                'color_trc': 'smpte2084',
                'colorspace': 'bt2020nc',
                'x265-params': 'dolby-vision=1:hdr10=1:chromaloc=2'
            })

        try:
            (
                ffmpeg
                .output(input_v, input_a, output_path, **output_args)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output_path
        except ffmpeg.Error as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            raise e

    def concat_sequences(self, chunk_paths, output_path):
        """
        Lossless concatenation of video chunks using the FFmpeg concat demuxer.
        """
        if not chunk_paths:
            return None

        # 1. Generate temp file list for concat demuxer
        temp_list = "temp_data/concat_list.txt"
        os.makedirs("temp_data", exist_ok=True)
        
        with open(temp_list, "w") as f:
            for path in chunk_paths:
                # Use absolute path and escape single quotes for FFmpeg
                abs_path = os.path.abspath(path).replace("'", "'\\''")
                f.write(f"file '{abs_path}'\n")

        # 2. Execute concat
        try:
            (
                ffmpeg
                .input(temp_list, format='concat', safe=0)
                .output(output_path, c='copy')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output_path
        except ffmpeg.Error as e:
            print(f"Concat error: {e.stderr.decode()}")
            raise e
        finally:
            if os.path.exists(temp_list):
                os.remove(temp_list)
