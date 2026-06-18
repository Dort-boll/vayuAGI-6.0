"""Media Generator — Image and Video generation using free APIs."""
from __future__ import annotations
import requests
from ..security.dns_resolver import RESOLVER
from ..logger import get_logger

log = get_logger("media")

class MediaGenerator:
    def generate_image(self, prompt: str) -> str:
        try:
            clean_prompt = prompt.replace("generate image", "").replace("draw", "").replace("create image", "").strip()
            hostname = "image.pollinations.ai"
            ip = RESOLVER.resolve(hostname)
            
            url = f"https://{ip}/prompt/{requests.utils.quote(clean_prompt)}?width=512&height=512&nologo=true"
            headers = {'Host': hostname, 'User-Agent': 'Mozilla/5.0'}
            
            resp = requests.head(url, headers=headers, timeout=15, allow_redirects=True, verify=True)
            if resp.status_code == 200:
                return f"https://{hostname}/prompt/{requests.utils.quote(clean_prompt)}?width=512&height=512&nologo=true"
            raise Exception("Image generation service returned an error.")
        except Exception as exc:
            log.error(f"Image gen failed: {exc}")
            raise

    def generate_video(self, prompt: str) -> str:
        try:
            return f"[Video Generation Queued] To execute '{prompt}', host a local Stable Video Diffusion WebUI."
        except Exception as exc:
            log.error(f"Video gen failed: {exc}")
            return f"[Video Gen Error] {exc}"
