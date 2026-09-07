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
      --accent-gray: #64748b;
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
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin-bottom: 24px;
    }
    .stat-card {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius);
      padding: 14px 18px;
    }
    .stat-val { font-size: 22px; font-weight: 800; color: var(--text); margin-top: 2px; }
    .stat-lbl { font-size: 11px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }

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
    th {
      background: #172033;
      padding: 12px 16px;
      color: var(--text-muted);
      font-weight: 700;
      border-bottom: 1px solid var(--surface-border);
      user-select: none;
    }
    th.sortable {
      cursor: pointer;
      transition: color 0.15s;
    }
    th.sortable:hover {
      color: var(--primary);
      background: #1c273e;
    }
    th.sorted {
      color: var(--text);
    }
    .sort-icon {
      margin-left: 4px;
      font-size: 11px;
      opacity: 0.6;
    }
    th.sorted .sort-icon {
      opacity: 1;
      color: var(--primary);
    }
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
    /* CATEGORY BADGES */
    .badge-cat-admin {
      display: inline-block;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
    }
    .cat-admin-renungan { background: #1e3a8a; color: #bfdbfe; }
    .cat-admin-esai { background: #581c87; color: #f5d0fe; }
    .cat-admin-readers { background: #14532d; color: #bbf7d0; }
    .cat-admin-ulasan { background: #78350f; color: #fde68a; }

    /* STATUS SELECTOR */
    .status-select {
      padding: 5px 8px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      border: 1px solid transparent;
      outline: none;
      cursor: pointer;
    }
    .status-published { background: #064e3b; color: #6ee7b7; border-color: #047857; }
    .status-draft { background: #78350f; color: #fde68a; border-color: #b45309; }
    .status-unpublished { background: #334155; color: #cbd5e1; border-color: #475569; }

    /* FILTER BUTTONS */
    .filter-btn {
      padding: 5px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      background: var(--surface);
      border: 1px solid var(--surface-border);
      color: var(--text-muted);
    }
    .filter-btn.active {
      background: var(--primary);
      border-color: var(--primary);
      color: white;
    }

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
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #10b981;
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      z-index: 100;
      box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
      display: none;
      animation: fadeIn 0.2s;
    }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

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

  <body>
    <div class="toast" id="toast"></div>

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
        <div class="stat-lbl">🟢 Published (Live)</div>
        <div class="stat-val" id="statPub" style="color:#6ee7b7;">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">🟡 Draft</div>
        <div class="stat-val" id="statDraft" style="color:#fde68a;">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">⚪ Unpublished</div>
        <div class="stat-val" id="statUnpub" style="color:#cbd5e1;">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Total Berkas Naskah</div>
        <div class="stat-val" id="statFiles">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Poster & Audio</div>
        <div class="stat-val" id="statMedia">-</div>
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
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
          <input type="text" id="searchTable" placeholder="🔍 Cari judul/topik/penulis..." style="padding:8px 14px; border-radius:8px; background:var(--surface); border:1px solid var(--surface-border); color:var(--text); width:230px; outline:none;" oninput="filterTable()">
          <div style="display:flex; gap:4px;">
            <button class="filter-btn active" onclick="setStatusFilter('all', this)">Semua Status</button>
            <button class="filter-btn" onclick="setStatusFilter('published', this)">🟢 Published</button>
            <button class="filter-btn" onclick="setStatusFilter('draft', this)">🟡 Draft</button>
            <button class="filter-btn" onclick="setStatusFilter('unpublished', this)">⚪ Unpublished</button>
          </div>
          <div style="display:flex; gap:4px; margin-left:6px;">
            <button class="filter-btn active" onclick="setCategoryTabFilter('all', this)">Semua Kategori</button>
            <button class="filter-btn" onclick="setCategoryTabFilter('renungan-harian', this)">🌅 Renungan</button>
            <button class="filter-btn" onclick="setCategoryTabFilter('esai-kontemplasi', this)">✍️ Esai</button>
            <button class="filter-btn" onclick="setCategoryTabFilter('readers-voice', this)">👥 Voice</button>
            <button class="filter-btn" onclick="setCategoryTabFilter('ulasan-serat', this)">📜 Ulasan</button>
          </div>
        </div>
        <button class="btn btn-primary" onclick="createNewEntry()">➕ Tambah Tulisan Baru</button>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th class="sortable" onclick="handleSort('status')">Status <span id="sort-status" class="sort-icon">⇅</span></th>
              <th class="sortable" onclick="handleSort('category')">Kategori <span id="sort-category" class="sort-icon">⇅</span></th>
              <th class="sortable" onclick="handleSort('date')">Tanggal <span id="sort-date" class="sort-icon">▼</span></th>
              <th class="sortable" onclick="handleSort('title')">Judul Tulisan / Penulis <span id="sort-title" class="sort-icon">⇅</span></th>
              <th class="sortable" onclick="handleSort('lang')">Bahasa <span id="sort-lang" class="sort-icon">⇅</span></th>
              <th class="sortable" onclick="handleSort('media')">Media <span id="sort-media" class="sort-icon">⇅</span></th>
              <th class="sortable" onclick="handleSort('gdoc')">Google Doc <span id="sort-gdoc" class="sort-icon">⇅</span></th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody id="tableBody">
            <tr><td colspan="8" style="text-align:center; padding:30px;">Memuat data...</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- PANEL EDITOR -->
    <div class="panel" id="panel-editor">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:10px;">
        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
          <button class="btn btn-secondary btn-sm" onclick="switchTab('list')">← Kembali</button>
          <span style="font-size:13px; color:var(--text-muted);">Berkas:</span>
          <strong id="currentFileLabel" style="font-family:'JetBrains Mono', monospace; color:var(--primary);">-</strong>
          
          <span style="font-size:13px; color:var(--text-muted); margin-left:4px;">Status:</span>
          <select id="editorStatusSelect" class="status-select status-published" onchange="updateEditorStatus(this.value)">
            <option value="published">🟢 Published</option>
            <option value="draft">🟡 Draft</option>
            <option value="unpublished">⚪ Unpublished</option>
          </select>

          <span style="font-size:13px; color:var(--text-muted); margin-left:4px;">Kategori:</span>
          <select id="editorCatSelect" class="status-select" style="background:#1e293b; border-color:#475569; color:#f8fafc;" onchange="updateEditorCategory(this.value)">
            <option value="renungan-harian">🌅 Renungan Harian</option>
            <option value="esai-kontemplasi">✍️ Esai Kontemplasi</option>
            <option value="readers-voice">👥 Reader's Voice</option>
            <option value="ulasan-serat">📜 Ulasan Serat</option>
          </select>

          <span style="font-size:13px; color:var(--text-muted); margin-left:4px;">Penulis:</span>
          <input type="text" id="editorAuthorInput" placeholder="Nama Penulis..." style="padding:4px 10px; font-size:12px; border-radius:6px; background:#1e293b; border:1px solid #475569; color:#f8fafc; outline:none; width:150px;" oninput="updateEditorAuthor(this.value)">
        </div>
        <div style="display:flex; gap:8px;">
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
    let currentStatusFilter = 'all';
    let currentCatFilter = 'all';
    let sortKey = 'date';
    let sortAsc = false; // Default: terbaru ke lama

    function showToast(msg) {
      const t = document.getElementById('toast');
      t.innerText = msg;
      t.style.display = 'block';
      setTimeout(() => { t.style.display = 'none'; }, 2500);
    }

    // Auto load on open (secured by Tailscale)
    loadData();

    function switchTab(tabId) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      document.querySelector(`button[onclick="switchTab('${tabId}')"]`).classList.add('active');
      document.getElementById(`panel-${tabId}`).classList.add('active');
    }

    function setStatusFilter(status, btn) {
      currentStatusFilter = status;
      document.querySelectorAll('button[onclick^="setStatusFilter"]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderTable();
    }

    function setCategoryTabFilter(cat, btn) {
      currentCatFilter = cat;
      document.querySelectorAll('button[onclick^="setCategoryTabFilter"]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderTable();
    }

    function handleSort(key) {
      if (sortKey === key) {
        sortAsc = !sortAsc;
      } else {
        sortKey = key;
        sortAsc = (key === 'date' ? false : true);
      }
      updateSortIcons();
      renderTable();
    }

    function updateSortIcons() {
      ['status', 'category', 'date', 'title', 'lang', 'media', 'gdoc'].forEach(k => {
        const icon = document.getElementById(`sort-${k}`);
        const th = icon ? icon.closest('th') : null;
        if (!icon || !th) return;
        
        if (sortKey === k) {
          th.classList.add('sorted');
          icon.innerText = sortAsc ? '▲' : '▼';
        } else {
          th.classList.remove('sorted');
          icon.innerText = '⇅';
        }
      });
    }

    function loadData() {
      fetch('/api/list')
        .then(r => r.json())
        .then(data => {
          renunganList = data.files;
          document.getElementById('statPub').innerText = data.stats.published_count;
          document.getElementById('statDraft').innerText = data.stats.draft_count;
          document.getElementById('statUnpub').innerText = data.stats.unpublished_count;
          document.getElementById('statFiles').innerText = data.stats.total_files;
          document.getElementById('statMedia').innerText = `${data.stats.poster_count} poster / ${data.stats.audio_count} audio`;
          updateSortIcons();
          renderTable();
        });
    }

    function renderTable() {
      const tbody = document.getElementById('tableBody');
      const q = document.getElementById('searchTable').value.toLowerCase();
      tbody.innerHTML = '';

      let filtered = renunganList.filter(f => {
        const matchesQuery = !q || f.title.toLowerCase().includes(q) || f.date.includes(q) || f.fname.toLowerCase().includes(q) || (f.author && f.author.toLowerCase().includes(q));
        const matchesStatus = currentStatusFilter === 'all' || f.status === currentStatusFilter;
        const matchesCategory = currentCatFilter === 'all' || f.category === currentCatFilter;
        return matchesQuery && matchesStatus && matchesCategory;
      });

      // Sorting
      filtered.sort((a, b) => {
        let valA = '', valB = '';
        if (sortKey === 'date') {
          valA = a.date || '';
          valB = b.date || '';
        } else if (sortKey === 'status') {
          valA = a.status || '';
          valB = b.status || '';
        } else if (sortKey === 'category') {
          valA = a.category || '';
          valB = b.category || '';
        } else if (sortKey === 'title') {
          valA = a.title || '';
          valB = b.title || '';
        } else if (sortKey === 'lang') {
          valA = a.lang || '';
          valB = b.lang || '';
        } else if (sortKey === 'media') {
          valA = (a.has_poster ? '2' : '0') + (a.has_audio ? '1' : '0');
          valB = (b.has_poster ? '2' : '0') + (b.has_audio ? '1' : '0');
        } else if (sortKey === 'gdoc') {
          valA = a.gdoc || '';
          valB = b.gdoc || '';
        }

        let comp = 0;
        if (valA < valB) comp = -1;
        else if (valA > valB) comp = 1;

        return sortAsc ? comp : -comp;
      });

      if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:24px; color:var(--text-muted);">Tidak ada tulisan yang cocok dengan filter.</td></tr>';
        return;
      }

      const catBadges = {
        'renungan-harian': '<span class="badge-cat-admin cat-admin-renungan">🌅 Renungan</span>',
        'esai-kontemplasi': '<span class="badge-cat-admin cat-admin-esai">✍️ Esai</span>',
        'readers-voice': '<span class="badge-cat-admin cat-admin-readers">👥 Voice</span>',
        'ulasan-serat': '<span class="badge-cat-admin cat-admin-ulasan">📜 Ulasan</span>'
      };

      filtered.forEach(f => {
        const tr = document.createElement('tr');
        const langBadge = f.lang === 'id' ? '<span class="badge badge-id">ID</span>' : (f.lang === 'en' ? '<span class="badge badge-en">EN</span>' : '<span class="badge badge-jv">JAWA</span>');
        const posterBadge = f.has_poster ? '<span class="badge badge-poster">Poster</span>' : '-';
        const audioBadge = f.has_audio ? '<span class="badge badge-audio">Audio</span>' : '-';
        const gdocLink = f.gdoc ? `<a href="${f.gdoc}" target="_blank" style="color:var(--primary); text-decoration:none;">Buka GDoc ↗</a>` : '-';

        const statusClass = f.status === 'published' ? 'status-published' : (f.status === 'draft' ? 'status-draft' : 'status-unpublished');
        const catBadge = catBadges[f.category] || '<span class="badge-cat-admin cat-admin-renungan">🌅 Renungan</span>';
        const authorHtml = f.author ? `<div style="font-size:11.5px; color:#38bdf8; font-weight:600; margin-top:2px;">✍️ ${f.author}</div>` : '';

        tr.innerHTML = `
          <td>
            <select class="status-select ${statusClass}" onchange="changeStatus('${f.fname}', this.value, this)">
              <option value="published" ${f.status === 'published' ? 'selected' : ''}>🟢 Published</option>
              <option value="draft" ${f.status === 'draft' ? 'selected' : ''}>🟡 Draft</option>
              <option value="unpublished" ${f.status === 'unpublished' ? 'selected' : ''}>⚪ Unpublished</option>
            </select>
          </td>
          <td>${catBadge}</td>
          <td style="font-weight:700; white-space:nowrap;">${f.date}</td>
          <td>
            <strong>${f.title}</strong>
            ${authorHtml}
            <div style="font-size:11px; color:var(--text-muted); font-family:'JetBrains Mono', monospace; margin-top:2px;">${f.fname}</div>
          </td>
          <td>${langBadge}</td>
          <td>${posterBadge} ${audioBadge}</td>
          <td>${gdocLink}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="openEditor('${f.fname}', '${f.status}', '${f.category || 'renungan-harian'}', '${f.author || ''}')">✏️ Edit</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    function changeStatus(fname, newStatus, selectElem) {
      fetch('/api/status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file: fname, status: newStatus })
      })
      .then(r => r.json())
      .then(d => {
        if (d.status === 'ok') {
          showToast(`Status ${fname} diganti: ${newStatus}`);
          if (selectElem) {
            selectElem.className = 'status-select ' + (newStatus === 'published' ? 'status-published' : (newStatus === 'draft' ? 'status-draft' : 'status-unpublished'));
          }
          loadData();
        } else {
          alert('Gagal ngganti status: ' + d.error);
        }
      });
    }

    function filterTable() {
      renderTable();
    }

    function openEditor(fname, status, category, author) {
      currentActiveFile = fname;
      document.getElementById('currentFileLabel').innerText = fname;
      
      const sel = document.getElementById('editorStatusSelect');
      sel.value = status || 'published';
      sel.className = 'status-select ' + (sel.value === 'published' ? 'status-published' : (sel.value === 'draft' ? 'status-draft' : 'status-unpublished'));

      const catSel = document.getElementById('editorCatSelect');
      catSel.value = category || 'renungan-harian';

      const authInp = document.getElementById('editorAuthorInput');
      authInp.value = author || '';

      fetch(`/api/get?file=${encodeURIComponent(fname)}`)
        .then(r => r.json())
        .then(d => {
          document.getElementById('codeEditor').value = d.content;
          updatePreview();
          switchTab('editor');
        });
    }

    function updateEditorStatus(newStatus) {
      const sel = document.getElementById('editorStatusSelect');
      sel.className = 'status-select ' + (newStatus === 'published' ? 'status-published' : (newStatus === 'draft' ? 'status-draft' : 'status-unpublished'));
      
      let raw = document.getElementById('codeEditor').value;
      if (raw.startsWith('---')) {
        if (/^status:\s*.*$/m.test(raw)) {
          raw = raw.replace(/^status:\s*.*$/m, 'status: ' + newStatus);
        } else {
          raw = raw.replace(/^---/, '---\\nstatus: ' + newStatus);
        }
      } else {
        raw = '---\\nstatus: ' + newStatus + '\\n---\\n\\n' + raw;
      }
      document.getElementById('codeEditor').value = raw;
      showToast('Status diset ke ' + newStatus + ' (klik Simpan Naskah)');
    }

    function updateEditorCategory(newCat) {
      let raw = document.getElementById('codeEditor').value;
      if (raw.startsWith('---')) {
        if (/^category:\s*.*$/m.test(raw)) {
          raw = raw.replace(/^category:\s*.*$/m, 'category: ' + newCat);
        } else {
          raw = raw.replace(/^---/, '---\\ncategory: ' + newCat);
        }
      } else {
        raw = '---\\ncategory: ' + newCat + '\\n---\\n\\n' + raw;
      }
      document.getElementById('codeEditor').value = raw;
      showToast('Kategori diset ke ' + newCat + ' (klik Simpan Naskah)');
    }

    function updateEditorAuthor(newAuthor) {
      let raw = document.getElementById('codeEditor').value;
      if (raw.startsWith('---')) {
        if (/^author:\s*.*$/m.test(raw)) {
          raw = raw.replace(/^author:\s*.*$/m, 'author: "' + newAuthor + '"');
        } else {
          raw = raw.replace(/^---/, '---\\nauthor: "' + newAuthor + '"');
        }
      } else {
        raw = '---\\nauthor: "' + newAuthor + '"\\n---\\n\\n' + raw;
      }
      document.getElementById('codeEditor').value = raw;
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
          showToast('Naskah kasil kasimpen wonten ing server!');
          loadData();
        } else {
          alert('Gagal nyimpen naskah: ' + d.error);
        }
      });
    }

    function createNewEntry() {
      const catChoice = prompt('Pilih Kategori Tulisan:\n1 = 🌅 Renungan Harian\n2 = ✍️ Esai Kontemplasi\n3 = 👥 Reader’s Voice (Kiriman Pembaca)\n4 = 📜 Ulasan Serat', '1');
      if (!catChoice) return;
      
      let cat = 'renungan-harian';
      let catPrefix = 'renungan';
      if (catChoice === '2') { cat = 'esai-kontemplasi'; catPrefix = 'esai'; }
      else if (catChoice === '3') { cat = 'readers-voice'; catPrefix = 'suara-pembaca'; }
      else if (catChoice === '4') { cat = 'ulasan-serat'; catPrefix = 'ulasan'; }

      const date = prompt('Masukkan Tanggal (YYYY-MM-DD):', new Date().toISOString().split('T')[0]);
      if (!date) return;
      const topic = prompt('Masukkan Topik / Sesirah Singkat (contoh: rila, sumeleh, eling):', 'kontemplasi');
      if (!topic) return;
      const author = prompt('Nama Penulis (kosongkan jika anonim / tim):', (cat === 'readers-voice' ? 'Nama Pembaca' : 'Satya Adi Dharma'));

      const fname = `${catPrefix}-${topic.toLowerCase().replace(/\\s+/g, '-')}-ind-${date}.md`;
      const template = `---
title: "Sesirah Tulisan ${date}"
date: ${date}
status: draft
category: ${cat}
author: "${author || ''}"
tags: ['kontemplasi', 'bahasa-indonesia', 'sang-guru-sejati']
language: id
---

# Sesirah Tulisan ${date}

*${date}*

*RENUNGAN PENYISWAAN*

*Sesirah Tulisan*

_Sugeng Enjang, Salam Karahayon_

*📖 SABDA HARI INI :*

Sasangka Jati : _"Tulis kutipan sabda suci ing mriki..."_

💭 *URAIAN* :

Tulis wedharan, panyuraos, utawi esai kontemplasi kanthi cetha lan runtut ing mriki...

🙏 *PRAKTIK* :

1. Langkah setunggal
2. Langkah kalih
3. Langkah tiga

📝 *APLIKASI* :

1. Pitakenan panyuraos kapisan?
`;
      currentActiveFile = fname;
      document.getElementById('currentFileLabel').innerText = fname;
      document.getElementById('editorStatusSelect').value = 'draft';
      document.getElementById('editorCatSelect').value = cat;
      document.getElementById('editorAuthorInput').value = author || '';
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
          showToast('Berkas kasil kaunggah: ' + d.filename);
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
        elif parsed.path == "/api/status":
            self.handle_api_status()
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
        pub_count = 0
        draft_count = 0
        unpub_count = 0

        for f in md_files:
            fname = os.path.basename(f)
            with open(f, "r", encoding="utf-8") as fp:
                raw = fp.read()

            m_date = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
            date_iso = m_date.group(1) if m_date else "2026-08-01"

            # Status
            status = "published"
            m_st = re.search(r'^status:\s*([a-zA-Z0-9_-]+)', raw, re.MULTILINE | re.IGNORECASE)
            if m_st:
                status = m_st.group(1).lower().strip()
            
            if status == "draft":
                draft_count += 1
            elif status == "unpublished":
                unpub_count += 1
            else:
                status = "published"
                pub_count += 1

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

            # Category
            cat = "renungan-harian"
            m_cat = re.search(r'^category:\s*([a-zA-Z0-9_-]+)', raw, re.MULTILINE | re.IGNORECASE)
            if m_cat:
                cat = m_cat.group(1).lower().strip()
            elif "ulasan" in fname.lower():
                cat = "ulasan-serat"
            elif "esai" in fname.lower():
                cat = "esai-kontemplasi"
            elif "suara" in fname.lower() or "voice" in fname.lower():
                cat = "readers-voice"

            cat_map = {
                "renungan": "renungan-harian",
                "renungan-harian": "renungan-harian",
                "esai": "esai-kontemplasi",
                "esai-kontemplasi": "esai-kontemplasi",
                "readers-voice": "readers-voice",
                "reader-voice": "readers-voice",
                "suara-pembaca": "readers-voice",
                "ulasan": "ulasan-serat",
                "ulasan-serat": "ulasan-serat"
            }
            cat = cat_map.get(cat, "renungan-harian")

            # Author
            author = ""
            m_auth = re.search(r'^author:\s*([^\n\r]+)', raw, re.MULTILINE | re.IGNORECASE)
            if m_auth:
                author = m_auth.group(1).replace('"', '').replace("'", '').strip()

            stem = fname.replace("renungan-", "").replace(".md", "")
            core_topic = re.sub(r'-\d{4}-\d{2}-\d{2}', '', stem)
            core_topic = re.sub(r'-\d+-agustus-\d{4}', '', core_topic)
            core_topic = re.sub(r'-(?:ind|eng|jv)$', '', core_topic)

            base_no_ext = os.path.splitext(fname)[0]
            has_audio = os.path.exists(os.path.join(RENUNGAN_DIR, base_no_ext + ".ogg")) or os.path.exists(os.path.join(RENUNGAN_DIR, base_no_ext + ".mp3"))
            if has_audio:
                audios.add(base_no_ext)

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
                "status": status,
                "category": cat,
                "author": author,
                "has_poster": has_poster,
                "has_audio": has_audio,
                "gdoc": gdoc
            })

        response = {
            "stats": {
                "published_count": pub_count,
                "draft_count": draft_count,
                "unpublished_count": unpub_count,
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

    def handle_api_status(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
            fname = os.path.basename(data.get("file", ""))
            new_status = data.get("status", "published").lower().strip()
            if not fname or new_status not in ["published", "draft", "unpublished"]:
                return self.send_json({"status": "error", "error": "Invalid params"}, status=400)

            p1 = os.path.join(RENUNGAN_DIR, fname)
            p2 = os.path.join(SHARE_DIR, fname)
            if not os.path.exists(p1):
                return self.send_json({"status": "error", "error": "File not found"}, status=404)

            with open(p1, "r", encoding="utf-8") as fp:
                raw = fp.read()

            if raw.startswith("---"):
                if re.search(r'^status:\s*.*$', raw, re.MULTILINE):
                    updated = re.sub(r'^status:\s*.*$', f"status: {new_status}", raw, flags=re.MULTILINE)
                else:
                    updated = re.sub(r'^---', f"---\nstatus: {new_status}", raw, count=1)
            else:
                updated = f"---\nstatus: {new_status}\n---\n\n" + raw

            with open(p1, "w", encoding="utf-8") as fp:
                fp.write(updated)
            if os.path.exists(SHARE_DIR):
                with open(p2, "w", encoding="utf-8") as fp:
                    fp.write(updated)

            self.send_json({"status": "ok", "file": fname, "new_status": new_status})
        except Exception as e:
            self.send_json({"status": "error", "error": str(e)}, status=500)

    def handle_api_upload(self):
        content_type = self.headers.get('Content-Type', '')
        if 'multipart/form-data' not in content_type:
            return self.send_json({"status": "error", "error": "Expected multipart form"}, status=400)

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        
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
