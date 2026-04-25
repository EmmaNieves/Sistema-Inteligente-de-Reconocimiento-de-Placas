import tkinter as tk
from tkinter import font as tkfont
import threading
import cv2
import time
from PIL import Image, ImageTk
from datetime import datetime
from ultralytics import YOLO
import easyocr
from database import save_plate, init_db, plate_exists

# ──────────────────────────────────────────────
#  Colores y estilos
# ──────────────────────────────────────────────
BG          = "#0a0d14"
PANEL       = "#111827"
CARD        = "#1a2235"
BORDER      = "#1e3a5f"
ACCENT      = "#00d4ff"
ACCENT2     = "#0080ff"
GREEN       = "#00ff88"
RED         = "#ff3860"
YELLOW      = "#ffd700"
TEXT        = "#e2e8f0"
MUTED       = "#64748b"
WHITE       = "#ffffff"

# ──────────────────────────────────────────────
#  App principal
# ──────────────────────────────────────────────
class PlacasApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PLACAS DETECTOR v2.0")
        self.configure(bg=BG)
        self.geometry("1280x780")
        self.resizable(True, True)
        self.minsize(960, 640)

        # Estado
        self.mode         = tk.StringVar(value="idle")   # idle | nueva | identificar
        self.cam_running  = False
        self.cap          = None
        self.last_frame   = None
        self.status_text  = tk.StringVar(value="Selecciona un modo para comenzar")
        self.plate_result = tk.StringVar(value="—")
        self.result_type  = tk.StringVar(value="none")   # none | nueva | existente
        self.fps_val      = tk.StringVar(value="0.0")
        self.history      = []   # lista de (placa, tipo, hora)

        # Modelos (carga en hilo para no bloquear la GUI)
        self.yolo   = None
        self.reader = None
        self.models_ready = False
        threading.Thread(target=self._load_models, daemon=True).start()
        print("Hilo de modelos iniciado")
        init_db()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Carga de modelos ──────────────────────
    def _load_models(self):
        import time
        time.sleep(0.5)  # espera que Tkinter inicie
        self.yolo   = YOLO("yolov8n.pt")
        self.reader = easyocr.Reader(["es"], gpu=False)
        self.models_ready = True
        self.after(0, lambda: self.status_text.set("✅ Modelos listos — Selecciona un modo"))

    # ── Construcción de UI ────────────────────
    def _build_ui(self):
        # ── Fuentes ──
        self.font_title  = tkfont.Font(family="Courier New", size=22, weight="bold")
        self.font_label  = tkfont.Font(family="Courier New", size=10)
        self.font_plate  = tkfont.Font(family="Courier New", size=36, weight="bold")
        self.font_small  = tkfont.Font(family="Courier New", size=9)
        self.font_btn    = tkfont.Font(family="Courier New", size=12, weight="bold")
        self.font_hist   = tkfont.Font(family="Courier New", size=9)

        # ── Header ──
        header = tk.Frame(self, bg=PANEL, height=60)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        tk.Label(header, text="◈  SISTEMA DE RECONOCIMIENTO DE PLACAS",
                 font=self.font_title, fg=ACCENT, bg=PANEL).pack(side="left", padx=20, pady=12)

        self._fps_badge = tk.Label(header, textvariable=self.fps_val,
                                   font=self.font_label, fg=GREEN, bg=PANEL)
        self._fps_badge.pack(side="right", padx=20)
        tk.Label(header, text="FPS:", font=self.font_label, fg=MUTED, bg=PANEL).pack(side="right")

        # ── Separador ──
        tk.Frame(self, bg=ACCENT2, height=2).pack(fill="x")

        # ── Cuerpo principal ──
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=12)

        # Columna izquierda — cámara
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        cam_header = tk.Frame(left, bg=CARD, height=32)
        cam_header.pack(fill="x")
        cam_header.pack_propagate(False)
        tk.Label(cam_header, text="● FEED EN VIVO", font=self.font_label,
                 fg=ACCENT, bg=CARD).pack(side="left", padx=10)
        self._cam_dot = tk.Label(cam_header, text="◉ ACTIVA", font=self.font_small,
                                  fg=GREEN, bg=CARD)
        self._cam_dot.pack(side="right", padx=10)

        self.cam_canvas = tk.Canvas(left, bg="#060a12", highlightthickness=1,
                                     highlightbackground=BORDER)
        self.cam_canvas.pack(fill="both", expand=True, pady=(0, 0))
        self._draw_idle_cam()

        # Columna derecha — controles
        right = tk.Frame(body, bg=BG, width=320)
        right.pack(side="right", fill="y", padx=(14, 0))
        right.pack_propagate(False)

        # ── Tarjeta modos ──
        mode_card = tk.Frame(right, bg=CARD, relief="flat")
        mode_card.pack(fill="x", pady=(0, 10))

        tk.Label(mode_card, text="MODO DE OPERACIÓN", font=self.font_small,
                 fg=MUTED, bg=CARD).pack(anchor="w", padx=14, pady=(12, 6))

        self.btn_nueva = self._make_btn(mode_card, "＋  REGISTRAR NUEVA PLACA",
                                         ACCENT2, self._start_nueva)
        self.btn_nueva.pack(fill="x", padx=14, pady=4)

        self.btn_ident = self._make_btn(mode_card, "🔍  IDENTIFICAR PLACA",
                                         "#1a4a2a", self._start_identificar, fg=GREEN)
        self.btn_ident.pack(fill="x", padx=14, pady=4)

        self.btn_stop = self._make_btn(mode_card, "■  DETENER",
                                        "#3a1515", self._stop, fg=RED)
        self.btn_stop.pack(fill="x", padx=14, pady=(4, 12))

        # ── Tarjeta resultado ──
        self.result_card = tk.Frame(right, bg=CARD, relief="flat")
        self.result_card.pack(fill="x", pady=(0, 10))

        tk.Label(self.result_card, text="RESULTADO", font=self.font_small,
                 fg=MUTED, bg=CARD).pack(anchor="w", padx=14, pady=(12, 4))

        self.plate_badge = tk.Frame(self.result_card, bg="#0d1a2e", height=80)
        self.plate_badge.pack(fill="x", padx=14, pady=4)
        self.plate_badge.pack_propagate(False)

        self.plate_lbl = tk.Label(self.plate_badge, textvariable=self.plate_result,
                                   font=self.font_plate, fg=ACCENT, bg="#0d1a2e")
        self.plate_lbl.place(relx=0.5, rely=0.5, anchor="center")

        self.result_lbl = tk.Label(self.result_card, text="",
                                    font=self.font_label, bg=CARD, fg=TEXT)
        self.result_lbl.pack(pady=(4, 12))

        # ── Estado ──
        status_card = tk.Frame(right, bg=CARD)
        status_card.pack(fill="x", pady=(0, 10))
        tk.Label(status_card, text="ESTADO", font=self.font_small,
                 fg=MUTED, bg=CARD).pack(anchor="w", padx=14, pady=(10, 2))
        tk.Label(status_card, textvariable=self.status_text, font=self.font_small,
                 fg=TEXT, bg=CARD, wraplength=280, justify="left").pack(
                     anchor="w", padx=14, pady=(0, 10))

        # ── Historial ──
        hist_card = tk.Frame(right, bg=CARD)
        hist_card.pack(fill="both", expand=True)
        tk.Label(hist_card, text="HISTORIAL", font=self.font_small,
                 fg=MUTED, bg=CARD).pack(anchor="w", padx=14, pady=(10, 4))

        self.hist_frame = tk.Frame(hist_card, bg=CARD)
        self.hist_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ── Barra de estado inferior ──
        footer = tk.Frame(self, bg=PANEL, height=28)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        tk.Label(footer, text="YOLO v8  ·  EasyOCR  ·  SQLite",
                 font=self.font_small, fg=MUTED, bg=PANEL).pack(side="left", padx=14)
        self._clock_lbl = tk.Label(footer, text="", font=self.font_small,
                                    fg=MUTED, bg=PANEL)
        self._clock_lbl.pack(side="right", padx=14)
        self._tick_clock()

    # ── Helpers UI ────────────────────────────
    def _make_btn(self, parent, text, bg, cmd, fg=WHITE):
        return tk.Button(parent, text=text, font=self.font_btn,
                         bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                         relief="flat", cursor="hand2", command=cmd,
                         pady=10, padx=8, bd=0)

    def _draw_idle_cam(self):
        self.cam_canvas.update_idletasks()
        w = self.cam_canvas.winfo_width() or 640
        h = self.cam_canvas.winfo_height() or 480
        self.cam_canvas.delete("all")
        self.cam_canvas.create_rectangle(0, 0, w, h, fill="#060a12", outline="")
        self.cam_canvas.create_text(w//2, h//2 - 20, text="[ SIN SEÑAL ]",
                                     font=self.font_title, fill=BORDER)
        self.cam_canvas.create_text(w//2, h//2 + 20,
                                     text="Selecciona un modo para activar la cámara",
                                     font=self.font_small, fill=MUTED)

    def _tick_clock(self):
        self._clock_lbl.config(text=datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.after(1000, self._tick_clock)

    def _add_history(self, plate, tipo):
        hora = datetime.now().strftime("%H:%M:%S")
        color = GREEN if tipo == "nueva" else YELLOW
        tag = "NUEVA" if tipo == "nueva" else "EXISTE"

        row = tk.Frame(self.hist_frame, bg="#0d1a2e")
        row.pack(fill="x", pady=2)
        tk.Label(row, text=hora, font=self.font_hist, fg=MUTED, bg="#0d1a2e",
                 width=9).pack(side="left")
        tk.Label(row, text=f"[{tag}]", font=self.font_hist, fg=color, bg="#0d1a2e",
                 width=7).pack(side="left")
        tk.Label(row, text=plate, font=self.font_hist, fg=TEXT, bg="#0d1a2e").pack(side="left", padx=4)

        # Mantener últimas 8 entradas
        children = self.hist_frame.winfo_children()
        if len(children) > 8:
            children[0].destroy()

    # ── Control de modos ──────────────────────
    def _start_nueva(self):
        if not self.models_ready:
            self.status_text.set("⏳ Modelos aún cargando, espera...")
            return
        self.mode.set("nueva")
        self.plate_result.set("—")
        self.result_lbl.config(text="")
        self._start_camera()
        self.status_text.set("🔵 Modo REGISTRO — apunta la cámara a la placa")
        self.btn_nueva.config(bg="#0040a0")
        self.btn_ident.config(bg="#1a4a2a")

    def _start_identificar(self):
        if not self.models_ready:
            self.status_text.set("⏳ Modelos aún cargando, espera...")
            return
        self.mode.set("identificar")
        self.plate_result.set("—")
        self.result_lbl.config(text="")
        self._start_camera()
        self.status_text.set("🟢 Modo IDENTIFICACIÓN — apunta la cámara a la placa")
        self.btn_nueva.config(bg=ACCENT2)
        self.btn_ident.config(bg="#0a3020")

    def _stop(self):
        self.mode.set("idle")
        self.cam_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self._draw_idle_cam()
        self._cam_dot.config(text="◎ INACTIVA", fg=MUTED)
        self.status_text.set("⏹ Detenido — Selecciona un modo para comenzar")
        self.btn_nueva.config(bg=ACCENT2)
        self.btn_ident.config(bg="#1a4a2a")

    # ── Cámara ────────────────────────────────
    def _start_camera(self):
        if self.cam_running:
            return
        self.cap = cv2.VideoCapture("http://192.168.20.51:4747/video")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not self.cap.isOpened():
            self.status_text.set("❌ No se pudo abrir la cámara")
            return
        self.cam_running = True
        self._cam_dot.config(text="◉ ACTIVA", fg=GREEN)
        threading.Thread(target=self._camera_loop, daemon=True).start()

    def _camera_loop(self):
        prev_time = time.time()
        cooldown = 0  # segundos tras detección exitosa

        while self.cam_running:
            if not self.cap or not self.cap.isOpened():
                break

            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            curr_time = time.time()
            fps = 1.0 / max(curr_time - prev_time, 1e-6)
            prev_time = curr_time
            self.after(0, lambda f=f"{fps:.1f}": self.fps_val.set(f))

            detections = []
            detected_plate = None

            if cooldown > 0:
                cooldown -= curr_time - prev_time
            else:
                results = self.yolo(frame, conf=0.5, verbose=False)
                for result in results:
                    for box in result.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = float(box.conf[0])
                        crop = frame[y1:y2, x1:x2]
                        if crop.size == 0:
                            continue
                        ocr_res = self.reader.readtext(
                            crop,
                            allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"
                        )
                        for (_, text, prob) in ocr_res:
                            if prob > 0.65 and len(text) >= 5:
                                plate_text = text.upper().replace(" ", "").replace("-", "")
                                detections.append((x1, y1, x2, y2,
                                                   f"{plate_text} {conf:.0%}", (0, 255, 136)))
                                if detected_plate is None:
                                    detected_plate = (plate_text, frame.copy())
                            else:
                                detections.append((x1, y1, x2, y2,
                                                   f"? {conf:.0%}", (0, 160, 255)))

            # Dibujar overlay
            display = self._draw_frame(frame, detections, fps)
            self._update_canvas(display)

            # Procesar detección
            if detected_plate:
                plate_text, snap = detected_plate
                mode = self.mode.get()
                if mode == "nueva":
                    is_new = save_plate(plate_text, snap)
                    tipo = "nueva" if is_new else "existente"
                    msg = "✅ PLACA REGISTRADA" if is_new else "⚠️ Ya estaba registrada"
                    color = GREEN if is_new else YELLOW
                    self.after(0, lambda t=plate_text, m=msg, c=color, tp=tipo:
                               self._show_result(t, m, c, tp))
                    cooldown = 3.0
                elif mode == "identificar":
                    exists = plate_exists(plate_text)
                    tipo = "existente" if exists else "desconocida"
                    msg = "✅ PLACA IDENTIFICADA" if exists else "❌ Placa no encontrada"
                    color = GREEN if exists else RED
                    self.after(0, lambda t=plate_text, m=msg, c=color, tp=tipo:
                               self._show_result(t, m, c, tp))
                    cooldown = 3.0

            time.sleep(0.01)

    def _draw_frame(self, frame, detections, fps):
        h, w = frame.shape[:2]
        overlay = frame.copy()

        # Barra superior
        cv2.rectangle(overlay, (0, 0), (w, 50), (10, 13, 20), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        mode = self.mode.get()
        mode_txt = "● REGISTRAR NUEVA PLACA" if mode == "nueva" else \
                   "● IDENTIFICAR PLACA" if mode == "identificar" else "● EN ESPERA"
        mode_color = (0, 160, 255) if mode == "nueva" else \
                     (0, 255, 136) if mode == "identificar" else (100, 100, 100)

        cv2.putText(frame, mode_txt, (14, 34),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, mode_color, 2)
        cv2.putText(frame, f"FPS {fps:.1f}", (w - 110, 34),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 180, 200), 2)

        # Recuadros
        for (x1, y1, x2, y2, label, color) in detections:
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 8, y1), color, -1)
            cv2.putText(frame, label, (x1 + 4, y1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 13, 20), 2)

        # Barra inferior
        cv2.rectangle(frame, (0, h - 30), (w, h), (10, 13, 20), -1)
        cv2.putText(frame, "SISTEMA DE RECONOCIMIENTO DE PLACAS  |  YOLOv8 + EasyOCR",
                    (14, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 80, 100), 1)

        return frame

    def _update_canvas(self, frame):
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.cam_canvas.update_idletasks()
            cw = self.cam_canvas.winfo_width()
            ch = self.cam_canvas.winfo_height()
            if cw < 10 or ch < 10:
                return
            img = Image.fromarray(rgb).resize((cw, ch), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.cam_canvas.delete("all")
            self.cam_canvas.create_image(0, 0, anchor="nw", image=photo)
            self.cam_canvas._photo = photo  # evitar garbage collection
        except Exception:
            pass

    # ── Resultado ─────────────────────────────
    def _show_result(self, plate, msg, color, tipo):
        self.plate_result.set(plate)
        self.plate_lbl.config(fg=color)
        self.result_lbl.config(text=msg, fg=color)
        self.status_text.set(f"{msg}: {plate}")
        self._add_history(plate, "nueva" if tipo in ("nueva", "existente") else "desconocida")

        # Parpadeo del badge
        self._flash_badge(color, 3)

    def _flash_badge(self, color, n):
        if n <= 0:
            self.plate_badge.config(bg="#0d1a2e")
            self.plate_lbl.config(bg="#0d1a2e")
            return
        bg = color if n % 2 == 0 else "#0d1a2e"
        self.plate_badge.config(bg=bg)
        self.plate_lbl.config(bg=bg)
        self.after(200, lambda: self._flash_badge(color, n - 1))

    # ── DB helpers ────────────────────────────
    

    # ── Cierre ────────────────────────────────
    def _on_close(self):
        self.cam_running = False
        if self.cap:
            self.cap.release()
        self.destroy()


if __name__ == "__main__":
    app = PlacasApp()
    app.mainloop()
