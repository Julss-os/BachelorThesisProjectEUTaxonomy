import pandas as pd
import numpy as np
import random
from datetime import timedelta

df = pd.read_csv("/Users/juliafries/PycharmProjects/BachelorThesisProjectEuTaxonomy/conformance_pipeline/data/input/Production_Data.csv")

# Mapping of activites
# Activity → Battery Production Step
activity_to_step = {
    "Slurry Production": "Electrode Manufacturing – Slurry Mixing",
    "Coating": "Electrode Manufacturing – Coating",
    "Drying": "Electrode Manufacturing – Drying",
    "Calendering": "Electrode Manufacturing – Calendering",
    "Slitting": "Electrode Manufacturing – Slitting",
    "Notching": "Electrode Manufacturing – Notching",
    "Lamination and Stacking": "Cell Assembly – Stacking",
    "Electrolyte Injection": "Cell Assembly – Electrolyte Filling",
    "Formation": "Cell Finishing – Formation",
    "Aging": "Cell Finishing – Aging",
    "Degassing": "Cell Finishing – Degassing",
    "Battery Management System Attachment": "Module Assembly – BMS Integration",
    "Battery Pack Assembly": "Pack Assembly – Final Assembly",
    "Safe to Ship Battery": "Final QA – Safe to Ship"
}

# Part Desc → Battery Production Step (fallback)
part_to_step = {
    "Cable Head": "Module Assembly",
    "Flange": "Pack Assembly",
    "Plug": "Cell Assembly",
    "Connector": "Module Assembly",
    "Housing": "Cell Assembly",
    "Terminal": "Cell Assembly",
    "Lid": "Cell Assembly",
    "Clamp": "Cell Assembly",
    "Shell": "Pack Assembly",
    "Gauge": "Final Inspection / EOL Testing"
}

# sequence of battery production
battery_process_sequence = [
    "Electrode Manufacturing – Slurry Mixing",
    "Electrode Manufacturing – Coating",
    "Electrode Manufacturing – Drying",
    "Electrode Manufacturing – Calendering",
    "Electrode Manufacturing – Slitting",
    "Electrode Manufacturing – Notching",
    "Cell Assembly – Stacking",
    "Cell Assembly – Electrolyte Filling",
    "Cell Finishing – Formation",
    "Cell Finishing – Aging",
    "Cell Finishing – Degassing",
    "Module Assembly – BMS Integration",
    "Pack Assembly – Final Assembly",
    "Final QA – Safe to Ship"
]

# Filling machine and activity
step_to_activity = {v: k for k, v in activity_to_step.items()}
step_to_machine = {step: f"Machine {i+1}" for i, step in enumerate(battery_process_sequence)}

# assign correct battery production step
def assign_battery_step(row):
    act = str(row["Activity"]).split(" - ")[0].strip()
    if act in activity_to_step:
        return activity_to_step[act]
    elif row["Part Desc."] in part_to_step:
        return part_to_step[row["Part Desc."]]
    else:
        return "Unknown / Irrelevant"

df["Battery Production Step"] = df.apply(assign_battery_step, axis=1)

# Enrich log with missing battery production stepy
final_rows = []

for case_id, group in df.groupby("Case ID"):

    #sort and group
    group_sorted = group.sort_values("Start Timestamp")
    present_steps = set(group_sorted["Battery Production Step"])

    #check missing steps
    missing_steps = [step for step in battery_process_sequence if step not in present_steps]

    base_start = pd.to_datetime(group_sorted.iloc[0]["Start Timestamp"])
    enriched_rows = [group_sorted]

    #create new rows for missing steps and fills in
    for i, step in enumerate(missing_steps):
        new_row = group_sorted.iloc[0].copy()
        activity = step_to_activity[step]
        machine = step_to_machine[step]

        # generate time stamp
        start_time = base_start + timedelta(hours=(i + 1) * 2)
        complete_time = start_time + timedelta(minutes=random.randint(30, 90))
        duration = complete_time - start_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)


        new_row["Activity"] = f"{activity} - {machine}"
        new_row["Resource"] = new_row["Activity"]
        new_row["Battery Production Step"] = step
        new_row["Part Desc."] = "Battery Cell"
        new_row["Start Timestamp"] = start_time.strftime('%Y/%m/%d %H:%M:%S.000')
        new_row["Complete Timestamp"] = complete_time.strftime('%Y/%m/%d %H:%M:%S.000')
        new_row["Span"] = f"{int(hours):03d}:{int(minutes):02d}"
        new_row["Work Order  Qty"] = group_sorted.iloc[0]["Work Order  Qty"]
        new_row["Worker ID"] = group_sorted.iloc[0]["Worker ID"]
        new_row["Report Type"] = random.choice(['S', 'D'])

        qty_total = int(group_sorted.iloc[0]["Work Order  Qty"])
        qty_completed = random.randint(1, qty_total)
        remaining = qty_total - qty_completed
        qty_rejected = random.randint(0, min(remaining, 2))
        qty_for_mrb = remaining - qty_rejected

        new_row["Qty Completed"] = qty_completed
        new_row["Qty Rejected"] = qty_rejected
        new_row["Qty for MRB"] = qty_for_mrb
        new_row["Rework"] = random.choice(['Y', 'N'])

        enriched_rows.append(pd.DataFrame([new_row]))

    #connects new and old rows and saves it
    final_case_log = pd.concat(enriched_rows, ignore_index=True)
    final_rows.append(final_case_log)

# Safe final log
final_df = pd.concat(final_rows, ignore_index=True)
final_df.sort_values(by=["Case ID", "Start Timestamp"], inplace=True)
final_df.to_csv("/Users/juliafries/PycharmProjects/BachelorThesisProjectEuTaxonomy/conformance_pipeline/data/output/Production_Data_enrich_activities.csv", index=False)


print("Activity enriched Log is saved in conformance_pipeline/data/output/")