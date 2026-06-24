import json

with open('drc_329_raw.json', 'r') as f:
    d = json.load(f)

if 'data' not in d or not isinstance(d['data'], list):
    print("Invalid data")
    exit(1)

summary_counts = {}
for cat in d['data']:
    cat_name = cat.get('name')
    for item in cat.get('list', []):
        sub_type = item.get('title') or item.get('subType') or "Unknown"
        key = f"{cat_name} -> {sub_type}"
        
        # Count the number of actual errors in this group
        err_count = 0
        if 'list' in item:
            err_count = len(item['list'])
        elif 'errorList' in item:
            err_count = len(item['errorList'])
        elif 'items' in item:
            err_count = len(item['items'])
        else:
            err_count = 1
            
        if key not in summary_counts:
            summary_counts[key] = 0
        summary_counts[key] += err_count

with open('drc_329_summary.txt', 'w') as f:
    for k, v in summary_counts.items():
        f.write(f"{k}: {v} errors\n")

print("Saved to drc_329_summary.txt")
