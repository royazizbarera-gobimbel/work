---
name: dsm-report
description: Menyusun laporan DSM (Daily Standup Meeting) harian GO Backend ke folder docs-go-roy/DSM per tanggal. Gunakan saat user minta "bikin DSM", "laporan DSM", "laporan siang/sore", "daily report", atau menyebut standup harian.
---

# DSM Report Skill (GO Backend Superapp)

Skill ini membuat/memperbarui file laporan DSM dari instruksi user. User cukup menyebutkan apa yang dikerjakan; agent menstrukturkan menjadi format baku.

## 📁 Lokasi & Struktur File

```
docs-go-roy/DSM/<YYYY-MM-DD>/
├── DSM-Siang.md
└── DSM-Sore.md
```

- `<YYYY-MM-DD>` = tanggal laporan (default hari ini, zona `Asia/Jakarta`, kecuali user menyebut tanggal lain).
- **DSM-Siang.md** = laporan sesi siang.
- **DSM-Sore.md** = laporan "sampai sore" / akhir hari.
- Buat folder tanggal jika belum ada. Buat hanya file yang diminta (siang/sore/both).

## 👤 NAMA & Total

- NAMA **default = `ROY`**. Jika user menyebut nama lain, pakai nama itu.
- Satu file boleh berisi **beberapa orang** (mis. rekap tim). Formatnya: blok nama, lalu daftar `Task 1..N` milik orang itu, penomoran task mulai dari 1 lagi per orang.
- Cantumkan **Total Task** untuk tiap blok nama (jumlah task milik orang tersebut).

## 🧾 Format Baku File

```markdown
NAMA : ROY

Total Task : 3

---

Task 1
Task : <judul singkat tiket / pekerjaan>
GitHub : <repo>#<nomor>   (atau URL issue lengkap; "-" bila belum ada)
Status : <status>
Yang dikerjakan :
- <1 kalimat lengkap: apa yang ditambah/diubah/diperbaiki + alasannya/aturannya + objek konkretnya>
- <1 kalimat lengkap berikutnya>

Kendala :
- <kendala singkat> (atau "Tidak ada")

Butuh Bantuan :
- <bantuan yang dibutuhkan> (atau "Tidak ada")

---

Task 2
Task : ...
GitHub : ...
Status : ...
Yang dikerjakan :
- ...

Kendala :
- ...

Butuh Bantuan :
- ...
```

## 🔧 Aturan Penulisan

1. **1 Task = 1 tiket GitHub** (`repo#nomor`, mis. `db-go#2967`). Jika user menyebut pekerjaan non-tiket, tetap 1 task dengan `GitHub : -`.
2. **Status** hanya boleh salah satu:
   - `Staging`
   - `In Progres`
   - `ToDo`
   - `Done`
   - `Pending`
3. **Yang dikerjakan**: 2–5 poin, **tiap poin = 1 kalimat lengkap yang informatif**. Poin harus menjawab: apa yang ditambah/diubah/diperbaiki, di objek mana (endpoint, file, field, tabel, service), dan alasannya (feedback BisDev, aturan bisnis, bug yang terjadi).
   - Bukan sekadar menyebut aktivitas. `Cek query presensi` = kurang. `Perbaiki query presensi harian agar tidak dobel saat ada 2 jadwal di tanggal yang sama` = benar.
   - Sebut angka/kriteria bisnis bila ada (mis. "hanya jenis ujian UH, PAT, PAS, UTS, US").
   - Sebut endpoint + method bila menyangkut API (mis. `PATCH /api/v1/kelas/data-kelas/:idkelas`).
   - Sebut nama tabel/kolom/field apa adanya bila relevan.
   - Jangan menyembunyikan detail jadi kalimat umum ("menyempurnakan alur data").
4. **Kendala** dan **Butuh Bantuan**: isi `Tidak ada` jika kosong.
5. **Jangan mengarang** data. Hanya tulis yang diberikan/diinstruksikan user. Jika informasi wajib tidak disebut, isi `-`.
6. Urutan task mengikuti urutan yang disebut user (atau prioritas status bila diminta).
7. Jika file tanggal tersebut sudah ada:
   - Pertahankan task lama.
   - Tambahkan task baru dari instruksi terbaru.
   - Perbarui `Total Task` dan status/poin yang berubah. Jangan menduplikasi task yang sama (cocokkan lewat `GitHub`/`Task`).
8. **Bahasa**: Indonesia sehari-hari, ringkas, apa adanya.
   - Tulis seperti orang bercerita ke rekan kerja, bukan bahasa laporan formal atau puitis.
   - **Dilarang majas/gaya bahasa kiasan**: metafora, hiperbola, personifikasi, kata berlebihan (mis. "menuntaskan", "menjelajah", "merapikan ekosistem", "menyelaraskan lanskap", "mengawal", "menuntun").
   - Hindari kata sifat berbunga dan istilah teknis yang tidak perlu. Pakai kata kerja biasa: `tambah`, `ubah`, `perbaiki`, `cek`, `hapus`, `pindah`, `sesuaikan`.
   - Sebut objek konkret (nama endpoint, file, field, service). Jangan mengaburkan dengan istilah umum.
   - Contoh benar: `Tambah kolom gedung_id di create rencana kegiatan`.
   - Contoh salah: `Menuntaskan penyelarasan struktur data pada alur kegiatan pusat`.
   - Istilah teknis (nama tabel/kolom/endpoint/status) tetap ditulis apa adanya, tidak diterjemahkan.

## 🚀 Alur Kerja Agent

1. Tentukan tanggal (`Asia/Jakarta`) dan jenis file (`Siang`/`Sore`) dari instruksi user.
2. Ekstrak daftar task dari instruksi: judul, GitHub, status, poin pekerjaan, kendala, bantuan.
3. Pastikan `Total Task` sesuai jumlah task di file.
4. Tulis/merge ke `docs-go-roy/DSM/<tanggal>/DSM-<Siang|Sore>.md`.
5. Laporkan path file yang dibuat/diupdate secara singkat.

## 🧪 Contoh

Instruksi user:
> DSM siang: db-go#2967 profil pegawai, status staging. Yang dikerjakan: mapping field staging-beta, proxy api-superapps-v2. Kendala: data beta masih tipis. Butuh bantuan: sample data lengkap. Plus db-go#3001 fix presensi, status in progres, yang dikerjakan: cek query presensi.

Hasil `docs-go-roy/DSM/2026-11-17/DSM-Siang.md`:

```markdown
NAMA : ROY

Total Task : 2

---

Task 1
Task : Endpoint Lihat Profil Pegawai
GitHub : db-go#2967
Status : Staging
Yang dikerjakan :
- Menyesuaikan mapping field profil pegawai ke skema staging-beta (biodata, jabatan SO aktif, riwayat SO beserta cakupan)
- Menambahkan proxy endpoint profil pegawai di api-superapps-v2 dan go-superapp-api
- Mengubah query baca ke $queryRaw + Prisma.sql agar performa lebih terkontrol

Kendala :
- Data beta masih tipis

Butuh Bantuan :
- Sample data lengkap untuk UAT

---

Task 2
Task : Perbaikan Presensi
GitHub : db-go#3001
Status : In Progres
Yang dikerjakan :
- Memperbaiki query presensi harian agar tidak dobel saat ada 2 jadwal di tanggal yang sama
- Menambahkan validasi jam masuk dan jam pulang yang tidak berurutan

Kendala :
- Tidak ada

Butuh Bantuan :
- Tidak ada
```

Contoh poin yang **kurang** (terlalu umum): `Cek query presensi`, `Perbaiki bug`, `Update endpoint`.
Contoh poin yang **benar**: `Memperbaiki query presensi harian agar tidak dobel saat ada 2 jadwal di tanggal yang sama`.
