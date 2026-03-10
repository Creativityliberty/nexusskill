"""
Video Renderer
===============
Generates slideshow videos from images, optionally with audio narration.
Uses ffmpeg (must be installed on system).

Install: System package 'ffmpeg'
"""

import subprocess
import os
import tempfile
from pathlib import Path


class VideoRenderer:
    """Renders slideshow videos from images + optional audio."""

    def render(self, filepath, images=None, audio=None, duration=3,
               fps=1, resolution="1920x1080", **kwargs):
        """
        Generate a video slideshow.
        
        Args:
            filepath: Output path (.mp4)
            images: List of image file paths
            audio: Optional audio file path for narration
            duration: Seconds per image (default: 3)
            fps: Frames per second (default: 1)
            resolution: Video resolution (default: 1920x1080)
        """
        if not images:
            return {"renderer": "video", "status": "no_images"}

        # Check ffmpeg availability
        if not self._ffmpeg_available():
            return {"renderer": "video", "status": "skipped", "reason": "ffmpeg not found"}

        # Create a temporary file list for ffmpeg
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            for img in images:
                f.write(f"file '{os.path.abspath(img)}'\n")
                f.write(f"duration {duration}\n")
            # Repeat last image to avoid cut-off
            if images:
                f.write(f"file '{os.path.abspath(images[-1])}'\n")
            list_file = f.name

        try:
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat', '-safe', '0',
                '-i', list_file,
                '-vf', f'scale={resolution.replace("x", ":")}:force_original_aspect_ratio=decrease,'
                       f'pad={resolution.replace("x", ":")}:(ow-iw)/2:(oh-ih)/2:color=black',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
            ]

            if audio:
                cmd.extend(['-i', audio, '-c:a', 'aac', '-shortest'])

            cmd.append(filepath)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                return {
                    "renderer": "video",
                    "status": "error",
                    "error": result.stderr[:500]
                }

            return {
                "renderer": "video_renderer",
                "images": len(images),
                "duration_total": len(images) * duration,
                "resolution": resolution,
                "has_audio": audio is not None
            }

        finally:
            os.unlink(list_file)

    def _ffmpeg_available(self):
        """Check if ffmpeg is installed."""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
