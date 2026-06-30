import json
import logging
from typing import List, Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

class MitreKnowledgeBase:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MitreKnowledgeBase, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, stix_path: Optional[str] = None):
        if self._initialized:  # type: ignore
            return
            
        self.techniques_by_id = {}  # type: ignore
        self.techniques_by_name = {}  # type: ignore
        self.tactics_by_name = {}  # type: ignore
        self.all_techniques = []  # type: ignore
        
        if not stix_path:
            stix_path = os.getenv("MITRE_STIX_PATH", "/data/mitre/enterprise-attack.json")
            
        self._load_stix(stix_path)
        self._initialized = True

    def _load_stix(self, stix_path: str):
        if not os.path.exists(stix_path):
            logger.warning(f"MITRE STIX dataset not found at {stix_path}. Skipping load.")
            return

        try:
            with open(stix_path, "r", encoding="utf-8") as f:
                stix_data = json.load(f)
                
            objects = stix_data.get("objects", [])
            for obj in objects:
                obj_type = obj.get("type")
                if obj_type == "attack-pattern":
                    external_references = obj.get("external_references", [])
                    mitre_id = None
                    for ref in external_references:
                        if ref.get("source_name") == "mitre-attack":
                            mitre_id = ref.get("external_id")
                            break
                            
                    if mitre_id:
                        technique = {
                            "id": mitre_id,
                            "name": obj.get("name"),
                            "description": obj.get("description"),
                            "kill_chain_phases": [p.get("phase_name") for p in obj.get("kill_chain_phases", [])],
                            "platforms": obj.get("x_mitre_platforms", []),
                            "data_sources": obj.get("x_mitre_data_sources", [])
                        }
                        self.techniques_by_id[mitre_id] = technique
                        self.techniques_by_name[technique["name"].lower()] = technique
                        self.all_techniques.append(technique)
                        
                elif obj_type == "x-mitre-tactic":
                    self.tactics_by_name[obj.get("name", "").lower()] = {
                        "id": obj.get("x_mitre_shortname"),
                        "name": obj.get("name"),
                        "description": obj.get("description")
                    }
            logger.info(f"Loaded {len(self.techniques_by_id)} MITRE techniques.")
        except Exception as e:
            logger.error(f"Failed to load MITRE STIX dataset: {e}")

    def lookup_technique(self, technique_id: str) -> Optional[Dict[str, Any]]:
        return self.techniques_by_id.get(technique_id.upper())

    def lookup_tactic(self, tactic_name: str) -> Optional[Dict[str, Any]]:
        return self.tactics_by_name.get(tactic_name.lower())

    def search(self, query: str) -> List[Dict[str, Any]]:
        query = query.lower()
        results = []
        for tech in self.all_techniques:
            if query in tech["id"].lower() or query in tech["name"].lower() or (tech.get("description") and query in tech["description"].lower()):
                results.append(tech)
        return results

mitre_kb = MitreKnowledgeBase()
