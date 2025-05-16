import random
from core.turn_flow import TurnFlow
from core.track_loader import TrackType

class Race:
    """
    鎖步模擬多車賽事，並維持動態距離與尾流狀態
    """
    def __init__(self, car_states, segments, events, seed=0):
        self.flows = []
        for i, car in enumerate(car_states):
            flow = TurnFlow(
                car_state=car,
                segments=segments,
                events=events,
                seed=seed + i,
                is_player=(i == 0),
                personality=getattr(car, 'personality', 'balanced')
            )
            # 初始化距離
            flow.distance_to_ai = None
            self.flows.append(flow)
        self.results = {flow: [] for flow in self.flows}

    def update_distances(self):
        # 根據累計時間計算與前車間距
        sorted_flows = sorted(self.flows, key=lambda f: f.total_time)
        for idx, flow in enumerate(sorted_flows):
            if idx == 0:
                flow.distance_to_ai = float('inf')
            else:
                front = sorted_flows[idx - 1]
                gap_time = flow.total_time - front.total_time
                avg_speed = flow.car_state.get('speed_module.speed') or 0
                speed_mps = avg_speed / 3.6
                flow.distance_to_ai = gap_time * speed_mps

    def run(self, laps):
        total_segments = laps * len(self.flows[0].segments)
        for _ in range(total_segments):
            # 鎖步前先更新動態距離與尾流
            self.update_distances()

            # 收集本段所有車的用時
            segment_times = []
            for flow in self.flows:
                t = flow.simulate_turn()
                segment_times.append(t)
            # 記錄本段結果
            for flow, t in zip(self.flows, segment_times):
                self.results[flow].append(t)

    def standings(self):
        totals = {flow: sum(times) for flow, times in self.results.items()}
        return sorted(totals.items(), key=lambda x: x[1])

    def print_standings(self):
        print("\n===== 最終排名 =====")
        for idx, (flow, total) in enumerate(self.standings(), start=1):
            name = getattr(flow.car_state, 'name', f'Car{idx}')
            print(f"第 {idx} 名: {name}，總用時: {total:.2f}s")
