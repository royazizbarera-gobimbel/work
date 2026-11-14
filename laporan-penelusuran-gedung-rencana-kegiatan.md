# Laporan Penelusuran Kendala Tampilan Rencana Kegiatan

Berikut disampaikan hasil penelusuran (root cause analysis) terkait kendala baris data rencana kegiatan yang tidak tampil pada menu "Rencana Kegiatan" untuk 6 sekretariat yang dilaporkan:

---

## 1. Kesimpulan Singkat (Status Data)

* Data di database 100% ADA, lengkap, dan tidak hilang.
* Tidak ada anomali atau kegagalan pada proses migrasi/bulk insert sistem.

---

## 2. Akar Masalah (Root Cause)

Kendala ini terjadi karena adanya ambiguitas data master gedung di db_go, di mana pada 1 sekretariat terdapat lebih dari 1 gedung yang sama-sama berstatus Aktif dan Penerimaan (is_penerimaan = true):

1. Sesuai Arahan Awal Migrasi:
   Ketika 1 sekretariat memiliki lebih dari 1 gedung penerimaan aktif, arahan bisnis di awal adalah mengambil salah satu gedung penerimaan yang valid. Sistem secara deterministik memilih gedung penerimaan pertama yang terdaftar (berdasarkan ID gedung terkecil).
2. Perilaku Filter di Menu UI:
   Pada menu Rencana Kegiatan, UI mewajibkan pengguna memilih 1 Gedung spesifik. User cabang secara alami memilih gedung operasional harian mereka (yang kebetulan memiliki ID gedung lebih baru/besar), sementara data hasil migrasi tersimpan pada gedung penerimaan pasangannya di sekretariat yang sama.
3. Akibatnya:
   Saat filter UI menyaring gedung yang dipilih user, query mengeksekusi WHERE gedung_id = [gedung_terpilih], sehingga tabel menampilkan No records karena data tersimpan pada gedung penerimaan yang satunya.

---

## 3. Fakta Data pada 6 Sekretariat yang Dilaporkan

Berdasarkan query database, seluruh 6 sekretariat tersebut memang memiliki 2 gedung penerimaan aktif:

| Cabang          | Kota            | Sekretariat          | Gedung di DB (Hasil Insert) | Gedung yang Dipilih User di UI |
| :-------------- | :-------------- | :------------------- | :-------------------------- | :----------------------------- |
| Pematangsiantar | Pematangsiantar | Melanthon Siregar 30 | 158 (MELANTHON SIREGAR 41B) | 778 (Melanthon Siregar No. 30) |
| Tangerang Kota  | Tangerang Kota  | Kelapa Kuning        | 234 (Daan Mogot 16)         | 786 (Jalan Dalam No. 4)        |
| Pekalongan      | Tegal           | Kartini - Tegal      | 245 (KS Tubun 13)           | 814 (Kartini No. 27)           |
| Makassar        | Makassar        | Sultan Alauddin      | 344 (Sultan Alauddin 197)   | 802 (Sultan Alauddin 78 C)     |
| Yogyakarta      | Yogyakarta      | Taman Siswa          | 255 (TAMAN SISWA 85)        | 776 (TAMAN SISWA 141)          |
| Jakarta 3       | Jatisampurna    | Kranggan Raya        | 625 (KRANGGAN RAYA 9E)      | 790 (KRANGGAN RAYA 9G)         |

Secara total nasional, terdapat 12 sekretariat yang memiliki kondisi multi-penerimaan serupa.

Pembuktian: Jika di dropdown filter UI saat ini user memilih gedung di kolom "Gedung di DB", seluruh baris kegiatan langsung tampil lengkap.

---

## 4. Solusi & Rekomendasi

Untuk menyelaraskan dengan kebutuhan operasional cabang:

1. Solusi Cepat (Backend Data Alignment):
   Tim Backend siap menjalankan script penyesuaian (update query) untuk memindahkan gedung_id pada rencana kegiatan di 6 (atau 12) sekretariat tersebut ke gedung operasional utama yang diinginkan cabang (gedung terupdate).
2. Solusi Jangka Panjang (Master Data Cleaning):
   Perlu konfirmasi ke tim operasional/BisDev untuk menonaktifkan bendera is_penerimaan = false pada gedung yang sudah tidak menjadi sekretariat penerimaan utama, agar ke depannya setiap sekretariat hanya memiliki 1 gedung penerimaan tunggal.

Mohon arahan apakah kami dapat langsung mengeksekusi penyesuaian gedung_id ke gedung operasional utama untuk sekretariat-sekretariat tersebut.

Terima kasih.
