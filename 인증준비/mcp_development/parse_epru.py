import sys

def check_epru(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        docs = content.split("||")
        sch_docs = []
        pcb_docs = []
        for d in docs:
            if '"docType":"SCH"' in d:
                sch_docs.append(d)
            elif '"docType":"PCB"' in d:
                pcb_docs.append(d)
                
        print(f"Found {len(sch_docs)} SCH docs and {len(pcb_docs)} PCB docs in {file_path}.")
        
        if sch_docs:
            print("Schematic UUID:", sch_docs[0][:150]) # print start of json
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

check_epru("/tmp/temp.epru")
