import unittest
import os
import sys

# 允許匯入專案模組
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.event_engine import Event
from core.turn_flow import TurnFlow
from core.track_loader import TrackSegment, TrackType


class DummyCarState:
    def __init__(self):
        self.data = {
            "speed_module": {"speed": 100, "acceleration": 10, "top_speed": 150},
            "handling_module": {"handling": 1.0},
            "fuel_module": {"fuel": 50, "consumption_rate": 0},
        }

    def get(self, key_path):
        d = self.data
        for part in key_path.split('.'):
            d = d.get(part, {})
        return d if d != {} else 0

    def apply_change(self, target, method, value):
        parts = target.split('.')
        d = self.data
        for p in parts[:-1]:
            d = d.setdefault(p, {})
        k = parts[-1]
        if method == 'set':
            d[k] = value
        elif method == 'add':
            d[k] = d.get(k, 0) + value
        elif method == 'multiply':
            d[k] = d.get(k, 1) * value

    def summary(self):
        return {}


class TestTurnFlowMultiEvents(unittest.TestCase):
    def test_solo_event_blocks_others(self):
        car = DummyCarState()
        segment = TrackSegment("S", TrackType.STRAIGHT, {"length": 100})
        events_data = [
            {
                "id": "solo",
                "category": "fault",
                "name": "SoloEvent",
                "description": [],
                "trigger": {"segment_type": ["Straight"], "conditions": [{"name": "Always"}], "probability": 1.0},
                "options": [{"key": "A", "consequences": []}],
                "solo": True,
                "priority": 5,
            },
            {
                "id": "normal",
                "category": "tactic",
                "name": "NormalEvent",
                "description": [],
                "trigger": {"segment_type": ["Straight"], "conditions": [{"name": "Always"}], "probability": 1.0},
                "options": [{"key": "A", "consequences": []}],
                "priority": 1,
            },
        ]
        events = [Event(d) for d in events_data]
        flow = TurnFlow(car, [segment], seed=1, events=events, is_player=False)
        flow.simulate_turn()
        self.assertEqual(flow.log[0]["events"], ["SoloEvent"])

    def test_straight_limit_single_fault(self):
        car = DummyCarState()
        segment = TrackSegment("S", TrackType.STRAIGHT, {"length": 100})
        events_data = [
            {
                "id": "f1",
                "category": "fault",
                "name": "Fault1",
                "description": [],
                "trigger": {"segment_type": ["Straight"], "conditions": [{"name": "Always"}], "probability": 1.0},
                "options": [{"key": "A", "consequences": []}],
                "priority": 5,
            },
            {
                "id": "f2",
                "category": "fault",
                "name": "Fault2",
                "description": [],
                "trigger": {"segment_type": ["Straight"], "conditions": [{"name": "Always"}], "probability": 1.0},
                "options": [{"key": "A", "consequences": []}],
                "priority": 4,
            },
        ]
        events = [Event(d) for d in events_data]
        flow = TurnFlow(car, [segment], seed=2, events=events, is_player=False)
        flow.simulate_turn()
        self.assertEqual(flow.log[0]["events"], ["Fault1"])

    def test_corner_allows_two_faults(self):
        car = DummyCarState()
        segment = TrackSegment("C", TrackType.MEDIUM_CORNER, {"length": 100})
        events_data = [
            {
                "id": "f1",
                "category": "fault",
                "name": "Fault1",
                "description": [],
                "trigger": {"segment_type": ["Medium Corner"], "conditions": [{"name": "Always"}], "probability": 1.0},
                "options": [{"key": "A", "consequences": []}],
                "priority": 5,
            },
            {
                "id": "f2",
                "category": "fault",
                "name": "Fault2",
                "description": [],
                "trigger": {"segment_type": ["Medium Corner"], "conditions": [{"name": "Always"}], "probability": 1.0},
                "options": [{"key": "A", "consequences": []}],
                "priority": 4,
            },
        ]
        events = [Event(d) for d in events_data]
        flow = TurnFlow(car, [segment], seed=3, events=events, is_player=False)
        flow.simulate_turn()
        self.assertEqual(set(flow.log[0]["events"]), {"Fault1", "Fault2"})


if __name__ == "__main__":
    unittest.main()

