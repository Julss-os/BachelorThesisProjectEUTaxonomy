import pandas as pd
import os

log_file_path = "/Users/juliafries/PycharmProjects/BachelorThesisProjectEuTaxonomy/conformance_pipeline/data/output/Production_Data_enrich_activities.csv"
df = pd.read_csv(log_file_path)

# Drop duplicates
df.drop_duplicates(inplace=True)

# Date and time format
df['Start Timestamp'] = pd.to_datetime(df['Start Timestamp'], format='%Y/%m/%d %H:%M:%S.%f', errors='coerce')
df['Complete Timestamp'] = pd.to_datetime(df['Complete Timestamp'], format='%Y/%m/%d %H:%M:%S.%f', errors='coerce')



# Fill Rework NaN with 0
df['Rework'] = df['Rework'].fillna('N')

# Calculate Span based on Start and End Timestamp
def calculate_span(start, end):
    if pd.isnull(start) or pd.isnull(end):
        return '000:00'
    duration = end - start
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours):03d}:{int(minutes):02d}"

df['Span'] = df.apply(lambda row: calculate_span(row['Start Timestamp'], row['Complete Timestamp']), axis=1)

# Calculate Span_minutes
def span_to_minutes(span_str):
    if pd.isnull(span_str):
        return None
    try:
        hours, minutes = map(int, span_str.split(':'))
        return hours * 60 + minutes
    except ValueError:
        return None

df['Span_minutes'] = df['Span'].apply(span_to_minutes)


# Split Activity attribute
def split_activity(activity_str):
    if pd.isnull(activity_str):
        return pd.Series([None, None])
    if '-' in activity_str:
        parts = activity_str.split(' - ', 1)
        return pd.Series(parts)
    else:
        return pd.Series([activity_str, activity_str])

df[['Activity_only', 'Machine']] = df['Activity'].apply(split_activity)

df.to_csv("/Users/juliafries/PycharmProjects/BachelorThesisProjectEuTaxonomy/conformance_pipeline/data/output/Production_Data_cleaned_enrich_activities.csv", index=False)
print("Activity enriched Log is saved in conformance_pipeline/data/output/")