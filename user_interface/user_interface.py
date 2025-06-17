import streamlit as st
from climate_adaptation_model import FullCRVAProcess
import os
import pandas as pd
import zipfile
import io

OUTPUT_DIR = "/Users/juliafries/PycharmProjects/BachelorThesisProjectEuTaxonomy/user_interface/data/output/"
UPLOAD_DIR = os.path.join(OUTPUT_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# process initialization
if 'process' not in st.session_state or st.session_state.get("force_restart", False):
    st.session_state.process = FullCRVAProcess()
    st.session_state.force_restart = False

process = st.session_state.process

# Page Config
st.set_page_config(page_title="EU Taxonomy – Climate Adaptation Alignment Check", layout="centered")
st.title("EU Taxonomy – Climate Adaptation Alignment Check")
st.markdown("---")

# Sidebar
st.sidebar.markdown("### Current State")
st.sidebar.code(process.state)
st.sidebar.markdown("### Event Log")
st.sidebar.dataframe(pd.DataFrame(process.log))

#logic

if process.state == 'start':
    st.subheader("Step 1: Screening – Physical Climate Risks")
    st.markdown("**Required ** Check Appendix A")
    risk = st.selectbox("Are there physical climate risks affecting the activity?", ["None", "Yes"])
    if st.button("Continue"):
        process.log_custom("risk_assessment_completed")
        if risk == "None":
            process.screen_risks_none()
            process.finish_no_risk()
            st.success("No risks identified. Alignment check completed.")
        else:
            process.screen_risks_found()
            st.success("Risks found. Proceed to materiality.")

elif process.state == 'risks_identified':
    st.subheader("Step 2: Materiality Assessment")
    st.markdown("Check if the identified risks are any material to the economic activity")
    material = st.selectbox("Are any identified risks considered material?", ["No", "Yes"])
    if st.button("Continue Materiality Assessment"):
        process.log_custom("materiality_assessment_completed")
        if material == "No":
            process.assess_materiality_none()
            process.finish_no_material()
            st.success("No material risks. Alignment check completed.")
            st.session_state.force_restart = True
            st.rerun()
        else:
            process.assess_materiality_some()
            st.success("Material risk confirmed. Proceed to technique evaluation.")

elif process.state == 'material_risks_exist':
    st.subheader("Step 3: Evaluate Adaptation Techniques")
    st.markdown("**Required Data:** Overview of adaptation techniques")
    if st.button("Continue when evaluated adaptation techniques "):
        process.evaluate_techniques()
        st.success("Techniques evaluated. Upload adaptation plan next.")

elif process.state == 'evaluate_adaptation_techniques':
    st.subheader("Step 4: Upload Adaptation Plan")
    st.markdown("**Required Data:** Final adaptation plan document")
    uploaded_file = st.file_uploader("Upload your adaptation plan document", key="adaptation_plan")
    if uploaded_file is not None:
        st.success("Adaptation plan uploaded.")
        file_path = os.path.join(UPLOAD_DIR, f"adaptation_plan_{uploaded_file.name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        process.log_custom(f"adaptation_plan_uploaded: {uploaded_file.name}")
        process.create_adaptation_plan()
        process.conduct_crva()
        st.rerun()

elif process.state == 'conduct_crva':
    st.subheader("Step 5: Validate Climate Projection Sources")
    st.markdown("**Required Data:** Source used (e.g., IPCC, peer-reviewed publications, open models)")
    source = st.text_input("Enter your climate projection source:")
    if st.button("Submit Source") and source:
        process.select_validated_sources()
        process.log_custom(f"climate_projection_source: {source}")
        st.success("Source recorded. Continue to lifespan decision.")
        st.rerun()

elif process.state == 'validated_climate_projection_sources_chosen':
    st.subheader("Step 6: Lifespan of the Activity")
    st.markdown("**Required Data:** Expected lifespan of the activity in years")
    lifespan = st.number_input("Expected lifespan (in years)?", min_value=1)
    if st.button("Submit Lifespan"):
        process.log_custom(f"lifespan_years: {lifespan}")
        if lifespan <= 10:
            process.lifespan_short()
        else:
            process.lifespan_long()
        process.generate_crva_report()
        process.complete_alignment()
        st.success("Projection applied and CRVA report generated. Continue to KPI upload.")

elif process.state == 'climate_adaptation_alignment_completed':
    st.subheader("Step 7: Upload KPI Monitoring Plan")
    st.markdown("**Required Data:** KPI plan or monitoring document")
    kpi_file = st.file_uploader("Upload your KPI monitoring plan")
    if kpi_file is not None:
        file_path = os.path.join(UPLOAD_DIR, f"kpi_plan_{kpi_file.name}")
        with open(file_path, "wb") as f:
            f.write(kpi_file.getbuffer())
        process.log_custom(f"kpi_plan_uploaded: {kpi_file.name}")
        process.upload_plan()
        process.check_plan()
        process.create_kpi()
        process.monitor_kpi()
        process.confirm_success()
        st.rerun()

elif process.state == 'adaptation_successful':
    st.success("The economic activity is aligned with the EU Taxonomy objective 'Climate Change Adaptation'.")
    st.markdown("All requirements have been fulfilled.")
    if st.button("Finish Alignment Check"):
        log_path = os.path.join(OUTPUT_DIR, "event_log.csv")
        process.finish_success()
        process.export_log(filepath=log_path)
        st.success(f"Event log saved to: {log_path}")

elif process.state in ['no_risks_identified', 'no_material_risks']:
    st.success("EU Taxonomy alignment check completed (no adaptation required).")
    if st.button("Export Event Log"):
        log_path = os.path.join(OUTPUT_DIR, "event_log.csv")
        process.export_log(filepath=log_path)
        st.success(f"Event log saved to {log_path}")

if st.button("Restart Alignment Check"):
    st.session_state.clear()
    st.session_state.force_restart = True
    st.rerun()