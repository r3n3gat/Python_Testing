# tools/print_points.py
import json

with open("clubs.json", "r", encoding="utf-8") as f:
    clubs = json.load(f)["clubs"]

# tableau Markdown
print("| Club | Points |")
print("|------|--------|")
for c in clubs:
    print(f"| {c['name']} | {c['points']} |")
