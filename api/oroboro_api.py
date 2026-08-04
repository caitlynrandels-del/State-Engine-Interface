"""
OROBORO API - FastAPI Ingestion & Control Service
Provides endpoints for client data upload, simulation initialization, step execution, and telemetry streaming.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import asyncio

from engine.world import World
from engine.particle import Particle

app = FastAPI(
    title="OROBORO Stateful Particle Engine API",
    version="2.0.0",
    description="Framework-agnostic template API for custom agent-based simulation ingestion."
)

# Global simulation instance holder
simulation_state = {
    "world": None,
    "running": False,
    "tick_rate": 0.1
}

class SimulationConfig(BaseModel):
    width: int = Field(1000, description="Spatial domain width")
    height: int = Field(1000, description="Spatial domain height")
    tick_rate_ms: int = Field(50, description="Execution delay per tick")

class ParticlePayload(BaseModel):
    id: int
    x: float
    y: float
    dx: float = 0.0
    dy: float = 0.0
    metadata: Dict[str, Any] = {}

class DatasetUpload(BaseModel):
    config: SimulationConfig
    particles: List[ParticlePayload]

@app.post("/api/v2/initialize", summary="Upload custom dataset and initialize world")
def initialize_simulation(data: DatasetUpload):
    world = World(width=data.config.width, height=data.config.height)
    
    for p_data in data.particles:
        particle = Particle(particle_id=p_data.id, x=p_data.x, y=p_data.y, metadata=p_data.metadata)
        particle.set_velocity(p_data.dx, p_data.dy)
        
        # Configure default template state machine (e.g. SUSCEPTIBLE by default or mapped via metadata)
        initial_state = p_data.metadata.get("initial_state", "SUSCEPTIBLE")
        particle.fsm.state = initial_state
        
        # Example flexible transition registration based on metadata rules
        particle.fsm.add_transition("SUSCEPTIBLE", "EXPOSED", lambda e, ctx: len(e.observe(ctx.get("nearby", []))) >= 1)
        particle.fsm.add_transition("EXPOSED", "INFECTIOUS", lambda e, ctx: e.timer > 10)
        particle.fsm.add_transition("INFECTIOUS", "RECOVERED", lambda e, ctx: e.timer > 30)
        
        world.add_particle(particle)

    simulation_state["world"] = world
    simulation_state["running"] = False
    simulation_state["tick_rate"] = data.config.tick_rate_ms / 1000.0

    return {
        "status": "success",
        "message": f"Initialized OROBORO world with {len(data.particles)} entities.",
        "domain_bounds": [data.config.width, data.config.height]
    }

@app.post("/api/v2/step", summary="Execute a single simulation tick")
def simulation_step():
    world: World = simulation_state.get("world")
    if not world:
        raise HTTPException(status_code=400, detail="Simulation world not initialized. Upload dataset first.")
    
    world.step()
    return world.get_state_snapshot()

@app.get("/api/v2/telemetry", summary="Get real-time simulation snapshot")
def get_telemetry():
    world: World = simulation_state.get("world")
    if not world:
        return {"status": "uninitialized", "particles": []}
    return world.get_state_snapshot()

@app.post("/api/v2/control", summary="Control simulation execution flow")
def control_simulation(action: str):
    if action not in ["start", "pause", "reset"]:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'start', 'pause', or 'reset'.")
    
    if action == "start":
        simulation_state["running"] = True
    elif action == "pause":
        simulation_state["running"] = False
    elif action == "reset":
        simulation_state["world"] = None
        simulation_state["running"] = False

    return {"status": "success", "action": action, "running": simulation_state["running"]}
