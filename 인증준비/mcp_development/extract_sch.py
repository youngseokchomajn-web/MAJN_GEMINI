import sys, json

def extract_sch(file_path, output_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    docs = content.split("||")
    sch_doc = None
    for d in docs:
        if '"docType":"SCH"' in d:
            sch_doc = d
            break
            
    if sch_doc:
        # Save the exact json string
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sch_doc)
        print(f"Schematic extracted to {output_path}")
    else:
        print("No schematic found.")

extract_sch("/tmp/temp.epru", "/Users/youngseok/Desktop/majn/인증준비/mcp_development/Recovered_Schematic.json")
