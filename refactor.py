import os
import shutil
import re

# Base paths
ROOT_DIR = r"D:\MAIN DATA\Documents\Semester 6\KP BRIN"
SRC_DIR = os.path.join(ROOT_DIR, "src")
KPBRIN_DIR = os.path.join(SRC_DIR, "kpbrin")
SCRIPTS_DIR = os.path.join(SRC_DIR, "scripts")

# Directories to create
DIRS_TO_CREATE = [
    KPBRIN_DIR,
    os.path.join(KPBRIN_DIR, "data"),
    os.path.join(KPBRIN_DIR, "data", "cleaning"),
    os.path.join(KPBRIN_DIR, "core"),
    os.path.join(KPBRIN_DIR, "xai"),
    os.path.join(KPBRIN_DIR, "skill_gap"),
    os.path.join(KPBRIN_DIR, "prototype"),
    SCRIPTS_DIR,
    os.path.join(SCRIPTS_DIR, "experiments"),
    os.path.join(SCRIPTS_DIR, "batch")
]

for d in DIRS_TO_CREATE:
    os.makedirs(d, exist_ok=True)

# Create __init__.py files
init_dirs = [
    KPBRIN_DIR,
    os.path.join(KPBRIN_DIR, "data"),
    os.path.join(KPBRIN_DIR, "data", "cleaning"),
    os.path.join(KPBRIN_DIR, "core"),
    os.path.join(KPBRIN_DIR, "xai"),
    os.path.join(KPBRIN_DIR, "skill_gap"),
    os.path.join(KPBRIN_DIR, "prototype")
]
for d in init_dirs:
    init_path = os.path.join(d, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write("")

# Move definitions
MOVES = [
    # Data
    (os.path.join(SRC_DIR, "Cleaning"), os.path.join(KPBRIN_DIR, "data", "cleaning")),
    (os.path.join(SRC_DIR, "RankingJob", "parse_input.py"), os.path.join(KPBRIN_DIR, "data", "parse_input.py")),
    (os.path.join(SRC_DIR, "RankingJob", "sub_clo.py"), os.path.join(KPBRIN_DIR, "data", "sub_clo.py")),
    (os.path.join(SRC_DIR, "RankingJob", "build_sub_clo_profiles.py"), os.path.join(KPBRIN_DIR, "data", "build_sub_clo_profiles.py")),
    (os.path.join(SRC_DIR, "RankingJob", "feature_engineering.py"), os.path.join(KPBRIN_DIR, "data", "feature_engineering.py")),
    (os.path.join(SRC_DIR, "generate_dummy_students.py"), os.path.join(KPBRIN_DIR, "data", "generate_dummy_students.py")),
    
    # Core
    (os.path.join(SRC_DIR, "RankingJob", "full_pipeline.py"), os.path.join(KPBRIN_DIR, "core", "full_pipeline.py")),
    (os.path.join(SRC_DIR, "RankingJob", "embedding_cache.py"), os.path.join(KPBRIN_DIR, "core", "embedding_cache.py")),
    (os.path.join(SRC_DIR, "RankingJob", "issuer_tiers.py"), os.path.join(KPBRIN_DIR, "core", "issuer_tiers.py")),
    
    # XAI
    (os.path.join(SRC_DIR, "Explainable AI"), os.path.join(KPBRIN_DIR, "xai")),
    
    # Skill Gap
    (os.path.join(SRC_DIR, "Skill Gap"), os.path.join(KPBRIN_DIR, "skill_gap")),
    
    # Prototype
    (os.path.join(SRC_DIR, "prototype"), os.path.join(KPBRIN_DIR, "prototype")),
    
    # Experiments
    (os.path.join(SRC_DIR, "run_eks08_cert_impact.py"), os.path.join(SCRIPTS_DIR, "experiments", "run_eks08_cert_impact.py")),
    (os.path.join(SRC_DIR, "run_eks09_dice_cert_impact.py"), os.path.join(SCRIPTS_DIR, "experiments", "run_eks09_dice_cert_impact.py")),
    (os.path.join(SRC_DIR, "run_eks10_all_students.py"), os.path.join(SCRIPTS_DIR, "experiments", "run_eks10_all_students.py")),
    (os.path.join(SRC_DIR, "run_eks11_real_cert_impact.py"), os.path.join(SCRIPTS_DIR, "experiments", "run_eks11_real_cert_impact.py")),
    (os.path.join(SRC_DIR, "run_experiments.py"), os.path.join(SCRIPTS_DIR, "experiments", "run_experiments.py")),
    (os.path.join(SRC_DIR, "run_xai_experiments.py"), os.path.join(SCRIPTS_DIR, "experiments", "run_xai_experiments.py")),
    (os.path.join(SRC_DIR, "run_xai_experiments_v2.py"), os.path.join(SCRIPTS_DIR, "experiments", "run_xai_experiments_v2.py")),
    (os.path.join(SRC_DIR, "run_xai_experiments_v3.py"), os.path.join(SCRIPTS_DIR, "experiments", "run_xai_experiments_v3.py")),
    (os.path.join(SRC_DIR, "format_eks11.py"), os.path.join(SCRIPTS_DIR, "experiments", "format_eks11.py")),
    
    # Batch
    (os.path.join(SRC_DIR, "batch_process_students.py"), os.path.join(SCRIPTS_DIR, "batch", "batch_process_students.py")),
    (os.path.join(SRC_DIR, "batch_run_evaluations.py"), os.path.join(SCRIPTS_DIR, "batch", "batch_run_evaluations.py")),
    (os.path.join(SRC_DIR, "dump_shap_input.py"), os.path.join(SCRIPTS_DIR, "batch", "dump_shap_input.py"))
]

for src_path, dst_path in MOVES:
    if os.path.exists(src_path):
        if os.path.isdir(src_path) and os.path.isdir(dst_path):
            # Move contents of src to dst
            for item in os.listdir(src_path):
                s = os.path.join(src_path, item)
                d = os.path.join(dst_path, item)
                if os.path.exists(d):
                    if os.path.isdir(d):
                        shutil.rmtree(d)
                    else:
                        os.remove(d)
                shutil.move(s, dst_path)
            # Remove empty src dir
            try:
                os.rmdir(src_path)
            except:
                pass
        else:
            if os.path.exists(dst_path):
                if os.path.isdir(dst_path):
                    shutil.rmtree(dst_path)
                else:
                    os.remove(dst_path)
            shutil.move(src_path, dst_path)
            
print("Moves completed.")

# Now we need to update imports.
import_map = {
    # Core
    "from full_pipeline": "from kpbrin.core.full_pipeline",
    "import full_pipeline": "from kpbrin.core import full_pipeline",
    "from embedding_cache": "from kpbrin.core.embedding_cache",
    "import embedding_cache": "from kpbrin.core import embedding_cache",
    "from issuer_tiers": "from kpbrin.core.issuer_tiers",
    "import issuer_tiers": "from kpbrin.core import issuer_tiers",
    
    # Data
    "from parse_input": "from kpbrin.data.parse_input",
    "import parse_input": "from kpbrin.data import parse_input",
    "from sub_clo": "from kpbrin.data.sub_clo",
    "import sub_clo": "from kpbrin.data import sub_clo",
    "from build_sub_clo_profiles": "from kpbrin.data.build_sub_clo_profiles",
    "from feature_engineering": "from kpbrin.data.feature_engineering",
    
    # XAI
    "from shap_explain": "from kpbrin.xai.shap_explain",
    "from dice_explain": "from kpbrin.xai.dice_explain",
    "from explainability": "from kpbrin.xai.explainability",
    
    # Skill Gap
    "from skill_gap_analysis": "from kpbrin.skill_gap.skill_gap_analysis",
    "from baseline_keyword_matching": "from kpbrin.skill_gap.baseline_keyword_matching"
}

def replace_in_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    original = content
    for old_i, new_i in import_map.items():
        pattern = r'^\s*' + old_i + r'\b'
        content = re.sub(pattern, new_i, content, flags=re.MULTILINE)
        
    # Remove sys.path.append hacks
    content = re.sub(r'sys\.path\.append\(.*?RankingJob.*?\)\n?', '', content)
    content = re.sub(r'sys\.path\.append\(.*?Explainable AI.*?\)\n?', '', content)
    content = re.sub(r'sys\.path\.append\(.*?prototype.*?\)\n?', '', content)
    
    # App-specific overrides because streamlit runs from inside its dir or outside
    # We should rely on standard python packages (running as module or with proper PYTHONPATH)
    
    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

for root, dirs, files in os.walk(SRC_DIR):
    for file in files:
        if file.endswith(".py"):
            replace_in_file(os.path.join(root, file))

print("Imports updated.")

# Cleanup old directories if empty
for d in ["RankingJob", "Explainable AI", "Skill Gap", "Cleaning", "prototype"]:
    p = os.path.join(SRC_DIR, d)
    if os.path.exists(p):
        try:
            # os.rmdir only removes if empty
            os.rmdir(p) 
        except:
            pass
