from fastapi import APIRouter, HTTPException
from app.modules.mitre.service import mitre_kb

router = APIRouter(prefix="/mitre", tags=["MITRE"])

@router.get("/techniques/{technique_id}")
async def get_technique(technique_id: str):
    result = mitre_kb.lookup_technique(technique_id)
    if not result:
        raise HTTPException(status_code=404, detail="Technique not found")
    return result

@router.get("/tactics/{tactic_name}")
async def get_tactic(tactic_name: str):
    result = mitre_kb.lookup_tactic(tactic_name)
    if not result:
        raise HTTPException(status_code=404, detail="Tactic not found")
    return result

@router.get("/search")
async def search_mitre(q: str):
    return mitre_kb.search(q)
