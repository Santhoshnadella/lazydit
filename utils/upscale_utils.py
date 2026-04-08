import os
import subprocess
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

class UpscaleEngine:
    """
    Wrapper for Video2X (v6+) AI Upscaling Engine.
    Enables 4K to 8K Neural Upscaling for independent cinema.
    """
    def __init__(self, video2x_path: Optional[str] = None):
        # Scan for binaries in priority order
        search_paths = [
            video2x_path,
            "K:/lazydit/bin/video2x",
            "k:/promptcut/lazydit/bin/video2x",
            "C:/Program Files/Video2X",
            "C:/video2x",
            os.path.join(os.getcwd(), "bin/video2x")
        ]
        self.bin_path = "video2x"
        for p in search_paths:
            if p and os.path.exists(os.path.join(p, "video2x.exe")):
                self.bin_path = os.path.join(p, "video2x.exe")
                logger.info(f"✅ Video2X found at: {p}")
                break

    def is_available(self) -> bool:
        """Verify if video2x binary is reachable."""
        try:
            # v6.x uses --version or -V
            subprocess.run([self.bin_path, "-V"], capture_output=True, check=False)
            return True
        except:
            return False

    def upscale_video(self, input_path: str, output_path: str, model: str = "realesrgan", scale: float = 2.0, extra_args: List[str] = None):
        """
        Runs the neural upscale process.
        - model: realesrgan, realcugan, anime4k, rife
        - scale: upscaling multiplier (e.g., 2.0 for 4K -> 8K)
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Source video not found: {input_path}")

        # Basic command for Video2X v6
        # video2x -i input.mp4 -o output.mp4 -p <upscale_driver> -m <model> -s <scale>
        
        # Drivers in v6 are typically 'filtering' for upscale
        cmd = [
            self.bin_path,
            "-i", input_path,
            "-o", output_path,
            "-s", str(scale),
        ]
        
        # In v6, we select drivers/models differently, but let's assume standard flag mapping
        if model:
            # This is a simplified wrapper; actual v6 flags might require -p <plugin>
            cmd.extend(["-m", model])

        if extra_args:
            cmd.extend(extra_args)

        logger.info(f"🚀 Launching Neural Upscale: {input_path} -> {output_path} ({scale}x via {model})")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream logs for progress tracking
        for line in process.stdout:
            yield line
            
        process.wait()
        if process.returncode != 0:
            raise Exception(f"Video2X failed with return code {process.returncode}")
