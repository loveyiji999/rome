from core.turn_flow import TurnFlow

class Race:
    def __init__(self, car_states, segments, events, seed=0):
        """
        car_states: list of CarState instances (player first, then AIs)
        segments: list of TrackSegment instances
        events: list of Event instances
        seed: base random seed
        """
        self.flows = []
        for i, car in enumerate(car_states):
            flow = TurnFlow(car, segments, seed=seed + i, events=events,
                            is_player=(i == 0), personality=car.personality if hasattr(car, 'personality') else 'balanced')
            self.flows.append(flow)
        # store per-flow per-turn times
        self.results = {flow: [] for flow in self.flows}

    def run(self, laps):
        """
        Run the race for given number of laps.
        Uses lock-step simulation: each segment, collect times for all cars then update.
        """
        segments_per_lap = len(self.flows[0].segments)
        total_segments = laps * segments_per_lap
        for seg_idx in range(total_segments):
            # lock-step: collect times for this segment for all flows
            times = []
            for flow in self.flows:
                segment_time = flow.simulate_turn()
                times.append(segment_time)
            # record results after all have simulated this segment
            for flow, t in zip(self.flows, times):
                self.results[flow].append(t)

    def standings(self):
        """
        Return list of tuples (flow, total_time) sorted by total_time ascending.
        """
        totals = {flow: sum(self.results[flow]) for flow in self.flows}
        # sort by time
        sorted_flows = sorted(totals.items(), key=lambda x: x[1])
        return sorted_flows

    def print_standings(self):
        print("\n===== 最終排名 =====")
        standings = self.standings()
        for pos, (flow, total) in enumerate(standings, start=1):
            name = flow.car_state.name if hasattr(flow.car_state, 'name') else f'Car{pos}'
            print(f"第 {pos} 名: {name} ，總用時: {total:.2f}s")
