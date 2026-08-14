import pandas as pd
import json

df = pd.read_csv(r'D:\MAIN DATA\Documents\Semester 6\KP BRIN\results\Eksperimen_XAI\EKS11_RealCertImpact\EKS11_Summary_AllStudents.csv')

lines = []
lines.append('# Hasil Eksperimen 11 (Matkul Saja vs Matkul + Sertifikat Real)')
lines.append('')
lines.append('Tabel berikut menunjukkan 5 rekomendasi pekerjaan teratas untuk tiap mahasiswa (berdasarkan Matkul saja), dan bagaimana posisi (rank) serta skor (score) pekerjaan tersebut berubah setelah sertifikat riil mahasiswa dimasukkan (Sertifikat diekstrak dari PDF asli/simulasi profil mahasiswa).')
lines.append('')

for student, group in df.groupby('student_name'):
    lines.append(f'### {student}')
    lines.append('| Rank (Saja) | Pekerjaan | Skor (Saja) | Rank (Certs) | Skor (Certs) | Kenaikan Skor |')
    lines.append('|---|---|---|---|---|---|')
    group = group.sort_values('rank_matkul_saja')
    for _, row in group.iterrows():
        rank_b = int(row['rank_matkul_saja'])
        rank_a = int(row['rank_matkul_dan_cert'])
        rank_a_str = str(rank_a) if rank_a > 0 else 'Out of Top 100'
        
        # Add visual indicator for rank jump
        if rank_a > 0 and rank_a < rank_b:
            rank_a_str = f'**{rank_a}** (Naik!)'
            
        score_b = f"{row['score_matkul_saja']:.3f}"
        score_a = f"{row['score_matkul_dan_cert']:.3f}"
        inc = f"{row['score_increase']:.3f}"
        if row['score_increase'] > 0:
            inc = f"**+{inc}** 🚀"
            
        lines.append(f"| {rank_b} | {row['job_title']} | {score_b} | {rank_a_str} | {score_a} | {inc} |")
    lines.append('')

with open(r'C:\Users\booma\.gemini\antigravity-ide\brain\72a7ea60-b9c8-4f9d-864e-f99e66f05e1e\eks11_real_cert_impact.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('Artifact created!')
