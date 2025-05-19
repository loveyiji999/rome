import unittest
import os
import sys

# 確保可以從 tests 以外匯入核心模組
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.event_engine import Event
from core.turn_flow import TurnFlow
from core.track_loader import TrackSegment, TrackType

class DummyCarState:
    def __init__(self):
        self.data = {
            "speed_module": {"speed": 100, "acceleration": 10, "top_speed": 150},
            "handling_module": {"handling": 1.0},
            "fuel_module": {"fuel": 50, "consumption_rate": 0}
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

class TestEventPriority(unittest.TestCase):
    def test_high_priority_triggers_first(self):
        car = DummyCarState()
        segment = TrackSegment("T1", TrackType.STRAIGHT, {"length": 100})
        events_data = [
            {
                "id": "low",
                "category": "Test",
                "name": "LowPriority",
                "description": [],
                "trigger": {"segment_type": ["Straight"], "conditions": [{"name": "Always"}], "probability": 1.0},
                "options": [{"key": "A", "consequences": []}],
                "priority": 1,
            },
            {
                "id": "high",
                "category": "Test",
                "name": "HighPriority",
                "description": [],
                "trigger": {"segment_type": ["Straight"], "conditions": [{"name": "Always"}], "probability": 1.0},
                "options": [{"key": "A", "consequences": []}],
                "priority": 5,
            },
        ]
        events = [Event(d) for d in events_data]
        severity_order = {"high": 0, "medium": 1, "low": 2}
        events.sort(key=lambda e: (severity_order.get(e.severity, 1), -e.priority))
        flow = TurnFlow(car, [segment], seed=42, events=events, is_player=False)
        flow.simulate_turn()
        self.assertEqual(flow.log[0]["event"], "HighPriority")

if __name__ == "__main__":
    unittest.main()
