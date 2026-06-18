"""VAYU AGI 6 — Ultra-smooth, secure, responsive CustomTkinter GUI."""
from __future__ import annotations
import queue
import threading
import io
from typing import Any
import customtkinter as ctk
import requests
from PIL import Image

from ..core.orchestrator import Orchestrator
from ..memory.memory_fabric import MemoryFabric
from ..config import CONFIG

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VayuAGIApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("VAYU AGI 6 — Ultimate Cognitive OS")
        self.geometry("1400x900")
        self.minsize(1000, 700)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.orchestrator = Orchestrator()
        self.memory = MemoryFabric()
        self._result_q: queue.Queue[dict[str, Any]] = queue.Queue()
        self._pending_meta = ""
        self._current_image_ref = None

        self._build_ui()
        self._poll_results()

    def _build_ui(self) -> None:
        self.top_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#1e1e2e")
        self.top_frame.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(self.top_frame, text="VAYU AGI 6", font=("Segoe UI", 24, "bold"), text_color="#cdd6f4").pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(self.top_frame, text="Self-Reflective Multimodal OS", font=("Segoe UI", 12), text_color="#94e2d5").pack(side="left", pady=10)

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.body.grid_columnconfigure(0, weight=4)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_rowconfigure(0, weight=1)

        self.chat_frame = ctk.CTkFrame(self.body)
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.chat_display = ctk.CTkScrollableFrame(self.chat_frame, fg_color="#181825")
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.chat_display.grid_columnconfigure(0, weight=1)
        self._print_welcome()

        self.input_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.input_frame, font=("Segoe UI", 14), height=45, placeholder_text="Ask VAYU anything…", fg_color="#1e1e2e", border_color="#45475a")
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry.bind("<Return>", lambda _e: self._send())

        self.send_btn = ctk.CTkButton(self.input_frame, text="Send", width=100, height=45, command=self._send, font=("Segoe UI", 14, "bold"))
        self.send_btn.grid(row=0, column=1)

        self.sidebar = ctk.CTkFrame(self.body)
        self.sidebar.grid(row=0, column=1, sticky="nsew")
        self.sidebar.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.sidebar, text="System Status", font=("Segoe UI", 16, "bold"), text_color="#cdd6f4").pack(pady=(20, 10))
        sec_status = f"Security: {'ACTIVE' if CONFIG.doh_enabled else 'OFF'}\nDNS: 1.1.1.1 DoH\nRate Limit: {CONFIG.rate_limit_per_min}/min"
        self.stats_label = ctk.CTkLabel(self.sidebar, text=f"Memory: 0 entries\nStatus: Idle\nIntent: None\n\n{sec_status}", justify="left", font=("Consolas", 12), text_color="#a6adc8")
        self.stats_label.pack(pady=10)

        self.history_box = ctk.CTkScrollableFrame(self.sidebar, label_text="Conversation History", label_text_color="#cdd6f4", fg_color="#181825")
        self.history_box.pack(fill="both", expand=True, padx=10, pady=10)

    def _print_welcome(self) -> None:
        lbl = ctk.CTkLabel(self.chat_display, text="╔══════════════════════════════════════════╗\n║   VAYU AGI 6  •  Cognitive OS  v6.2.0    ║\n╚══════════════════════════════════════════╝\n\nFeatures:\n- Semantic Memory Cache (Cost Effective)\n- Self-Reflection Engine (High Accuracy)\n- 1.1.1.1 DoH Secure Routing\n\nTry:\n- 'Search the web for AI news'\n- 'Draw a futuristic city'", justify="left", font=("Segoe UI", 14), text_color="#cdd6f4")
        lbl.pack(anchor="w", pady=10)

    def _send(self) -> None:
        query = self.entry.get().strip()
        if not query: return
        self.entry.delete(0, "end")
        
        lbl = ctk.CTkLabel(self.chat_display, text=f"🧑 You:  {query}", justify="left", font=("Segoe UI", 14), text_color="#89b4fa")
        lbl.pack(anchor="w", pady=5)
        
        self.send_btn.configure(state="disabled", text="Thinking...")
        self.stats_label.configure(text="Memory: querying...\nStatus: Processing\nIntent: Parsing")

        threading.Thread(target=self._worker, args=(query,), daemon=True).start()

    def _worker(self, query: str) -> None:
        try:
            result = self.orchestrator.run(query)
        except Exception as exc:
            result = {"answer": f"[fatal] {exc}", "source": "error", "elapsed": 0.0, "plan": {}, "media": None}
        self._result_q.put(result)

    def _poll_results(self) -> None:
        try:
            while True:
                result = self._result_q.get_nowait()
                self._render_result(result)
        except queue.Empty:
            pass
        self.after(100, self._poll_results)

    def _render_result(self, result: dict[str, Any]) -> None:
        answer: str = result.get("answer", "")
        media = result.get("media")
        
        lbl = ctk.CTkLabel(self.chat_display, text="🤖 VAYU:", justify="left", font=("Segoe UI", 14, "bold"), text_color="#a6e3a1")
        lbl.pack(anchor="w", pady=(10, 0))

        if media and media.get("type") == "image":
            try:
                img_url = media["url"]
                resp = requests.get(img_url, timeout=20)
                img_data = Image.open(io.BytesIO(resp.content))
                ctk_img = ctk.CTkImage(img_data, size=(400, 400))
                img_lbl = ctk.CTkLabel(self.chat_display, image=ctk_img, text="")
                img_lbl.pack(anchor="w", pady=5)
                self._current_image_ref = ctk_img
            except Exception as e:
                err_lbl = ctk.CTkLabel(self.chat_display, text=f"[Image load error: {e}]", text_color="#f38ba8")
                err_lbl.pack(anchor="w")

        ans_lbl = ctk.CTkLabel(self.chat_display, text=answer, justify="left", font=("Segoe UI", 13), text_color="#cdd6f4", wraplength=800)
        ans_lbl.pack(anchor="w", pady=2)

        meta = f"[Model: {result.get('model','?')} | Source: {result.get('source','?')} | Time: {result.get('elapsed','?')}s]"
        p = result.get("plan", {})
        mem = self.memory.stats()["entries"]
        self.stats_label.configure(text=f"Memory: {mem} entries\nStatus: Idle\nIntent: {p.get('intent', '?')} / {p.get('domain', '?')}")

        meta_lbl = ctk.CTkLabel(self.chat_display, text=meta, justify="left", font=("Consolas", 10), text_color="#585b70")
        meta_lbl.pack(anchor="w", pady=(0, 10))

        lbl_h = ctk.CTkLabel(self.history_box, text=f"• {answer[:50]}...", anchor="w", font=("Segoe UI", 11), text_color="#a6adc8")
        lbl_h.pack(fill="x", padx=4, pady=2)

        self.send_btn.configure(state="normal", text="Send")
        self.chat_display._parent_canvas.yview_moveto(1.0)
