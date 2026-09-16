from __future__ import annotations

import queue
import sys
import threading
from pathlib import Path
from tkinter import Button, DoubleVar, StringVar, TclError, Tk, filedialog, messagebox
from tkinter import ttk
from urllib.parse import urlparse

import yt_dlp
from PIL import Image, ImageTk


class MultiPlatformDownloader:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("MapleXD Downloader version 1.0")
        self.root.geometry("720x430")
        self.root.minsize(620, 380)
        self.root.configure(bg="#D9FFFB")

        self.url = StringVar()
        self.format = StringVar(value="mp4")
        self.quality = StringVar(value="720p")
        self.output_dir = StringVar(
            value=str(Path.home() / "Downloads" / "MapleXD Downloads")
        )
        self.status = StringVar(value="พร้อมดาวน์โหลด")
        self.progress_value = DoubleVar(value=0)
        self.progress_label = StringVar(value="0%")
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.downloading = False
        self.logo_image: ImageTk.PhotoImage | None = None

        self._build_ui()
        self.root.after(100, self._process_events)

    def _build_ui(self) -> None:
        style = ttk.Style(self.root)
        style.configure("App.TFrame", background="#D9FFFB")
        style.configure("Card.TFrame", background="#D9FFFB")
        style.configure(
            "Title.TLabel",
            background="#D9FFFB",
            foreground="#243b64",
            font=("Segoe UI", 19, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background="#D9FFFB",
            foreground="#60708c",
            font=("Segoe UI", 9),
        )
        style.configure(
            "Field.TLabel",
            background="#D9FFFB",
            foreground="#263852",
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background="#edf1f7",
            foreground="#3a4d68",
            font=("Segoe UI", 9),
        )
        style.configure(
            "Accent.TButton",
            background="#d9578f",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=(10, 8),
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#b83f73"), ("disabled", "#aeb6c2")],
            foreground=[("disabled", "#ffffff")],
        )
        style.configure(
            "Secondary.TButton",
            background="#e6ebf3",
            foreground="#243b64",
            padding=(9, 5),
        )
        style.map("Secondary.TButton", background=[("active", "#d2dae7")])
        style.configure(
            "Pink.Horizontal.TProgressbar",
            troughcolor="#dfe4ec",
            background="#d9578f",
            lightcolor="#ed83ad",
            darkcolor="#b83f73",
        )

        frame = ttk.Frame(self.root, padding=16, style="App.TFrame")
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        card = ttk.Frame(frame, padding=18, style="Card.TFrame")
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(2, weight=1)
        card.rowconfigure(8, weight=1)

        logo_path = Path(__file__).with_name("MapleXD.jpg")
        if logo_path.exists():
            logo = Image.open(logo_path)
            logo.thumbnail((96, 96))
            self.logo_image = ImageTk.PhotoImage(logo)
            self.root.iconphoto(True, self.logo_image)
            ttk.Label(card, image=self.logo_image, background="#D9FFFB").grid(
                row=0, column=0, rowspan=2, padx=(0, 14), pady=4
            )

        ttk.Label(
            card,
            text="MapleXD Downloader",
            style="Title.TLabel",
        ).grid(row=0, column=1, columnspan=3, sticky="w", pady=(2, 0))
        ttk.Label(
            card,
            text="ดาวน์โหลดวิดีโอและเสียงจากแพลตฟอร์มที่รองรับ",
            style="Subtitle.TLabel",
        ).grid(row=1, column=1, columnspan=3, sticky="w", pady=(0, 12))

        platforms = (
            ("YouTube", "#ff0033"),
            ("TikTok", "#111111"),
        )
        platform_bar = ttk.Frame(card, style="Card.TFrame")
        platform_bar.grid(row=2, column=1, columnspan=3, sticky="w", pady=(0, 10))
        for index, (name, color) in enumerate(platforms):
            ttk.Label(
                platform_bar,
                text=name,
                background=color,
                foreground="#ffffff",
                font=("Segoe UI", 8, "bold"),
                padding=(9, 4),
            ).grid(row=0, column=index, padx=(0, 6))

        ttk.Label(card, text="ลิงก์วิดีโอ:", style="Field.TLabel").grid(
            row=3, column=1, sticky="w", padx=(0, 10), pady=6
        )
        url_entry = ttk.Entry(card, textvariable=self.url)
        url_entry.grid(row=3, column=2, sticky="ew", pady=6)
        url_entry.bind("<Control-KeyPress-v>", self._paste_url)
        url_entry.bind("<Control-KeyPress-V>", self._paste_url)
        url_entry.bind("<Shift-KeyPress-Insert>", self._paste_url)
        url_entry.focus_set()
        ttk.Button(card, text="วางลิงก์", style="Secondary.TButton", command=self._paste_url).grid(
            row=3, column=3, padx=(8, 0), pady=6
        )

        ttk.Label(card, text="รูปแบบ:", style="Field.TLabel").grid(
            row=4, column=1, sticky="w", padx=(0, 10), pady=6
        )
        format_box = ttk.Combobox(
            card, textvariable=self.format, values=("mp4", "mp3"), state="readonly", width=12
        )
        format_box.grid(row=4, column=2, sticky="w", pady=6)
        format_box.bind("<<ComboboxSelected>>", self._format_changed)

        ttk.Label(card, text="คุณภาพ:", style="Field.TLabel").grid(
            row=5, column=1, sticky="w", padx=(0, 10), pady=6
        )
        self.quality_box = ttk.Combobox(
            card,
            textvariable=self.quality,
            values=("360p", "480p", "720p", "1080p", "1440p", "2160p"),
            state="readonly",
            width=12,
        )
        self.quality_box.grid(row=5, column=2, sticky="w", pady=6)

        ttk.Label(card, text="โฟลเดอร์ปลายทาง:", style="Field.TLabel").grid(
            row=6, column=1, sticky="w", padx=(0, 10), pady=6
        )
        ttk.Entry(card, textvariable=self.output_dir).grid(
            row=6, column=2, sticky="ew", pady=6
        )
        ttk.Button(card, text="เลือก...", style="Secondary.TButton", command=self._choose_folder).grid(
            row=6, column=3, padx=(8, 0), pady=6
        )

        self.download_button = Button(
            card,
            text="ดาวน์โหลดเลย",
            command=self._start_download,
            bg="#d9578f",
            fg="#ffffff",
            activebackground="#b83f73",
            activeforeground="#ffffff",
            disabledforeground="#ffffff",
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        self.download_button.grid(row=7, column=1, columnspan=3, sticky="ew", pady=(18, 10))

        ttk.Progressbar(
            card, mode="determinate", maximum=100, variable=self.progress_value,
            style="Pink.Horizontal.TProgressbar",
        ).grid(row=8, column=1, columnspan=2, sticky="ew", pady=6)
        ttk.Label(card, textvariable=self.progress_label, width=6, style="Subtitle.TLabel").grid(
            row=8, column=3, sticky="e", pady=6
        )
        ttk.Label(card, textvariable=self.status, wraplength=590, style="Status.TLabel").grid(
            row=9, column=1, columnspan=3, sticky="ew", pady=(8, 0)
        )
        ttk.Label(
            card,
            text="ใช้กับเนื้อหาที่คุณมีสิทธิ์ดาวน์โหลด • ต้องติดตั้ง FFmpeg",
            style="Subtitle.TLabel",
        ).grid(row=10, column=1, columnspan=3, sticky="w", pady=(14, 0))

    def _format_changed(self, _event: object = None) -> None:
        if self.format.get() == "mp3":
            self.quality_box.configure(values=("128 kbps", "192 kbps", "256 kbps", "320 kbps"))
            self.quality.set("192 kbps")
        else:
            self.quality_box.configure(
                values=("360p", "480p", "720p", "1080p", "1440p", "2160p")
            )
            self.quality.set("720p")

    def _choose_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.output_dir.get())
        if selected:
            self.output_dir.set(selected)

    def _paste_url(self, event: object = None) -> str:
        try:
            clipboard = self.root.clipboard_get().strip()
        except TclError:
            messagebox.showwarning(
                "วางลิงก์ไม่สำเร็จ",
                "ไม่พบข้อความในคลิปบอร์ด กรุณาคัดลอกลิงก์วิดีโอก่อน",
            )
            return "break"
        if hasattr(event, "widget") and isinstance(event.widget, ttk.Entry):
            event.widget.delete(0, "end")
            event.widget.insert(0, clipboard)
        else:
            self.url.set(clipboard)
        return "break"

    @staticmethod
    def _is_supported_url(value: str) -> bool:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname)

    def _start_download(self) -> None:
        url = self.url.get().strip()
        output_dir_text = self.output_dir.get().strip()
        output_dir = Path(output_dir_text).expanduser()
        if not self._is_supported_url(url):
            messagebox.showerror(
                "ลิงก์ไม่ถูกต้อง",
                "กรุณาใส่ลิงก์วิดีโอที่ถูกต้อง เช่น YouTube หรือ TikTok",
            )
            return
        if not output_dir_text:
            messagebox.showerror("โฟลเดอร์ไม่ถูกต้อง", "กรุณาเลือกโฟลเดอร์ปลายทาง")
            return

        self.downloading = True
        self.download_button.configure(state="disabled")
        self.progress_value.set(0)
        self.progress_label.set("0%")
        self.status.set("กำลังเริ่มดาวน์โหลด...")
        threading.Thread(
            target=self._download,
            args=(url, output_dir, self.format.get(), self.quality.get()),
            daemon=True,
        ).start()

    def _download(
        self, url: str, output_dir: Path, media_format: str, quality: str
    ) -> None:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            options: dict[str, object] = {
                "noplaylist": True,
                "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
                "progress_hooks": [self._progress_hook],
            }
            bundled_ffmpeg = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "ffmpeg"
            if (bundled_ffmpeg / "ffmpeg.exe").exists():
                options["ffmpeg_location"] = str(bundled_ffmpeg)
            if media_format == "mp3":
                options.update(
                    {
                        "format": "bestaudio/best",
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": quality.split()[0],
                            }
                        ],
                    }
                )
            else:
                height = quality.removesuffix("p")
                options["format"] = (
                    f"bestvideo*[height<={height}]+bestaudio/best[height<={height}]"
                )
                options["merge_output_format"] = "mp4"

            with yt_dlp.YoutubeDL(options) as downloader:
                downloader.download([url])
            self.events.put(("done", "ดาวน์โหลดเสร็จแล้ว"))
        except yt_dlp.utils.DownloadError as error:
            self.events.put(("error", self._friendly_error(str(error))))
        except (OSError, ValueError) as error:
            self.events.put(("error", f"ไม่สามารถบันทึกไฟล์ได้: {error}"))

    def _progress_hook(self, data: dict[str, object]) -> None:
        if data.get("status") == "downloading":
            downloaded = data.get("downloaded_bytes", 0)
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            if isinstance(downloaded, int) and isinstance(total, int) and total:
                percent = min(100, downloaded * 100 / total)
                self.events.put(("progress", percent))
        elif data.get("status") == "finished":
            self.events.put(("status", "กำลังประมวลผลไฟล์..."))

    @staticmethod
    def _friendly_error(error: str) -> str:
        if "ffmpeg" in error.lower():
            return "ไม่พบ FFmpeg กรุณาติดตั้ง FFmpeg และเพิ่มลงใน PATH ก่อนใช้งาน"
        return f"ดาวน์โหลดไม่สำเร็จ: {error.splitlines()[-1]}"

    def _process_events(self) -> None:
        try:
            while True:
                event, value = self.events.get_nowait()
                if event == "progress":
                    percent = float(value)
                    self.progress_value.set(percent)
                    self.progress_label.set(f"{percent:.0f}%")
                elif event == "status":
                    self.status.set(str(value))
                elif event == "done":
                    self.progress_value.set(100)
                    self.progress_label.set("100%")
                    self.status.set(str(value))
                    self._finish_download()
                    messagebox.showinfo("สำเร็จ", str(value))
                elif event == "error":
                    self.status.set(str(value))
                    self._finish_download()
                    messagebox.showerror("เกิดข้อผิดพลาด", str(value))
        except queue.Empty:
            pass
        self.root.after(100, self._process_events)

    def _finish_download(self) -> None:
        self.downloading = False
        self.download_button.configure(state="normal")


def main() -> None:
    root = Tk()
    try:
        ttk.Style(root).theme_use("vista")
    except TclError:
        pass
    MultiPlatformDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
