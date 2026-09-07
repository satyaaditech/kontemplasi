import os
import shutil
import glob
import re
import json

def build_clean_pustaka():
    renungan_dir = "/home/satyaaditech/kontemplasi/renungan"
    pustaka_dir = "/home/satyaaditech/kontemplasi"
    os.makedirs(pustaka_dir, exist_ok=True)

    md_files = sorted(glob.glob(os.path.join(renungan_dir, "*.md")))

    def clean_markdown_artifacts(text):
        if not text:
            return ""
        t = re.sub(r'^[#\s]+', '', text)
        t = re.sub(r'^title:\s*["\']?', '', t)
        t = re.sub(r'["\']?$', '', t)
        t = t.replace("*", "").replace("_", "").replace("#", "").replace("`", "")
        t = re.sub(r'\s+', ' ', t).strip()
        return t

    def parse_date(fname, raw_text):
        m = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
        if m:
            return m.group(1)
        m = re.search(r'(\d{1,2})-agustus-(\d{4})', fname, re.IGNORECASE)
        if m:
            day = int(m.group(1))
            year = m.group(2)
            return f"{year}-08-{day:02d}"
        months = {
            'januari': '01', 'februari': '02', 'maret': '03', 'april': '04',
            'mei': '05', 'juni': '06', 'juli': '07', 'agustus': '08',
            'september': '09', 'oktober': '10', 'november': '11', 'desember': '12',
            'january': '01', 'february': '02', 'march': '03', 'may': '05',
            'june': '06', 'july': '07', 'august': '08', 'october': '10', 'december': '12'
        }
        m = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', raw_text)
        if m:
            day = int(m.group(1))
            mon_str = m.group(2).lower()
            year = m.group(3)
            if mon_str in months:
                return f"{year}-{months[mon_str]}-{day:02d}"
        return "2026-08-01"

    parsed_files = []
    for fpath in md_files:
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            raw = f.read()

        date_iso = parse_date(fname, raw)

        # Detect lang
        lang = "jv"
        if "-ind" in fname or "ind" in fname.lower() and not "pindha" in fname:
            lang = "id"
        elif "-eng" in fname:
            lang = "en"
        if "*SABDA HARI INI" in raw or "*URAIAN" in raw or "Salam Bahagia" in raw:
            lang = "id"
        elif "*DAILY SCRIPTURE" in raw or "*EXPOSITION" in raw:
            lang = "en"
        elif "*PETHIKAN DINTEN" in raw or "*ANDHARAN" in raw:
            lang = "jv"

        # Topic normalization
        stem = fname.replace("renungan-", "").replace(".md", "")
        core_topic = re.sub(r'-\d{4}-\d{2}-\d{2}', '', stem)
        core_topic = re.sub(r'-\d+-agustus-\d{4}', '', core_topic)
        core_topic = re.sub(r'-(?:ind|eng|jv)$', '', core_topic)
        core_topic = re.sub(r'-(?:v\d+|ronde\d+)$', '', core_topic)
        core_topic = re.sub(r'-(?:selasa|senin|rabu|kamis|jumat|sabtu|minggu)', '', core_topic)

        # Version rank (for choosing best draft)
        v_rank = 1
        if "-v6" in fname: v_rank = 6
        elif "-v5" in fname: v_rank = 5
        elif "-v4" in fname: v_rank = 4
        elif "-v3" in fname: v_rank = 3
        elif "-v2" in fname: v_rank = 2
        elif "ronde2" in fname: v_rank = 2

        # Extract title
        title = ""
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        for l in lines[1:6]:
            if "RENUNGAN" not in l and not l.startswith("_Salam") and not l.startswith("_Sugeng") and not l.startswith("_Greetings") and not l.startswith("---"):
                title = clean_markdown_artifacts(l)
                if title: break
        if not title:
            title = core_topic.replace("-", " ").title()

        # Date string formatted
        date_match = re.search(r'^\*([A-Z\s,0-9]+)\*', raw, re.MULTILINE)
        date_str = clean_markdown_artifacts(date_match.group(1).strip()) if date_match else date_iso

        # GDoc
        gdoc_match = re.search(r'https://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)(?:/edit)?', raw)
        gdoc_url = gdoc_match.group(0) if gdoc_match else ""

        # Audio
        base_no_ext = os.path.splitext(fname)[0]
        audio_file = ""
        for ext in [".ogg", ".mp3"]:
            cand = os.path.join(renungan_dir, base_no_ext + ext)
            if os.path.exists(cand):
                audio_file = f"renungan/{base_no_ext}{ext}"
                break

        # STRICT POSTER MATCHING ONLY
        poster_file = ""
        group_id = f"{date_iso}_{core_topic}"

        explicit_posters = {
            "2026-09-05_teladan": "renungan/poster-teladan-2026-09-05.jpg",
            "2026-09-02_menerima-perubahan": "renungan/poster-menerima-perubahan-2026-09-02.jpg",
            "2026-09-01_nama-baik": "renungan/poster-nama-baik-2026-09-01.jpg",
            "2026-08-28_eling": "renungan/poster-ketidak-kekalan-2026-08-28.jpg",
            "2026-08-27_beban-batin": "renungan/poster-beban-batin-2026-08-27.jpg",
            "2026-08-25_ngunjara-hawa-napsu": "renungan/newsletter-ngunjara-hawa-napsu-2026-08-25.png",
            "2026-08-20_budi-darma": "renungan/infografis-budi-darma-2026-08-20.png",
            "2026-08-19_nderek-paduka": "renungan/creative_infographic_nderek_paduka_2026-08-19.jpg",
            "2026-08-11_sabar": "renungan/poster-sabda-khusus-kesabaran-2026-08-11.jpg"
        }

        if group_id in explicit_posters and os.path.exists(os.path.join(pustaka_dir, explicit_posters[group_id])):
            poster_file = explicit_posters[group_id]

        # Book source
        book_source = "Sasangka Jati"
        if "BRSR" in raw or "Bawa Raos" in raw:
            book_source = "Bawa Raos (BRSR)"
        elif "Sabda Khusus" in raw or "SKH" in raw:
            book_source = "Sabda Khusus (SKH)"
        elif "TKL" in raw or "Taman Kamulyan" in raw:
            book_source = "Taman Kamulyan (TKL)"
        elif "UUJM" in raw or "Ular-Ular" in raw:
            book_source = "Ular-Ular (UUJM)"
        elif "Hasta Sila" in raw:
            book_source = "Sasangka Jati (Hasta Sila)"
        elif "Tunggal Sabda" in raw:
            book_source = "Sasangka Jati (Tunggal Sabda)"
        elif "Panembah" in raw:
            book_source = "Sasangka Jati (Panembah)"

        # Excerpt
        sabda_excerpt = ""
        sabda_match = re.search(r'(?:PETHIKAN DINTEN PUNIKA|SABDA HARI INI|DAILY SCRIPTURE)\s*:\s*\n*(.*?)(?=\n\s*(?:Terjemahan|Translation|💭|\*ANDHARAN|\*URAIAN|\*EXPOSITION|$))', raw, re.DOTALL | re.IGNORECASE)
        if sabda_match:
            sabda_excerpt = clean_markdown_artifacts(sabda_match.group(1).strip())
            sabda_excerpt = (sabda_excerpt[:140] + "...") if len(sabda_excerpt) > 140 else sabda_excerpt

        # Tags
        tags = [book_source.split("(")[0].strip()]
        for kw, tag in [
            ("sabar", "Sabar"), ("rila", "Rila"), ("narima", "Narima"),
            ("pangapura", "Pengampunan"), ("mengampuni", "Pengampunan"), ("pangaksama", "Pengampunan"),
            ("lisan", "Lisan"), ("eling", "Eling"), ("hawa napsu", "Hawa Nafsu"), ("nafsu", "Hawa Nafsu"),
            ("panembah", "Panembah"), ("sukma", "Kasukman"), ("kamardikan", "Kamardikan"),
            ("merdeka", "Kamardikan"), ("beban", "Katentreman"), ("sumelang", "Piandel"),
            ("teladan", "Keteladanan"), ("budi darma", "Budi Darma")
        ]:
            if kw in raw.lower() and tag not in tags:
                tags.append(tag)

        # Extract status (published/draft/unpublished)
        status = "published"
        m_st = re.search(r'^status:\s*([a-zA-Z0-9_-]+)', raw, re.MULTILINE | re.IGNORECASE)
        if m_st:
            status = m_st.group(1).lower().strip()

        # Extract category
        cat = "renungan-harian"
        m_cat = re.search(r'^category:\s*([a-zA-Z0-9_-]+)', raw, re.MULTILINE | re.IGNORECASE)
        if m_cat:
            cat = m_cat.group(1).lower().strip()
        elif "ulasan" in fname.lower() or "ulasan" in core_topic.lower():
            cat = "ulasan-serat"
        elif "esai" in fname.lower() or "esai" in core_topic.lower():
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

        # Extract author
        author = ""
        m_auth = re.search(r'^author:\s*([^\n\r]+)', raw, re.MULTILINE | re.IGNORECASE)
        if m_auth:
            author = m_auth.group(1).replace('"', '').replace("'", '').strip()

        parsed_files.append({
            "fname": fname,
            "date_iso": date_iso,
            "date_str": date_str,
            "core_topic": core_topic,
            "group_id": group_id,
            "lang": lang,
            "v_rank": v_rank,
            "title": title,
            "book": book_source,
            "tags": tags[:4],
            "gdoc": gdoc_url,
            "audio": audio_file,
            "poster": poster_file,
            "excerpt": sabda_excerpt,
            "status": status,
            "category": cat,
            "author": author,
            "raw": raw
        })

    # Group into deduplicated entries
    groups = {}
    for pf in parsed_files:
        if pf.get("status") in ["draft", "unpublished"]:
            continue
        gid = pf["group_id"]
        if gid not in groups:
            groups[gid] = []
        groups[gid].append(pf)

    deduped_articles = []
    for gid, files in groups.items():
        files.sort(key=lambda x: x["v_rank"], reverse=True)
        
        versions = {}
        for f in files:
            l = f["lang"]
            if l not in versions:
                versions[l] = f
        
        primary = versions.get("id") or versions.get("jv") or versions.get("en") or files[0]

        poster = next((f["poster"] for f in files if f["poster"]), "")
        audio = next((f["audio"] for f in files if f["audio"]), "")
        gdoc = next((f["gdoc"] for f in files if f["gdoc"]), "")

        available_langs = sorted(list(versions.keys()))

        versions_payload = {}
        for l, item in versions.items():
            versions_payload[l] = {
                "title": item["title"],
                "date": item["date_str"],
                "gdoc": item["gdoc"] or gdoc,
                "audio": item["audio"] or audio,
                "raw": item["raw"]
            }

        deduped_articles.append({
            "id": gid,
            "date_iso": primary["date_iso"],
            "date": primary["date_str"],
            "title": primary["title"],
            "book": primary["book"],
            "tags": primary["tags"],
            "excerpt": primary["excerpt"],
            "poster": poster,
            "audio": audio,
            "gdoc": gdoc,
            "primary_lang": primary["lang"],
            "category": primary.get("category", "renungan-harian"),
            "author": primary.get("author", ""),
            "available_langs": available_langs,
            "versions": versions_payload
        })

    # STRICT SORT: NEWEST FIRST
    deduped_articles.sort(key=lambda x: x["date_iso"], reverse=True)

    articles_json_str = json.dumps(deduped_articles, ensure_ascii=False)

    html_template = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pustaka Penyiswaan - E-Library Ajaran Sang Guru Sejati</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300;1,400&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #f8fafc;
      --surface: #ffffff;
      --surface-border: #e2e8f0;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --primary: #1e3a8a;
      --primary-light: #eff6ff;
      --primary-border: #bfdbfe;
      --accent-gold: #b45309;
      --accent-gold-bg: #fef3c7;
      --accent-green: #15803d;
      --accent-green-bg: #dcfce7;
      --card-hover: #ffffff;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
      --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
      --shadow-lg: 0 10px 25px -5px rgba(0,0,0,0.08), 0 8px 10px -6px rgba(0,0,0,0.04);
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 16px;
      --font-ui: 'Plus Jakarta Sans', -apple-system, sans-serif;
      --font-serif: 'Merriweather', Georgia, serif;
    }}

    [data-theme="dark"] {{
      --bg: #090d16;
      --surface: #131b2e;
      --surface-border: #1e293b;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --primary: #3b82f6;
      --primary-light: #1e293b;
      --primary-border: #2563eb;
      --accent-gold: #fbbf24;
      --accent-gold-bg: #291b00;
      --accent-green: #4ade80;
      --accent-green-bg: #052e16;
      --card-hover: #17223b;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
      --shadow-md: 0 4px 6px rgba(0,0,0,0.4);
      --shadow-lg: 0 10px 25px rgba(0,0,0,0.6);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: var(--font-ui);
      background-color: var(--bg);
      color: var(--text-main);
      line-height: 1.6;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      transition: background-color 0.2s ease, color 0.2s ease;
    }}

    .container {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 0 20px;
      width: 100%;
    }}

    /* HEADER */
    header {{
      background-color: var(--surface);
      border-bottom: 1px solid var(--surface-border);
      position: sticky;
      top: 0;
      z-index: 40;
      backdrop-filter: blur(8px);
    }}

    .nav-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 72px;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: var(--text-main);
    }}

    .brand-icon {{
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, #1e3a8a, #3b82f6);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 20px;
      box-shadow: 0 2px 8px rgba(30,58,138,0.25);
    }}

    .brand-text h1 {{
      font-size: 18px;
      font-weight: 700;
      letter-spacing: -0.02em;
      line-height: 1.2;
    }}

    .brand-text p {{
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 500;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .theme-toggle {{
      background: var(--bg);
      border: 1px solid var(--surface-border);
      color: var(--text-main);
      padding: 8px 14px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-size: 13px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s;
    }}
    .theme-toggle:hover {{
      background: var(--primary-light);
      border-color: var(--primary);
    }}

    /* HERO & SEARCH BAR */
    .hero {{
      padding: 32px 0 24px;
      text-align: center;
    }}

    .hero h2 {{
      font-size: 26px;
      font-weight: 800;
      letter-spacing: -0.02em;
      margin-bottom: 8px;
      color: var(--text-main);
    }}

    .hero p {{
      font-size: 15px;
      color: var(--text-muted);
      max-width: 650px;
      margin: 0 auto 24px;
    }}

    .search-container {{
      max-width: 680px;
      margin: 0 auto 20px;
      position: relative;
    }}

    .search-input {{
      width: 100%;
      padding: 14px 20px 14px 48px;
      font-size: 15px;
      font-family: inherit;
      background: var(--surface);
      border: 2px solid var(--surface-border);
      border-radius: 12px;
      color: var(--text-main);
      box-shadow: var(--shadow-sm);
      outline: none;
      transition: all 0.2s;
    }}

    .search-input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 4px var(--primary-light);
    }}

    .search-icon {{
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 18px;
      pointer-events: none;
    }}

    /* CATEGORY NAV */
    .category-nav {{
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 8px;
      margin: 0 auto 24px;
      max-width: 850px;
    }}

    .cat-pill {{
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 13.5px;
      font-weight: 600;
      background: var(--surface);
      border: 1px solid var(--surface-border);
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.15s;
      box-shadow: var(--shadow-sm);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .cat-pill:hover {{
      border-color: var(--primary);
      color: var(--primary);
      transform: translateY(-1px);
    }}

    .cat-pill.active {{
      background: var(--primary);
      border-color: var(--primary);
      color: #ffffff;
      box-shadow: 0 4px 10px rgba(30, 58, 138, 0.2);
    }}

    .badge-cat {{
      font-size: 11px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 4px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}
    .cat-renungan {{ background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }}
    .cat-esai {{ background: #fdf4ff; color: #86198f; border: 1px solid #f5d0fe; }}
    .cat-readers {{ background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; }}
    .cat-ulasan {{ background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }}

    /* FILTERS */
    .filter-bar {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--surface-border);
    }}

    .lang-tabs {{
      display: flex;
      background: var(--surface);
      border: 1px solid var(--surface-border);
      padding: 4px;
      border-radius: 10px;
      gap: 4px;
    }}

    .lang-tab {{
      padding: 6px 14px;
      border-radius: 7px;
      font-size: 13px;
      font-weight: 600;
      border: none;
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.15s;
    }}

    .lang-tab.active {{
      background: var(--primary);
      color: white;
      box-shadow: var(--shadow-sm);
    }}

    .topic-chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}

    .topic-chip {{
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      background: var(--surface);
      border: 1px solid var(--surface-border);
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.15s;
    }}

    .topic-chip:hover, .topic-chip.active {{
      background: var(--accent-gold-bg);
      border-color: var(--accent-gold);
      color: var(--accent-gold);
      font-weight: 600;
    }}

    /* GRID & CARDS */
    .articles-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 20px;
      margin-bottom: 60px;
    }}

    .article-card {{
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius-md);
      padding: 20px;
      display: flex;
      flex-direction: column;
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: var(--shadow-sm);
      position: relative;
    }}

    .article-card:hover {{
      transform: translateY(-3px);
      box-shadow: var(--shadow-md);
      border-color: var(--primary-border);
    }}

    .card-meta {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 10px;
      font-size: 12px;
    }}

    .card-date {{
      color: var(--text-muted);
      font-weight: 700;
      letter-spacing: 0.02em;
    }}

    .lang-pills {{
      display: flex;
      gap: 4px;
      align-items: center;
    }}

    .lang-badge {{
      display: inline-block;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .lang-badge.id {{ background: #fee2e2; color: #991b1b; }}
    .lang-badge.jv {{ background: #fef3c7; color: #92400e; }}
    .lang-badge.en {{ background: #e0e7ff; color: #3730a3; }}

    .card-title {{
      font-size: 16px;
      font-weight: 700;
      line-height: 1.4;
      margin-bottom: 8px;
      color: var(--text-main);
    }}

    .card-book {{
      font-size: 12px;
      font-weight: 600;
      color: var(--accent-gold);
      margin-bottom: 8px;
    }}

    .card-excerpt {{
      font-family: var(--font-serif);
      font-size: 13px;
      color: var(--text-muted);
      font-style: italic;
      line-height: 1.5;
      margin-bottom: 16px;
      flex-grow: 1;
    }}

    .card-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-top: 1px solid var(--surface-border);
      padding-top: 12px;
      margin-top: auto;
      font-size: 12px;
    }}

    .card-tags {{
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
    }}

    .mini-tag {{
      background: var(--bg);
      color: var(--text-muted);
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 500;
      border: 1px solid var(--surface-border);
    }}

    .card-features {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
    }}

    .poster-pill {{
      background: var(--accent-green-bg);
      color: var(--accent-green);
      font-weight: 700;
      font-size: 11px;
      padding: 2px 6px;
      border-radius: 4px;
      display: inline-flex;
      align-items: center;
      gap: 3px;
    }}

    /* MODAL / READER */
    .modal-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.65);
      z-index: 100;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
      backdrop-filter: blur(4px);
    }}

    .modal-overlay.active {{
      display: flex;
    }}

    .reader-modal {{
      background: var(--surface);
      width: 100%;
      max-width: 860px;
      max-height: 90vh;
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-lg);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      border: 1px solid var(--surface-border);
      animation: modalSlide 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    @keyframes modalSlide {{
      from {{ opacity: 0; transform: translateY(20px) scale(0.98); }}
      to {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}

    .reader-header {{
      padding: 14px 20px;
      border-bottom: 1px solid var(--surface-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--surface);
      position: sticky;
      top: 0;
      z-index: 10;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .reader-title-area {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}

    .reader-lang-switcher {{
      display: flex;
      background: var(--bg);
      padding: 3px;
      border-radius: 8px;
      gap: 3px;
      border: 1px solid var(--surface-border);
    }}

    .reader-lang-btn {{
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      border: none;
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.15s;
    }}

    .reader-lang-btn.active {{
      background: var(--primary);
      color: white;
    }}

    .reader-actions {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .btn {{
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: 1px solid transparent;
      text-decoration: none;
      transition: all 0.15s;
    }}

    .btn-primary {{
      background: var(--primary);
      color: white;
    }}
    .btn-primary:hover {{
      opacity: 0.9;
    }}

    .btn-secondary {{
      background: var(--bg);
      border-color: var(--surface-border);
      color: var(--text-main);
    }}
    .btn-secondary:hover {{
      background: var(--primary-light);
      border-color: var(--primary);
    }}

    .btn-close {{
      background: transparent;
      border: none;
      font-size: 20px;
      color: var(--text-muted);
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 6px;
    }}
    .btn-close:hover {{
      background: var(--bg);
      color: var(--text-main);
    }}

    /* SEAMLESS POSTER CONTAINER */
    .poster-hero {{
      margin-bottom: 24px;
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid var(--surface-border);
      background: var(--bg);
      box-shadow: var(--shadow-sm);
      text-align: center;
      position: relative;
    }}

    .poster-img {{
      width: 100%;
      height: auto;
      max-height: 480px;
      object-fit: contain;
      display: block;
      cursor: zoom-in;
      transition: transform 0.2s;
    }}

    .poster-hint {{
      padding: 8px;
      font-size: 12px;
      color: var(--text-muted);
      background: var(--surface);
      border-top: 1px solid var(--surface-border);
      font-family: var(--font-ui);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }}

    .reader-body {{
      padding: 28px 36px 40px;
      overflow-y: auto;
      font-family: var(--font-serif);
      font-size: 16px;
      line-height: 1.8;
      color: var(--text-main);
    }}

    .reader-body h1, .reader-body h2, .reader-body h3 {{
      font-family: var(--font-ui);
      font-weight: 700;
      line-height: 1.3;
      margin: 20px 0 12px;
      color: var(--text-main);
    }}

    .reader-body h1 {{ font-size: 22px; color: var(--primary); }}
    .reader-body h2 {{ font-size: 17px; margin-top: 24px; border-bottom: 1px solid var(--surface-border); padding-bottom: 6px; }}

    .reader-body p {{
      margin-bottom: 16px;
    }}

    .reader-body blockquote {{
      border-left: 4px solid var(--accent-gold);
      background: var(--accent-gold-bg);
      padding: 16px 20px;
      border-radius: 0 var(--radius-md) var(--radius-md) 0;
      margin: 20px 0;
      font-style: italic;
      color: var(--text-main);
    }}

    .reader-body ul, .reader-body ol {{
      margin: 14px 0 18px 24px;
    }}
    .reader-body li {{
      margin-bottom: 8px;
    }}

    /* LIGHTBOX */
    .lightbox-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.9);
      z-index: 250;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}
    .lightbox-overlay.active {{ display: flex; }}
    .lightbox-img {{
      max-width: 95vw;
      max-height: 95vh;
      border-radius: 8px;
      box-shadow: 0 0 30px rgba(0,0,0,0.8);
      cursor: zoom-out;
    }}

    /* TOAST */
    .toast {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #0f172a;
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      box-shadow: var(--shadow-lg);
      display: none;
      z-index: 200;
      animation: fadeIn 0.2s ease;
    }}
    .toast.show {{ display: block; }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* FOOTER */
    footer {{
      margin-top: auto;
      border-top: 1px solid var(--surface-border);
      background: var(--surface);
      padding: 24px 0;
      text-align: center;
      font-size: 13px;
      color: var(--text-muted);
    }}

    @media (max-width: 640px) {{
      .hero h2 {{ font-size: 22px; }}
      .articles-grid {{ grid-template-columns: 1fr; }}
      .reader-body {{ padding: 20px; font-size: 15px; }}
      .nav-bar {{ height: 60px; }}
      .brand-text p {{ display: none; }}
    }}
  </style>
</head>
<body>

  <!-- HEADER -->
  <header>
    <div class="container nav-bar">
      <a href="#" class="brand">
        <div class="brand-icon">📜</div>
        <div class="brand-text">
          <h1>Pustaka Penyiswaan</h1>
          <p>E-Library Ajaran Sang Guru Sejati</p>
        </div>
      </a>
      <div class="header-actions">
        <button class="theme-toggle" id="themeToggle" onclick="toggleTheme()">
          <span id="themeIcon">🌙</span> <span id="themeText">Dark</span>
        </button>
      </div>
    </div>
  </header>

  <!-- MAIN CONTAINER -->
  <main class="container">
    <!-- HERO SECTION -->
    <section class="hero">
      <h2>Kumpulan Kontemplasi berdasar Ajaran Sang Guru Sejati</h2>
      <p>Kumpulan pethikan sabda murni, ulasan panyuraos batin, sarta tuntunan laku padintenan ingkang katata jangkep lan runtut.</p>
      
      <!-- SEARCH INPUT -->
      <div class="search-container">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" class="search-input" placeholder="Tulis tema, sabda, utawi tembung kunci (contoh: teladan, sabar, rila, mengampuni)..." oninput="filterArticles()">
      </div>

      <!-- CATEGORY NAV -->
      <div class="category-nav">
        <button class="cat-pill active" data-cat="all" onclick="setCategoryFilter('all', this)">✨ Semua Materi</button>
        <button class="cat-pill" data-cat="renungan-harian" onclick="setCategoryFilter('renungan-harian', this)">🌅 Renungan Harian</button>
        <button class="cat-pill" data-cat="esai-kontemplasi" onclick="setCategoryFilter('esai-kontemplasi', this)">✍️ Esai Kontemplasi</button>
        <button class="cat-pill" data-cat="readers-voice" onclick="setCategoryFilter('readers-voice', this)">👥 Reader’s Voice</button>
        <button class="cat-pill" data-cat="ulasan-serat" onclick="setCategoryFilter('ulasan-serat', this)">📜 Ulasan Serat</button>
      </div>
    </section>

    <!-- FILTER BAR -->
    <section class="filter-bar">
      <div class="lang-tabs">
        <button class="lang-tab active" data-lang="all" onclick="setLangFilter('all')">Sedaya ({len(deduped_articles)})</button>
        <button class="lang-tab" data-lang="id" onclick="setLangFilter('id')">🇮🇩 Indonesia</button>
        <button class="lang-tab" data-lang="jv" onclick="setLangFilter('jv')">ꦗꦮ Basa Jawi</button>
        <button class="lang-tab" data-lang="en" onclick="setLangFilter('en')">🇬🇧 English</button>
      </div>

      <div class="topic-chips" id="topicChips">
        <span class="topic-chip active" onclick="setTopicFilter('all')">Sedaya Tema</span>
        <span class="topic-chip" onclick="setTopicFilter('Keteladanan')">Keteladanan</span>
        <span class="topic-chip" onclick="setTopicFilter('Sabar')">Sabar</span>
        <span class="topic-chip" onclick="setTopicFilter('Rila')">Rila</span>
        <span class="topic-chip" onclick="setTopicFilter('Narima')">Narima</span>
        <span class="topic-chip" onclick="setTopicFilter('Pengampunan')">Pengampunan</span>
        <span class="topic-chip" onclick="setTopicFilter('Eling')">Eling</span>
        <span class="topic-chip" onclick="setTopicFilter('Hawa Nafsu')">Hawa Nafsu</span>
      </div>
    </section>

    <!-- ARTICLES GRID -->
    <section class="articles-grid" id="articlesGrid">
      <!-- Generated via JS -->
    </section>
  </main>

  <!-- READER MODAL -->
  <div class="modal-overlay" id="readerModal" onclick="closeModalOnOverlay(event)">
    <div class="reader-modal">
      <div class="reader-header">
        <div class="reader-title-area">
          <div class="reader-lang-switcher" id="modalLangSwitcher">
            <!-- Dynamic language buttons (ID/JV/EN) -->
          </div>
          <span id="modalDate" style="font-size:13px; font-weight:700; color:var(--text-muted);"></span>
        </div>
        <div class="reader-actions">
          <button class="btn btn-secondary" onclick="shareArticle()">🔗 Bagikan</button>
          <button class="btn btn-primary" onclick="copyWhatsApp()">📋 Salin WA</button>
          <a id="modalGDocBtn" href="#" target="_blank" class="btn btn-secondary" style="display:none;">📄 Google Doc</a>
          <button class="btn-close" onclick="closeModal()">✕</button>
        </div>
      </div>
      
      <!-- INLINE AUDIO BAR IF PRESENT -->
      <div id="modalAudioContainer" style="display:none; padding:12px 24px; background:var(--primary-light); border-bottom:1px solid var(--surface-border);">
        <audio id="modalAudioPlayer" controls style="width:100%; height:36px; outline:none;"></audio>
      </div>

      <div class="reader-body" id="modalContent">
        <!-- Rendered text -->
      </div>
    </div>
  </div>

  <!-- LIGHTBOX FOR POSTER ZOOM -->
  <div class="lightbox-overlay" id="lightboxModal" onclick="closeLightbox()">
    <img id="lightboxImg" class="lightbox-img" src="" alt="Infografis Poster Renungan">
  </div>

  <!-- TOAST NOTIFICATION -->
  <div class="toast" id="toast">Format WhatsApp kasil kasalin!</div>

  <!-- FOOTER -->
  <footer>
    <div class="container">
      <p>© 2026 Pustaka Penyiswaan</p>
    </div>
  </footer>

  <!-- SCRIPT -->
  <script>
    const articlesData = {articles_json_str};

    let currentLang = 'all';
    let currentTopic = 'all';
    let currentCategory = 'all';
    let currentSearch = '';
    let activeArticle = null;
    let currentActiveLang = 'id';

    function setCategoryFilter(cat, btn) {{
      currentCategory = cat;
      document.querySelectorAll('.cat-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderArticles();
    }}

    function renderArticles() {{
      const grid = document.getElementById('articlesGrid');
      grid.innerHTML = '';

      const filtered = articlesData.filter(a => {{
        const matchCategory = (currentCategory === 'all' || a.category === currentCategory);
        const matchLang = (currentLang === 'all' || a.available_langs.includes(currentLang));
        const matchTopic = (currentTopic === 'all' || a.tags.includes(currentTopic) || a.book.includes(currentTopic));
        const q = currentSearch.toLowerCase().trim();
        
        let matchSearch = !q || a.title.toLowerCase().includes(q) || a.date.toLowerCase().includes(q) || a.excerpt.toLowerCase().includes(q);
        if (!matchSearch) {{
          for (const l in a.versions) {{
            if (a.versions[l].raw.toLowerCase().includes(q)) {{
              matchSearch = true;
              break;
            }}
          }}
        }}
        return matchCategory && matchLang && matchTopic && matchSearch;
      }});

      if (filtered.length === 0) {{
        grid.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:60px 20px; color:var(--text-muted);">
          <div style="font-size:36px; margin-bottom:12px;">🍃</div>
          <h3>Boten wonten materi ingkang cocog</h3>
          <p>Cobi gantos tembung kunci utawi saringan tema sanesipun.</p>
        </div>`;
        return;
      }}

      filtered.forEach(a => {{
        const card = document.createElement('div');
        card.className = 'article-card';
        card.onclick = () => openReader(a);

        const langPillsHtml = a.available_langs.map(l => {{
          const lClass = l === 'id' ? 'id' : (l === 'en' ? 'en' : 'jv');
          const lLabel = l === 'id' ? 'ID' : (l === 'en' ? 'ENG' : 'JAWA');
          return `<span class="lang-badge ${{lClass}}">${{lLabel}}</span>`;
        }}).join('');

        const audioIcon = a.audio ? '🔊' : '';
        const gdocIcon = a.gdoc ? '📄' : '';
        const posterBadge = a.poster ? `<span class="poster-pill">🖼️ Poster</span>` : '';

        const catLabels = {{
          'renungan-harian': '🌅 Renungan',
          'esai-kontemplasi': '✍️ Esai',
          'readers-voice': '👥 Voice',
          'ulasan-serat': '📜 Ulasan'
        }};
        const catClass = a.category === 'esai-kontemplasi' ? 'cat-esai' : (a.category === 'readers-voice' ? 'cat-readers' : (a.category === 'ulasan-serat' ? 'cat-ulasan' : 'cat-renungan'));
        const catBadge = `<span class="badge-cat ${{catClass}}">${{catLabels[a.category] || '🌅 Renungan'}}</span>`;
        const authorHtml = a.author ? `<div style="font-size:11.5px; color:var(--text-muted); margin-bottom:6px; font-weight:600;">✍️ Oleh: ${{a.author}}</div>` : '';

        const tagsHtml = a.tags.map(t => `<span class="mini-tag">${{t.replace(/[*#_~`]/g, '').trim()}}</span>`).join('');

        const cleanTitle = a.title.replace(/[*#_~`]/g, '').trim();
        const cleanDate = (a.date || a.date_iso).replace(/[*#_~`]/g, '').trim();
        const cleanBook = (a.book || '').replace(/[*#_~`]/g, '').trim();
        const cleanExcerpt = (a.excerpt || '').replace(/[*#_~`]/g, '').trim();

        card.innerHTML = `
          <div class="card-meta">
            <span class="card-date">${{cleanDate}}</span>
            <div style="display:flex; gap:6px; align-items:center;">
              ${{catBadge}}
              ${{posterBadge}}
              <div class="lang-pills">${{langPillsHtml}}</div>
            </div>
          </div>
          <h3 class="card-title">${{cleanTitle}}</h3>
          ${{authorHtml}}
          <div class="card-book">📖 ${{cleanBook}}</div>
          <div class="card-excerpt">"${{cleanExcerpt || 'Klik kagem maos wedharan jangkep...'}}"</div>
          <div class="card-footer">
            <div class="card-tags">${{tagsHtml}}</div>
            <div class="card-features">
              ${{audioIcon}} ${{gdocIcon}}
            </div>
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    function openReader(articleOrId, preferredLang) {{
      let article = articleOrId;
      if (typeof articleOrId === 'string') {{
        article = articlesData.find(a => a.group_id === articleOrId || a.id === articleOrId || (a.versions && Object.values(a.versions).some(v => v.fname === articleOrId)));
      }}
      if (!article) return;
      activeArticle = article;
      const modal = document.getElementById('readerModal');
      const langSwitcher = document.getElementById('modalLangSwitcher');

      // Update URL Hash for direct deep-linking
      if (history.replaceState) {{
        history.replaceState(null, '', '#' + encodeURIComponent(article.group_id));
      }} else {{
        window.location.hash = encodeURIComponent(article.group_id);
      }}

      if (preferredLang && article.versions[preferredLang]) {{
        currentActiveLang = preferredLang;
      }} else if (currentLang !== 'all' && article.versions[currentLang]) {{
        currentActiveLang = currentLang;
      }} else if (article.versions['id']) {{
        currentActiveLang = 'id';
      }} else if (article.versions['jv']) {{
        currentActiveLang = 'jv';
      }} else {{
        currentActiveLang = article.available_langs[0];
      }}

      langSwitcher.innerHTML = '';
      article.available_langs.forEach(l => {{
        const btn = document.createElement('button');
        btn.className = 'reader-lang-btn' + (l === currentActiveLang ? ' active' : '');
        btn.innerText = l === 'id' ? '🇮🇩 Indonesia' : (l === 'en' ? '🇬🇧 English' : 'ꦗꦮ Basa Jawi');
        btn.onclick = () => switchReaderLang(l);
        langSwitcher.appendChild(btn);
      }});

      renderReaderContent();
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }}

    function switchReaderLang(lang) {{
      if (!activeArticle || !activeArticle.versions[lang]) return;
      currentActiveLang = lang;
      document.querySelectorAll('.reader-lang-btn').forEach(btn => {{
        const isMatch = (lang === 'id' && btn.innerText.includes('Indonesia')) ||
                        (lang === 'en' && btn.innerText.includes('English')) ||
                        (lang === 'jv' && btn.innerText.includes('Basa Jawi'));
        btn.classList.toggle('active', isMatch);
      }});
      renderReaderContent();
    }}

    function renderReaderContent() {{
      if (!activeArticle) return;
      const v = activeArticle.versions[currentActiveLang] || activeArticle.versions[activeArticle.primary_lang] || Object.values(activeArticle.versions)[0];
      if (!v) return;

      const content = document.getElementById('modalContent');
      const dateEl = document.getElementById('modalDate');
      const gdocBtn = document.getElementById('modalGDocBtn');
      const audioContainer = document.getElementById('modalAudioContainer');
      const audioPlayer = document.getElementById('modalAudioPlayer');

      const catLabels = {{
        'renungan-harian': '🌅 Renungan Harian',
        'esai-kontemplasi': '✍️ Esai Kontemplasi',
        'readers-voice': '👥 Reader’s Voice',
        'ulasan-serat': '📜 Ulasan Serat'
      }};
      const catClass = activeArticle.category === 'esai-kontemplasi' ? 'cat-esai' : (activeArticle.category === 'readers-voice' ? 'cat-readers' : (activeArticle.category === 'ulasan-serat' ? 'cat-ulasan' : 'cat-renungan'));
      const catBadge = `<span class="badge-cat ${{catClass}}">${{catLabels[activeArticle.category] || '🌅 Renungan'}}</span>`;
      const authorBadge = activeArticle.author ? ` • ✍️ ${{activeArticle.author}}` : '';
      if (dateEl) {{
        dateEl.innerHTML = `${{catBadge}} <span style="margin-left:6px;">${{v.date || activeArticle.date_iso}}</span>${{authorBadge}}`;
      }}

      const gdocLink = v.gdoc || activeArticle.gdoc;
      if (gdocBtn) {{
        if (gdocLink) {{
          gdocBtn.href = gdocLink;
          gdocBtn.style.display = 'inline-flex';
        }} else {{
          gdocBtn.style.display = 'none';
        }}
      }}

      const audioSrc = v.audio || activeArticle.audio;
      if (audioContainer && audioPlayer) {{
        if (audioSrc) {{
          audioPlayer.src = audioSrc;
          audioContainer.style.display = 'block';
        }} else {{
          try {{ audioPlayer.pause(); }} catch(e) {{}}
          audioPlayer.src = '';
          audioContainer.style.display = 'none';
        }}
      }}

      let posterHtml = '';
      if (activeArticle.poster) {{
        posterHtml = `
          <div class="poster-hero">
            <img src="${{activeArticle.poster}}" alt="Infografis Poster" class="poster-img" onclick="openLightbox('${{activeArticle.poster}}')">
            <div class="poster-hint">🔍 Klik gambar poster kagem ningali wutuh / memperbesar</div>
          </div>
        `;
      }}

      let formatted = v.raw || '';
      formatted = formatted.replace(/^_(.*?)_$/gm, '<em>$1</em>');
      formatted = formatted.replace(/\\*([^\\*]+)\\*/g, '<strong>$1</strong>');
      formatted = formatted.replace(/_([^_]+)_/g, '<em>$1</em>');
      
      const paras = formatted.split('\\n\\n').map(p => {{
        p = p.trim();
        if (p.startsWith('<strong>📖') || p.startsWith('<strong>💭') || p.startsWith('<strong>🧘') || p.startsWith('<strong>🎯') || p.startsWith('<strong>📝')) {{
          return `<h2>${{p}}</h2>`;
        }}
        if (p.includes('<em>"<strong>') || p.includes('<em>"*')) {{
          return `<blockquote>${{p}}</blockquote>`;
        }}
        return `<p>${{p.replace(/\\n/g, '<br>')}}</p>`;
      }}).join('');

      if (content) {{
        content.innerHTML = posterHtml + paras;
      }}
    }}

    function closeModal() {{
      const modal = document.getElementById('readerModal');
      const audioPlayer = document.getElementById('modalAudioPlayer');
      if (audioPlayer) audioPlayer.pause();
      modal.classList.remove('active');
      document.body.style.overflow = '';
      activeArticle = null;
      if (history.replaceState) {{
        history.replaceState(null, '', window.location.pathname + window.location.search);
      }}
    }}

    function closeModalOnOverlay(e) {{
      if (e.target.id === 'readerModal') {{
        closeModal();
      }}
    }}

    function openLightbox(src) {{
      const lb = document.getElementById('lightboxModal');
      const img = document.getElementById('lightboxImg');
      img.src = src;
      lb.classList.add('active');
    }}

    function closeLightbox() {{
      const lb = document.getElementById('lightboxModal');
      lb.classList.remove('active');
    }}

    function shareArticle() {{
      if (!activeArticle) return;
      const v = activeArticle.versions[currentActiveLang] || Object.values(activeArticle.versions)[0];
      const title = v ? v.title.replace(/[*#_~`]/g, '').trim() : 'Pustaka Kontemplasi';
      const shareUrl = window.location.origin + window.location.pathname + '#' + encodeURIComponent(activeArticle.group_id);

      if (navigator.share) {{
        navigator.share({{
          title: title,
          text: `Waos naskah "${{title}}" wonten ing Pustaka Kontemplasi:`,
          url: shareUrl
        }}).catch(err => {{
          if (err.name !== 'AbortError') {{
            copyDirectUrl(shareUrl);
          }}
        }});
      }} else {{
        copyDirectUrl(shareUrl);
      }}
    }}

    function copyDirectUrl(url) {{
      navigator.clipboard.writeText(url).then(() => {{
        showToast("🔗 Tautan artikel kasil kasalin!");
      }}).catch(() => {{
        prompt("Salin tautan artikel menika:", url);
      }});
    }}

    function copyWhatsApp() {{
      if (!activeArticle) return;
      const v = activeArticle.versions[currentActiveLang] || Object.values(activeArticle.versions)[0];
      navigator.clipboard.writeText(v.raw).then(() => {{
        showToast("Format WhatsApp kasil kasalin!");
      }});
    }}

    function showToast(msg) {{
      const toast = document.getElementById('toast');
      toast.innerText = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2500);
    }}

    function setLangFilter(lang) {{
      currentLang = lang;
      document.querySelectorAll('.lang-tab').forEach(b => {{
        b.classList.toggle('active', b.dataset.lang === lang);
      }});
      renderArticles();
    }}

    function setTopicFilter(topic) {{
      currentTopic = topic;
      document.querySelectorAll('.topic-chip').forEach(c => {{
        c.classList.toggle('active', c.innerText.trim() === topic || (topic === 'all' && c.innerText.includes('Sedaya')));
      }});
      renderArticles();
    }}

    function filterArticles() {{
      currentSearch = document.getElementById('searchInput').value;
      renderArticles();
    }}

    function toggleTheme() {{
      const isDark = document.body.dataset.theme === 'dark';
      document.body.dataset.theme = isDark ? 'light' : 'dark';
      document.getElementById('themeIcon').innerText = isDark ? '🌙' : '☀️';
      document.getElementById('themeText').innerText = isDark ? 'Dark' : 'Light';
      localStorage.setItem('pustaka_theme', isDark ? 'light' : 'dark');
    }}

    const savedTheme = localStorage.getItem('pustaka_theme') || 'light';
    if (savedTheme === 'dark') {{
      document.body.dataset.theme = 'dark';
      document.getElementById('themeIcon').innerText = '☀️';
      document.getElementById('themeText').innerText = 'Light';
    }}

    function checkDeepLink() {{
      const rawHash = window.location.hash ? window.location.hash.substring(1) : '';
      if (!rawHash) return;
      const targetId = decodeURIComponent(rawHash);
      const article = articlesData.find(a => a.group_id === targetId || a.id === targetId || (a.versions && Object.values(a.versions).some(v => v.fname === targetId)));
      if (article) {{
        if (currentCategory !== 'all' && article.category && currentCategory !== article.category) {{
          setCat('all');
        }}
        openReader(article);
      }}
    }}

    renderArticles();
    checkDeepLink();
    window.addEventListener('hashchange', checkDeepLink);

    window.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') {{
        if (document.getElementById('lightboxModal').classList.contains('active')) {{
          closeLightbox();
        }} else {{
          closeModal();
        }}
      }}
      if (e.key === '/' && document.activeElement !== document.getElementById('searchInput')) {{
        e.preventDefault();
        document.getElementById('searchInput').focus();
      }}
    }});
  </script>
</body>
</html>
"""

    with open(os.path.join(pustaka_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_template)
    
    shutil.copy(os.path.join(pustaka_dir, "index.html"), "/home/satyaaditech/share/pustaka/index.html")
    print("Clean Markdown Artifacts Pustaka built successfully.")

if __name__ == "__main__":
    build_clean_pustaka()
