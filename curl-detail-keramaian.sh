#!/bin/bash

# Curl untuk drill-down detail Rencana Kegiatan ID 5275011 (Keramaian - MAS Ulumul Qur'An)
curl -s -G "http://localhost:3800/api/v1/bp-online/rencana-kegiatan-dengan-anggaran/list-detail" \
  --data-urlencode "tahun_ajaran=2026/2027" \
  --data-urlencode "acuan_kegiatan_id=2156" \
  --data-urlencode "nama_kegiatan=Keramaian - MAS Ulumul Qur\`An - 11 SMA - 12 SMA" \
  --data-urlencode "sekolah_id=0" \
  --data-urlencode "panen_id=11" \
  --data-urlencode "per_page=10" | jq .
