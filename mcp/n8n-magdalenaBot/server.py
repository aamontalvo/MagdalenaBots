#!/usr/bin/env python3
"""
n8n-magdalenaBot MCP Server
Model Context Protocol server for MagdalenaBot n8n integration

This server exposes hydrological analysis tools via MCP protocol
for use with n8n AI Agent nodes.
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel
    )
    from mcp.shared.exceptions import McpError
except ImportError:
    print("Error: mcp package not installed. Run: pip install mcp")
    sys.exit(1)

# Configuration from mcp.json
N8N_MCP_URL = "https://test.aichuann8n.com/mcp-server/http"
N8N_MCP_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1OTBlYjJhYy0yMjM0LTQ2MzctODNjZi03OWYyMmEwOTcwMDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJtY3Atc2VydmVyLWFwaSIsImp0aSI6IjYxOWI4NTgwLTdmNWEtNDA4NS05MzkzLTRkYTc5MGE4ZjIxNiIsImlhdCI6MTc3MDY1MzE0Mn0.Rf73coJYSPZxbu8KforGjnj-CaFcs8YLXbCe2Xr88d8"

# Station mappings
STATIONS = {
    "011375ab-c1be-4fa4-aa97-be2f39483b34": {
        "name": "Calamar",
        "ideam_code": "29037020",
        "location": "Bolívar"
    },
    "b7eac378-48b3-4c2c-9032-5991606c66f0": {
        "name": "Magangué",
        "ideam_code": "25027680",
        "location": "Bolívar"
    },
    "ea572438-c4de-471e-89dc-075996498b10": {
        "name": "Barrancabermeja",
        "ideam_code": "23157030",
        "location": "Santander"
    }
}

@dataclass
class AppContext:
    """Application context for lifespan management"""
    supabase_url: str
    supabase_key: str

@asynccontextmanager
async def app_lifespan(server: Server) -> AppContext:
    """Manage application lifecycle"""
    # Startup
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    
    yield AppContext(
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    # Shutdown
    pass

# Create MCP server
server = Server(
    "n8n-magdalenaBot",
    lifespan=app_lifespan
)

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="supabase://stations",
            name="stations",
            description="List of hydrological stations in Rio Magdalena",
            mimeType="application/json"
        ),
        Resource(
            uri="supabase://water_level_measurements",
            name="water_level_measurements",
            description="Historical water level measurements",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content"""
    if uri == "supabase://stations":
        return json.dumps(STATIONS, indent=2)
    elif uri == "supabase://water_level_measurements":
        return json.dumps({
            "description": "Water level measurements table",
            "columns": [
                "id", "station_id", "measurement_date", "water_level_m",
                "water_level_cm", "parameter", "quality_flag", "source"
            ],
            "parameter": "NivelMedioDiario",
            "stations": list(STATIONS.keys())
        }, indent=2)
    else:
        raise McpError(f"Unknown resource: {uri}")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_stations",
            description="Get list of available hydrological stations with their IDs and metadata",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="build_sql_query",
            description="Build a safe SQL query for water level data. ALWAYS use this before executing queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "station_id": {
                        "type": "string",
                        "description": "Station UUID"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum rows to return (default: 50, max: 10000)",
                        "default": 50
                    },
                    "aggregation": {
                        "type": "string",
                        "enum": ["none", "daily", "monthly", "yearly"],
                        "description": "Aggregation level"
                    }
                },
                "required": ["station_id"]
            }
        ),
        Tool(
            name="calculate_monthly_probability",
            description="Calculate monthly probability distribution (KDE) for water levels",
            inputSchema={
                "type": "object",
                "properties": {
                    "station_id": {
                        "type": "string",
                        "description": "Station UUID"
                    },
                    "years": {
                        "type": "integer",
                        "description": "Number of years to analyze"
                    }
                },
                "required": ["station_id"]
            }
        ),
        Tool(
            name="calculate_exceedance_frequency",
            description="Calculate exceedance frequency curves for flood risk assessment",
            inputSchema={
                "type": "object",
                "properties": {
                    "station_id": {
                        "type": "string",
                        "description": "Station UUID"
                    },
                    "thresholds": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Percentile thresholds (default: [10, 25, 50, 75, 90])"
                    }
                },
                "required": ["station_id"]
            }
        ),
        Tool(
            name="calculate_duration_curve",
            description="Calculate flow duration curve showing persistence of water levels",
            inputSchema={
                "type": "object",
                "properties": {
                    "station_id": {
                        "type": "string",
                        "description": "Station UUID"
                    }
                },
                "required": ["station_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute tool"""
    
    if name == "get_stations":
        return [TextContent(
            type="text",
            text=json.dumps({
                "stations": [
                    {
                        "id": station_id,
                        "name": info["name"],
                        "ideam_code": info["ideam_code"],
                        "location": info["location"]
                    }
                    for station_id, info in STATIONS.items()
                ]
            }, indent=2)
        )]
    
    elif name == "build_sql_query":
        station_id = arguments["station_id"]
        start_date = arguments.get("start_date")
        end_date = arguments.get("end_date")
        limit = min(arguments.get("limit", 50), 10000)
        aggregation = arguments.get("aggregation", "none")
        
        # Validate station_id
        if station_id not in STATIONS:
            return [TextContent(
                type="text",
                text=f"Error: Invalid station_id. Valid options: {list(STATIONS.keys())}"
            )]
        
        # Build query based on aggregation
        if aggregation == "none":
            query = f"""SELECT 
    measurement_date::date as fecha,
    water_level_m as nivel_metros,
    water_level_cm as nivel_centimetros,
    station_id
FROM water_level_measurements 
WHERE station_id = $1 
    AND parameter = 'NivelMedioDiario'"""
            
            params = [station_id]
            
            if start_date:
                query += f"\n    AND measurement_date >= ${len(params) + 1}"
                params.append(start_date)
            
            if end_date:
                query += f"\n    AND measurement_date <= ${len(params) + 1}"
                params.append(end_date)
            
            query += f"\nORDER BY measurement_date DESC\nLIMIT ${len(params) + 1}"
            params.append(limit)
            
        elif aggregation == "monthly":
            query = f"""SELECT 
    DATE_TRUNC('month', measurement_date) as mes,
    AVG(water_level_m) as promedio_metros,
    MIN(water_level_m) as minimo_metros,
    MAX(water_level_m) as maximo_metros,
    COUNT(*) as registros
FROM water_level_measurements 
WHERE station_id = $1 
    AND parameter = 'NivelMedioDiario'"""
            
            params = [station_id]
            
            if start_date:
                query += f"\n    AND measurement_date >= ${len(params) + 1}"
                params.append(start_date)
            
            if end_date:
                query += f"\n    AND measurement_date <= ${len(params) + 1}"
                params.append(end_date)
            
            query += f"""\nGROUP BY DATE_TRUNC('month', measurement_date)
ORDER BY mes DESC
LIMIT ${len(params) + 1}"""
            params.append(limit)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "query": query,
                "parameters": params,
                "station_name": STATIONS.get(station_id, {}).get("name", "Unknown")
            }, indent=2)
        )]
    
    elif name == "calculate_monthly_probability":
        station_id = arguments["station_id"]
        years = arguments.get("years")
        
        if station_id not in STATIONS:
            return [TextContent(
                type="text",
                text=f"Error: Invalid station_id"
            )]
        
        # Generate SQL for monthly probability analysis
        query = f"""WITH monthly_stats AS (
    SELECT 
        EXTRACT(MONTH FROM measurement_date) as mes,
        water_level_m,
        NTILE(10) OVER (PARTITION BY EXTRACT(MONTH FROM measurement_date) ORDER BY water_level_m) as decil
    FROM water_level_measurements 
    WHERE station_id = '{station_id}'
        AND parameter = 'NivelMedioDiario'"""
        
        if years:
            query += f"\n        AND measurement_date >= CURRENT_DATE - INTERVAL '{years} years'"
        
        query += """\n)
SELECT 
    mes,
    COUNT(*) as registros,
    AVG(water_level_m) as promedio,
    MIN(water_level_m) as minimo,
    MAX(water_level_m) as maximo,
    PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY water_level_m) as p10,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY water_level_m) as p25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY water_level_m) as p50,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY water_level_m) as p75,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY water_level_m) as p90
FROM monthly_stats
GROUP BY mes
ORDER BY mes;"""
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "description": f"Monthly probability analysis for {STATIONS[station_id]['name']}",
                "query": query,
                "station_id": station_id,
                "analysis_type": "monthly_probability"
            }, indent=2)
        )]
    
    elif name == "calculate_exceedance_frequency":
        station_id = arguments["station_id"]
        thresholds = arguments.get("thresholds", [10, 25, 50, 75, 90])
        
        if station_id not in STATIONS:
            return [TextContent(
                type="text",
                text=f"Error: Invalid station_id"
            )]
        
        query = f"""WITH all_levels AS (
    SELECT water_level_m
    FROM water_level_measurements 
    WHERE station_id = '{station_id}'
        AND parameter = 'NivelMedioDiario'
)
SELECT """
        
        percentiles = []
        for p in thresholds:
            percentiles.append(f"\n    PERCENTILE_CONT({p/100}) WITHIN GROUP (ORDER BY water_level_m) as p{p}")
        
        query += ",".join(percentiles)
        query += "\nFROM all_levels;"
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "description": f"Exceedance frequency for {STATIONS[station_id]['name']}",
                "query": query,
                "station_id": station_id,
                "analysis_type": "exceedance_frequency",
                "thresholds": thresholds
            }, indent=2)
        )]
    
    elif name == "calculate_duration_curve":
        station_id = arguments["station_id"]
        
        if station_id not in STATIONS:
            return [TextContent(
                type="text",
                text=f"Error: Invalid station_id"
            )]
        
        query = f"""WITH ranked_levels AS (
    SELECT 
        water_level_m,
        ROW_NUMBER() OVER (ORDER BY water_level_m DESC) as rank,
        COUNT(*) OVER () as total_count
    FROM water_level_measurements 
    WHERE station_id = '{station_id}'
        AND parameter = 'NivelMedioDiario'
)
SELECT 
    water_level_m as nivel,
    (rank::float / total_count * 100) as duracion_percentil,
    rank
FROM ranked_levels
WHERE rank IN (
    SELECT generate_series(1, total_count, GREATEST(total_count / 100, 1))
    FROM (SELECT COUNT(*) as total_count FROM water_level_measurements 
          WHERE station_id = '{station_id}' AND parameter = 'NivelMedioDiario') t
)
ORDER BY duracion_percentil;"""
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "description": f"Duration curve for {STATIONS[station_id]['name']}",
                "query": query,
                "station_id": station_id,
                "analysis_type": "duration_curve"
            }, indent=2)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Error: Unknown tool '{name}'"
        )]

async def main():
    """Run MCP server"""
    async with stdio_server(server) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
