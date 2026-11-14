#!/usr/bin/env bash
# ==============================================================================
# Script Smoke Test cURL: PATCH /icons/master/posisi-jabatan/:id
# Target Default: Gateway go-superapp-api di port 3800
# Dilengkapi Snapshot Awal & Auto-Rollback/Restore ke Kondisi Semula
# Sesuai SOP Migrasi SO: Clean schema v2, Raw Query, Zero Legacy Aliases.
# ==============================================================================

set -uo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

BASE_URL="${GATEWAY_URL:-http://localhost:3800/api/v1/icons/master/jabatan-posisi}"
TARGET_ID="2"

echo -e "${BOLD}${CYAN}====================================================================${NC}"
echo -e "${BOLD}${CYAN}  SMOKE TEST cURL: PATCH /icons/master/jabatan-posisi/:id          ${NC}"
echo -e "${BOLD}${CYAN}  Target Base URL: ${YELLOW}${BASE_URL}${NC}"
echo -e "${BOLD}${CYAN}  Target Test ID : ${YELLOW}${TARGET_ID}${NC}"
echo -e "${BOLD}${CYAN}====================================================================${NC}\n"

HAS_JQ=0
if command -v jq &> /dev/null; then
  HAS_JQ=1
fi

# ------------------------------------------------------------------------------
# STEP 0: Ambil Snapshot Data Awal Sebelum Pengujian
# ------------------------------------------------------------------------------
echo -e "${BOLD}${CYAN}--------------------------------------------------------------------${NC}"
echo -e "${BOLD}Step 0: ${GREEN}Mengambil Snapshot Data Awal ID ${TARGET_ID} Sebelum Pengujian${NC}"

ORIGINAL_JSON=""
if [ "$HAS_JQ" -eq 1 ]; then
  ORIGINAL_JSON=$(curl -s "${BASE_URL}?is_all_data=true" | jq -c ".data[] | select(.jabatan_posisi_id == ${TARGET_ID})")
fi

if [ -n "$ORIGINAL_JSON" ] && [ "$ORIGINAL_JSON" != "null" ]; then
  ORIG_DESKRIPSI=$(echo "$ORIGINAL_JSON" | jq -r '.deskripsi')
  ORIG_KODE=$(echo "$ORIGINAL_JSON" | jq -r '.kode_jabatan_posisi')
  ORIG_LEVEL=$(echo "$ORIGINAL_JSON" | jq -r '.level_jabatan_id')
  ORIG_BIDANG=$(echo "$ORIGINAL_JSON" | jq -r '.bidang_id // empty')
  ORIG_AKTIF=$(echo "$ORIGINAL_JSON" | jq -r '.is_aktif')
  ORIG_UPLINE=$(echo "$ORIGINAL_JSON" | jq -r '.upline // empty')
  echo -e "Snapshot data awal berhasil diambil:"
  echo "$ORIGINAL_JSON" | jq .
else
  # Fallback nilai awal staging default jika query awal kosong
  ORIG_DESKRIPSI="Kepala Seksi Cabang Umum"
  ORIG_KODE="11"
  ORIG_LEVEL=4
  ORIG_BIDANG=""
  ORIG_AKTIF=true
  ORIG_UPLINE=1
  echo -e "${YELLOW}Menggunakan fallback snapshot awal staging:${NC}"
  echo "deskripsi=$ORIG_DESKRIPSI, level=$ORIG_LEVEL, aktif=$ORIG_AKTIF, upline=$ORIG_UPLINE"
fi
echo ""

# Helper function untuk restore
restore_data() {
  echo -e "\n${BOLD}${CYAN}--------------------------------------------------------------------${NC}"
  echo -e "${BOLD}Restore Hook: ${GREEN}Mengembalikan Data Posisi ID ${TARGET_ID} ke Kondisi Awal${NC}"

  local restore_payload
  if [ -z "$ORIG_BIDANG" ]; then
    ORIG_BIDANG="null"
  fi
  if [ -z "$ORIG_UPLINE" ]; then
    ORIG_UPLINE="null"
  fi

  restore_payload=$(cat <<EOF
{
  "deskripsi": "${ORIG_DESKRIPSI}",
  "kode_jabatan_posisi": "${ORIG_KODE}",
  "level_jabatan_id": ${ORIG_LEVEL},
  "bidang_id": ${ORIG_BIDANG},
  "is_aktif": ${ORIG_AKTIF},
  "upline": ${ORIG_UPLINE}
}
EOF
)

  echo -e "${CYAN}Restore Payload:${NC} ${restore_payload}"
  local res
  res=$(curl -s -w "\n%{http_code}" -X PATCH "${BASE_URL}/${TARGET_ID}" \
    -H "Content-Type: application/json" \
    -d "${restore_payload}")
  local code
  code=$(echo "$res" | tail -n1)

  if [ "$code" -ge 200 ] && [ "$code" -lt 300 ]; then
    echo -e "${BOLD}${GREEN}✔ RESTORE BERHASIL: Status HTTP ${code} OK.${NC}"
  else
    echo -e "${BOLD}${RED}✘ RESTORE GAGAL: Status HTTP ${code}.${NC}"
  fi
}

# Trap agar saat exit/interrupt selalu dilakukan restore
trap restore_data EXIT

run_patch_test() {
  local test_num="$1"
  local test_name="$2"
  local target_id="$3"
  local json_payload="$4"
  local expected_status="$5"
  local full_url="${BASE_URL}/${target_id}"

  echo -e "${BOLD}${YELLOW}--------------------------------------------------------------------${NC}"
  echo -e "${BOLD}Test #${test_num}: ${GREEN}${test_name}${NC}"
  echo -e "${CYAN}Target URL:${NC} ${full_url}"
  echo -e "${CYAN}Payload:${NC} ${json_payload}"
  echo -e "${CYAN}cURL Command:${NC}"
  echo -e "  curl -s -i -X PATCH \"${full_url}\" -H \"Content-Type: application/json\" -d '${json_payload}'"
  echo -e "${YELLOW}Response:${NC}"

  local response
  local http_code
  local body
  response=$(curl -s -w "\n%{http_code}" -X PATCH "${full_url}" \
    -H "Content-Type: application/json" \
    -d "${json_payload}")

  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')

  if [ "$http_code" -eq "$expected_status" ]; then
    echo -e "Status HTTP: ${GREEN}${http_code} (SESUAI TARGET: ${expected_status})${NC}"
  else
    echo -e "Status HTTP: ${RED}${http_code} (TIDAK SESUAI TARGET: ${expected_status})${NC}"
  fi

  if [ "$HAS_JQ" -eq 1 ]; then
    if echo "$body" | jq empty 2>/dev/null; then
      echo "$body" | jq .
    else
      echo "$body"
    fi
  else
    echo "$body"
  fi
  echo ""
}

# ------------------------------------------------------------------------------
# EKSEKUSI PENGUJIAN SKENARIO
# ------------------------------------------------------------------------------

# 1. Test 404 Target ID Not Found
run_patch_test 1 "Target ID Tidak Ditemukan (404 Not Found)" \
  "999999" \
  '{"deskripsi":"Posisi Tidak Ada"}' \
  404

# 2. Test 400 Self Upline Protection
run_patch_test 2 "Cegah Self-Upline (400 Bad Request)" \
  "${TARGET_ID}" \
  "{\"upline\":${TARGET_ID}}" \
  400

# 3. Test 400 Upline ID Tidak Ada di Database
run_patch_test 3 "Upline ID Tidak Ada di Database (400 Bad Request)" \
  "${TARGET_ID}" \
  '{"upline":999999}' \
  400

# 4. Test 400 Level Jabatan Tidak Ada
run_patch_test 4 "Level Jabatan ID Tidak Ada (400 Bad Request)" \
  "${TARGET_ID}" \
  '{"level_jabatan_id":999999}' \
  400

# 5. Test 400 Bidang ID Tidak Ada
run_patch_test 5 "Bidang ID Tidak Ada (400 Bad Request)" \
  "${TARGET_ID}" \
  '{"bidang_id":999999}' \
  400

# 6. Test 200 Sukses Partial Update Deskripsi Sementara
run_patch_test 6 "Sukses Partial Update Deskripsi (200 OK)" \
  "${TARGET_ID}" \
  '{"deskripsi":"Kepala Seksi Cabang Umum [TEST UJI COBA]"}' \
  200

# 7. Test 200 Sukses Update Upline dan is_aktif
run_patch_test 7 "Sukses Update Upline & is_aktif (200 OK)" \
  "${TARGET_ID}" \
  '{"upline":1,"is_aktif":true}' \
  200

# 8. Verifikasi GET data saat kondisi ter-update
echo -e "${BOLD}${YELLOW}--------------------------------------------------------------------${NC}"
echo -e "${BOLD}Test #8: ${GREEN}Verifikasi Hasil Update via GET /icons/master/posisi-jabatan?upline=1${NC}"
echo -e "${CYAN}cURL Command:${NC}"
echo -e "  curl -s \"${BASE_URL}?upline=1\""
echo -e "${YELLOW}Response Data Preview:${NC}"
if [ "$HAS_JQ" -eq 1 ]; then
  curl -s "${BASE_URL}?upline=1" | jq ".data[] | select(.jabatan_posisi_id == ${TARGET_ID})"
else
  curl -s "${BASE_URL}?upline=1"
fi
echo ""

echo -e "${BOLD}${GREEN}====================================================================${NC}"
echo -e "${BOLD}${GREEN}  Smoke Test Selesai. Masuk ke Tahap Restore Otomatis...           ${NC}"
echo -e "${BOLD}${GREEN}====================================================================${NC}"
