-- DDL untuk Task XX: <nama-tabel>
-- Eksekusi manual di DBeaver oleh User Broy pada environment target (staging/prod)

-- Tambah / Ubah kolom
ALTER TABLE <nama_tabel>
  ADD COLUMN IF NOT EXISTS <nama_kolom> <tipe_data> <default_or_nullable>;

-- Index (jika diperlukan)
CREATE INDEX IF NOT EXISTS <idx_nama> ON <nama_tabel>(<nama_kolom>);
