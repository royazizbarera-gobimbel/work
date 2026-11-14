
# Tiket - Dashboard Iklan Produk

[RELATE TIKET] :

- https://github.com/GO-Bimbel/db-ecommerce/issues/83

## Latar Belakang

Aplikasi mobile (GoExpert Siswa, GoExpert TOBK, GoExpert Ortu, dan TCR) akan menampilkan 2 produk terlaris pada halaman awal. Saat ini Produk yang tampil bukan ditentukan pada transaksi penjualan terlari dengan status **Berhasil** pada Ecommerce atau dengan status bayar **> C1**, tetapi ditentukan secara manual melalui Dashboard

Dashboard ini akan digunakan untuk mengatur produk mana yang akan ditampilkan pada aplikasi, sehingga user (MKT/BDMMS) akan menyesuaikan produk yang akan tampil sesuai dengan kebutuhan marketing penjualan.

## Scope

- Melihat daftar produk yang sedang tampil pada aplikasi mobile
- Menambahkan produk yang akan tampil pada aplikasi mobile
- Mengubah produk yang ditampilkan pada aplikasi mobile
- Mengaktifkan atau menonaktifkan produk yang ditampilkan pada aplikasi mobile

## Acceptance Criteria

### List Data

- Dapat menampilkan semua produk yang pernah ditambahkan menjadai produk yang tampil pada aplikasi mobile | berarti get all + pagination aja??
- Data yang tampil sesuai dengan filter yang diinputkan | filternya apa aja??
- Dapat melakukan pencarian data menggunakan fitur Search, berdasarkan nama produk (bundling) | tambahkan query 'search' atau 'keyword' menyesuaikan fe nya

### Tambah

- Dapat menambahkan produk baru untuk tampil di aplikasi mobile | **tambahin data ke TABLE iklan_produk terus kolom id_bundling nya itu ngambil dari id_bundling_ecommerce di db produk kan??**
- Produk yang sudah pernah ditambahkan tidak dapat ditambahkan ulang (unique by id_bundling) | **noted**.
- Hanya dapat menambahkan 2 produk dengan status aktif dan tanggal awal tayang & tanggal akhir tayang pada periode yang sama atau saling beririsan. | **noted, maksimal 2 beririsan**
- Produk yang sudah melewati tanggal_awal dan tanggal_akhir penjualan tidak dapat dipilih. | **maksudnya dipilih disini tuh gmna?? siapa yang milih? bukannya otomatis terpilih tampil ke mobile kalo masih ada di periode awal dan akhir publishnya**
- Jika terdapat penambahan produk aktif tanggal tampil = 01 Agustus 2026 - 31 Agustus 2026. Namun sedang ada 2 produk aktif yang tampil pada tanggal 01 Juli 2026 - 15 Agustus 2026, maka tidak dapat menambahkan produk tersebut sebagai produk aktif. | **Tapi tetep bisa masuk ke db kan?? cuman gk tampil aja ke pengguna?? seandainya ada 3 produk ditambahkan di periode 01 Agustus 2026 - 31 Agustus 2026 maka nanti 2 kandidat yang diambil dari 3 produk itu yang mana?? atau throw error ketika menambahkan produk dengan periode yang beririsan >= 2 produk ditanggal yang sama?? Jadi wajib memilih periode dengan tanggal yang tidak beririsan .**
  Muncul message error : "Sedang ada produk {{NAMA_PRODUK_1}} & {{NAMA_PRODUK_2}} yang tampil pada tanggal {{TANGGAL_AWAL_TAMPIL}} - {{TANGGAL_AKHIR_TAMPIL}} silahkan pilih periode tanggal yang lain" | **Ini paling harus ngasih tau masing masing produk tampil di tanggal berapa, gk hanya ada 1 varibel aja biar lebih jelas ke user .**
- Jika terdapat penambahan produk aktif tanggal tampil = 01 Agustus 2026 - 31 Agustus 2026. Namun sedang ada 2 produk aktif dengan tanggal tampil yang beririsan, maka tidak dapat menambahkan produk tersebut sebagai produk aktif. | **Ini dah pasti sama kah tanggal 2 produk itu?? Secara logika bisa aja beda, misal produk 1 itu dari 01 Agustus 2026 - 15 Agustus 2026 dan produk 2 01 Agustus 2026 - 31 Agustus 2026 maka secara logika admin bisa menambahkan produk ke 3 di tanggal 16 Agustus 2026 - 31 Agustus 2026 karena di periode ini hanya ada produk 2 yang aktif .**
  Muncul message error : "Sedang ada produk {{NAMA_PRODUK_1}} dan {{NAMA_PRODUK_2}} yang tampil pada periode yang dipilih. Silakan pilih periode tanggal yang lain" | **Ini pointnya sama kaya yang diatas kan**
- Jika produk yang dipilih (berdasarkan id_bundling) sudah pernah ditambahkan namun statusnya Tidak Aktif, karena tanggal tayang sudah terlewat, maka tidak dapat menambahkan kembali produk tersebut dengan periode tanggal tayang berbeda. | **Status ini dinamis by tanggal tayang atau ada kolom khusus status?? di Update skema DDL nya belum ada status soalnya . Kalo nambah status, maka ada status apa aja?? AKTIF | TIDAK_AKTIF . Itu aja dua? as ENUM atau varchar? .**
  Muncul message error: "Produk {{NAMA_PRODUK}} sudah pernah tampil, jika ingin menampilkan kembali produk tersebut silahkan ubah Status, Tanggal Awal Tampil, dan Tanggal AKhir Tampil".

## Update Schema

```sql
CREATE TABLE iklan_produk (
 id serial4 NOT NULL,
	id_bundling int4 NOT NULL,
	id_kategori int4 NULL,
  tahun_ajaran varchar NOT NULL,
  tanggal_awal_publish timestamptz NOT NULL,
  tanggal_akhir_publish timestamptz NOT NULL,
	CONSTRAINT bundling_ecommerce_pkey PRIMARY KEY (id),
	CONSTRAINT kategori_ecommerce_fkey FOREIGN KEY (id_kategori) REFERENCES kategori_ecommerce(id) ON DELETE SET NULL,
	CONSTRAINT t_bundling_fk FOREIGN KEY (id_bundling) REFERENCES t_bundling(c_id_bundling) ON DELETE CASCADE ON UPDATE CASCADE
);
```

## 1. Create Tambah Iklan Produk

- path [POST] api/v1/ecommerce/dashboard/iklan-produk
- body:
  ```json
  ```

## 2. List Iklan Produk

- path [GET] api/v1/ecommerce/dashboard/iklan-produk
- params:
  ```json
  ```

## 3. Edit Iklan Produk

- path [PATCH] api/v1/ecommerce/dashboard/iklan-produk/{id}
- body:
  ```json
  ```

## 4. Delete Iklan Produk

- path [DELETE] api/v1/ecommerce/dashboard/iklan-produk/{id}
