from transitions import Machine
from datetime import datetime
import pandas as pd
import uuid

# all states
class FullCRVAProcess:
    states = [
        'start',
        'no_risks_identified',
        'risks_identified',
        'no_material_risks',
        'material_risks_exist',
        'evaluate_adaptation_techniques',
        'create_suitable_adaptation_plan',
        'conduct_crva',
        'validated_climate_projection_sources_chosen',
        'short_term_projections_applied',
        'long_term_projections_applied',
        'crva_report_generated',
        'climate_adaptation_alignment_completed',
        'upload_adaptation_plan',
        'check_adaptation_plan',
        'create_kpi',
        'monitor_kpi',
        'adaptation_successful',
        'end'
    ]

#all transitions
    def __init__(self):
        self.state = 'start'
        self.log = []
        self.case_id = str(uuid.uuid4())
        self.machine = Machine(model=self, states=FullCRVAProcess.states, initial='start')

        self.machine.add_transition('screen_risks_none', 'start', 'no_risks_identified', after='log_event')
        self.machine.add_transition('screen_risks_found', 'start', 'risks_identified', after='log_event')
        self.machine.add_transition('assess_materiality_none', 'risks_identified', 'no_material_risks', after='log_event')
        self.machine.add_transition('assess_materiality_some', 'risks_identified', 'material_risks_exist', after='log_event')
        self.machine.add_transition('evaluate_techniques', 'material_risks_exist', 'evaluate_adaptation_techniques', after='log_event')
        self.machine.add_transition('create_adaptation_plan', 'evaluate_adaptation_techniques', 'create_suitable_adaptation_plan', after='log_event')
        self.machine.add_transition('conduct_crva', 'create_suitable_adaptation_plan', 'conduct_crva', after='log_event')
        self.machine.add_transition('select_validated_sources', ['conduct_crva', 'create_suitable_adaptation_plan'], 'validated_climate_projection_sources_chosen', after='log_event')
        self.machine.add_transition('lifespan_short', 'validated_climate_projection_sources_chosen', 'short_term_projections_applied', after='log_event')
        self.machine.add_transition('lifespan_long', 'validated_climate_projection_sources_chosen', 'long_term_projections_applied', after='log_event')
        self.machine.add_transition('generate_crva_report', ['short_term_projections_applied', 'long_term_projections_applied'], 'crva_report_generated', after='log_event')
        self.machine.add_transition('complete_alignment', 'crva_report_generated', 'climate_adaptation_alignment_completed', after='log_event')
        self.machine.add_transition('upload_plan', 'climate_adaptation_alignment_completed', 'upload_adaptation_plan', after='log_event')
        self.machine.add_transition('check_plan', 'upload_adaptation_plan', 'check_adaptation_plan', after='log_event')
        self.machine.add_transition('create_kpi', 'check_adaptation_plan', 'create_kpi', after='log_event')
        self.machine.add_transition('monitor_kpi', 'create_kpi', 'monitor_kpi', after='log_event')
        self.machine.add_transition('confirm_success', 'monitor_kpi', 'adaptation_successful', after='log_event')
        self.machine.add_transition('finish_success', 'adaptation_successful', 'end', after='log_event')
        self.machine.add_transition('finish_no_risk', 'no_risks_identified', 'end', after='log_event')
        self.machine.add_transition('finish_no_material', 'no_material_risks', 'end', after='log_event')

    def log_event(self):
        self.log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': self.state,
            'case_id': self.case_id
        })

    def log_custom(self, event_name):
        self.log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': event_name,
            'case_id': self.case_id
        })

    def export_log(self, filepath):
        df = pd.DataFrame(self.log)
        df.to_csv(filepath, index=False)