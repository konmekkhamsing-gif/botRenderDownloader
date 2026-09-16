from __future__ import annotations

import os
import base64
import threading
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import requests
import yt_dlp
from flask import Flask, jsonify, request


app = Flask(__name__)
DOWNLOAD_KEY = os.environ.get("DOWNLOAD_KEY", "")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
COOKIES_B64 = os.environ.get("YTDLP_COOKIES_B64", "")
MAX_FILE_SIZE = 24 * 1024 * 1024


def is_supported_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.hostname)


def send_to_discord(file_path: Path, media_format: str) -> None:
    size = file_path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise ValueError("ไฟล์ใหญ่เกิน 24 MB ซึ่งเกินขนาดที่กำหนดไว้สำหรับ Discord Webhook")

    with file_path.open("rb") as file_handle:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            data={"content": f"ดาวน์โหลดเสร็จแล้ว ({media_format.upper()})"},
            files={"file": (file_path.name, file_handle, "video/mp4" if media_format == "mp4" else "audio/mpeg")},
            params={"wait": "true"},
            timeout=60,
        )
    response.raise_for_status()


def download_and_send(url: str, media_format: str) -> None:
    with tempfile.TemporaryDirectory(prefix="maplexd-") as temp_dir:
        output_dir = Path(temp_dir)
        cookies_path = output_dir / "cookies.txt"
        options: dict[str, object] = {
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
            "restrictfilenames": True,
            "remote_components": {"ejs"},
            "extractor_args": {
                "youtube": {
                    "player_client": ["web_safari", "web_embedded"],
                }
            },
        }
        if COOKIES_B64:
            try:
                cookies_path.write_bytes(base64.b64decode(COOKIES_B64, validate=True))
            except (ValueError, OSError) as error:
                raise ValueError("YTDLP_COOKIES_B64 ไม่ใช่ Base64 ที่ถูกต้อง") from error
            options["cookiefile"] = str(cookies_path)
        if media_format == "mp3":
            options.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }
            )
        else:
            options.update(
                {
                    "format": "bestvideo*+bestaudio/best",
                    "merge_output_format": "mp4",
                }
            )

        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.download([url])

        files = [path for path in output_dir.iterdir() if path.is_file()]
        if not files:
            raise RuntimeError("ไม่พบไฟล์ที่ดาวน์โหลด")
        send_to_discord(max(files, key=lambda path: path.stat().st_mtime), media_format)


def run_job(url: str, media_format: str) -> None:
    try:
        download_and_send(url, media_format)
    except (
        OSError,
        RuntimeError,
        ValueError,
        requests.RequestException,
        yt_dlp.utils.DownloadError,
    ) as error:
        if DISCORD_WEBHOOK_URL:
            requests.post(
                DISCORD_WEBHOOK_URL,
                json={"content": f"ดาวน์โหลดไม่สำเร็จ: {error}"},
                params={"wait": "true"},
                timeout=30,
            )


@app.get("/health")
def health() -> tuple[object, int]:
    return jsonify({"status": "ok"}), 200


@app.post("/download")
def download() -> tuple[object, int]:
    if not DOWNLOAD_KEY or request.headers.get("X-Download-Key") != DOWNLOAD_KEY:
        return jsonify({"error": "unauthorized"}), 401
    if not DISCORD_WEBHOOK_URL:
        return jsonify({"error": "DISCORD_WEBHOOK_URL is not configured"}), 500

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "JSON body is required"}), 400

    url = payload.get("url")
    media_format = payload.get("format", "mp4")
    if not is_supported_url(url):
        return jsonify({"error": "A valid http/https URL is required"}), 400
    if media_format not in {"mp3", "mp4"}:
        return jsonify({"error": "format must be mp3 or mp4"}), 400

    threading.Thread(
        target=run_job,
        args=(url.strip(), media_format),
        daemon=True,
    ).start()
    return jsonify({"status": "accepted", "message": "กำลังดาวน์โหลดและจะส่งไฟล์กลับ Discord"}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
