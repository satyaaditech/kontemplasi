#!/usr/bin/env python3
import os
import sys
import glob
import json
import re
import shutil
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 8088
BASE_DIR = "/home/satyaaditech/kontemplasi"
RENUNGAN_DIR = os.path.join(BASE_DIR, "renungan")
SHARE_DIR = "/home/satyaaditech/share/renungan"
SYNC_SCRIPT = os.path.join(BASE_DIR, "sync_to_github.sh")
ADMIN_PIN = "1949"  # Tahun Sabda Pangestu

HTML_ADMIN = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Portal - Pustaka Penyiswaan</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0f172a;
      --surface: #1e293b;
      --surface-border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --accent-green: #10b981;
      --accent-gold: #f59e0b;
      --accent-red: #ef4444;
      --radius: 10px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .header {
      background: var(--surface);
      border-bottom: 1px solid var(--surface-border);
      padding: 14px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 50;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 800;
      font-size: 18px;
    }
    .brand span { color: var(--primary); }
    .nav-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .btn {
      padding: 8px 16px;
      border-radius: var(--radius);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: 1px solid transparent;
      transition: all 0.15s;
      text-decoration: none;
    }
    .btn-primary { background: var(--primary); color: white; }
    .btn-primary:hover { background: var(--primary-hover); }
    .btn-success { background: var(--accent-green); color: white; }
    .btn-success:hover { filter: brightness(1.1); }
    .btn-secondary { background: var(--surface); border-color: var(--surface-border); color: var(--text); }
    .btn-secondary:hover { background: #2d3748; }
    .btn-danger { background: var(--accent-red); color: white; }
    .btn-sm { padding: 4px 10px; font-size: 12px; border-radius: 6px; }

    .main {
      padding: 24px;
      max-width: 1400px;
      margin: 0 auto;
      width: 100%;
      flex-grow: 1;
    }

    .stats-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .stat-card {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius);
      padding: 16px 20px;
    }
    .stat-val { font-size: 24px; font-weight: 800; color: var(--text); margin-top: 4px; }
    .stat-lbl { font-size: 12px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }

    .tabs {
      display: flex;
      gap: 8px;
      margin-bottom: 20px;
      border-bottom: 1px solid var(--surface-border);
      padding-bottom: 12px;
    }
    .tab-btn {
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      padding: 8px 16px;
      border-radius: var(--radius);
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
    }
    .tab-btn.active {
      background: var(--surface);
      color: var(--text);
      border-color: var(--surface-border);
    }

    .panel { display: none; }
    .panel.active { display: block; }

    /* TABLE */
    .table-container {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius);
      overflow: hidden;
    }
    table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }
    th { background: #172033; padding: 12px 16px; color: var(--text-muted); font-weight: 700; border-bottom: 1px solid var(--surface-border); }
    td { padding: 12px 16px; border-bottom: 1px solid var(--surface-border); vertical-align: middle; }
    tr:hover td { background: #243049; }

    .badge {
      display: inline-block;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
    }
    .badge-id { background: #991b1b; color: white; }
    .badge-jv { background: #92400e; color: white; }
    .badge-en { background: #3730a3; color: white; }
    .badge-poster { background: #065f46; color: #a7f3d0; }
    .badge-audio { background: #1e3a8a; color: #bfdbfe; }

    /* EDITOR */
    .editor-layout {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      height: calc(100vh - 220px);
    }
    .editor-pane, .preview-pane {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .pane-header {
      padding: 10px 16px;
      background: #172033;
      border-bottom: 1px solid var(--surface-border);
      font-size: 13px;
      font-weight: 700;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    textarea.code-editor {
      flex-grow: 1;
      background: transparent;
      border: none;
      color: var(--text);
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      padding: 16px;
      line-height: 1.6;
      resize: none;
      outline: none;
    }
    .preview-body {
      flex-grow: 1;
      padding: 20px;
      overflow-y: auto;
      font-size: 14px;
      line-height: 1.7;
    }
    .preview-body h1, .preview-body h2 { color: var(--primary); margin: 12px 0 8px; }
    .preview-body blockquote { border-left: 3px solid var(--accent-gold); padding-left: 12px; margin: 12px 0; color: #cbd5e1; }

    /* MODAL PIN */
    .pin-overlay {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.95);
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .pin-box {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      padding: 32px;
      border-radius: var(--radius);
      width: 100%;
      max-width: 360px;
      text-align: center;
      box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5);
    }
    .pin-box h3 { margin-bottom: 8px; font-size: 18px; }
    .pin-input {
      width: 100%;
      padding: 12px;
      font-size: 18px;
      text-align: center;
      letter-spacing: 4px;
      background: var(--bg);
      border: 2px solid var(--surface-border);
      border-radius: var(--radius);
      color: var(--text);
      margin: 16px 0;
      outline: none;
    }
    .pin-input:focus { border-color: var(--primary); }

    /* TOAST & LOG MODAL */
    .log-modal {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.8);
      z-index: 90;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .log-modal.active { display: flex; }
    .log-content {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius);
      width: 100%;
      max-width: 700px;
      max-height: 80vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .log-header { padding: 14px 20px; border-bottom: 1px solid var(--surface-border); font-weight: 700; display: flex; justify-content: space-between; align-items: center; }
    .log-body { padding: 16px; background: #0b0f19; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #38bdf8; overflow-y: auto; flex-grow: 1; white-space: pre-wrap; }

    @media (max-width: 900px) {
      .editor-layout { grid-template-columns: 1fr; height: auto; }
      textarea.code-editor { min-height: 400px; }
    }
  </style>
</head>
<body>

  <!-- PIN PROMPT OVERLAY -->
  <div class="pin-overlay" id="pinOverlay">
    <div class="pin-box">
      <div style="font-size:36px; margin-bottom:12px;">🛡️</div>
      <h3>Portal Admin Pustaka</h3>
      <p style="font-size:13px; color:var(--text-muted);">Mlebetaken PIN pribadi kagem mbikak kontrol.</p>
      <input type="password" id="pinInput" class="pin-input" placeholder="••••" maxlength="6" autofocus onkeydown="if(event.key==='Enter') checkPin()">
      <button class="btn btn-primary" style="width:100%; justify-content:center;" onclick="checkPin()">Mlebet / Login</button>
    </div>
  </div>

  <!-- HEADER -->
  <header class="header">
    <div class="brand">
      <span>📜</span> Admin Kontemplasi
    </div>
    <div class="nav-actions">
      <button class="btn btn-secondary" onclick="window.open('https://kontemplasi.satyaaditech.web.id', '_blank')">🌐 Buka Web Live</button>
      <button class="btn btn-success" id="btnDeploy" onclick="deployLive()">🚀 Terbitkan ke Website</button>
    </div>
  </header>

  <!-- MAIN -->
  <main class="main">
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-lbl">Total Materi Unik</div>
        <div class="stat-val" id="statUnique">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Total Berkas Naskah</div>
        <div class="stat-val" id="statFiles">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Poster Infografis</div>
        <div class="stat-val" id="statPosters">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Rekaman Audio</div>
        <div class="stat-val" id="statAudios">-</div>
      </div>
    </div>

    <!-- TABS -->
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('list')">📋 Daftar Renungan</button>
      <button class="tab-btn" onclick="switchTab('editor')">✏️ Pambesut Naskah (Editor)</button>
      <button class="tab-btn" onclick="switchTab('upload')">📤 Unggah Media</button>
    </div>

    <!-- PANEL LIST -->
    <div class="panel active" id="panel-list">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; gap:12px; flex-wrap:wrap;">
        <input type="text" id="searchTable" placeholder="🔍 Cari renungan..." style="padding:8px 14px; border-radius:8px; background:var(--surface); border:1px solid var(--surface-border); color:var(--text); width:320px; outline:none;" oninput="filterTable()">
        <button class="btn btn-primary" onclick="createNewEntry()">➕ Tambah Renungan Baru</button>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Tanggal</th>
              <th>Judul Renungan</th>
              <th>Bahasa</th>
              <th>Media</th>
              <th>Google Doc</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody id="tableBody">
            <tr><td colspan="6" style="text-align:center; padding:30px;">Memuat data renungan...</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- PANEL EDITOR -->
    <div class="panel" id="panel-editor">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-size:13px; color:var(--text-muted);">Berkas aktif:</span>
          <strong id="currentFileLabel" style="font-family:'JetBrains Mono', monospace; color:var(--primary);">-</strong>
        </div>
        <div style="display:flex; gap:8px;">
          <button class="btn btn-secondary" onclick="switchTab('list')">Kembali</button>
          <button class="btn btn-success" onclick="saveActiveFile()">💾 Simpan Naskah</button>
        </div>
      </div>

      <div class="editor-layout">
        <div class="editor-pane">
          <div class="pane-header">
            <span>Markdown Source</span>
            <span style="font-size:11px; color:var(--text-muted);">Auto-saved to server</span>
          </div>
          <textarea id="codeEditor" class="code-editor" placeholder="Ketik markdown renungan di sini..." oninput="updatePreview()"></textarea>
        </div>
        <div class="preview-pane">
          <div class="pane-header">
            <span>Live Preview</span>
          </div>
          <div id="previewBody" class="preview-body"></div>
        </div>
      </div>
    </div>

    <!-- PANEL UPLOAD -->
    <div class="panel" id="panel-upload">
      <div style="max-width:600px; margin:0 auto; background:var(--surface); border:1px solid var(--surface-border); border-radius:var(--radius); padding:28px;">
        <h3 style="margin-bottom:12px; font-size:16px;">Unggah Berkas Poster / Audio</h3>
        <p style="font-size:13px; color:var(--text-muted); margin-bottom:20px;">
          Format ingkang dipun-dukung: Gambar poster (.jpg, .png) utawi Rekaman audio (.ogg, .mp3).
        </p>

        <form id="uploadForm" enctype="multipart/form-data" onsubmit="handleUpload(event)">
          <div style="border:2px dashed var(--surface-border); padding:30px; text-align:center; border-radius:var(--radius); margin-bottom:20px;">
            <input type="file" id="fileInput" name="file" required style="display:none;" onchange="updateFileLabel(this)">
            <label for="fileInput" class="btn btn-secondary" style="cursor:pointer; margin-bottom:8px;">Pilih Berkas</label>
            <div id="selectedFileName" style="font-size:13px; color:var(--text-muted); margin-top:8px;">Belum ada berkas dipilih</div>
          </div>

          <button type="submit" class="btn btn-primary" style="width:100%; justify-content:center;">Unggah & Simpan ke Pustaka</button>
        </form>
      </div>
    </div>
  </main>

  <!-- LOG MODAL -->
  <div class="log-modal" id="logModal">
    <div class="log-content">
      <div class="log-header">
        <span id="logTitle">🚀 Menjalankan Deploy ke GitHub...</span>
        <button class="btn btn-secondary btn-sm" onclick="closeLogModal()">Tutup</button>
      </div>
      <div class="log-body" id="logText">Sedang memproses sinkronisasi dan build...</div>
    </div>
  </div>

  <script>
    let renunganList = [];
    let currentActiveFile = '';

    function checkPin() {
      const pin = document.getElementById('pinInput').value;
      if (pin === '1949') {
        document.getElementById('pinOverlay').style.display = 'none';
        sessionStorage.setItem('admin_auth', '1');
        loadData();
      } else {
        alert('PIN lepat! Mangga dipun-priksa malih.');
      }
    }

    if (sessionStorage.getItem('admin_auth') === '1') {
      document.getElementById('pinOverlay').style.display = 'none';
      loadData();
    }

    function switchTab(tabId) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      document.querySelector(`button[onclick="switchTab('${tabId}')"]`).classList.add('active');
      document.getElementById(`panel-${tabId}`).classList.add('active');
    }

    function loadData() {
      fetch('/api/list')
        .then(r => r.json())
        .then(data => {
          renunganList = data.files;
          document.getElementById('statUnique').innerText = data.stats.unique_count;
          document.getElementById('statFiles').innerText = data.stats.total_files;
          document.getElementById('statPosters').innerText = data.stats.poster_count;
          document.getElementById('statAudios').innerText = data.stats.audio_count;
          renderTable();
        });
    }

    function renderTable() {
      const tbody = document.getElementById('tableBody');
      const q = document.getElementById('searchTable').value.toLowerCase();
      tbody.innerHTML = '';

      const filtered = renunganList.filter(f => {
        return !q || f.title.toLowerCase().includes(q) || f.date.includes(q) || f.fname.toLowerCase().includes(q);
      });

      if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:24px; color:var(--text-muted);">Tidak ada renungan yang cocok.</td></tr>';
        return;
      }

      filtered.forEach(f => {
        const tr = document.createElement('tr');
        const langBadge = f.lang === 'id' ? '<span class="badge badge-id">ID</span>' : (f.lang === 'en' ? '<span class="badge badge-en">EN</span>' : '<span class="badge badge-jv">JAWA</span>');
        const posterBadge = f.has_poster ? '<span class="badge badge-poster">Poster</span>' : '-';
        const audioBadge = f.has_audio ? '<span class="badge badge-audio">Audio</span>' : '-';
        const gdocLink = f.gdoc ? `<a href="${f.gdoc}" target="_blank" style="color:var(--primary); text-decoration:none;">Buka GDoc ↗</a>` : '-';

        tr.innerHTML = `
          <td style="font-weight:700; white-space:nowrap;">${f.date}</td>
          <td><strong>${f.title}</strong><div style="font-size:11px; color:var(--text-muted); font-family:'JetBrains Mono', monospace;">${f.fname}</div></td>
          <td>${langBadge}</td>
          <td>${posterBadge} ${audioBadge}</td>
          <td>${gdocLink}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="openEditor('${f.fname}')">✏️ Edit</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    function filterTable() {
      renderTable();
    }

    function openEditor(fname) {
      currentActiveFile = fname;
      document.getElementById('currentFileLabel').innerText = fname;
      fetch(`/api/get?file=${encodeURIComponent(fname)}`)
        .then(r => r.json())
        .then(d => {
          document.getElementById('codeEditor').value = d.content;
          updatePreview();
          switchTab('editor');
        });
    }

    function updatePreview() {
      const raw = document.getElementById('codeEditor').value;
      const preview = document.getElementById('previewBody');
      let html = raw
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/\\*\\*([^\\*]+)\\*\\*/g, '<strong>$1</strong>')
        .replace(/\\*([^\\*]+)\\*/g, '<strong>$1</strong>')
        .replace(/_([^_]+)_/g, '<em>$1</em>')
        .replace(/\\n\\n/g, '<br><br>');
      preview.innerHTML = html;
    }

    function saveActiveFile() {
      if (!currentActiveFile) return;
      const content = document.getElementById('codeEditor').value;
      fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file: currentActiveFile, content: content })
      })
      .then(r => r.json())
      .then(d => {
        if (d.status === 'ok') {
          alert('Naskah kasil kasimpen wonten ing server!');
          loadData();
        } else {
          alert('Gagal nyimpen naskah: ' + d.error);
        }
      });
    }

    function createNewEntry() {
      const date = prompt('Masukkan Tanggal Renungan (YYYY-MM-DD):', new Date().toISOString().split('T')[0]);
      if (!date) return;
      const topic = prompt('Masukkan Topik (contoh: sabar, narima, eling):', 'kontemplasi');
      if (!topic) return;
      const fname = `renungan-${topic.toLowerCase().replace(/\\s+/g, '-')}-ind-${date}.md`;
      const template = `---
title: "Sesirah Renungan ${date}"
date: ${date}
tags: ['renungan', 'bahasa-indonesia', 'sang-guru-sejati']
language: id
---

# Sesirah Renungan ${date}

*${date}*

*RENUNGAN PENYISWAAN*

*Sesirah Renungan*

_Sugeng Enjang, Salam Karahayon_

*📖 SABDA HARI INI :*

Sasangka Jati : _"Tulis sabda murni ing mriki..."_

💭 *URAIAN* :

Tulis ulasan lan panyuraos batin ing mriki...

🙏 *PRAKTIK* :

1. Langkah setunggal
2. Langkah kalih
3. Langkah tiga

📝 *APLIKASI* :

1. Pitakenan kapisan?
`;
      currentActiveFile = fname;
      document.getElementById('currentFileLabel').innerText = fname;
      document.getElementById('codeEditor').value = template;
      updatePreview();
      switchTab('editor');
    }

    function updateFileLabel(input) {
      if (input.files && input.files[0]) {
        document.getElementById('selectedFileName').innerText = input.files[0].name + ` (${Math.round(input.files[0].size/1024)} KB)`;
      }
    }

    function handleUpload(e) {
      e.preventDefault();
      const form = document.getElementById('uploadForm');
      const formData = new FormData(form);
      fetch('/api/upload', {
        method: 'POST',
        body: formData
      })
      .then(r => r.json())
      .then(d => {
        if (d.status === 'ok') {
          alert('Berkas kasil kaunggah: ' + d.filename);
          document.getElementById('fileInput').value = '';
          document.getElementById('selectedFileName').innerText = 'Belum ada berkas dipilih';
          loadData();
          switchTab('list');
        } else {
          alert('Gagal ngunggah berkas: ' + d.error);
        }
      });
    }

    function deployLive() {
      document.getElementById('logModal').classList.add('active');
      document.getElementById('logText').innerText = 'Menjalankan sinkronisasi rsync, build static web, dan git push...\\nMohon tunggu sekejap...\\n';
      fetch('/api/deploy', { method: 'POST' })
        .then(r => r.json())
        .then(d => {
          document.getElementById('logText').innerText = d.output;
        })
        .catch(err => {
          document.getElementById('logText').innerText = 'Error: ' + err;
        });
    }

    function closeLogModal() {
      document.getElementById('logModal').classList.remove('active');
    }
  </script>
</body>
</html>
"""

class AdminHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_ADMIN.encode("utf-8"))
        elif parsed.path == "/api/list":
            self.handle_api_list()
        elif parsed.path == "/api/get":
            qs = parse_qs(parsed.query)
            fname = qs.get("file", [""])[0]
            self.handle_api_get(fname)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/save":
            self.handle_api_save()
        elif parsed.path == "/api/upload":
            self.handle_api_upload()
        elif parsed.path == "/api/deploy":
            self.handle_api_deploy()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_api_list(self):
        md_files = sorted(glob.glob(os.path.join(RENUNGAN_DIR, "*.md")), reverse=True)
        files_data = []
        posters = set()
        audios = set()
        unique_groups = set()

        for f in md_files:
            fname = os.path.basename(f)
            with open(f, "r", encoding="utf-8") as fp:
                raw = fp.read()

            m_date = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
            date_iso = m_date.group(1) if m_date else "2026-08-01"

            # Title
            title = ""
            for line in raw.splitlines()[:6]:
                if "title:" in line:
                    title = line.replace("title:", "").replace('"', '').replace("'", "").strip()
                    break
                elif line.startswith("# "):
                    title = line.replace("# ", "").strip()
                    break
            if not title:
                title = fname

            lang = "jv"
            if "-ind" in fname or "ind" in fname.lower() and not "pindha" in fname:
                lang = "id"
            elif "-eng" in fname:
                lang = "en"

            # Stem
            stem = fname.replace("renungan-", "").replace(".md", "")
            core_topic = re.sub(r'-\d{4}-\d{2}-\d{2}', '', stem)
            core_topic = re.sub(r'-\d+-agustus-\d{4}', '', core_topic)
            core_topic = re.sub(r'-(?:ind|eng|jv)$', '', core_topic)
            group_id = f"{date_iso}_{core_topic}"
            unique_groups.add(group_id)

            # Check media
            base_no_ext = os.path.splitext(fname)[0]
            has_audio = os.path.exists(os.path.join(RENUNGAN_DIR, base_no_ext + ".ogg")) or os.path.exists(os.path.join(RENUNGAN_DIR, base_no_ext + ".mp3"))
            if has_audio:
                audios.add(base_no_ext)

            # Check poster
            has_poster = False
            for p_cand in [f"poster-{core_topic}-{date_iso}.jpg", f"poster-{core_topic}.jpg", f"infografis-{core_topic}-{date_iso}.png"]:
                if os.path.exists(os.path.join(RENUNGAN_DIR, p_cand)):
                    has_poster = True
                    posters.add(p_cand)
                    break

            gdoc_match = re.search(r'https://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)', raw)
            gdoc = gdoc_match.group(0) if gdoc_match else ""

            files_data.append({
                "fname": fname,
                "date": date_iso,
                "title": title.replace("*", "").replace("#", "").strip(),
                "lang": lang,
                "has_poster": has_poster,
                "has_audio": has_audio,
                "gdoc": gdoc
            })

        response = {
            "stats": {
                "unique_count": len(unique_groups),
                "total_files": len(md_files),
                "poster_count": len(glob.glob(os.path.join(RENUNGAN_DIR, "poster-*.jpg")) + glob.glob(os.path.join(RENUNGAN_DIR, "infografis-*.png"))),
                "audio_count": len(glob.glob(os.path.join(RENUNGAN_DIR, "*.ogg")) + glob.glob(os.path.join(RENUNGAN_DIR, "*.mp3")))
            },
            "files": files_data
        }
        self.send_json(response)

    def handle_api_get(self, fname):
        fname = os.path.basename(fname)
        fpath = os.path.join(RENUNGAN_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as fp:
                content = fp.read()
            self.send_json({"status": "ok", "fname": fname, "content": content})
        else:
            self.send_json({"status": "error", "error": "File not found"}, status=404)

    def handle_api_save(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
            fname = os.path.basename(data.get("file", ""))
            content = data.get("content", "")
            if not fname:
                return self.send_json({"status": "error", "error": "Invalid filename"}, status=400)

            # Save to both kontemplasi and share
            p1 = os.path.join(RENUNGAN_DIR, fname)
            p2 = os.path.join(SHARE_DIR, fname)
            with open(p1, "w", encoding="utf-8") as fp:
                fp.write(content)
            if os.path.exists(SHARE_DIR):
                with open(p2, "w", encoding="utf-8") as fp:
                    fp.write(content)

            self.send_json({"status": "ok", "file": fname})
        except Exception as e:
            self.send_json({"status": "error", "error": str(e)}, status=500)

    def handle_api_upload(self):
        content_type = self.headers.get('Content-Type', '')
        if 'multipart/form-data' not in content_type:
            return self.send_json({"status": "error", "error": "Expected multipart form"}, status=400)

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        
        # Parse boundary
        boundary = None
        for item in content_type.split(';'):
            item = item.strip()
            if item.startswith('boundary='):
                boundary = item.split('=', 1)[1].strip('"\'').encode('utf-8')
                break
        
        if not boundary:
            return self.send_json({"status": "error", "error": "No boundary found"}, status=400)
        
        parts = body.split(b'--' + boundary)
        uploaded_name = ""
        for part in parts:
            if b'Content-Disposition' in part and b'filename=' in part:
                headers_part, file_data = part.split(b'\r\n\r\n', 1)
                file_data = file_data.rstrip(b'\r\n')
                m = re.search(r'filename="([^"]+)"', headers_part.decode('utf-8', errors='ignore'))
                if m:
                    uploaded_name = os.path.basename(m.group(1))
                    p1 = os.path.join(RENUNGAN_DIR, uploaded_name)
                    p2 = os.path.join(SHARE_DIR, uploaded_name)
                    with open(p1, 'wb') as fp:
                        fp.write(file_data)
                    if os.path.exists(SHARE_DIR):
                        shutil.copy(p1, p2)
                    break
        
        if uploaded_name:
            return self.send_json({"status": "ok", "filename": uploaded_name})
        self.send_json({"status": "error", "error": "No file uploaded"}, status=400)

    def handle_api_deploy(self):
        try:
            res = subprocess.run(["bash", SYNC_SCRIPT], capture_output=True, text=True, timeout=60)
            out = res.stdout + "\\n" + res.stderr
            self.send_json({"status": "ok", "output": out})
        except Exception as e:
            self.send_json({"status": "error", "output": str(e)}, status=500)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

def run():
    server = HTTPServer(("0.0.0.0", PORT), AdminHandler)
    print(f"Admin Portal running on http://0.0.0.0:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()
