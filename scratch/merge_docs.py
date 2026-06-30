import os

# Paths to the artifacts
brain_dir = r"c:\Users\jamerson.jpd\.gemini\antigravity\brain\a085c6c7-d6f4-4d23-b5f0-c1675dab2c02"
files_to_merge = [
    os.path.join(brain_dir, "implementation_plan.md"),
    os.path.join(brain_dir, "db_impact_report.md"),
    os.path.join(brain_dir, "auditoria_naturezas_cad.md")
]

output_file = r"C:\Users\jamerson.jpd\Desktop\SENTINELA\Documentacao_Completa_SENTINELA.md"

with open(output_file, "w", encoding="utf-8") as outfile:
    outfile.write("# DOCUMENTAÇÃO COMPLETA - PROJETO SENTINELA\n\n")
    outfile.write("---\n\n")
    
    for fpath in files_to_merge:
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
                outfile.write("\n\n---\n\n")
        else:
            print(f"File not found: {fpath}")

print("Master document created at:", output_file)
