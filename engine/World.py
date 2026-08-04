"""
OROBORO Engine - World Module (Template)
Manages spatial distribution, particle simulation ticks, and global context fields.
"""

from .particle import Particle

class World:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height
        self.particles = []
        self.tick_count = 0
        self.global_metrics = {}

    def add_particle(self, particle):
        self.particles.append(particle)

    def step(self, context=None):
        ctx = context or {}
        # Evaluate spatial interactions
        for particle in self.particles:
            nearby = particle.observe(self.particles)
            particle.evaluate(ctx, nearby)

        # Update physical positions
        for particle in self.particles:
            particle.update((self.width, self.height))

        self.tick_count += 1

    def get_state_snapshot(self):
        return {
            "tick": self.tick_count,
            "particle_count": len(self.particles),
            "particles": [
                {
                    "id": p.id,
                    "x": p.x,
                    "y": p.y,
                    "state": p.fsm.state,
                    "metadata": p.metadata
                }
                for p in self.particles
            ]
        }
