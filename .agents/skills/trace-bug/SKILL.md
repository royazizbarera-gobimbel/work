---
name: trace-bug
description: >-
  Standard workflow for tracing bugs, root causes, and data discrepancies across GO Superapp Backend microservices.
  Traces from any entry point (symptom, sample data, DB records, or endpoint), traverses the call chain down to the database,
  compares actual DB rows against application logic, and presents a concise root-cause breakdown without live-probing.
---

# Trace-Bug Skill (GO Backend Superapp)

Skill ini digunakan untuk menelusuri akar masalah bug (root-cause analysis), anomali data, selisih angka perhitungan, atau inkonsistensi status antar service dan database PostgreSQL.

---

## 🎯 Prinsip Utama Penelusuran Bug

1. **Fleksibel Terhadap Titik Masuk (Multi Entry-Point)**:
   - Investigasi tidak harus berawal dari URL/endpoint Frontend. Titik masuk bisa berupa:
     - **Sample Data / Entitas**: Nomor registrasi siswa, NIK petugas, `id_penugasan`, `c_id_gedung`, nomor nota.
     - **Gejala / Anomali Angka**: "Kenapa total capaian sekolah X terlipat ganda?", "Kenapa status siswa Y masih non-aktif?", "Kenapa field Z bernilai null?".
     - **Query / Tabel DB**: Investigasi langsung dari baris tabel tertentu yang mencurigakan.
     - **Endpoint / Controller**: Jika memang URL atau rute API disebutkan secara spesifik.

2. **Trace Alur Kode Duluan (Anti Probe Live URL - Sesuai taste.md)**:
   - Telusuri jalurnya melalui pembacaan kode sumber:
     `[Sample Data / Entity / DB Record] <---> [Data Service Query / Logic] <---> [Downstream / BFF Proxy]`.
   - Dilarang menembak (curl/probe) URL live remote secara membabi-buta tanpa memahami alur kode sumbernya.

3. **Bandingkan Data Riil di DB vs Hasil Olahan Aplikasi**:
   - Manfaatkan skill **`db-query`** (`docs-go-roy/scripts/go-psql-ro.sh`, default Staging) untuk mengambil row riil pada tabel database terkait.
   - Bandingkan:
     - **Kondisi Row di DB**: Apa nilai kolom aktualnya? Apakah ada record duplikat?
     - **Kondisi Olahan Kode**: Bagaimana SQL `$queryRaw`/Prisma memfilter data tersebut? Apakah ada manipulasi array di JavaScript/TypeScript (loop `+=`, filter, join) yang merusak nilai aslinya?

4. **Klasifikasi Titik Rusak (Pinpoint Root Cause)**:
   Tentukan secara objektif di mana titik kerusakannya berada:
   - 🔴 **Query SQL / ORM Issue**: Cartesian join, group by salah, tidak menggunakan `DISTINCT`, salah klausa `WHERE`.
   - 🔴 **Application Logic Issue**: Pengali looping sub-entitas (misal bug finance#1859), kesalahan mutasi state, parsing tanggal timezone.
   - 🔴 **Dirty / Anomalous Data**: Data historis kotor di DB (misal FK gantung, null value tak terduga).
   - 🔴 **Serialization / DTO Issue**: BigInt serialization error, field tertelan saat mapping antar service.

---

## 🛠️ Langkah-Langkah Eksekusi Tracing

### Langkah 1: Kunci Entitas & Titik Mulai
- Identifikasi parameter kunci dari laporan:
  - Misal diberikan sample ID: cari di service data mana tabel entitas tersebut berada (`rg "<nama_tabel>" -l` atau cek `schema.prisma`).
  - Misal diberikan gejala rumus: cari service data yang menghitung metrik tersebut.

### Langkah 2: Inspeksi Database (Data Fact-Checking)
- Gunakan `docs-go-roy/scripts/go-psql-ro.sh <service> -c "<SQL>"` (default STAGING).
- Cek skema kolomnya dulu (`\d <nama_tabel>`).
- Query sampling data yang dilaporkan bermasalah dengan `LIMIT 5-10`.
- Catat nilai aktual kolom di database.

### Langkah 3: Susur Kode Penghasil Data (Source Code Tracing)
- Buka file service/handler yang mengeksekusi query tersebut.
- Periksa transformasi data setelah query diambil:
  - Apakah ada loop yang salah menjumlahkan akumulasi?
  - Apakah ada kondisi `if-else` yang mem-bypass nilai?
  - Apakah downstream / BFF proxy ada yang mengubah shape response?

### Langkah 4: Sajikan Root-Cause Summary
Sajikan temuan secara padat dan terstruktur ke User Broy:

```markdown
### 🔍 Hasil Tracing Bug

1. **Titik Masuk & Entitas**: `<Entity / Sample ID / Gejala>`
2. **Call Chain & Komponen**:
   - Data Service: `<repo>` (`<file-service>:<line>`)
   - Downstream/BFF: `<repo-bff>` (`<file-controller/service>:<line>`)
   - Tabel DB: `<nama_tabel>`
3. **Kondisi Data Riil di DB (Empiris)**:
   - Baris di DB: `<nilai asli kolom di database>`
4. **Kondisi Output Aplikasi**:
   - Nilai yang keluar: `<nilai yang dialami/dikeluhkan>`
5. **Akar Masalah (Root Cause)**:
   - `<Penjelasan teknis mengapa selisih/bug terjadi>`
6. **Rekomendasi Perbaikan**:
   - `<File yang harus diubah dan solusi logikanya>`
```

---

## ⚠️ Safeguard & Rules

- **Ekonomi Token**: Lakukan pencarian spesifik (grep `-n`, `read_file` per range baris method). Jangan dump isi file besar yang tidak relevan ke context.
- **Tanpa Asumsi / Halusinasi**: Fakta DB harus dicek langsung lewat `go-psql-ro.sh`, bukan berasumsi isi DB.
- **Jangan Mengubah Kode Saat Tracing**: Skill ini murni diagnostik & fact-checking. Perbaikan kode dilakukan setelah akar masalah disepakati bersama user broy.
