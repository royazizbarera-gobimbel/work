#!/bin/bash

# Curl untuk drill-down detail Rencana Kegiatan ID 5279286 (freq: 3 Berulang)
curl -s -G "http://localhost:3800/api/v1/bp-online/rencana-kegiatan-dengan-anggaran/list-detail" \
  --data-urlencode "tahun_ajaran=2026/2027" \
  --data-urlencode "acuan_kegiatan_id=3165" \
  --data-urlencode "nama_kegiatan=Entri & Bundel SoRef Cabang (PR, UH, PTS, PAS, PAT, TKA, US) - T. Nyak Arif - -" \
  --data-urlencode "per_page=10" | jq .
