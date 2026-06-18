"""Web Search Engine — secured via 1.1.1.1 DoH resolution."""
from __future__ import annotations
import requests
from ..security.dns_resolver import RESOLVER
from ..logger import get_logger

log = get_logger("web")

class WebSearch:
    def search(self, query: str) -> str:
        try:
            hostname = "html.duckduckgo.com"
            ip = RESOLVER.resolve(hostname)
            
            url = f"https://{ip}/html/?q={requests.utils.quote(query)}"
            headers = {'User-Agent': 'Mozilla/5.0', 'Host': hostname}
            
            resp = requests.get(url, headers=headers, timeout=10, verify=True)
            resp.raise_for_status()
            
            text = resp.text
            start = text.find("<div class=\"links_main results_links\">")
            if start != -1:
                end = text.find("</div>", start + 500)
                snippet = text[start+500:end].replace("<b>", "").replace("</b>", "").strip()
                return f"Web search results for '{query}':\n{snippet[:500]}...\n\n(Routed securely via 1.1.1.1)"
            return f"Searched the web for '{query}'. No parseable results found."
        except Exception as exc:
            log.error(f"Web search failed: {exc}")
            return f"[Web Search Error] {exc}"
