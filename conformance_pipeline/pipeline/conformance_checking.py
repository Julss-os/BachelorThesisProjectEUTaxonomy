import pandas as pd
import random
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter

log_df = pd.read_csv("/Users/juliafries/PycharmProjects/BachelorThesisProjectEuTaxonomy/conformance_pipeline/data/output/Production_Data_substance_enriched.csv", parse_dates=['Start Timestamp'])

#clean log
log_df = log_df.rename(columns={'Activity': 'concept:name'})
log_df = dataframe_utils.convert_timestamp_columns_in_df(log_df)
log_df = log_df.rename(columns={'Start Timestamp': 'time:timestamp'})

# convert to event log
parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'Case ID'}
event_log = log_converter.apply(log_df, parameters=parameters, variant=log_converter.Variants.TO_EVENT_LOG)

# constraints
declare_model = {
    'PP-001 (No POPs use)': lambda e: not (e.get('POP', False) and not e.get('is_trace_contaminant', False)),
    #'PP-002 (Minimal mercury)': lambda e: not (str(e.get('substance_id', '')).lower() == 'mc' and e.get('concentration', 0.0) > 0.0005),
    'PP-003 (No ODS use)': lambda e: not e.get('ODS', False),
    'PP-004 (No RoHS substances unless compliant)': lambda e: not (e.get('RoHS', False) and not e.get('compliance_status', True)),
    'PP-005 (No REACH substances unless compliant)': lambda e: not (e.get('REACH', False) and not e.get('compliance_status', True)),
    'PP-006 (No SVHCs above 0.1%)': lambda e: not (e.get('SVHC', False) and e.get('concentration', 0.0) > 0.1),
    'PP-008-01 (Lead <= 0.01%)': lambda e: not ('lead' in str(e.get('substance_id', '')).lower() and e.get('concentration', 0.0) > 0.01),
    #'PP-008-02 (Cadmium <= 0.002%)': lambda e: not (str(e.get('substance_id', '')).lower() == 'cd' and e.get('concentration', 0.0) > 0.002),
    'CE-003 (Traceability of substances)': lambda e: pd.notnull(e.get('trace_log')),
    'CM-001 (Secondary raw materials)': lambda e: not (e.get('secondary_flag', False) and e.get('material_origin', '') != 'secondary'),
    'CM-002 (GHG emission reductions)': lambda e: pd.notnull(e.get('CO2_emissions'))
}
#conformance checking
results = []
for trace in event_log:
    case_id = trace.attributes['concept:name']
    trace_result = {'Case ID': case_id}
    for constraint_name, condition_func in declare_model.items():
        violated = any(not condition_func(event) for event in trace)
        trace_result[constraint_name] = 'VIOLATED' if violated else 'OK'
    results.append(trace_result)

results_df = pd.DataFrame(results)
print(results_df)

# Violation + rate
print("\nSummary of Violations:")
violation_summary = results_df.drop(columns=["Case ID"]).apply(lambda col: (col == 'VIOLATED').mean()).sort_values(ascending=False)
violation_summary_pct = (violation_summary * 100).round(2)
violation_summary_pct.to_csv("/Users/juliafries/PycharmProjects/BachelorThesisProjectEuTaxonomy/conformance_pipeline/data/output/Conformance_violation", header=["Violation Rate (%)"])
print(violation_summary)

# save
results_df.to_csv("/Users/juliafries/PycharmProjects/BachelorThesisProjectEuTaxonomy/conformance_pipeline/data/output/Conformance_checking_Results", index=False)
print("Conformance Checking Results saved in conformance_pipeline/data/output/")