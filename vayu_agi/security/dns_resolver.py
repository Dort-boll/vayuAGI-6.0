"""Cloudflare 1.1.1.1 DNS-over-HTTPS (DoH) Resolver."""
from __future__ import annotations
import requests
import socket
from ..config import CONFIG
from ..logger import get_logger

log = get_logger("doh")

class DoHResolver:
    def __init__(self):
        self.enabled = CONFIG.doh_enabled
        self.endpoint = CONFIG.doh_endpoint
        self._cache: dict[str, str] = {}

    def resolve(self, hostname: str) -> str:
        if not self.enabled:
            return socket.gethostbyname(hostname)
            
        if hostname in self._cache:
            return self._cache[hostname]

        try:
            headers = {"accept": "application/dns-json"}
            params = {"name": hostname, "type": "A"}
            resp = requests.get(self.endpoint, headers=headers, params=params, timeout=5)
            resp.raise_for_status()
            
            data = resp.json()
            if data.get("Answer"):
                ip = data["Answer"][0]["data"]
                self._cache[hostname] = ip
                log.debug(f"DoH Resolved {hostname} -> {ip}")
                return ip
        except Exception as e:
            log.warning(f"DoH failed for {hostname}, falling back to system DNS: {e}")
            
        return socket.gethostbyname(hostname)

RESOLVER = DoHResolver()
