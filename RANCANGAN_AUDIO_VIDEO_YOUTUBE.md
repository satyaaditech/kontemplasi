# Rantaman & Implementasi Sistem Otomasi Audio & Video Renungan Penyiswaan

Dokumen punika ngandhut asil rembagan, arsitektur, sarta implementasi tahap wiwitan sistem otomatis video renungan Pangestu kagem Pak Satya Adi Dharma.

---

## 1. Tujuan Utama & Nilai Manfaat
- Nyawisaken renungan harian mawi format audiovisual (video YouTube kanthi swanten AI alami sarta hardcoded subtitle ageng lan kontras cetha).
- Nggampilaken para sesepuh / kadang kesiswaan ingkang sampun remeng paningalipun supados cekap ngeklik satunggal link YouTube langsung saged mirengaken sarta maos teks kanthi cetha lan gampil.

---

## 2. Arsitektur Audio (Google Gemini Dual-Voice Engine)
- **Engine**: Google Gemini 2.5 Audio Modality (`gemini-2.5-flash-preview-tts` / Google AI Studio API Key).
- **Konfigurasi Teknis**:
  - `temperature`: `0.0` (presisi verbatim 100%, nyegah pambalikan ukara/redundancy).
  - `systemInstruction`: Strict voiceover narrator prompt tanpa improvisasi/filler.
- **Pambagian Karakter Swanten**:
  - **Karakter 1 (`Charon` - Priya)**: Mligi maos **Pethikan Sabda Suci Basa Jawi** murni (wibawa, anteng, jero, wening).
  - **Jedha Wening**: Silent pause 1.5 detik.
  - **Karakter 2 (`Aoede` - Wanita)**: Maos **Pembuka, Terjemahan Sabda, Uraian, Langkah Praktik, Renungan Inti, dumugi Panutup Satuhu** (anget, luwes, tenang, kontemplatif).
- **Versi Basa Inggris (English Version)**:
  - Ngginakaken struktur sami: `Charon` (Sabda Basa Jawi asli) ➔ jedha ➔ `Aoede` (English Translation, Commentary, and Closing).

---

## 3. Render Video & Hardcoded Subtitles (Lokal Laptop Server)
- **Visual**: Ambient dark-ocean/navy 1080p canvas mawi header "RENUNGAN PENYISWAAN" lan badge pamicara (`🎙️ PETHIKAN SABDA SUCI` / `🎙️ URAIAN & REFLEKSI`).
- **Subtitle Engine**: Advanced SubStation Alpha (`.ass`) kanthi font ageng cetha kontras dhuwur.
- **Renderer**: FFmpeg `-preset veryfast -tune stillimage` (durasi render 4 menit namung mbetahaken ~15-25 detik kanthi ukuran file entheng < 1 MB).

---

## 4. Integrasi YouTube (@siswatalkstv)
- **Channel**: `siswatalks tv` (`@siswatalkstv`)
- **Channel ID**: `UC_5RC62vCuO5rKurQAf0OnQ`
- **Autentikasi**: OAuth 2.0 Token tersimpan permanen di `~/.config/youtube/token.json`.
- **Script Uploader**: `/home/satyaaditech/kontemplasi/upload_youtube.py`
- **Uji Coba Pertama (Verified Sample)**:
  - Link: https://youtu.be/5uDWXtXuUJw (Status: Public)

---

## 5. Rencana Tahap Salajengipun (Next Phase)
- Otomasi *End-to-End Pipeline* saben enjang:
  1. Generate naskah renungan harian (.md).
  2. Generate dual-voice audio Gemini (.mp3).
  3. Generate .ass subtitle alignment.
  4. Render video FFmpeg (.mp4).
  5. Upload otomatis ke YouTube `@siswatalkstv` -> ambil URL `https://youtu.be/...`.
  6. Sisipkan link YouTube ke teks WhatsApp Telegram thread 1096 dan website `kontemplasi.satyaaditech.web.id`.
