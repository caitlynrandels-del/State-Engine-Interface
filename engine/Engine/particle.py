"""
OROBORO Engine - Particle Module (Template)
Spatial agent representation supporting arbitrary metadata, state machines, and local memory.
"""

import math
import time
from .state import StateMachine

class Particle:
    def __init__(self, particle_id, x, y, metadata=None):
        self.id = particle_id
        self.x = float(x)
        self.y = float(y)
        self.velocity = [0.0, 0.0]
        self.metadata = metadata or {}
        
        # FSM and Memory
        self.fsm = StateMachine("IDLE")
        self.timer = 0
        self.memory = []
        self.radius = 15.0

    def set_position(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def set_velocity(self, dx, dy):
        self.velocity = [float(dx), float(dy)]

    def observe(self, neighbors):
        nearby = []
        for n in neighbors:
            if n.id == self.id:
                continue
            dist = math.hypot(self.x - n.x, self.y - n.y)
            if dist <= self.radius:
                nearby.append((n, dist))
        return nearby

    def evaluate(self, context, nearby):
        # Record temporal trace
        self.memory.append({
            "time": time.time(),
            "state": self.fsm.state,
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "nearby_count": len(nearby)
        })
        if len(self.memory) > 100:
            self.memory.pop(0)

        # Evaluate FSM transitions
        old_state, new_state = self.fsm.update(self, {"context": context, "nearby": nearby})
        if new_state:
            print(f"[FSM] Entity {self.id:04d} transitioned: {old_state} -> {new_state}")

    def update(self, bounds=(1000, 1000)):
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        # Boundary collision / reflection
        max_x, max_y = bounds
        if not 0 <= self.x <= max_x:
            self.velocity[0] *= -1
            self.x = max(0.0, min(max_x, self.x))
        if not 0 <= self.y <= max_y:
            self.velocity[1] *= -1
            self.y = max(0.0, min(max_y, self.y))

        self.timer += 1
