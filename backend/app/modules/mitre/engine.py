import os
import glob
import yaml
import logging
from typing import List, Dict, Any, Optional
from app.models.normalized_event import NormalizedEvent
from app.modules.mitre.service import mitre_kb

logger = logging.getLogger(__name__)

class MitreMappingEngine:
    def __init__(self, rules_dir: Optional[str] = None):
        if not rules_dir:
            # relative to the project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            rules_dir = os.path.join(base_dir, "rules")
            
        self.rules_dir = rules_dir
        self.rules = []
        self._load_rules()

    def _load_rules(self):
        if not os.path.exists(self.rules_dir):
            logger.warning(f"Rules directory not found: {self.rules_dir}")
            return
            
        for filepath in glob.glob(os.path.join(self.rules_dir, "*.yaml")):
            try:
                with open(filepath, 'r') as f:
                    rule = yaml.safe_load(f)
                    if rule and 'technique_id' in rule and 'conditions' in rule:
                        self.rules.append(rule)
            except Exception as e:
                logger.error(f"Failed to load rule {filepath}: {e}")
                
        logger.info(f"Loaded {len(self.rules)} MITRE mapping rules.")

    def _evaluate_condition(self, event_dict: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        
        event_val = event_dict.get(field)
        if event_val is None:
            # Check nested inside raw_message if applicable, but for deterministic rules we rely on normalized fields
            return False
            
        event_val_str = str(event_val).lower()
        
        if operator == "equals":
            return event_val_str == str(value).lower()
        elif operator == "contains":
            return str(value).lower() in event_val_str
        elif operator == "in":
            return event_val_str in [str(v).lower() for v in value]
        elif operator == "contains_any":
            return any(str(v).lower() in event_val_str for v in value)
            
        return False

    def evaluate_event(self, event: NormalizedEvent) -> List[Dict[str, Any]]:
        matches = []
        event_dict = {
            "event_action": event.event_action,
            "event_provider": event.event_provider,
            "raw_message": event.raw_message,
            # Add more fields as needed for rules
        }
        
        for rule in self.rules:
            # All conditions must pass (AND)
            match = True
            for condition in rule.get('conditions', []):
                if not self._evaluate_condition(event_dict, condition):
                    match = False
                    break
            
            if match:
                technique_info = mitre_kb.lookup_technique(rule['technique_id'])
                matches.append({
                    "rule_id": rule.get('id'),
                    "technique_id": rule['technique_id'],
                    "confidence": rule.get('confidence', 'medium'),
                    "description": f"Matched rule: {rule.get('name')}. {technique_info.get('name') if technique_info else ''}"
                })
                
        return matches

mapping_engine = MitreMappingEngine()
