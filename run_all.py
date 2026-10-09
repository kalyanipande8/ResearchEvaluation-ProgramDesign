"""End-to-end pipeline: simulate a 340-patient observational-study cohort,
generate a real auto-derived codebook, build a process map with real
attrition/timing metrics, and score the program against RE-AIM."""
import json
import os

from src.simulate_cohort import simulate
from src.codebook_generator import generate_codebook
from src.process_map import build_process_map
from src.evaluation_framework import score_re_aim

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("=== Simulating 340-patient observational health-study cohort ===")
df = simulate()
df.to_csv("data/cohort.csv", index=False)
print(df.shape)

print("\n=== Auto-generated data codebook ===")
codebook = generate_codebook(df)
codebook.to_csv("data/codebook.csv", index=False)
print(codebook[["variable", "dtype", "n_missing", "pct_missing"]])

print("\n=== Process map (funnel, timing, site attrition) ===")
process_map = build_process_map(df)
print(json.dumps(process_map, indent=2))
with open("results/process_map.json", "w") as f:
    json.dump(process_map, f, indent=2)

print("\n=== RE-AIM evaluation framework score ===")
re_aim = score_re_aim(df, process_map)
print(json.dumps(re_aim, indent=2))
with open("results/re_aim_score.json", "w") as f:
    json.dump(re_aim, f, indent=2)

summary = {
    "n_patients": len(df),
    "n_variables_documented": len(codebook),
    "overall_followup_completion_rate_pct": process_map["overall_followup_completion_rate_pct"],
    "re_aim_dimension_scores": re_aim["dimension_scores"],
    "overall_re_aim_score": re_aim["overall_re_aim_score"],
}
with open("results/summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n=== Summary ===")
print(json.dumps(summary, indent=2))
