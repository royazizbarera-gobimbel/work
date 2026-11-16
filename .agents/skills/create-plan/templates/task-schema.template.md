---
task_id: "XX"
title: "Perubahan Skema / DDL Database <nama-tabel>"
type: "schema"
status: "TODO" # TODO | IN_PROGRESS | DONE
services:
  - <service-data>
---
# Task XX: Perubahan Skema / DDL Database `<nama-tabel>`

## 🎯 1. Target Database & DDL File

- **Service Data**: `<service-data>`
- **Database Target**: `<db-name>`
- **File DDL SQL**: [`tasks/ddl-task-XX-<nama>.sql`](<tasks/ddl-task-XX-<nama>.sql>)

> [!IMPORTANT]
> DDL HANYA BOLEH DIEKSEKUSI DI DBEAVER OLEH USER BROY. AI DILARANG MENJALANKAN DDL ATAU PRISMA MIGRATE.

## 🧪 2. Verification

1. **Verifikasi DB Manual (DBeaver / Script RO)**:
   - Pastikan tabel/kolom sudah terbentuk di DBeaver atau cek via:
     ```bash
     docs-go-roy/scripts/go-psql-ro.sh <service-data> -c "\d <nama_tabel>"
     ```
2. **Sinkronisasi Prisma & Build**:
   ```bash
   npx --prefix /home/broy/work/<service-data> prisma db pull
   npx --prefix /home/broy/work/<service-data> prisma generate
   npm --prefix /home/broy/work/<service-data> run build
   ```

### Execution Log (Diisi Saat Eksekusi)

- [ ] Status: `PENDING / PASS / FAIL`
- [ ] Catatan: `...`
