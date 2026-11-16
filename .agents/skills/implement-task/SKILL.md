---
name: implement-task
description: >-
  Standard workflow for implementing modular tasks in GO Superapp Backend.
  Executes non-schema tasks directly according to task planning, strictly adheres to AGENTS.md and taste.md,
  pauses to discuss and confirm findings/anomalies with user broy before proceeding,
  and delegates build verification to subagents for parallel execution.
---

# Implement-Task Skill (GO Backend Superapp)

Skill ini digunakan untuk mengeksekusi implementasi coding per task file (`tasks/XX-*.md`) secara fokus, aman, dan terverifikasi.

---

## 🎯 Aturan Utama Eksekusi Coding

1. **HANYA Task Non-Schema**:
   - AI **HANYA mengeksekusi task bertipe `endpoint-flow`, `service`, `cron-worker`, dll.**
   - **Task `schema` (DDL / ALTER / CREATE TABLE / INDEX) MUTLAK DIKERJAKAN USER BROY** di DBeaver. AI dilarang menyentuh atau mengeksekusi DDL selain membaca schema dan menjalankan `prisma db pull` / `generate` jika diarahkan.
2. **Kepatuhan Aturan Dasar (`AGENTS.md` & `taste.md`)**:
   - **KENDALI PENUH GIT DI TANGAN USER**: Dilarang keras membuat branch, switch, commit, atau push (`git checkout -b`, `git branch`, dll). AI langsung bekerja di branch yang disediakan user.
   - **HANYA READ-ONLY SELECT KE DB**: Menggunakan `docs-go-roy/scripts/go-psql-ro.sh`. Wajib `$queryRaw` untuk SELECT di Prisma, dilarang mutasi DB langsung, dilarang high-query tanpa `LIMIT`.
   - **BigInt Serialization**: Konversi nilai BigInt ke number (`Number(...)`) atau string (`val.toString()`).
   - **Jangan Try-Catch Pemanggilan Antar-Service**: Teruskan error service data asli ke BFF tanpa false information.
   - **Proxy/BFF Params/Body `any`**: Pada modul BFF baru (`go-superapp-api`), gunakan `any` tanpa DTO (kecuali Protobuf/gRPC).
   - **Token & Output Economy**: Bekerja efisien tanpa narasi play-by-play yang bertele-tele antar tool call.
3. **Gerbang Diskusi / Temuan di Tengah Jalan**:
   - Jika saat implementasi ditemukan:
     - Inkonsistensi data DB atau edge cases yang belum tercakup di planning.
     - Perbedaan kontrak data antar service tujuan.
     - Ambigu atau potensi breaking change ke consumer mobile/web.
   - **JANGAN ASUMSI SENDIRI / JANGAN LANJUT KODING DULU**.
   - **Wajib jeda sejenak, paparkan temuan secara ringkas, dan diskusikan/konfirmasi langsung ke User Broy**.
4. **Verifikasi Build Paralel via Subagent**:
   - Saat implementasi selesai dan butuh verifikasi build (`npm run build` pada data-svc dan BFF), **gunakan subagent (`invoke_subagent`)** agar build berjalan di background secara paralel tanpa memblokir atau membuang token turn utama.
   - Verifikasi cukup sampai `npm run build` (tanpa lint).

---

## 🚀 Alur Kerja Implementasi Task

### 1. Baca Task File Terkait
- Baca file task yang dipilih, misal: `docs-go-roy/implementation-plan/progress/.../tasks/XX-nama-flow.md`.
- Pahami target file data-service, target file BFF, payload contract, dan rencana testing-nya.

### 2. Implementasi Kode Sesuai Planning
- Terapkan perubahan pada file yang bersangkutan (data service terlebih dahulu, kemudian BFF).
- Ikuti standar pattern eksisting di repo tersebut.
- Jika ada temuan anomali data/kode -> Stop dan diskusikan dengan user broy.

### 3. Build Verification via Subagent (Paralel)
- Delegasikan verifikasi build ke subagent:
  ```json
  {
    "TypeName": "self",
    "Role": "Build Verifier",
    "Prompt": "Jalankan build smoke pada repo terkait: npm --prefix /home/broy/work/<repo-data> run build dan npm --prefix /home/broy/work/<repo-bff> run build. Laporkan status Exit Code dan log singkatnya."
  }
  ```
- Tunggu notifikasi subagent selesai.

### 4. Smoke Test & Sanity Check
- Lakukan pengujian empiris sesuai skenario testing di dalam file task (curl endpoint lokal/staging).
- Pastikan lolos Sanity Check Hirarki Data ($\sum \text{Child} == \text{Parent}$) dan bukan false-positive 200 OK dengan payload kosong.

### 5. Update Status Task & Plan Index
- Update status di dalam file task `tasks/XX-*.md`:
  - Ubah `status: "DONE"`.
  - Isi `Execution Log` dengan hasil curl aktual.
- Update tabel indeks di `plan.md`:
  - Ubah status task tersebut dari `TODO` / `IN_PROGRESS` menjadi `DONE`.
- Laporkan ringkasan perubahan ke User Broy (`Changed`, `Verify`, `Notes`, `Recommendation`) dan serahkan urusan git commit ke user.
