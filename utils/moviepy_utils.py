from moviepy import VideoFileClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.VideoClip import TextClip
import json

class TimelineBuilder:
    def parse_timeline(self, timeline_json):
        """
        Parses a JSON timeline (ShotTower style) and builds a MoviePy composition.
        """
        data = json.loads(timeline_json) if isinstance(timeline_json, str) else timeline_json
        clips = []
        
        for scene in data.get('scenes', []):
            base_clip = VideoFileClip(scene['video_path']).subclip(scene['start'], scene['end'])
            
            # Apply color/VFX if specified (usually done via ComfyUI first, but can do basic here)
            # ...
            
            # Motion Graphics / Overlays
            overlays = []
            for mg in scene.get('motion_graphics', []):
                if mg['type'] == 'text':
                    # MoviePy 2.x TextClip initialization
                    txt = TextClip(
                        text=mg['text'], 
                        font_size=mg.get('size', 70), 
                        color=mg.get('color', 'white'), 
                        font='Arial'
                    )
                    txt = txt.with_position(mg.get('position', 'center')).with_duration(mg.get('duration', 5))
                    overlays.append(txt)
            
            if overlays:
                scene_clip = CompositeVideoClip([base_clip] + overlays)
            else:
                scene_clip = base_clip
                
            clips.append(scene_clip)
            
        final_video = concatenate_videoclips(clips)
        return final_video

    def render_scene_chunk(self, scene_data, output_path):
        """Renders a single scene chunk to disk to save memory."""
        base_clip = VideoFileClip(scene_data['video_path']).subclip(scene_data['start'], scene_data['end'])
        
        overlays = []
        for mg in scene_data.get('motion_graphics', []):
            if mg['type'] == 'text':
                txt = TextClip(text=mg['text'], font_size=mg.get('size', 70), color=mg.get('color', 'white'), font='Arial')
                txt = txt.with_position(mg.get('position', 'center')).with_duration(mg.get('duration', 5))
                overlays.append(txt)
        
        final_scene = CompositeVideoClip([base_clip] + overlays) if overlays else base_clip
        final_scene.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        
        # Explicit cleanup for RAM safety
        base_clip.close()
        final_scene.close()
        return output_path
