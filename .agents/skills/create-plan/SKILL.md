---
name: create-plan
description: >-
  Standard workflow for designing and planning GO Superapp Backend tasks.
  Breaks tickets into modular tasks (1 task = 1 file in tasks/ with embedded testing),
  keeps data-svc and BFF together in 1 flow/endpoint task, manages schema updates,
  and structures plan.md as an index dashboard with recommended branches.
---
# Create-Plan Skill (GO Backend Superapp)

Skill ini digunakan untuk merancang arsitektur implementasi tiket/fitur secara modular dan terstruktur sebelum koding dimulai.

---

## 🎯 Prinsip Utama Perancangan Task

1. **`plan.md` Adalah Generic Plan & Dashboard Index**:
   - Berisi gambaran helikopter (high-level / generic plan): latar belakang tiket, aturan bisnis umum, urutan deploy, rekomendasi branch per repo, dan tabel daftar task.
   - **TIDAK memuat detail teknis coding yang mendalam** (tidak ada potongan fungsi/query panjang).
   - Menjadi peta navigasi utama untuk memantau progres keseluruhan tiket.
2. **Detail Implementasi & Testing Ada di Masing-Masing File Task (`tasks/XX-nama-task.md`)**:
   - Detail teknis implementasi (query SQL/Prisma, perubahan handler, DTO, edge cases, script curl, data empiris, dan verification build) **seluruhnya dituangkan secara mendalam di dalam file task masing-masing**.
   - Setiap file task mandiri (self-contained) dan fokus pada 1 flow flow endpoint atau 1 skema DDL.
3. **Data-Service & BFF Mengalir dalam 1 Task yang Sama**:
   - Jika satu perubahan mencakup endpoint di service data dan consumer BFF-nya (`go-superapp-api`, dll.), **keduanya dikelompokkan ke dalam 1 task yang sama (1 flow)**.
   - Jangan memisahkan data-svc dan BFF ke task terpisah agar dependensi kontrak API tidak terpecah.
4. **Perubahan Skema / DDL = Task Tersendiri + File `*.sql` Terpisah**:
   - Jika ada pembuatan tabel baru, penambahan kolom, atau alter index, pisahkan ke dalam task skema tersendiri (misal: `tasks/01-schema-database.md`).
   - Script SQL **TIDAK DITULIS PANJANG DI FILE MD**, melainkan dibuatkan file SQL terpisah di folder `tasks/` (misal: `tasks/ddl-task-01-<nama>.sql`).
   - File task MD skema dibuat super ringkas: hanya referensi target DB, link file SQL, dan langkah verifikasi manual di DB + build pull prisma.
5. **Rekomendasi Branch & Larangan Mutasi Git oleh AI**:
   - Base branch **SELALU DARI `main`**.
   - AI **DILARANG KERAS MEMBUAT / SWITCH / CHECKOUT BRANCH SENDIRI** (`git checkout -b`, `git branch`, `git switch`).
   - `plan.md` hanya memberikan **rekomendasi nama branch** (misal: `enh/<nomor-tiket>-<slug>` atau `feat/<nomor-tiket>-<slug>`) dengan base `main`.
   - AI langsung bekerja di branch yang disediakan / dibuka oleh user broy.

---

## 📁 Struktur Direktori Output Tiket

Setiap perencanaan tiket disimpan di:
`docs-go-roy/implementation-plan/progress/yy-mm-dd-HHmm-<repo>-<nomor-tiket>-<slug>/`

```text
yy-mm-dd-HHmm-<repo>-<nomor-tiket>-<slug>/
├── plan.md               # Master Dashboard & Indexing (dari plan.template.md)
└── tasks/
    ├── 01-schema-<nama-tabel>.md         # (Opsional: dari task-schema.template.md)
    ├── 02-<fitur-flow-utama>.md          # (1 flow: dari task-flow.template.md)
    └── 03-<fitur-flow-kedua-atau-cron>.md # (Flow tambahan / cron / integrasi)
```

---

## 📑 File Templates

Skill ini menyediakan template terpisah di subfolder `templates/`:

1. **`templates/plan.template.md`**: Template dashboard utama `plan.md` (metadata, branch recommendation, urutan deploy, indeks task).
2. **`templates/task-flow.template.md`**: Template task flow endpoint lengkap (service data + BFF + embedded testing & curl sanity check).
3. **`templates/task-schema.template.md`**: Template task DDL / perubahan skema database + sinkronisasi Prisma.

---

## 🚀 Alur Kerja Agent Saat Menggunakan Skill Ini (Two-Phase / Staged - Opsi 2)

Proses perencanaan dibagi menjadi **2 fase** yang rapi dan terukur:

### 📍 FASE 1: Alignment & Pembuatan Dashboard Index (`plan.md`)
1. **Analisis Tiket**:
   - Pahami issue, rumus bisnis/perhitungan, tabel database yang disentuh, dan proxy BFF yang menjadi consumer-nya.
2. **Setup Folder Tiket**:
   - Buat direktori: `docs-go-roy/implementation-plan/progress/yy-mm-dd-HHmm-<repo>-<tiket>-<slug>/tasks/`.
3. **Generate `plan.md` (Master Index Saja)**:
   - Salin dari `templates/plan.template.md`.
   - Cantumkan rekomendasi branch (`main` based) untuk setiap repo.
   - Cantumkan tabel index daftar task (breakdown flow fitur, target service, tipe task).
4. **Konfirmasi ke User Broy**:
   - Tampilkan link ke `plan.md`, rekomendasi branch, dan daftar pecahan task-nya.
   - **Tunggu persetujuan user broy** sebelum membuat file-file task di dalam folder `tasks/`.

---

### 📍 FASE 2: Pembuatan File Task di `tasks/` (Setelah Plan Disetujui)
Setelah User Broy mengonfirmasi (misal: *"oke gas"*, *"lanjut"*):
1. **Generate Seluruh File Task di `tasks/`**:
   - **Task Schema (jika ada)**:
     - Buat file SQL: `tasks/ddl-task-01-<nama>.sql` (dari `templates/ddl.template.sql`).
     - Buat file task: `tasks/01-schema-<nama>.md` (dari `templates/task-schema.template.md`).
   - **Task Endpoint Flow**:
     - Buat file task: `tasks/02-<nama-flow>.md` (dari `templates/task-flow.template.md`) yang **menggabungkan data-svc + BFF + skenario testing & curl** dalam 1 file.
     - Lanjutkan untuk seluruh task yang terdaftar di `plan.md`.
2. **Siap Eksekusi**:
   - Laporkan bahwa seluruh file task telah selesai di-generate.
   - Minta konfirmasi task mana yang akan dieksekusi pertama kali.
