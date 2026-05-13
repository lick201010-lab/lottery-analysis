#!/bin/bash
cd "$(dirname "$0")/.."
echo "Fetching latest MarkSix data from lottery.hk..."
/c/Users/Yvette/AppData/Local/Programs/Python/Python312/python.exe scripts/fetch_marksix.py
echo "Merging and recalculating stats..."
/c/Users/Yvette/AppData/Local/Programs/Python/Python312/python.exe scripts/merge_marksix.py
echo "Done! Latest draw: $(python3 -c "import json; d=json.load(open('frontend/public/data/draws.json')); print(d[0]['draw_number'], d[0]['draw_date'])")"
