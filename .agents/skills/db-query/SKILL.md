---
name: db-query
description: >-
  Standard workflow for safely querying and investigating PostgreSQL databases in GO Superapp Backend.
  Defaults to STAGING environment (via active DATABASE_URL in .env), requires explicit user instruction
  for PROD (localhost:700x with GO_PSQL_ALLOW_PROD=1), inspects schema before querying, enforces LIMIT,
  and operates strictly read-only using docs-go-roy/scripts/go-psql-ro.sh.
---

# DB-Query Skill (GO Backend Superapp)

Skill ini digunakan untuk melakukan penelusuran skema, investigasi data, sampling row empiris, dan verifikasi database PostgreSQL secara aman dan terkontrol.

---

## 🎯 Prinsip Utama Akses Database

1. **Jalur Resmi: `docs-go-roy/scripts/go-psql-ro.sh`**:
   - Seluruh eksekusi query PostgreSQL WAJIB melalui script ini:
     ```bash
     docs-go-roy/scripts/go-psql-ro.sh <repo-service> -c "<SQL>"
     ```
   - Sesi DB dipaksa server-side **read-only** (`default_transaction_read_only=on`, `statement_timeout=30s`, `lock_timeout=5s`).
   - Dilarang membuat script koneksi sendiri atau hardcode kredensial.

2. **Aturan Environment: Default STAGING vs PROD**:
   - **DEFAULT = STAGING**:
     - Secara default, query SELALU diarahkan ke **Staging** (menggunakan baris aktif `DATABASE_URL` di `<repo-service>/.env`, misal IP `17.8.20.239`/`17.8.20.240` port `5432`).
     - Cukup jalankan langsung: `docs-go-roy/scripts/go-psql-ro.sh <repo-service> -c "<SQL>"`.
   - **PROD (HANYA JIKA DIMINTA EKSPLISIT OLEH USER BROY)**:
     - Jangan pernah menyentuh PROD kecuali User Broy secara eksplisit meminta data Production (misal: *"cek data di prod bro"*).
     - Database PROD terhubung melalui tunnel localhost port `700x` (misal `7001`, `7003`, `7009`).
     - Saat mengakses PROD, wajib menambahkan environment flag:
       ```bash
       GO_PSQL_ALLOW_PROD=1 docs-go-roy/scripts/go-psql-ro.sh <repo-service> -c "<SQL>"
       ```
     - **Larangan Keras di PROD**: Mutlak dilarang query tanpa `LIMIT` atau full-table scan pada tabel transaksi besar.

3. **Cek Skema DULU Sebelum Menulis Query (Aturan taste.md)**:
   - Dilarang menebak kolom atau query membabi-buta ke tabel yang belum diketahui strukturnya.
   - Periksa model Prisma di `<repo-service>/prisma/schema.prisma` terlebih dahulu, ATAU
   - Periksa struktur tabel via psql:
     ```bash
     docs-go-roy/scripts/go-psql-ro.sh <repo-service> -c "\d <nama_tabel>"
     docs-go-roy/scripts/go-psql-ro.sh <repo-service> -c "\dt <prefix>*"
     ```
   - **Integritas Penamaan Kolom/Tabel**: Pertahankan prefix asli (`c_`, `t_`, `m_`, `p_`, dll) persis apa adanya.

4. **Operasi Mutlak READ-ONLY**:
   - Hanya diizinkan query `SELECT`, `EXPLAIN`, `\d`, `\dt`.
   - Dilarang keras melakukan mutasi data: `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `DROP`, `ALTER`.

5. **Anti High-Query & Table Lock**:
   - Wajib selalu menyertakan klausa `LIMIT` (default 5–10) untuk sampling data.
   - Wajib memfilter kolom berindeks (`id`, `c_nik`, `sekolah_id`, rentang tanggal).
   - Hindari cartesian product / join tanpa on-clause yang jelas.

---

## 🛠️ Contoh Command Penggunaan

### 1. Inspeksi Skema (Staging - Default)
```bash
# Cek daftar tabel tertentu
docs-go-roy/scripts/go-psql-ro.sh db-sellma -c "\dt penugasan_*"

# Cek detail kolom & tipe data suatu tabel
docs-go-roy/scripts/go-psql-ro.sh db-sellma -c "\d penugasan_wablast_detail_siswa"
```

### 2. Sampling Data Empiris (Staging - Default)
```bash
# Cek 5 data terbaru dengan LIMIT
docs-go-roy/scripts/go-psql-ro.sh db-sellma -c "SELECT id, id_jenis_penugasan_wa_blast, wa_terkirim, tanggal_realisasi FROM penugasan_wablast ORDER BY id DESC LIMIT 5;"
```

### 3. Sampling Data di PROD (Hanya Saat Diminta Eksplisit)
```bash
# Cek data di PROD dengan izin user broy
GO_PSQL_ALLOW_PROD=1 docs-go-roy/scripts/go-psql-ro.sh db-sellma -c "SELECT id, wa_terkirim FROM penugasan_wablast ORDER BY id DESC LIMIT 5;"
```

---

## 📊 Checklist Verifikasi Query (Sanity Check)

Sebelum menggunakan query SQL ke dalam kode aplikasi (`$queryRaw`), verifikasi:
- [ ] Kolom dan tabel sudah terbukti ada di skema aktual (bukan halusinasi).
- [ ] Hasil query bukan false-positive kosong atau terlipat ganda karena loop sub-entitas.
- [ ] Nilai kolom bertipe `bigint` sudah diantisipasi untuk dikonversi (`Number(...)` / `val.toString()`).
- [ ] Query telah diuji mandiri dengan script ini dan mengembalikan data yang valid.
