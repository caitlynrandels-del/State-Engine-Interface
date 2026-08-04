"""
OROBORO Engine - State & FSM Module (Template)
Generic Finite State Machine and State Transition Manager for Agent-Based Simulation.
"""

import random

class StateMachine:
    def __init__(self, initial_state="IDLE"):
        self.state = initial_state
        self.timer = 0
        self.transitions = {}

    def add_transition(self, from_state, to_state, condition_fn):
        if from_state not in self.transitions:
            self.transitions[from_state] = []
        self.transitions[from_state].append({
            "to": to_state,
            "condition": condition_fn
        })

    def update(self, entity, context):
        self.timer += 1
        if self.state in self.transitions:
            for t in self.transitions[self.state]:
                if t["condition"](entity, context):
                    old_state = self.state
                    self.state = t["to"]
                    self.timer = 0
                    return old_state, self.state
        return None, None
