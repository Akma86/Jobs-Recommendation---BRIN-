import pandas as pd
import re

combined_data = []

# =====================================================
# TELU SURABAYA
# =====================================================
try:
    df_ts = pd.read_excel(
        r"D:\MAIN DATA\Documents\Semester 6\KP BRIN\Dataset\Mata Kuliah\Telu Surabaya\TeluSurabaya.xlsx"
    )

    for _, row in df_ts.iterrows():

        course_name = str(row.get("Mata Kuliah", "")).strip()

        text = str(row.get("full_clo_text", ""))

        matches = re.findall(
            r'(\[CLO[^\]]+\])\s*Hasil:\s*([^|\n]+)',
            text
        )

        for code, desc in matches:
            combined_data.append({
                "course_name": course_name,
                "sub_clo_code": code.strip("[]"),
                "sub_clo_text": desc.strip(),
                "source_file": "TeluSurabaya.xlsx"
            })

    print("✓ TeluSurabaya.xlsx")

except Exception as e:
    print(f"✕ TeluSurabaya.xlsx : {e}")


# =====================================================
# ITS
# =====================================================
try:
    df_its = pd.read_excel(
        r"D:\MAIN DATA\Documents\Semester 6\KP BRIN\Dataset\Mata Kuliah\ITS\ITS_SI_BRIN.xlsx"
    )

    df_its["Nama Mata Kuliah"] = (
        df_its["Nama Mata Kuliah"]
        .ffill()
    )

    for _, row in df_its.iterrows():

        if (
            pd.notna(row["Kode CLO"])
            and pd.notna(
                row["Deskripsi Capaian Pembelajaran Mata Kuliah (CLO)"]
            )
        ):

            combined_data.append({
                "course_name": str(row["Nama Mata Kuliah"]).strip(),
                "sub_clo_code": str(row["Kode CLO"]).strip(),
                "sub_clo_text":
                    str(
                        row[
                            "Deskripsi Capaian Pembelajaran Mata Kuliah (CLO)"
                        ]
                    ).strip(),
                "source_file": "ITS_SI_BRIN.xlsx"
            })

    print("✓ ITS_SI_BRIN.xlsx")

except Exception as e:
    print(f"✕ ITS_SI_BRIN.xlsx : {e}")


# =====================================================
# TELU JAKARTA
# =====================================================
try:
    df_j = pd.read_excel(
        r"D:\MAIN DATA\Documents\Semester 6\KP BRIN\Dataset\Mata Kuliah\TeluJakarta\Clean\Dataset_CLO_OBE_SI_TelUJakarta.xlsx",
        sheet_name="Dataset CLO + Skills"
    )

    df_j["Nama Mata Kuliah"] = (
        df_j["Nama Mata Kuliah"]
        .ffill()
    )

    for _, row in df_j.iterrows():

        if (
            pd.notna(row["CLO Code"])
            and pd.notna(row["CLO Description"])
        ):

            combined_data.append({
                "course_name": str(row["Nama Mata Kuliah"]).strip(),
                "sub_clo_code": str(row["CLO Code"]).strip(),
                "sub_clo_text": str(row["CLO Description"]).strip(),
                "source_file":
                    "Dataset_CLO_OBE_SI_TelUJakarta.xlsx"
            })

    print("✓ Dataset_CLO_OBE_SI_TelUJakarta.xlsx")

except Exception as e:
    print(
        f"✕ Dataset_CLO_OBE_SI_TelUJakarta.xlsx : {e}"
    )


# =====================================================
# FINAL DATAFRAME
# =====================================================
df_final = pd.DataFrame(combined_data)

df_final = df_final.dropna(
    subset=[
        "course_name",
        "sub_clo_code",
        "sub_clo_text"
    ]
)

df_final = df_final.drop_duplicates(
    subset=[
        "course_name",
        "sub_clo_code",
        "sub_clo_text"
    ]
)

df_final = df_final.sort_values(
    ["course_name", "sub_clo_code"]
)

print("\n========== SUMMARY ==========")
print(f"Total rows : {len(df_final)}")
print(f"Total courses : {df_final['course_name'].nunique()}")
print("=============================")

output_file = "sub_clo_profiles.csv"

df_final.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print(f"\nSaved -> {output_file}")