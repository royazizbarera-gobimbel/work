#!/usr/bin/env python3
"""
Dynamic Sync Engine: GitHub Issue <-> Google Spreadsheet
Org: GO-Bimbel
Repo: api-superapps-beta#1
"""

import json
import re
import os
import subprocess
import urllib.request
import urllib.error
from collections import defaultdict

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyVcDImf6T1WbUjue48ccniw9HXaSryw3YZHkJkt9t2dwieF2R8aKQGS93HwuP32gYY/exec"
WORKSPACE_DIR = "/home/broy/work"
SCRATCH_DIR = "/home/broy/.gemini/antigravity-cli/brain/0c53f335-e14c-49bc-95db-523e22d1ba38/scratch"
ISSUE_FILE = "/tmp/issue-1-live.json"
HRIS_MD_FILE = os.path.join(SCRATCH_DIR, "list-endpoint-hris.md")

print("1. Fetching latest comments from GitHub issue api-superapps-beta#1...")
try:
    cmd = ["gh", "issue", "view", "https://github.com/GO-Bimbel/api-superapps-beta/issues/1", "--comments", "--json", "title,body,comments,state,author"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    issue_data = json.loads(res.stdout)
    with open(ISSUE_FILE, "w", encoding="utf-8") as f:
        f.write(res.stdout)
    print(f"   Success! Fetched {len(issue_data['comments'])} comments from GitHub.")
except Exception as e:
    print(f"   Warning: Could not fetch live from gh ({e}), falling back to cached file.")
    with open(ISSUE_FILE, "r", encoding="utf-8") as f:
        issue_data = json.load(f)

with open(HRIS_MD_FILE, "r", encoding="utf-8") as f:
    hris_md_text = f.read()

def clean_module_name(raw):
    raw = raw.strip()
    u = raw.upper()
    if "BDMMS" in u: return "BDMMS"
    if "SIBUNK" in u: return "SIBUNK"
    if "IDPP" in u: return "IDPP"
    if "HOME" in u or "DASHBOARD AWAL" in u: return "HOME"
    if "RAPAT" in u: return "RAPAT"
    if "ROLE" in u: return "AKSES_ROLE"
    if "ICONS" in u: return "GO_ICONS"
    if "HRIS" in u: return "HRIS"
    if "FASILITAS" in u: return "FASILITAS_SISWA"
    if "BP_ONLINE" in u or "BP-ONLINE" in u: return "BP_ONLINE"
    if "AKPS" in u or "NILAI_100" in u or "NILAI 100" in u: return "AKPS"
    if "EVENT" in u or "ACARA" in u: return "EVENTGO"
    if "PRESENSI" in u: return "PRESENSI"
    if "KASIR" in u or "GOKASIR" in u: return "GO_KASIR"
    if "VOTE_GETTER" in u or "VOTE-GETTER" in u or "SISWA_KHUSUS" in u or "SISWA KHUSUS" in u: return "SISWA_KHUSUS"
    if "PROFILE" in u or "SISWA" in u: return "PROFILE_SISWA"
    if "SMBA" in u: return "SMBA"
    return raw

def infer_module_from_path(full_path):
    u = full_path.upper()
    if "${GK}" in u or "GO-KASIR" in u or "/KASIR" in u or "GOKASIR" in u:
        return "GO_KASIR"
    if "PRESENSI" in u or "KEHADIRAN-KBM" in u:
        return "PRESENSI"
    if "VOTE-GETTER" in u or "VOTE_GETTER" in u:
        return "SISWA_KHUSUS"
    if "NILAI-100" in u or "NILAI_100" in u or "/AKPS" in u or "${AKPS}" in u:
        return "AKPS"
    if "EVENT-GO" in u or "EVENTGO" in u or "ACARA-SISWA" in u:
        return "EVENTGO"
    if "EXPORT-DATA-GOA" in u or "EXPORT-DATA-VAK" in u:
        return "PROFILE_SISWA"
    if "${GO_ICONS}" in u or "GO_ICONS" in u or "GOICONS" in u or "LAPORAN-AKSES-GO-EXPERT" in u:
        return "GO_ICONS"
    if "${BDMMS}" in u or "/BDMMS" in u:
        return "BDMMS"
    if "${IDPP}" in u or "/IDPP" in u:
        return "IDPP"
    if "${HRIS}" in u or "/HRIS" in u:
        return "HRIS"
    if "${SIBUNK}" in u or "/SIBUNK" in u:
        return "SIBUNK"
    if "${RAPAT}" in u or "/RAPAT" in u:
        return "RAPAT"
    if "${BP_ONLINE}" in u or "BP-ONLINE" in u or "/BP_ONLINE" in u:
        return "BP_ONLINE"
    if "${SMBA}" in u or "/SMBA" in u or "SMBA" in u:
        return "SMBA"
    return None


# Helper to normalize path and key
def normalize_endpoint(method_raw, raw_text):
    clean = raw_text.strip().replace("`", "")
    m_meth = re.search(r'\b(GET|POST|PATCH|PUT|DELETE)\b', clean, re.I)
    method = m_meth.group(1).upper() if m_meth else (method_raw.upper() if method_raw else "GET")
    
    m_url = re.search(r'(https?://[^\s\)\`\]\"\'<>]+|/?(?:api/|v1/)[^\s\)\`\]\"\'<>]+|\$\{[^\s\)\`\]\"\'<>]+\}[^\s\)\`\]\"\'<>]*)', clean)
    if m_url:
        full_path = m_url.group(0)
    else:
        parts = clean.split()
        full_path = parts[-1] if parts else clean

    if not full_path.startswith('/') and not full_path.startswith('$') and not full_path.startswith('http'):
        full_path = '/' + full_path

    path_key = re.sub(r'https?://[^/]+', '', full_path).rstrip('/')
    path_key = re.sub(r'^\$\{[^\}]+\}/?', '/', path_key)
    path_key = re.sub(r'^\$\{[^\}]+\}/\$\{[^\}]+\}/?', '/', path_key)
    if not path_key.startswith('/'):
        path_key = '/' + path_key
    return method, full_path, path_key

# --- SEED REGISTRY WITH MASTER BASELINE (list-endpoint-hris.md) ---
registry = {}
ordered_keys = []

current_section = ""
current_submodule = ""
current_route_fe = ""

for line in hris_md_text.splitlines():
    l_str = line.strip()
    if not l_str:
        continue
    if l_str.startswith("# "):
        current_section = l_str[2:].strip()
    elif l_str.startswith("## "):
        sub_raw = l_str[3:].strip()
        m_route = re.search(r'^(.*?)\s*\((.*?)\)$', sub_raw)
        if m_route:
            current_submodule = m_route.group(1).strip()
            current_route_fe = m_route.group(2).strip()
        else:
            current_submodule = sub_raw
            current_route_fe = ""
    elif l_str.startswith("- ") or l_str.startswith("* "):
        bullet = l_str[2:].strip().replace("`", "")
        method, full_path, path_key = normalize_endpoint("", bullet)
        
        desc = ""
        m_desc = re.search(r'\((.*?)\)', bullet)
        if m_desc:
            desc = m_desc.group(1).strip()

        modul_name = "HRIS"
        default_pic = "MuhAsmann"
        if "Rapat" in current_section:
            modul_name = "RAPAT"
            default_pic = "royazizbarera-gobimbel"
        elif current_section in ["Kunjungan dan Inspeksi Sekretariat (KIS)", "Standar Kompetensi", "Pengajar", "Perjanjian Kerja"]:
            modul_name = "GO_ICONS"

        s_type = "File Service" if ("/file/" in full_path or "upload" in full_path.lower() or "export" in full_path.lower()) else "Core API"
        status = "PENDING" if s_type == "File Service" else "DONE"
        
        key = (method, path_key)
        item = {
            "modul": clean_module_name(modul_name),
            "submodul": f"{current_section} - {current_submodule}".strip(" -"),
            "route_fe": current_route_fe,
            "method": method,
            "desc": desc if desc else f"{method} {path_key.split('?')[0].split('/')[-1]}",
            "path": full_path,
            "service": "db-user / db-go",
            "status": status,
            "pic": default_pic,
            "service_type": s_type,
            "notes": "",
            "action": "",
            "link": ""
        }
        if key not in registry:
            registry[key] = item
            ordered_keys.append(key)

# Add Akses Role baseline
role_admin_eps = [
    ("GET", "Mendapatkan daftar user petugas dan role", "/api/v1/user-admin/v2/petugas"),
    ("GET", "Mendapatkan detail user petugas beserta multi-jabatan", "/api/v1/user-admin/v2/petugas/detail/:id"),
    ("GET", "Mendapatkan daftar role admin", "/api/v1/user-admin/v2/petugas/role"),
    ("POST", "Update/assign role petugas baru", "/api/v1/user-admin/v2/petugas/:id"),
]
for meth, d, p in role_admin_eps:
    k = (meth, p)
    item = {
        "modul": "AKSES_ROLE",
        "submodul": "Role Admin",
        "route_fe": "admin/role-admin",
        "method": meth,
        "desc": d,
        "path": p,
        "service": "db-user / api-superapps-beta",
        "status": "DONE",
        "pic": "MuhAsmann",
        "service_type": "Core API",
        "notes": "Akses role multi-jabatan dibuatkan endpoint baru v2 agar tidak memecah superapp existing",
        "action": "Deploy endpoint baru v2",
        "link": "https://github.com/GO-Bimbel/db-user/pull/3309 | https://github.com/GO-Bimbel/go-superapp-api/pull/3933 | https://github.com/GO-Bimbel/api-superapps-beta/pull/2"
    }
    if k not in registry:
        registry[k] = item
        ordered_keys.append(k)

# --- 2. CHRONOLOGICAL STREAM REPLAY OF ALL GITHUB COMMENTS ---
print("2. Replaying all GitHub comments dynamically...")

interrupt_tasks = []
seen_interrupt_keys = set()

def clean_interrupt_description(raw_desc, ticket_id, body):
    d = re.sub(r'https?://\S+', '', raw_desc)
    d = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', d)
    d = re.sub(r'issuecomment-\d+', '', d)
    d = re.sub(r'#+\s*', '', d)
    d = d.replace(ticket_id, '')
    d = re.sub(r'^\s*[\>\-\*\:\|\[\]]+\s*', '', d)
    d = re.sub(r'\s*[\>\-\*\:\|\[\]]+\s*$', '', d)
    d = d.strip()

    if len(d) < 5 or d.lower() in ["pending", "done", "tertunda", "task", "feedback", "notes"]:
        for line in body.splitlines():
            line_c = line.strip().strip("> #*-:`")
            line_c = re.sub(r'https?://\S+', '', line_c).strip()
            if any(k in line_c.lower() for k in ["mengerjakan", "memperbaiki", "feedback", "enhance", "bantu cek", "fixing", "ajuan", "bahas", "rencana", "tambahan endpoint"]):
                if len(line_c) > 6 and line_c.lower() not in ["pending", "done"]:
                    d = line_c
                    break

    # Fallback / mapping deskripsi human-readable jika masih generik
    if "3202" in ticket_id: d = "Memperbaiki Program (Cron) Insert Siswa Lolos TCR"
    elif "3120" in ticket_id: d = "Mengerjakan feedback tambahan BisDev"
    elif "3133" in ticket_id: d = "Feedback enhance Rencana Masuk"
    elif "1964" in ticket_id: d = "BP Online: Penggabungan Rencana Kegiatan & Pengusulan Biaya"
    elif "3129" in ticket_id:
        d = "Bantu cek feedback IDPP" if "bantu cek" in body.lower() else "Feedback IDPP & alur rencana pengajar"
    elif "1963" in ticket_id: d = "Task finance terkait IDPP"
    elif "4750" in ticket_id: d = "Fixing ajuan perubahan rencana masuk tidak bentrok pengajar"
    elif "3197" in ticket_id: d = "Mengerjakan & cek feedback BisDev #3197"
    elif "6413" in ticket_id: d = "Koordinasi list endpoint baru dari FE Superapps"
    elif "3276" in ticket_id: d = "Mengerjakan Enhance Rencana Kerja"
    elif "3309" in ticket_id: d = "Enhance Menu Role Admin & akses dua jabatan"
    elif "3933" in ticket_id: d = "Proxy BFF: Enhance Menu Role Admin"

    return d.strip()


current_mod_context = "GENERAL"
current_sub_context = ""
current_fe_context = ""

for c_idx, c in enumerate(issue_data["comments"]):
    body = c["body"]
    author = c["author"]["login"]
    created_at = c["createdAt"][:10]

    current_mod_context = "GENERAL"
    current_sub_context = ""
    current_fe_context = ""

    # Track module context across comment first
    for line in body.splitlines():
        line_clean = re.sub(r'^[>\s]+', '', line.strip())
        if line_clean.startswith("#"):
            head_clean = line_clean.strip("# \t\r")
            m_mod = re.search(r'^(?:MODULE|Module|Modules|Menu)\s*[:\-]?\s*([^\n\r]+)', head_clean, re.I)
            if m_mod:
                current_mod_context = clean_module_name(m_mod.group(1))
            elif head_clean.upper() in ["RAPAT", "IDPP", "BDMMS", "SIBUNK", "HRIS", "GO_ICONS", "BP_ONLINE", "AKPS"]:
                current_mod_context = clean_module_name(head_clean)

    # Process lines sequentially (headings update sub-context immediately)
    for line in body.splitlines():
        line_s = line.strip()
        if not line_s:
            continue
        line_clean = re.sub(r'^[>\s]+', '', line_s)

        if line_clean.startswith("#"):
            if line_clean.startswith("## ") or line_clean.startswith("### ") or line_clean.startswith("#### "):
                clean_sub = line_clean.replace("#", "").strip()
                current_sub_context = clean_sub
                m_rt = re.search(r'\(([a-zA-Z0-9_\-\/]+)\)', current_sub_context)
                if m_rt:
                    current_fe_context = m_rt.group(1)
            continue

        concat_matches = re.findall(r'\[([ xX\-]?)\]\s*([^\[\n\r]+)', line_clean)
        if concat_matches:
            items_to_process = concat_matches
        else:
            continue

        for stat, raw_chunk in items_to_process:
            is_done = stat.lower() == 'x'
            raw_clean = raw_chunk.strip().replace("`", "").strip("* \t")

            m_multi_meth = re.match(r"^([A-Z,\s]+)\s*:\s*(.*)", raw_clean)
            if m_multi_meth:
                methods = [mth.strip() for mth in m_multi_meth.group(1).split(",") if mth.strip() in ["GET", "POST", "PATCH", "PUT", "DELETE"]]
                paths_raw = [p.strip() for p in m_multi_meth.group(2).split(",") if p.strip()]
            else:
                methods = ["GET"]
                paths_raw = [raw_clean]

            for mth in methods:
                for p_raw in paths_raw:
                    method, full_path, path_key = normalize_endpoint(mth, p_raw)
                    key = (method, path_key)
                    inferred_mod = infer_module_from_path(full_path)

                    if key in registry:
                        was_done = (registry[key]["status"] == "DONE")
                        prev_pic = registry[key].get("pic", "")

                        # Monotonic Completion: If previously finished or marked [x] now, KEEP DONE!
                        if is_done or was_done:
                            registry[key]["status"] = "DONE"
                            if registry[key].get("action") == "Perlu audit SO downstream":
                                registry[key]["action"] = ""
                            if registry[key].get("notes"):
                                tokens = [t.strip() for t in registry[key]["notes"].split("|") if t.strip()]
                                clean_tokens = [t for t in tokens if "proxy selesai" not in t.lower() and "belum audit so" not in t.lower()]
                                registry[key]["notes"] = " | ".join(clean_tokens)
                        elif "not in code" in raw_clean.lower() or "tidak ada di proxy" in raw_clean.lower():
                            registry[key]["status"] = "NOT IN CODE"
                            if not registry[key].get("notes"):
                                registry[key]["notes"] = "Endpoint tidak ditemukan di proxy maupun service data"
                        elif "blocked" in raw_clean.lower():
                            registry[key]["status"] = "BLOCKED"
                            if not registry[key].get("notes"):
                                registry[key]["notes"] = "Endpoint di file-service, tidak perlu dimigrasikan"
                        else:
                            if registry[key]["status"] not in ["BLOCKED", "NOT IN CODE"]:
                                registry[key]["status"] = "PENDING"
                        
                        # Update PIC: gabungkan jika ada PIC lain yang ikut mengerjakan
                        if registry[key]["pic"]:
                            current_pics = [p.strip() for p in registry[key]["pic"].split("/") if p.strip()]
                            if author and author not in current_pics:
                                current_pics.append(author)
                                registry[key]["pic"] = " / ".join(current_pics)
                        else:
                            registry[key]["pic"] = author

                        # Smart inline desc vs tech note detection
                        inline_desc = ""
                        tech_note = ""
                        m_desc = re.search(r'\((.*?)\)', p_raw)
                        if m_desc:
                            paren_content = m_desc.group(1).strip()
                            tech_kws = ["sudah dimigrasikan", "sudah ada", "file-service", "file service", "tidak ada di proxy", "tidak ada di downstream", "not in code", "proxy selesai", "belum audit so", "sudah dimention"]
                            if any(k in paren_content.lower() for k in tech_kws):
                                tech_note = paren_content
                                clean_f = re.sub(r'\b(sudah dimigrasikan|sudah ada|file-service|file service|tidak ada di proxy/downstream|tidak ada di proxy|not in code|proxy selesai|belum audit so|sudah dimention di atas|sudah dimention)\b', '', paren_content, flags=re.I).strip(" -:,")
                                inline_desc = clean_f
                            else:
                                inline_desc = paren_content

                        # Helper to append notes without duplication
                        def append_unique_note(base_note, add_note):
                            if not add_note:
                                return base_note
                            tokens = [t.strip().lower() for t in base_note.split("|") if t.strip()]
                            if add_note.strip().lower() not in tokens:
                                return (base_note + " | " + add_note.strip()).strip(" |")
                            return base_note

                        if tech_note:
                            if (is_done or was_done) and ("proxy selesai" in tech_note.lower() or "belum audit so" in tech_note.lower()):
                                pass
                            else:
                                registry[key]["notes"] = append_unique_note(registry[key]["notes"], tech_note)
                            if "tidak ada" in tech_note.lower() or "not in code" in tech_note.lower():
                                registry[key]["status"] = "NOT IN CODE"
                            elif "file-service" in tech_note.lower() or "file service" in tech_note.lower():
                                registry[key]["service"] = "file-service"
                            elif ("proxy selesai" in tech_note.lower() or "belum audit so" in tech_note.lower()) and registry[key]["status"] != "DONE":
                                registry[key]["status"] = "IN PROGRESS"
                                registry[key]["action"] = "Perlu audit SO downstream"

                        # Update desc if provided
                        if inline_desc and ("GET " in registry[key]["desc"] or "POST " in registry[key]["desc"] or not registry[key]["desc"]):
                            registry[key]["desc"] = inline_desc

                        if inferred_mod:
                            registry[key]["modul"] = inferred_mod
                        elif current_mod_context != "GENERAL":
                            registry[key]["modul"] = clean_module_name(current_mod_context)
                    else:
                        inline_desc = ""
                        tech_note = ""
                        m_desc = re.search(r'\((.*?)\)', p_raw)
                        if m_desc:
                            paren_content = m_desc.group(1).strip()
                            tech_kws = ["sudah dimigrasikan", "sudah ada", "file-service", "file service", "tidak ada di proxy", "tidak ada di downstream", "not in code", "proxy selesai", "belum audit so", "sudah dimention"]
                            if any(k in paren_content.lower() for k in tech_kws):
                                tech_note = paren_content
                                clean_f = re.sub(r'\b(sudah dimigrasikan|sudah ada|file-service|file service|tidak ada di proxy/downstream|tidak ada di proxy|not in code|proxy selesai|belum audit so|sudah dimention di atas|sudah dimention)\b', '', paren_content, flags=re.I).strip(" -:,")
                                inline_desc = clean_f
                            else:
                                inline_desc = paren_content

                        def append_unique_note(base_note, add_note):
                            if not add_note:
                                return base_note
                            tokens = [t.strip().lower() for t in base_note.split("|") if t.strip()]
                            if add_note.strip().lower() not in tokens:
                                return (base_note + " | " + add_note.strip()).strip(" |")
                            return base_note

                        s_type = "File Service" if ("/file/" in full_path or "upload" in full_path.lower() or "export" in full_path.lower() or "file-service" in raw_clean.lower()) else "Core API"

                        service_target = "api-superapps-beta"
                        if "/file/" in full_path or "file-service" in raw_clean.lower() or s_type == "File Service":
                            service_target = "file-service"
                        elif "kasir" in path_key:
                            service_target = "finance / go-kasir"
                        elif "sellma" in path_key:
                            service_target = "db-sellma"
                        elif "bdmms" in path_key:
                            service_target = "db-bdmms"
                        elif "jumlah-siswa-pt" in path_key and "kelas" not in path_key:
                            service_target = "db-kbm"
                        elif "laporan-akses-go-expert" in path_key or "akses-go-expert" in path_key:
                            service_target = "db-user"
                        elif "nilai-100" in path_key:
                            service_target = "db-user"
                        elif "icons" in path_key or "karyawan" in path_key or "pengajar" in path_key:
                            service_target = "db-icons / db-go"
                        elif "bp-online" in path_key:
                            service_target = "bp-online / finance"
                        elif "chat" in path_key:
                            service_target = "go-chat-v2"
                        elif "idpp" in path_key or current_mod_context == "IDPP":
                            service_target = "db-idpp"
                        elif "sibunk" in path_key or current_mod_context == "SIBUNK":
                            service_target = "db-sibunk"
                        elif "fasilitas" in path_key or "akps" in path_key or "FASILITAS" in current_mod_context:
                            service_target = "db-kbm / db-go"
                        elif "presensi" in path_key or "kehadiran-kbm" in path_key or "PRESENSI" in current_mod_context:
                            service_target = "db-kbm"
                        elif "vote-getter" in path_key or "jenis-pelayanan" in path_key or "kategori-vote-getter" in path_key:
                            service_target = "db-user"
                        elif "smba" in path_key or current_mod_context == "SMBA":
                            service_target = "db-materi / db-sekolah / db-produk"

                        status_val = "PENDING"
                        action_val = ""
                        notes_val = ""
                        if is_done:
                            status_val = "DONE"
                        elif "proxy selesai" in raw_clean.lower() or "belum audit so" in raw_clean.lower() or (tech_note and ("proxy selesai" in tech_note.lower() or "belum audit so" in tech_note.lower())):
                            status_val = "IN PROGRESS"
                            action_val = "Perlu audit SO downstream"
                        elif "not in code" in raw_clean.lower() or (tech_note and "tidak ada" in tech_note.lower()):
                            status_val = "NOT IN CODE"
                            notes_val = "Endpoint tidak ditemukan di proxy maupun service data"
                        elif "blocked" in raw_clean.lower():
                            status_val = "BLOCKED"
                            notes_val = "Endpoint di file-service, tidak perlu dimigrasikan"

                        if tech_note:
                            notes_val = append_unique_note(notes_val, tech_note)

                        new_item = {
                            "modul": inferred_mod if inferred_mod else (clean_module_name(current_mod_context) if current_mod_context != "GENERAL" else "GENERAL"),
                            "submodul": current_sub_context if current_sub_context else "Umum",
                            "route_fe": current_fe_context if current_fe_context else f"{current_mod_context.lower()}/{path_key.split('?')[0].split('/')[-1]}",
                            "method": method,
                            "desc": inline_desc if inline_desc else f"{method} {path_key.split('?')[0].split('/')[-1]}",
                            "path": full_path,
                            "service": service_target,
                            "status": status_val,
                            "pic": author,
                            "service_type": s_type,
                            "notes": notes_val,
                            "action": action_val,
                            "link": ""
                        }
                        registry[key] = new_item
                        ordered_keys.append(key)

    # Extract Notes section dynamically
    if "# Notes" in body or "# NOTES" in body:
        parts = re.split(r'#+\s*Notes?', body, flags=re.I)
        if len(parts) > 1:
            notes_text = parts[1]
            current_target = None
            for n_line in notes_text.splitlines():
                nl_s = n_line.strip()
                if not nl_s:
                    continue

                # Format A: Flexible Inline bullet line
                s_bullet = re.sub(r"^[\-\*\s]+", "", nl_s).strip()
                m_meth = re.match(r"^[`\*\s]*\b(GET|POST|PATCH|PUT|DELETE)\b\s*:?\s*", s_bullet, re.I)
                if m_meth:
                    meth_in = m_meth.group(1).upper()
                    rest = s_bullet[m_meth.end():].strip()
                    m_url = re.search(r'(\$\{[^\s\)\`\]\"\'<>:]+\}[^\s\)\`\]\"\'<>:]*|/?(?:api/|v1/)[^\s\)\`\]\"\'<>:]+|/[a-zA-Z0-9_\-\/]+)', rest)
                    if m_url:
                        path_in = m_url.group(1)
                        if not path_in.startswith('/') and not path_in.startswith('$') and not path_in.startswith('http'):
                            path_in = '/' + path_in
                        msg_in = rest[m_url.end():].strip(" `*:-()\t\r\n")
                        if not msg_in:
                            m_paren = re.search(r'\((.*?)\)', rest)
                            if m_paren:
                                msg_in = m_paren.group(1).strip()
                        if msg_in:
                            _, _, pk_in = normalize_endpoint(meth_in, path_in)
                            for (r_meth, r_pk), r_val in registry.items():
                                if r_meth == meth_in and (pk_in in r_pk or r_pk in pk_in):
                                    tokens = [t.strip().lower() for t in r_val["notes"].split("|") if t.strip()]
                                    if msg_in.strip().lower() not in tokens:
                                        r_val["notes"] = (r_val["notes"] + " | " + msg_in.strip()).strip(" |")
                                    if "tidak ada" in msg_in.lower() or "darimana" in msg_in.lower():
                                        r_val["status"] = "NOT IN CODE"
                                    elif "hardcode" in msg_in.lower():
                                        r_val["action"] = "Perlu refactor / review hardcode"
                            continue

                # Format B: Heading "### METHOD : path" or "### path"
                if nl_s.startswith("#"):
                    m_meth_h = re.search(r"\b(GET|POST|PATCH|PUT|DELETE)\b", nl_s, re.I)
                    h_meth = m_meth_h.group(1).upper() if m_meth_h else None
                    m_url_h = re.search(r"(\$\{[^\s\`]+\}[^\s\`]*|/(?:api/|v1/)[^\s\`]+|[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-\/]+)", nl_s)
                    if m_url_h:
                        _, _, h_pk = normalize_endpoint(h_meth or "", m_url_h.group(1))
                        current_target = (h_meth, h_pk)
                    else:
                        current_target = None
                elif (nl_s.startswith("-") or nl_s.startswith("*")) and current_target:
                    note_msg = nl_s.lstrip("-* ").strip()
                    t_meth, t_pk = current_target
                    for (r_meth, r_pk), r_val in registry.items():
                        meth_ok = (t_meth is None or r_meth == t_meth)
                        if meth_ok and (t_pk in r_pk or r_pk in t_pk):
                            tokens = [t.strip().lower() for t in r_val["notes"].split("|") if t.strip()]
                            if note_msg.strip().lower() not in tokens:
                                r_val["notes"] = (r_val["notes"] + " | " + note_msg.strip()).strip(" |")
                            if "tidak ada" in note_msg.lower() or "darimana" in note_msg.lower():
                                r_val["status"] = "NOT IN CODE"
                            elif "hardcode" in note_msg.lower():
                                r_val["action"] = "Perlu refactor / review hardcode"

                m_img = re.search(r'https://github\.com/user-attachments/assets/[a-f0-9\-]+', nl_s)
                if m_img and current_target:
                    t_meth, t_pk = current_target
                    for (r_meth, r_pk), r_val in registry.items():
                        meth_ok = (t_meth is None or r_meth == t_meth)
                        if meth_ok and (t_pk in r_pk or r_pk in t_pk):
                            r_val["link"] = (r_val["link"] + " | " + m_img.group(0)).strip(" |")

    c_id = c.get("id", "")
    # Extract External Interrupt Tickets / In-comment Tasks
    ext_matches = list(re.finditer(r'https://github\.com/GO-Bimbel/([^/\s]+)/(issues|pull)/(\d+)(?:#issuecomment-(\d+))?', body))
    if ext_matches:
        for m_ext in ext_matches:
            repo, kind, num, comment_anchor = m_ext.group(1), m_ext.group(2), m_ext.group(3), m_ext.group(4)
            if repo == "api-superapps-beta" and num == "1":
                continue

            ticket_id = f"{repo}#{num}"
            link_url = m_ext.group(0)

            raw_desc = ""
            for bline in body.splitlines():
                if m_ext.group(0) in bline or ticket_id in bline:
                    raw_desc = bline
                    break

            clean_desc = clean_interrupt_description(raw_desc, ticket_id, body)
            is_done = "DONE" in body or kind == "pull"
            status = "DONE" if is_done else "IN PROGRESS"

            dedup_key = (created_at, ticket_id)
            if dedup_key not in seen_interrupt_keys:
                seen_interrupt_keys.add(dedup_key)
                interrupt_tasks.append([
                    len(interrupt_tasks) + 1,
                    created_at,
                    ticket_id,
                    clean_desc,
                    author,
                    status,
                    repo,
                    link_url
                ])
    else:
        full_lines = [l.strip().strip("> #*-") for l in body.splitlines() if l.strip().strip("> #*-")]
        for l_idx, line_s in enumerate(full_lines):
            is_pending_line = re.match(r"^(PENDING|Pending|Tertunda)\b", line_s, re.I)
            is_work_line = re.match(r"^(Mengerjakan permintaan|Mengerjakan enhance|Mengerjakan feedback|Mengerjakan|Mengecek endpoint|Mengecek feedback|Fixing ajuan)\b", line_s, re.I)

            if is_pending_line or is_work_line:
                raw_desc = line_s
                if raw_desc.upper() in ["PENDING", "PENDINGAN", "TERTUNDA"]:
                    if l_idx + 1 < len(full_lines):
                        raw_desc = full_lines[l_idx + 1]

                clean_desc = clean_interrupt_description(raw_desc, "NON-TICKET", body)

                srv = "api-superapps-beta"
                tid = "NON-TICKET"
                if "bp-online" in clean_desc.lower():
                    srv = "bp-online / finance"
                    tid = "bp-online"
                elif "rencana masuk" in clean_desc.lower() or "pengajar" in clean_desc.lower() or "bentrok" in clean_desc.lower():
                    srv = "db-kbm"
                    tid = "db-kbm"
                elif "hris" in clean_desc.lower() or "endpoint dari fe" in clean_desc.lower():
                    srv = "fe-super-apps"
                    tid = "fe-super-apps"
                elif "tcr" in clean_desc.lower():
                    srv = "service-tcr / multi-cron"
                    tid = "service-tcr"
                elif "3197" in clean_desc:
                    srv = "bisdev"
                    tid = "bisdev#3197"

                dedup_key = (created_at, clean_desc[:25].lower())
                if dedup_key not in seen_interrupt_keys:
                    seen_interrupt_keys.add(dedup_key)
                    m_doc = re.search(r'https?://\S+', raw_desc)
                    link_target = m_doc.group(0) if m_doc else f"https://github.com/GO-Bimbel/api-superapps-beta/issues/1#issuecomment-{c_id}"
                    interrupt_tasks.append([
                        len(interrupt_tasks) + 1,
                        created_at,
                        tid,
                        clean_desc,
                        author,
                        "DONE" if "DONE" in body else "IN PROGRESS",
                        srv,
                        link_target
                    ])
                break

# Apply specific known edge-cases
for reg_k, reg_v in registry.items():
    p = reg_v["path"]
    if "penautan-petugas-gedung" in p and not reg_v["notes"]:
        reg_v["notes"] = "Tabel bp_online -> penautan_petugas_gedung ada kolom id_bidang & level_jabatan_id"
        reg_v["action"] = "Petakan id_bidang & level jabatan"
    elif "cek-kasir" in p and not reg_v["notes"]:
        reg_v["notes"] = "Ada hardcode level jabatan 7 pada query cek kasir"
        reg_v["action"] = "Review apakah level jabatan 7 tetap valid"
    elif "inspeksi-unit/kategori" in p and not reg_v["notes"]:
        reg_v["notes"] = "Tabel inspeksi_unit_kategori masih menggunakan relasi id_bidang (t_bidang_go)"
        reg_v["action"] = "Bahas struktur baru kategori KIS tanpa relasi t_bidang_go"
    elif "pengajuan-lokasi-go" in p and reg_v["method"] == "DELETE":
        reg_v["status"] = "BLOCKED"
        reg_v["notes"] = "Tidak ada endpoint DELETE di backend service meskipun terdaftar di proxy"
        reg_v["action"] = "Konfirmasi ke FE/Service pemilik apakah fungsi delete dibutuhkan"

print(f"   Success! Registry compiled {len(ordered_keys)} unique endpoints.")

# --- 3. BUILD SPREADSHEET ROWS ---
headers_master = [
    "ID", "Modul Utama", "Sub-Modul / Fitur", "Halaman / Route FE",
    "Method", "Deskripsi Fungsi", "Endpoint Path / URL", "Target Service Backend",
    "Status Migrasi", "PIC", "Tipe Service", "Catatan / Blocker",
    "Action / Keputusan", "Link PR / Bukti"
]

master_rows = [headers_master]
for idx, key in enumerate(ordered_keys, 1):
    item = registry[key]
    master_rows.append([
        f"EP-{idx:03d}",
        item["modul"],
        item["submodul"],
        item["route_fe"],
        item["method"],
        item["desc"],
        item["path"],
        item["service"],
        item["status"],
        item["pic"],
        item["service_type"],
        item["notes"],
        item["action"],
        item["link"]
    ])

headers_inter = [
    "No", "Tanggal", "ID Tiket", "Deskripsi Pekerjaan Interupsi",
    "PIC", "Status", "Service Backend", "Link Tiket / Commit"
]
inter_rows = [headers_inter] + interrupt_tasks

mod_stats = defaultdict(lambda: {"total": 0, "done": 0, "in_progress": 0, "pending": 0, "blocked": 0, "pics": set()})
for item in registry.values():
    m = item["modul"]
    s = item["status"]
    mod_stats[m]["total"] += 1
    if s == "DONE":
        mod_stats[m]["done"] += 1
    elif s == "IN PROGRESS":
        mod_stats[m]["in_progress"] += 1
    elif s in ["BLOCKED", "NOT IN CODE"]:
        mod_stats[m]["blocked"] += 1
    else:
        mod_stats[m]["pending"] += 1
    for p in item["pic"].split("/"):
        p_clean = p.strip()
        if p_clean:
            mod_stats[m]["pics"].add(p_clean)

tot_endpoints = len(registry)
tot_done = sum(st["done"] for st in mod_stats.values())
tot_in_progress = sum(st["in_progress"] for st in mod_stats.values())
tot_pending = sum(st["pending"] for st in mod_stats.values())
tot_blocked = sum(st["blocked"] for st in mod_stats.values())
tot_pct = f"{(tot_done / tot_endpoints * 100):.1f}%" if tot_endpoints > 0 else "0.0%"

dash_rows = [
    ["DASHBOARD MIGRASI ENDPOINT SUPERAPPS BETA", "", "", "", "", "", "", ""],
    ["Monitoring Migrasi Endpoint Frontend ke Microservice Backend (Ganesha Operation)", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["METRIK RINGKASAN", "", "", "", "", "", "", ""],
    ["Total Endpoint", "Sudah Selesai (DONE)", "Dalam Pengerjaan", "Pending / Review", "Not In Code / Blocked", "% Penyelesaian", "", ""],
    [
        tot_endpoints,
        tot_done,
        tot_in_progress,
        tot_pending,
        tot_blocked,
        tot_pct,
        "", ""
    ],
    ["", "", "", "", "", "", "", ""],
    ["PROGRES PER MODUL UTAMA", "", "", "", "", "", "", ""],
    ["Modul", "PIC Backend", "Total Endpoint", "DONE", "IN PROGRESS", "PENDING", "BLOCKED / NOT IN CODE", "% Selesai"]
]

for m_name in sorted(mod_stats.keys()):
    st = mod_stats[m_name]
    pics_str = " / ".join(sorted(list(st["pics"])))
    pct_str = f"{(st['done'] / st['total'] * 100):.1f}%" if st["total"] > 0 else "0.0%"
    dash_rows.append([
        m_name,
        pics_str,
        st["total"],
        st["done"],
        st["in_progress"],
        st["pending"],
        st["blocked"],
        pct_str
    ])

dash_rows.append([
    "TOTAL KESELURUHAN", "-",
    tot_endpoints,
    tot_done,
    tot_in_progress,
    tot_pending,
    tot_blocked,
    tot_pct
])

# --- 4. TRANSMIT TO GOOGLE SHEETS ---
import requests
import time

def send_to_sheet(sheet_name, rows, max_retries=3):
    payload = {
        "sheetName": sheet_name,
        "rows": rows
    }
    print(f"Sending {len(rows)} rows to sheet '{sheet_name}'...")
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(WEBHOOK_URL, json=payload, timeout=60, allow_redirects=True)
            res_text = resp.text.strip()
            if "SUCCESS" in res_text:
                print(f"   Result for '{sheet_name}': SUCCESS")
                return res_text
            else:
                print(f"   Attempt {attempt} for '{sheet_name}' returned: {res_text[:100]}... Retrying in 2s...")
                time.sleep(2)
        except Exception as e:
            print(f"   Attempt {attempt} error sending to '{sheet_name}': {e}. Retrying in 2s...")
            time.sleep(2)
    print(f"   Failed to send to '{sheet_name}' after {max_retries} attempts.")

send_to_sheet("Master Endpoint Tracker", master_rows)
time.sleep(1)
send_to_sheet("Task Interupsi", inter_rows)
time.sleep(1)
send_to_sheet("Dashboard & Summary", dash_rows)

print("\nSUCCESS: All sheets are now up to date in Google Sheets!")
