#!/usr/bin/env bash
# ==============================================================================
# Script Smoke Test cURL: GET /icons/master/posisi-jabatan (findAll)
# Target Default: Gateway go-superapp-api di port 3800
# Sesuai SOP Migrasi SO: Clean schema v2, no legacy aliases, raw query verified.
# ==============================================================================

set -uo pipefail

# Warna terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Konfigurasi Target URL (default gateway port 3800)
BASE_URL="${GATEWAY_URL:-http://localhost:3800/api/v1/icons/master/jabatan-posisi}"

echo -e "${BOLD}${CYAN}====================================================================${NC}"
echo -e "${BOLD}${CYAN}  SMOKE TEST cURL: GET /icons/master/jabatan-posisi (findAll)      ${NC}"
echo -e "${BOLD}${CYAN}  Target Base URL: ${YELLOW}${BASE_URL}${NC}"
echo -e "${BOLD}${CYAN}====================================================================${NC}\n"

# Helper function untuk cek ketersediaan jq
HAS_JQ=0
if command -v jq &> /dev/null; then
  HAS_JQ=1
fi

run_test() {
  local test_num="$1"
  local test_name="$2"
  local query_params="$3"
  local full_url="${BASE_URL}"

  if [ -n "$query_params" ]; then
    full_url="${BASE_URL}?${query_params}"
  fi

  echo -e "${BOLD}${YELLOW}--------------------------------------------------------------------${NC}"
  echo -e "${BOLD}Test #${test_num}: ${GREEN}${test_name}${NC}"
  echo -e "${CYAN}Query Params:${NC} ${query_params:-'(None - Default)'}"
  echo -e "${CYAN}cURL Command:${NC}"
  echo -e "  curl -s \"${full_url}\""
  echo -e "${YELLOW}Response:${NC}"

  # Eksekusi cURL dengan penangkapan HTTP status code
  local response
  local http_code
  response=$(curl -s -w "\n%{http_code}" "${full_url}")
  http_code=$(echo "$response" | tail -n1)
  local body
  body=$(echo "$response" | sed '$d')

  if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    echo -e "Status HTTP: ${GREEN}${http_code} OK${NC}"
  else
    echo -e "Status HTTP: ${RED}${http_code} ERROR${NC}"
  fi

  if [ "$HAS_JQ" -eq 1 ]; then
    # Jika ada jq, tampilkan summary ringkas dan preview
    local is_json
    if echo "$body" | jq empty 2>/dev/null; then
      local total_count
      local page
      local per_page
      local data_length

      total_count=$(echo "$body" | jq -r '.metadata.total_count // .total_data // "N/A"')
      page=$(echo "$body" | jq -r '.metadata.page // "N/A"')
      per_page=$(echo "$body" | jq -r '.metadata.per_page // "N/A"')
      data_length=$(echo "$body" | jq -r '.data | length // 0')

      echo -e "Summary: [Total: ${BOLD}${total_count}${NC} | Rows Diterima: ${BOLD}${data_length}${NC} | Page: ${page} | Per Page: ${per_page}]"
      echo -e "${CYAN}Preview 1 Data Pertama:${NC}"
      echo "$body" | jq -r '.data[0] // "Data kosong []"'
    else
      echo "$body"
    fi
  else
    echo "$body"
  fi
  echo ""
}

# Menu Skenario Test
declare -A TEST_CASES=(
  [1]="Default Pagination (page=1, per_page=10)|page=1&per_page=10"
  [2]="Custom Pagination (page=2, per_page=3)|page=2&per_page=3"
  [3]="Filter Keyword Deskripsi (keyword=Staf)|keyword=Staf&page=1&per_page=5"
  [4]="Filter Keyword Kode (keyword=11)|keyword=11&page=1&per_page=5"
  [5]="Filter Status Aktif (is_aktif=true)|is_aktif=true&page=1&per_page=5"
  [6]="Filter Status Non-Aktif (is_aktif=false)|is_aktif=false&page=1&per_page=5"
  [7]="Filter Level Jabatan ID (level_jabatan_id=4)|level_jabatan_id=4&page=1&per_page=5"
  [8]="Filter Bidang ID (bidang_id=12)|bidang_id=12&page=1&per_page=5"
  [9]="Filter Upline / Atasan Langsung (upline=1)|upline=1&page=1&per_page=5"
  [10]="Filter Kode Cakupan PUSAT (cakupan=PUSAT)|cakupan=PUSAT&page=1&per_page=5"
  [11]="Filter Kode Cakupan CABANG (cakupan=CABANG)|cakupan=CABANG&page=1&per_page=5"
  [12]="Filter Master Cakupan ID (master_cakupan_id=1)|master_cakupan_id=1&page=1&per_page=5"
  [13]="Filter Exclude IDs (exclude_ids=1,2,3)|exclude_ids=1,2,3&page=1&per_page=5"
  [14]="Sorting Ascending Deskripsi (order_by=deskripsi&sort=asc)|order_by=deskripsi&sort=asc&page=1&per_page=5"
  [15]="Sorting Descending ID (order_by=jabatan_posisi_id&sort=desc)|order_by=jabatan_posisi_id&sort=desc&page=1&per_page=5"
  [16]="All Data Tanpa Pagination (is_all_data=true)|is_all_data=true"
  [17]="Kombinasi Multi-Filter (is_aktif=true & cakupan=PUSAT & page=1 & per_page=3)|is_aktif=true&cakupan=PUSAT&page=1&per_page=3"
)

TARGET_ARG="${1:-all}"

if [ "$TARGET_ARG" == "all" ]; then
  for i in $(seq 1 17); do
    IFS="|" read -r t_name t_query <<< "${TEST_CASES[$i]}"
    run_test "$i" "$t_name" "$t_query"
  done
elif [[ "$TARGET_ARG" =~ ^[0-9]+$ ]] && [ "$TARGET_ARG" -ge 1 ] && [ "$TARGET_ARG" -le 17 ]; then
  IFS="|" read -r t_name t_query <<< "${TEST_CASES[$TARGET_ARG]}"
  run_test "$TARGET_ARG" "$t_name" "$t_query"
else
  echo -e "${RED}Argumen tidak valid: ${TARGET_ARG}${NC}"
  echo "Penggunaan:"
  echo "  $0        -> Jalankan semua test (1-17)"
  echo "  $0 all    -> Jalankan semua test (1-17)"
  echo "  $0 <1-17> -> Jalankan nomor test spesifik"
  echo "  GATEWAY_URL=http://localhost:3800/api/v1/icons/master/jabatan-posisi $0"
  exit 1
fi

echo -e "${BOLD}${GREEN}====================================================================${NC}"
echo -e "${BOLD}${GREEN}  Smoke Test Selesai.                                              ${NC}"
echo -e "${BOLD}${GREEN}====================================================================${NC}"
