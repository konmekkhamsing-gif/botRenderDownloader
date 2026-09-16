# MapleXD Video Downloader

โปรแกรม Windows แบบหน้าต่างสำหรับดาวน์โหลดวิดีโอจากหลายแพลตฟอร์มเป็น MP4 หรือเสียง MP3 พร้อมโลโก้ MapleXD

รองรับ YouTube, TikTok และแพลตฟอร์มอื่น ๆ ที่ `yt-dlp` รองรับ

## ติดตั้ง

1. ติดตั้ง Python 3.10 ขึ้นไป และเลือก **Add Python to PATH**
2. ติดตั้ง [FFmpeg](https://ffmpeg.org/download.html) และเพิ่มโฟลเดอร์ที่มี `ffmpeg.exe` ลงใน `PATH`
3. เปิด PowerShell ในโฟลเดอร์นี้ แล้วรัน:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## เริ่มใช้งาน

```powershell
.\.venv\Scripts\python.exe app.py
```

วางลิงก์วิดีโอจากแพลตฟอร์มที่รองรับ เลือก MP3 หรือ MP4 จากนั้นเลือกคุณภาพ:

- MP3: `128`, `192`, `256` หรือ `320 kbps`
- MP4: `360p`, `480p`, `720p`, `1080p`, `1440p` หรือ `2160p` (ถ้าวิดีโอต้นฉบับมีคุณภาพนั้น)

เลือกโฟลเดอร์ปลายทาง แล้วกด **ดาวน์โหลด**

ใช้กับเนื้อหาที่คุณมีสิทธิ์ดาวน์โหลดและเป็นไปตามเงื่อนไขการให้บริการของแพลตฟอร์มนั้น ๆ เท่านั้น วิดีโอส่วนตัวหรือวิดีโอที่ต้องล็อกอินอาจดาวน์โหลดไม่ได้

## สร้างไฟล์โปรแกรมสำหรับแจก

สร้างไฟล์ `.exe` แบบไฟล์เดียว:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\build.ps1
```

ไฟล์ที่ได้คือ `dist\MapleXDDownloader.exe` พร้อมไอคอน MapleXD ผู้ใช้ปลายทางไม่ต้องติดตั้ง Python

หากต้องการตัวติดตั้งแบบมีขั้นตอน ให้ติดตั้ง [Inno Setup](https://jrsoftware.org/isinfo.php) แล้วเปิด `installer.iss` ด้วย Inno Setup จากนั้นกด **Compile** จะได้ `installer\MapleXDDownloader-Setup.exe`

หากมีไฟล์ `ffmpeg.exe` ให้วางไว้ที่ `ffmpeg\ffmpeg.exe` ก่อนรัน `build.ps1` เพื่อรวม FFmpeg ไปกับโปรแกรมด้วย

## Backend สำหรับ Discord และ BotGhost

โฟลเดอร์ `backend` เป็นบริการสำหรับ Render ที่รับคำสั่งจาก BotGhost แล้วส่งไฟล์กลับ Discord ผ่าน Webhook

1. สร้าง Discord Webhook ในห้องที่จะให้บอทส่งไฟล์
2. สร้าง Render Web Service จาก repository นี้ โดยใช้ไฟล์ `render.yaml`
3. ตั้งค่า Environment Variable ใน Render:
   - `DISCORD_WEBHOOK_URL`: URL ของ Discord Webhook
   - `DOWNLOAD_KEY`: คีย์ลับสำหรับเรียก API
   - `YTDLP_COOKIES_B64`: เนื้อหา `cookies.txt` ที่แปลงเป็น Base64 (ถ้าจำเป็น)
4. ใน BotGhost ใช้ HTTP Request:
   - Method: `POST`
   - URL: `https://ชื่อบริการ.onrender.com/download`
   - Header: `X-Download-Key: ค่าเดียวกับ DOWNLOAD_KEY`
   - JSON body:
     ```json
     {
       "url": "{option_url}",
       "format": "{option_format}"
     }
     ```

บอทจะส่งไฟล์ MP4/MP3 กลับเข้า Channel ที่สร้าง Webhook ไว้ ไฟล์เกิน 24 MB จะถูกปฏิเสธเพื่อไม่ให้เกิดการอัปโหลดค้าง ใช้กับเนื้อหาที่มีสิทธิ์ดาวน์โหลดเท่านั้น

### Cookie สำหรับแพลตฟอร์มที่ต้องยืนยันตัวตน

อย่าส่ง Cookie ผ่านแชทหรือ commit ลง GitHub ใช้เฉพาะ Cookie ของบัญชีที่คุณมีสิทธิ์ใช้ และทราบว่า Cookie อาจทำให้บัญชีถูกเข้าถึงได้ หากรั่วไหลให้ logout ทุกอุปกรณ์/เปลี่ยนรหัสผ่านทันที

แปลงไฟล์เป็น Base64 ในเครื่อง แล้วนำค่าที่ได้ไปใส่เป็น Secret `YTDLP_COOKIES_B64` บน Render:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("cookies.txt"))
```

หลังเพิ่ม Secret แล้วกด **Manual Deploy → Deploy latest commit** ใหม่
