import pandas as pd
import matplotlib.pyplot as plt
import os

input_path = "/Users/juliafries/PycharmProjects/BachelorThesisProjectEuTaxonomy/data_analysis/data/input/FinalListConstraints.csv"
output_dir = "/Users/juliafries/PycharmProjects/BachelorThesisProjectEuTaxonomy/data_analysis/data/output"
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(input_path)

# climate goal distirbution (tabel)
climate_table = df["Constraint Category"].value_counts().reset_index()
climate_table.columns = ["Constraint Category", "Count"]
climate_table.to_csv(os.path.join(output_dir, "climate_goal_counts.csv"), index=False)

# constraint type count (tabel)
type_table = df["Model Type"].value_counts().reset_index()
type_table.columns = ["Model Type", "Count"]
type_table.to_csv(os.path.join(output_dir, "constraint_type_counts.csv"), index=False)

# Granularity count as Table
granularity_table = df["Granularity"].value_counts().reset_index()
granularity_table.columns = ["Granularity", "Count"]
granularity_table.to_csv(os.path.join(output_dir, "granularity_counts.csv"), index=False)

# process perpective diagram
def split_perspectives(value):
    if pd.isna(value):
        return []
    return [v.strip().lower() for v in str(value).split("/")]

df_exp = df.copy()
df_exp["Process_Perspective_Split"] = df_exp["Process Perspective"].apply(split_perspectives)
df_exploded = df_exp.explode("Process_Perspective_Split").reset_index(drop=True)

perspective_table = df_exploded["Process_Perspective_Split"].value_counts().reset_index()
perspective_table.columns = ["Process Perspective", "Count"]
perspective_table.to_csv(os.path.join(output_dir, "process_perspective_counts.csv"), index=False)

#  Process Perspective + Granularität diagram
def clean_string(s):
    if isinstance(s, str):
        return s.strip().lower().replace(" ", "")
    return ""

df["Granularity_clean"] = df["Granularity"].apply(clean_string).replace({"wihtin": "within"})
df["ProcessPerspective_clean"] = df["Process Perspective"].apply(clean_string)

df["Combined Type"] = df["ProcessPerspective_clean"].str.capitalize() + " (" + df["Granularity_clean"] + ")"
combined_type_table = df["Combined Type"].value_counts().reset_index()
combined_type_table.columns = ["Constraint Type", "Count"]
combined_type_table.to_csv(os.path.join(output_dir, "combined_constraint_type_counts.csv"), index=False)


plt.figure(figsize=(12, 6))
plt.bar(combined_type_table["Constraint Type"], combined_type_table["Count"], color="orange")
plt.xlabel("Constraint Classification (Process Perspective + Granularity)")
plt.ylabel("Number of Constraints")
plt.title("Distribution of Constraints by Normalized Type")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.savefig(os.path.join(output_dir, "constraint_distribution.png"), dpi=300)
plt.close()

# Diagramm: Lifecycle Phase + Event Log Availability
df["Combined_Category"] = df["Lifecycle Phase"] + " | " + df["Event Log Availability"]
combined_counts = df["Combined_Category"].value_counts().reset_index()
combined_counts.columns = ["Category", "Count"]

plt.figure(figsize=(10, 6))
plt.bar(combined_counts["Category"], combined_counts["Count"], color="orange")
plt.xlabel("Lifecycle Phase | Event Log Availability")
plt.ylabel("Number of Constraints")
plt.title("Constraint Distribution by Lifecycle Phase and Event Log Availability")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.savefig(os.path.join(output_dir, "lifecycle_event_log_distribution.png"), dpi=300)
plt.close()

