# BachelorThesis
# EU Taxonomy – Data Pipeline, Analysis & User Interface

This project implements a complete process chain to evaluate the compliance of battery production data with the EU Taxonomy.  
It consists of three main modules: a **rule-based data pipeline**, an **analysis module** for regulatory requirements, and a **user-guided interface** for manual assessment.

---

## 1. Conformance Pipeline

The `conformance_pipeline` module processes production data in several stages:

### Processing Steps

Source input Event log: https://data.4tu.nl/articles/_/12697997/1

1. **Activity Enrichment**  
   Adds missing activities based on a modeled process logic.

2. **Data Cleaning**  
   Normalizes time and column formats, filters incomplete records.

3. **Material & Substance Enrichment**  
   Links activities with substance databases (e.g., PFAS, SVHC), calculates CO₂ emissions and compliance flags.

4. **Conformance Checking**  
   Validates traces against regulatory rules derived from the EU Taxonomy.

### Execution

```bash
cd conformance_pipeline
python main.py
```

### Output

Results are stored in `conformance_pipeline/data/output/`:

- `Production_Data_enrich_activities.csv`
- `Production_Data_cleaned_enrich_activities.csv`
- `Production_Data_substance_enriched.csv`
- `Conformance_checking_Results.csv`
- `Conformance_violation.csv`

---

## 2. Regulatory Requirements Analysis

The `data_analysis` module processes extracted EU Taxonomy constraints.

### Analysis Workflow

- Aggregates constraints by:
  - Category (`Constraint Category`)
  - Type (`Model Type`)
  - Granularity (`Granularity`)
  - Process Perspective (`Process Perspective`)
- Combines perspective & granularity into fine-grained classifications
- Visualizes:
  - Distribution of constraint types
  - Coverage across lifecycle phases and event log availability

### Execution

```bash
cd data_analysis
python data_analysis.py
```

### Output

Results are stored in `data_analysis/data/output/`:

- `climate_goal_counts.csv`
- `constraint_type_counts.csv`
- `granularity_counts.csv`
- `process_perspective_counts.csv`
- `combined_constraint_type_counts.csv`
- `constraint_distribution.png`
- `lifecycle_event_log_distribution.png`

---

## 3. User Interface for Alignment Check

The `user_interface` module provides a guided Streamlit interface for performing the EU Taxonomy alignment check.  
It walks users through a process model using a state machine that captures:

- Climate risk screening
- Materiality assessment
- Adaptation technique evaluation
- Upload of adaptation plans
- Source selection & projections
- KPI plan submission

An event log with `timestamp`, `event`, and `case_id` is generated automatically.

### Run Interface

```bash
cd user_interface
streamlit run user_interface.py
```

### Output

Results are saved in `user_interface/data/output/`:

- `event_log.csv`
- Uploaded documents in `uploads/`

---

## Dependencies

Installable via `requirements.txt`:

- `pandas`
- `numpy`
- `streamlit`
- `transitions`
- `matplotlib`
- `pm4py`

---

## Author

Julia Fries  