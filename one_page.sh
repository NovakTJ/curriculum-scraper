#!/bin/bash
mkdir -p ordered_text_page1_only
for file in ordered_text_old/*.txt; do
  out="ordered_text_page1_only/$(basename "$file")"
  awk '/^--- PAGE 1 ---/{flag=1; next} /^--- PAGE 2 ---/{flag=0} flag' "$file" > "$out"
done