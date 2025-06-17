import pandas as pd
import random
import numpy as np

log_file_path = "/Users/juliafries/PycharmProjects/BachelorThesisProjectEuTaxonomy/conformance_pipeline/data/output/Production_Data_cleaned_enrich_activities.csv"
log_df = pd.read_csv(log_file_path)

# Mapping of material numbers
activity_to_material = {
    'Turning & Milling': 'MAT-1007',
    'Slurry Production': 'MAT-2001',
    'Coating': 'MAT-2001',
    'Drying': 'MAT-1003',
    'Slitting': 'MAT-1003',
    'Notching': 'MAT-1003',
    'Lamination and Stacking': 'MAT-2002',
    'Cell Assembly': 'MAT-1010',
    'Electrolyte Injection': 'MAT-1004',
    'Formation': 'MAT-1001',
    'Aging': 'MAT-1001',
    'Degassing': 'MAT-1001',
    'Battery Management System Attachment': 'MAT-2003',
    'Battery Pack Assembly': 'MAT-1001',
    'Laser Marking': 'MAT-1001',
    'Lapping': 'MAT-1001',
    'Round Grinding': 'MAT-1001',
    'Final Inspection Q.C.': 'N/A',
    'Packing': 'N/A',
    'Safe to Ship Battery': 'N/A'
}

# fakr bom list with Substance, Compliance & Flags
bom_list = {
    'MAT-1001': ('NMC', True, {}),
    'MAT-1002': ('Graphite', True, {}),
    'MAT-1003': ('PVDF', True, {}),
    'MAT-1004': ('LiPF₆', True, {}),
    'MAT-1007': ('Copper/Aluminum Foil', True, {}),
    'MAT-1010': ('Separator (Polyethylene)', True, {}),
    'MAT-2001': ('Brominated Flame Retardants', False, {'RoHS': True, 'REACH': True, 'SVHC': True}),
    'MAT-2002': ('PFAS', True, {'POP': True, 'REACH': True, 'SVHC': True}),
    'MAT-2003': ('Lead (in solder)', False, {'RoHS': True, 'REACH': True, 'SVHC': True}),
    'N/A': ('Unknown', True, {}),
}

# mapping
log_df['Activity_only'] = log_df['Activity'].apply(lambda x: x.split('-')[0].strip())
log_df['material_number'] = log_df['Activity_only'].map(activity_to_material).fillna('N/A')

# extract bom infos
bom_mapped = log_df['material_number'].apply(lambda x: pd.Series(bom_list.get(x, ('Unknown', True, {}))))
log_df[['substance_id', 'compliance_status']] = bom_mapped.iloc[:, :2]

# add flags (POP, RoHS, REACH, SVHC)
flags_expanded = bom_mapped.iloc[:, 2].apply(pd.Series)
for flag in ['POP', 'RoHS', 'REACH', 'SVHC']:
    log_df[flag] = flags_expanded.get(flag, pd.Series(False, index=log_df.index)).fillna(False).astype(bool)


# concentration
def assign_concentration(row):
    if row['substance_id'] == 'PFAS':
        return round(random.uniform(0.01, 0.09), 3)
    elif row['substance_id'] == 'Brominated Flame Retardants':
        return round(random.uniform(0.01, 0.08), 3)
    elif 'lead' in str(row['substance_id']).lower():
        return round(random.uniform(0.005, 0.015), 4)
    else:
        return 0.0
log_df['concentration'] = log_df.apply(assign_concentration, axis=1)

# CO2 emissions
def assign_co2_emissions(activity):
    if activity in ['Slurry Production', 'Coating', 'Drying']:
        return round(random.uniform(5, 20), 2)
    elif activity == 'Formation':
        return round(random.uniform(5, 15), 2)
    else:
        return round(random.uniform(0.1, 2), 2)
log_df['CO2_emissions'] = log_df['Activity_only'].apply(assign_co2_emissions)

# is_trace_contaminant
def assign_is_trace_contaminant(row):
    if row['substance_id'] == 'PFAS':
        return np.random.choice([True, False], p=[0.1, 0.9])
    else:
        return False
log_df['is_trace_contaminant'] = log_df.apply(assign_is_trace_contaminant, axis=1)

# trace_log
log_df['trace_log'] = log_df.apply(lambda x: None if random.random() < 0.01 else f"trace_{random.randint(1, 10)}", axis=1)

# material_origin + secondary_flag
def assign_material_origin():
    return 'secondary' if random.random() < 0.2 else 'primary'
log_df['material_origin'] = log_df.apply(lambda x: assign_material_origin(), axis=1)

def assign_secondary_flag(origin):
    return True if origin == 'secondary' or random.random() < 0.1 else False
log_df['secondary_flag'] = log_df['material_origin'].apply(assign_secondary_flag)

# save
output_path = "/Users/juliafries/PycharmProjects/BachelorThesisProjectEuTaxonomy/conformance_pipeline/data/output/Production_Data_substance_enriched.csv"
log_df.to_csv(output_path, index=False)

print("Enriched material log saved in conformance_pipeline/data/output/")
