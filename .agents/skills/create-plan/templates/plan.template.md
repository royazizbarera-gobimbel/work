---
ticket: <repo>#<nomor>
title: "<Judul Tiket>"
status: IN_PROGRESS
services:
  - <service-data>
  - <proxy-bff>
assignee: broy
created: YYYY-MM-DD HH:mm
updated: YYYY-MM-DD HH:mm
---

# [<repo>#<nomor>] <Judul Tiket>

**Nomor Issue**: `<repo>#<nomor>`
**Status Plan**: `APPROVED / IN_PROGRESS`

---

## 🌿 Rekomendasi Branch

> [!WARNING]
> Base Branch **SELALU DARI `main`**.
> AI **DILARANG MEMBUAT / SWITCH / CHECKOUT BRANCH SENDIRI**. Seluruh kendali Git (buat branch, switch, commit, push) 100% dilakukan manual oleh User Broy. AI hanya merekomendasikan nama branch dan langsung bekerja di branch yang disediakan/aktif dibuka oleh user.

| Repository | Base Branch | Rekomendasi Nama Branch | Catatan |
| :--- | :--- | :--- | :--- |
| `<service-data>` | `main` | `enh/<nomor>-<slug>` | User buat branch dari `main` |
| `<proxy-bff>` | `main` | `enh/<nomor>-<slug>` | User buat branch dari `main` |

---

## 🔌 1. Dependensi Service & Urutan Deploy

| Service | Port Lokal | Peran | Urutan Deploy |
| :--- | :--- | :--- | :--- |
| `<service-data>` | `30XX` | Data Source | 1 |
| `<proxy-bff>` | `38XX` | BFF Proxy | 2 |

---

## 📋 2. Index Task Implementasi

| No | File Task | Tipe | Scope / Flow | Status |
| :---: | :--- | :--- | :--- | :---: |
| 01 | [`tasks/01-schema-<nama>.md`](tasks/01-schema-<nama>.md) | Schema | DDL / Alter Table & Prisma Sync | `TODO` |
| 02 | [`tasks/02-<nama-flow>.md`](tasks/02-<nama-flow>.md) | Flow Endpoint | Data Service + BFF Proxy | `TODO` |

---

## 📌 3. Catatan Bisnis & Alignment Ringkas
- Ringkasan aturan bisnis utama tiket.
- Catatan alignment jika ada definisi rumus/metrik.
