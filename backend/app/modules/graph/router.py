import uuid
import json
from io import StringIO
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.models.user import User
from app.modules.graph.engine import PostgresGraphAdapter

router = APIRouter(prefix="/graph", tags=["Graph"])

@router.get("/")
async def get_graph(
    investigation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = PostgresGraphAdapter(db)
    return await repo.export_graph(investigation_id)

@router.get("/neighbors")
async def get_neighbors(
    investigation_id: uuid.UUID,
    node_value: str = Query(...),
    depth: int = Query(1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = PostgresGraphAdapter(db)
    return await repo.get_neighbors(investigation_id, node_value, depth)

@router.get("/export")
async def export_graph(
    investigation_id: uuid.UUID,
    format: str = Query("json"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = PostgresGraphAdapter(db)
    data = await repo.export_graph(investigation_id)
    
    if format == "json":
        return data
        
    elif format == "csv":
        output = StringIO()
        output.write("Source,Target,Type,Confidence\n")
        nodes_map = {n["id"]: f"{n['type']}:{n['value']}" for n in data["nodes"]}
        for edge in data["edges"]:
            src = nodes_map.get(edge["source"], "Unknown")
            tgt = nodes_map.get(edge["target"], "Unknown")
            output.write(f'"{src}","{tgt}","{edge["type"]}",{edge["confidence"]}\n')
        return PlainTextResponse(output.getvalue(), media_type="text/csv")
        
    elif format == "mermaid":
        output = StringIO()
        output.write("graph TD\n")
        nodes_map = {n["id"]: f"{n['type'].replace(' ', '')}_{n['value'].replace(' ', '_')}" for n in data["nodes"]}
        for n in data["nodes"]:
            sanitized_val = n["value"].replace('"', '')
            output.write(f'  {nodes_map[n["id"]]}["{sanitized_val}"]\n')
        for edge in data["edges"]:
            output.write(f'  {nodes_map[edge["source"]]} -->|{edge["type"]}| {nodes_map[edge["target"]]}\n')
        return PlainTextResponse(output.getvalue(), media_type="text/plain")
        
    elif format == "graphml":
        output = StringIO()
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n')
        output.write('  <graph id="G" edgedefault="directed">\n')
        for n in data["nodes"]:
            output.write(f'    <node id="{n["id"]}"/>\n')
        for i, edge in enumerate(data["edges"]):
            output.write(f'    <edge id="e{i}" source="{edge["source"]}" target="{edge["target"]}"/>\n')
        output.write('  </graph>\n</graphml>')
        return PlainTextResponse(output.getvalue(), media_type="application/xml")
        
    return Response(status_code=400, content="Unsupported format")
