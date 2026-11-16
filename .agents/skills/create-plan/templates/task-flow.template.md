---
task_id: "XX"
title: "<Nama Flow Fitur>"
type: "endpoint-flow"
status: "TODO" # TODO | IN_PROGRESS | DONE
services:
  - <service-data>
  - <proxy-bff>
---

# Task XX: <Nama Flow Fitur>

## 🎯 1. Scope & Flow Endpoint
Task ini mencakup 1 kesatuan flow dari data service sampai ke proxy/BFF:
- **Service Data (`<repo-data>`)**: `<path-file-service-data>` (Method: `...`)
- **BFF / Proxy (`<repo-bff>`)**: `<path-file-controller/service-bff>` (Route: `GET /api/v1/...`)
- **Downstream Consumers**: Web Superapp / Mobile / Dashboard Admin

## 💡 2. Business Logic & Contract Changes
- Penjelasan logika bisnis dan penanganan data.
- Payload request & response contract (additive-only, tipe data, bigint safe).

## 🛠️ 3. Implementation Steps
- [ ] **Data Service**:
  - [ ] Update / buat query di `<file-data-service>`.
  - [ ] Build & typecheck service data.
- [ ] **BFF Proxy**:
  - [ ] Update / routing handler di `<file-proxy>`.
  - [ ] Build & typecheck BFF proxy.

## 🧪 4. Testing & Verification Plan (Sanity Check)

### A. Skenario & Data Empiris
1. **Case 1: <Skenario Normal / Validasi Data>**:
   - Sample ID DB: `...`
   - Request Curl:
     ```bash
     curl -X GET "http://localhost:<PORT>/api/v1/..."
     ```
   - Expected Output:
     - Status: `200 OK`
     - Nilai numerik/field valid (bukan array kosong palsu): `...`

### B. Sanity Check Hirarki Data (Jika Terkait Akumulasi)
- [ ] $\sum \text{Child/Detail} == \text{Parent/Summary}$
- [ ] Tidak ada duplikasi / loop counting salah.

### C. Build Verification (Tanpa Lint)
```bash
npm --prefix /home/broy/work/<repo-data> run build
npm --prefix /home/broy/work/<repo-bff> run build
```

### D. Execution Log (Diisi Saat Eksekusi)
- [ ] Status: `PENDING / PASS / FAIL`
- [ ] Tanggal Uji: `...`
- [ ] Output Ringkas: `...`
