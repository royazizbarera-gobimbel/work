# broy-docs — Template Repo Workflow & Tracking

Repo **template** berisi cara kerja (SOP), struktur tracking, dan template dokumen
yang reusable untuk proyek apa pun. Fork/salin ini jadi `namaproyek-docs`, isi
bagian `PROJECT CONFIG` di `AGENTS.md`, hapus contoh, mulai kerja.

Diturunkan dari cara kerja nyata (scrum ringan + 3 track + testing sebagai gerbang
"Verified") lalu digeneralisasi. Tidak terikat stack tertentu.

## Isi

```
broy-docs/
  README.md              ← file ini
  AGENTS.md              ← ATURAN AGEN + SOP (hub semua aturan). Isi PROJECT CONFIG.
  CLAUDE.md              ← cuma nunjuk ke AGENTS.md
  .gitignore
  docs/
    GIT-WORKFLOW.md      ← SOP git: branch, commit, PR, review, larangan
    mvp/mvp-template.md          ← scope & release criteria per rilis
    epic/epic-template.md        ← source of truth story & task (fitur)
    sprints/sprint-template.md   ← potongan kerja 1–2 minggu
    enhancement/                 ← penyempurnaan fitur yang SUDAH ada
      README.md · enhancement-template.md · ENHANCEMENTS.md (roster)
    bugs/                        ← defect + semua laporan
      README.md · bug-template.md · BUGS.md (roster)
    testing/                     ← test plan per epic; gerbang "Verified"
      README.md · test-plan-template.md
```

## Model tracking

```
MVP  (docs/mvp/)          → scope & release criteria per versi rilis
Epic (docs/epic/)         → source of truth story & task (track FITUR)
Sprint (docs/sprints/)    → potongan kerja 1–2 minggu dari MVP aktif
Enhancement (docs/enhancement/) → penyempurnaan fitur yang SUDAH ada
Bug (docs/bugs/)          → defect + semua laporan
Testing (docs/testing/)   → test plan per epic; gerbang "Verified"
```

Tiap kerjaan masuk **tepat satu** track:

| Jenis kerjaan | Track | ID |
| ------------- | ----- | -- |
| Fitur baru | Epic (story) | `US-XX-YY` |
| Menyempurnakan fitur yang ada | Enhancement | `ENH-YYYYMMDD-XX` |
| Sesuatu yang rusak / laporan | Bug | `BUG-YYYYMMDD-XX` |
| Verifikasi manual/device | Testing | `TC-XX-YY` |

Rantai keterlacakan: `EPIC.AC → TC → (Fail) → BUG → fix → TC ulang → Pass → Done`.

## Cara pakai (bootstrap proyek baru)

1. Salin folder ini → `namaproyek-docs`, lalu `git init` (kalau belum).
2. Buka `AGENTS.md`, isi blok **PROJECT CONFIG** (nama proyek, stack, area,
   perintah verifikasi, prefix epic). Hapus baris contoh.
3. Sesuaikan `docs/GIT-WORKFLOW.md`: tabel scope commit + reviewer.
4. Buat MVP pertama dari `docs/mvp/mvp-template.md`, epik dari
   `docs/epic/epic-template.md`.
5. Mulai. Setiap dokumen baru menyalin template yang sesuai; jangan bikin dari nol.

## Konvensi ID (generik)

- Epic: `EPIC-XX` (mis. `EPIC-01`, `EPIC-A1`). Ganti `XX` sesuai skema proyek.
- Story: `US-XX-YY` (XX = nomor epic). Task: `T-XX-YY-Z`.
- Enhancement: `ENH-<tanggal>-<urut>`. Bug: `BUG-<tanggal>-<urut>`.
- Test case: `TC-XX-YY` (menaut ke Acceptance Criteria story).

`Status` di mana-mana: `Todo | On Progress | Done | Blocked | Later`.
