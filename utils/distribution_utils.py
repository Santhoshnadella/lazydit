import os
import subprocess
import json
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class DCPMaster:
    """
    Industrial Wrapper for OpenDCP (Digital Cinema Package) Mastering.
    Enables theatrical master dispatch from LazyDit.
    """
    def __init__(self, opendcp_path: Optional[str] = None):
        # Scan for binaries in priority order
        search_paths = [
            opendcp_path,
            "K:/lazydit/bin/opendcp",
            "k:/promptcut/lazydit/bin/cinema_engines",
            "C:/Program Files/OpenDCP",
            os.path.join(os.getcwd(), "bin/opendcp")
        ]
        self.bin_path = "opendcp"
        for p in search_paths:
            if p and os.path.exists(os.path.join(p, "opendcp_j2k.exe")):
                # Ensure we use the full path to the tools
                self.bin_path = os.path.join(p, "opendcp")
                logger.info(f"✅ Cinema Engine found at: {p}")
                break

    def detect_hdr(self, video_path: str) -> bool:
        """Detect if video has HDR metadata (Bt.2020/PQ)."""
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=color_space,color_transfer,color_primaries",
            "-of", "json", video_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            stream = data.get("streams", [{}])[0]
            # Check for HDR indicators
            is_hdr = (
                stream.get("color_transfer") == "smpte2084" or 
                stream.get("color_primaries") == "bt2020" or
                "hdr" in stream.get("color_transfer", "").lower()
            )
            return is_hdr
        except Exception as e:
            logger.warning(f"HDR detection failed: {e}")
            return False

    def extract_frames(self, video_path: str, output_dir: str, format: str = "tiff", force_hdr: Optional[bool] = None):
        """High-fidelity frame extraction for DCP mastering with HDR support."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Auto-detect HDR if not forced
        is_hdr = force_hdr if force_hdr is not None else self.detect_hdr(video_path)
        
        # Professional color space handling: 10-bit or 16-bit for HDR
        pix_fmt = "rgb48le" if is_hdr else "rgb24"
        
        logger.info(f"🎞️ Extracting frames (HDR: {is_hdr}, PixFmt: {pix_fmt})...")
        
        # -start_number 0 is critical for OpenDCP sequence naming
        cmd = [
            "ffmpeg", "-i", video_path,
            "-pix_fmt", pix_fmt,
            "-start_number", "0"
        ]
        
        if is_hdr:
            # Maintain HDR metadata during extraction if possible
            cmd.extend(["-color_primaries", "bt2020", "-color_trc", "smpte2084", "-colorspace", "bt2020nc"])
            
        cmd.append(os.path.join(output_dir, "frame_%06d." + format))
        
        return subprocess.run(cmd, capture_output=True, text=True)

    def extract_audio(self, video_path: str, output_file: str):
        """Extract theatrical PCM audio (48kHz, 24-bit)."""
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "pcm_s24le",
            "-ar", "48000", "-ac", "2",
            output_file
        ]
        return subprocess.run(cmd, capture_output=True, text=True)

    def check_availability(self) -> dict:
        """Verify if all 3 OpenDCP tools are reachable."""
        tools = ["j2k", "mxf", "xml"]
        status = {}
        for tool in tools:
            try:
                subprocess.run([f"{self.bin_path}_{tool}", "--version"], capture_output=True, check=False)
                status[tool] = True
            except:
                status[tool] = False
        return status

    def create_j2k_sequence(self, input_dir: str, output_dir: str, profile: str = "cinema2k", bandwidth: int = 125, 
                            threads: int = 8, overwrite: bool = True, stereo: bool = False, 
                            source_color: str = "sRGB", dci_resize: str = "none", 
                            xyz: bool = True, dpx_log: bool = False, precision: int = 12):
        """Standard DCI J2K encoding with full professional parameters."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        cmd = [
            f"{self.bin_path}_j2k",
            "--input", input_dir,
            "--output", output_dir,
            "--profile", profile,
            "--bandwidth", str(bandwidth),
            "--threads", str(threads)
        ]
        
        # J2K precision for DCI is typically 12-bit
        if precision != 12:
            cmd.extend(["--precision", str(precision)])

        if overwrite: cmd.append("--overwrite")
        if stereo: cmd.append("--stereo")
        if xyz: cmd.append("--xyz")
        if dpx_log: cmd.append("--dpx_log")
        if source_color != "sRGB": 
            cmd.extend(["--color", source_color])
        if dci_resize != "none":
            cmd.extend(["--resize", dci_resize])

        logger.info(f"🚀 Mastering J2K Sequence ({profile}, {precision}-bit) with {threads} threads...")
        return subprocess.run(cmd, capture_output=True, text=True)

    def wrap_mxf(self, type: str, input_dir: str, output_file: str, fps: str = "24"):
        """High-speed MXF wrapping for Image/Audio data."""
        cmd = [
            f"{self.bin_path}_mxf",
            "--type", type,
            "--input", input_dir,
            "--output", output_file,
            "--fps", fps
        ]
        return subprocess.run(cmd, capture_output=True, text=True)

    def generate_xml_metadata(self, title: str, mxf_video: str, mxf_audio: str, output_dir: str, 
                             kind: str = "feature", rating: str = "G", annotation: str = ""):
        """DCI XML Metadata creation (The Digital Passport) with annotation and rating."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        cmd = [
            f"{self.bin_path}_xml",
            "--title", title,
            "--kind", kind,
            "--rating", rating,
            "--video", mxf_video,
            "--audio", mxf_audio,
            "--output", output_dir
        ]
        if annotation:
            cmd.extend(["--annotation", annotation])
            
        return subprocess.run(cmd, capture_output=True, text=True)

    def _parse_srt_time(self, srt_time: str) -> str:
        """Convert SRT time (00:00:20,000) to DCI time (00:00:20:000)."""
        return srt_time.replace(",", ":")

    def prepare_subtitles(self, subtitle_path: str, output_xml: str, title: str = "PRO_SUB"):
        """Convert basic SRT subtitles to Cinema XML (Interop)."""
        import uuid
        import re
        sub_id = str(uuid.uuid4())
        
        subtitles_xml = []
        if subtitle_path.lower().endswith(".srt"):
            try:
                with open(subtitle_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Simple SRT Regex Parser
                pattern = re.compile(r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n((?:.+\n?)+)")
                matches = pattern.findall(content)
                
                for i, (index, start, end, text) in enumerate(matches):
                    text_clean = text.strip().replace("\n", " ")
                    subtitles_xml.append(f"""    <Subtitle SpotNumber="{i+1}" TimeIn="{self._parse_srt_time(start)}" TimeOut="{self._parse_srt_time(end)}" FadeUpTime="20" FadeDownTime="20">
      <Text HAlign="center" HPosition="0" VAlign="bottom" VPosition="8">{text_clean}</Text>
    </Subtitle>""")
            except Exception as e:
                logger.error(f"SRT Parsing failed: {e}")
                subtitles_xml = [f'    <Subtitle SpotNumber="1" TimeIn="00:00:01:000" TimeOut="00:00:04:000" FadeUpTime="20" FadeDownTime="20"><Text HAlign="center" HPosition="0" VAlign="bottom" VPosition="8">ERROR PARSING SRT</Text></Subtitle>']
        else:
            # Fallback for non-SRT
            subtitles_xml = [f'    <Subtitle SpotNumber="1" TimeIn="00:00:01:000" TimeOut="00:00:04:000" FadeUpTime="20" FadeDownTime="20"><Text HAlign="center" HPosition="0" VAlign="bottom" VPosition="8">MASTERED WITH LAZYDIT</Text></Subtitle>']

        xml_body = "\n".join(subtitles_xml)
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<DCSubtitle Version="1.0">
  <SubtitleID>{sub_id}</SubtitleID>
  <MovieTitle>{title}</MovieTitle>
  <ReelNumber>1</ReelNumber>
  <Language>English</Language>
  <Font Color="FFFFFFFF" Effect="shadow" EffectColor="FF000000" Italic="no" Size="42" Underline="no">
{xml_body}
  </Font>
</DCSubtitle>"""
        
        with open(output_xml, "w", encoding="utf-8") as f:
            f.write(xml_content)
        return output_xml

    def full_dispatch(self, title: str, source_video: str, source_audio: Optional[str] = None, 
                      subtitle_path: Optional[str] = None,
                      spatial_mode: str = "Standard 5.1",
                      spatial_profile: str = "atmos",
                      job_dir: str = "K:/lazydit/exports/DCP_JOB"):
        """
        End-to-end mastering pipeline (Pro Workflow).
        Integrates J2K Encoding (1) and XML Passport generation (3).
        Yields progress updates.
        """
        # 0. Setup Job Structure
        paths = {
            "frames": os.path.join(job_dir, "raw_frames"),
            "j2k": os.path.join(job_dir, "j2c"),
            "mxf": os.path.join(job_dir, "mxf"),
            "dcp": os.path.join(job_dir, "FINAL_DCP"),
            "audio_wav": os.path.join(job_dir, "audio.wav"),
            "subs_xml": os.path.join(job_dir, "subtitles.xml")
        }
        for p in paths.values():
            if not os.path.exists(p) and not p.endswith((".wav", ".xml")):
                os.makedirs(p)

        # 1. Extraction (Visual Essence)
        yield "🎞️ Stage 1/6: Extracting high-fidelity frames..."
        self.extract_frames(source_video, paths["frames"])

        # 2. Audio Preparation
        yield "🔊 Stage 2/6: Extracting and spatializing audio essence..."
        audio_src = source_audio if source_audio else source_video
        raw_wav = os.path.join(job_dir, "raw_audio.wav")
        self.extract_audio(audio_src, raw_wav)
        
        # Apply Spatial Logic (Atmos/HeSuVi)
        from .pedalboard_utils import AudioMaster, SpatialAudioEngine
        am = AudioMaster()
        
        layout = '5.1' if "5.1" in spatial_mode else '7.1.4'
        yield f"🎧 Mixing for {layout} ({spatial_mode})..."
        am.create_cinema_mix(raw_wav, paths["audio_wav"], layout=layout)
        
        if "Binaural" in spatial_mode:
            yield f"🧤 Virtualizing 3D Binaural ({spatial_profile})..."
            sae = SpatialAudioEngine()
            sae.virtualize_binaural(paths["audio_wav"], os.path.join(job_dir, "preview_binaural.wav"), profile=spatial_profile)

        # 3. Subtitle Preparation (Item 1)
        if subtitle_path:
            yield "✒️ Stage 3/6: Preparing Digital Cinema Subtitles..."
            self.prepare_subtitles(subtitle_path, paths["subs_xml"], title=title)
        else:
            yield "⏭️ Stage 3/6: No subtitles provided, skipping..."

        # 4. J2K Conversion (The Core Engine - Item 1)
        yield "💎 Stage 4/6: Encoding JPEG 2000 sequence (DCI compliant)..."
        # Force XYZ transform for DCI compliance
        self.create_j2k_sequence(paths["frames"], paths["j2k"], xyz=True)

        # 5. MXF Wrapping (Packaging)
        yield "📦 Stage 5/6: Wrapping essences into MXF containers..."
        video_mxf = os.path.join(paths["mxf"], "video.mxf")
        audio_mxf = os.path.join(paths["mxf"], "audio.mxf")
        self.wrap_mxf("picture", paths["j2k"], video_mxf)
        self.wrap_mxf("audio", paths["audio_wav"], audio_mxf)
        
        if subtitle_path:
            sub_mxf = os.path.join(paths["mxf"], "subtitles.mxf")
            self.wrap_mxf("subtitle", paths["subs_xml"], sub_mxf)

        # 6. XML Passport (Item 3)
        yield "📜 Stage 6/6: Generating Digital Passport (XML Metadata)..."
        self.generate_xml_metadata(title, video_mxf, audio_mxf, paths["dcp"])

        yield f"✅ Mastering Complete! DCP saved at: {paths['dcp']}"
