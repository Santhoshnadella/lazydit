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
            "C:/Program Files/OpenDCP",
            os.path.join(os.getcwd(), "bin/opendcp")
        ]
        self.bin_path = "opendcp"
        for p in search_paths:
            if p and os.path.exists(os.path.join(p, "opendcp_j2k.exe")):
                self.bin_path = os.path.join(p, "opendcp")
                break

    def extract_frames(self, video_path: str, output_dir: str, format: str = "tiff"):
        """High-fidelity frame extraction for DCP mastering."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # -start_number 0 is critical for OpenDCP sequence naming
        cmd = [
            "ffmpeg", "-i", video_path,
            "-pix_fmt", "rgb24",
            "-start_number", "0",
            os.path.join(output_dir, "frame_%06d." + format)
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
                            xyz: bool = True, dpx_log: bool = False):
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
        
        if overwrite: cmd.append("--overwrite")
        if stereo: cmd.append("--stereo")
        if xyz: cmd.append("--xyz")
        if dpx_log: cmd.append("--dpx_log")
        if source_color != "sRGB": 
            cmd.extend(["--color", source_color])
        if dci_resize != "none":
            cmd.extend(["--resize", dci_resize])

        logger.info(f"🚀 Mastering J2K Sequence with {threads} threads...")
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

    def full_dispatch(self, title: str, source_video: str, source_audio: str, job_dir: str):
        """End-to-end mastering pipeline (Pro Workflow)."""
        # This would involve extracting frames from video first, then j2k, then mxf, then xml.
        # This is the 'Robust' part of the Hollywood expansion.
        pass
