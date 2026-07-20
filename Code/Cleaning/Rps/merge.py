import pandas as pd

# ---------- paths ----------
PATH_TELU = "D:\MAIN DATA\Documents\Semester 6\KP BRIN\Dataset\TeluJakarta\Clean\Dataset_CLO_OBE_SI_TelUJakarta.xlsx"
PATH_PARAPHRASE = "D:\MAIN DATA\Documents\Semester 6\KP BRIN\Dataset\Telu Surabaya\clo_grouped_paraphrase_merged_1.xlsx"
PATH_ITS = "D:\MAIN DATA\Documents\Semester 6\KP BRIN\Dataset\ITS\ITS_SI_BRIN.xlsx"
OUTPUT_PATH = r"D:\MAIN DATA\Documents\Semester 6\KP BRIN\Code\Cleaning\Rps\Merged_CLO_Dataset.xlsx"

# ---------- load ----------
df1 = pd.read_excel(PATH_TELU, sheet_name="Dataset CLO + Skills")
ringkasan = pd.read_excel(PATH_TELU, sheet_name="Ringkasan MK")
skill_catalogue = pd.read_excel(PATH_TELU, sheet_name="Skill Catalogue")
df3 = pd.read_excel(PATH_PARAPHRASE)
df2 = pd.read_excel(PATH_ITS)

# ---------- clean: forward-fill merged cells from Excel ----------
merge_cols_1 = ["No", "Kode MK", "Nama Mata Kuliah", "SKS", "Semester"]
df1[merge_cols_1] = df1[merge_cols_1].ffill()

merge_cols_2 = ["Kode MK", "Nama Mata Kuliah"]
df2[merge_cols_2] = df2[merge_cols_2].ffill()

# ---------- 1) CLO_Skills_Base (master, apa adanya) ----------
clo_skills_base = df1.copy()

# ---------- 2) CLO_Paraphrase_Detail (filter ke course yang overlap Tel-U) ----------
# Alias manual: nama mata kuliah yang sama tapi penulisannya beda dikit antar file
# (bukan fuzzy-match otomatis, biar gak salah nyocokin ke MK yang beda konten)
NAME_ALIASES = {
    "Data Warehouse dan Business Intelligence": "Data Warehouse & Business Intelligence",
    "Tata Kelola dan Manajemen Teknologi Informasi": "Tata Kelola dan Managemen Teknologi Informasi",
}
df3["Mata Kuliah"] = df3["Mata Kuliah"].replace(
    {v: k for k, v in NAME_ALIASES.items()}
)

telu_courses = set(df1["Nama Mata Kuliah"].unique())
paraphrase_courses = set(df3["Mata Kuliah"].unique())
overlap_courses = telu_courses & paraphrase_courses

clo_paraphrase_detail = df3[df3["Mata Kuliah"].isin(overlap_courses)].copy()
clo_paraphrase_detail = clo_paraphrase_detail.rename(
    columns={"Mata Kuliah": "Nama Mata Kuliah"}
)

# ---------- 3) Course_Enriched (level-course merge) ----------
# Aggregate paraphrase CLO jadi satu blok teks per mata kuliah
paraphrase_agg = (
    clo_paraphrase_detail.groupby("Nama Mata Kuliah")
    .agg(
        jumlah_clo_paraphrase=("CLO-ID", "count"),
        clo_paraphrase_gabungan=(
            "clo_paraphrase",
            lambda x: " || ".join(str(t) for t in x.dropna()),
        ),
    )
    .reset_index()
)

# Ringkasan MK (skill summary per course) sebagai basis kolom kiri
course_enriched = ringkasan.merge(
    paraphrase_agg, on="Nama Mata Kuliah", how="left"
)
course_enriched["punya_paraphrase"] = course_enriched["jumlah_clo_paraphrase"].notna()
course_enriched["jumlah_clo_paraphrase"] = course_enriched[
    "jumlah_clo_paraphrase"
].fillna(0).astype(int)
course_enriched["clo_paraphrase_gabungan"] = course_enriched[
    "clo_paraphrase_gabungan"
].fillna("")

# ---------- 4) Skill_Catalogue (apa adanya) ----------
skill_catalogue_out = skill_catalogue.copy()

# ---------- 5) ITS_Reference (apa adanya, cleaned) ----------
its_reference = df2.copy()

# ---------- 6) ONE_SHEET: gabungin semua ke 1 sheet, format long, kolom 'source' ----------
def prep(df, source, rename_map, keep_cols):
    d = df.rename(columns=rename_map).copy()
    d["source"] = source
    for c in keep_cols:
        if c not in d.columns:
            d[c] = pd.NA
    return d[["source"] + keep_cols]

UNIFIED_COLS = [
    "kode_mk", "nama_mk", "sks", "semester",
    "clo_code", "clo_description", "clo_paraphrase",
    "bloom_taxonomy", "plo_supported",
    "skill_domain", "skill_technical", "skill_cognitive",
    "jumlah_clo_paraphrase",
]

part_skills = prep(
    clo_skills_base, "TelU_CLO_Skill",
    {
        "Kode MK": "kode_mk", "Nama Mata Kuliah": "nama_mk", "SKS": "sks",
        "Semester": "semester", "CLO Code": "clo_code",
        "CLO Description": "clo_description", "Bloom Taxonomy": "bloom_taxonomy",
        "PLO Supported": "plo_supported", "Skill Domain": "skill_domain",
        "Skill Technical": "skill_technical", "Skill Cognitive": "skill_cognitive",
    },
    UNIFIED_COLS,
)

part_paraphrase = prep(
    clo_paraphrase_detail, "TelU_CLO_Paraphrase",
    {
        "Nama Mata Kuliah": "nama_mk", "CLO-ID": "clo_code",
        "clo_paraphrase": "clo_paraphrase", "full_clo_text": "clo_description",
    },
    UNIFIED_COLS,
)

part_course = prep(
    course_enriched, "TelU_Course_Summary",
    {
        "Kode MK": "kode_mk", "Nama Mata Kuliah": "nama_mk", "SKS": "sks",
        "Semester": "semester", "Skill Domain": "skill_domain",
        "Technical Skills": "skill_technical", "Deskripsi": "clo_description",
        "clo_paraphrase_gabungan": "clo_paraphrase",
        "jumlah_clo_paraphrase": "jumlah_clo_paraphrase",
    },
    UNIFIED_COLS,
)

part_its = prep(
    its_reference, "ITS_Raw",
    {
        "Kode MK": "kode_mk", "Nama Mata Kuliah": "nama_mk",
        "Kode CLO": "clo_code",
        "Deskripsi Capaian Pembelajaran Mata Kuliah (CLO)": "clo_description",
    },
    UNIFIED_COLS,
)

part_catalogue = prep(
    skill_catalogue_out, "TelU_Skill_Catalogue",
    {
        "Skill Domain": "skill_domain", "Technical Skill": "skill_technical",
        "Jumlah CLO": "jumlah_clo_paraphrase", "Mata Kuliah": "nama_mk",
    },
    UNIFIED_COLS,
)

all_in_one = pd.concat(
    [part_skills, part_paraphrase, part_course, part_its, part_catalogue],
    ignore_index=True,
)

# ---------- write output ----------
import os

os.makedirs("/mnt/user-data/outputs", exist_ok=True)

with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
    all_in_one.to_excel(writer, sheet_name="All_Data_Combined", index=False)

# ---------- report ----------
print(f"Total course Tel-U (file 1): {len(telu_courses)}")
print(f"Total course paraphrase (file 3): {len(paraphrase_courses)}")
print(f"Overlap (di-enrich): {len(overlap_courses)}")
print(f"Total baris di 1 sheet gabungan: {len(all_in_one)}")
print(all_in_one['source'].value_counts())
print(f"\nOutput tersimpan di: {OUTPUT_PATH}")