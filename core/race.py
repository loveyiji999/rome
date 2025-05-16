from core.turn_flow import TurnFlow

class Race:
    """
    鎖步模擬多車賽事
    對每輛車建立一個 TurnFlow，並同時間段同時執行 simulate_turn。
    """
    def __init__(self, car_states, segments, events, seed=0):
        # car_states: list of CarState instances, 0 索引為玩家，其餘為 AI
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
            self.flows.append(flow)
        # 紀錄所有 flow 每段的用時
        self.results = {flow: [] for flow in self.flows}

    def run(self, laps):
        """
        執行指定圈數的賽事。
        鎖步機制：每段先收集所有車的 segment_time，再一次性更新狀態。
        """
        total_segments = laps * len(self.flows[0].segments)
        for _ in range(total_segments):
            # 收集本段所有車的用時
            segment_times = []
            for flow in self.flows:
                t = flow.simulate_turn()
                segment_times.append(t)
            # 鎖步更新：記錄結果後再進下一段
            for flow, t in zip(self.flows, segment_times):
                self.results[flow].append(t)

    def standings(self):
        """
        根據所有車的總時間排序，回傳 [(flow, total_time), ...]
        """
        totals = {flow: sum(times) for flow, times in self.results.items()}
        # 按時間升序排序
        sorted_list = sorted(totals.items(), key=lambda x: x[1])
        return sorted_list

    def print_standings(self):
        """
        CLI 輸出最終排行榜。
        """
        print("\n===== 最終排名 =====")
        for idx, (flow, total) in enumerate(self.standings(), start=1):
            name = getattr(flow.car_state, 'name', f'Car{idx}')
            print(f"第 {idx} 名: {name}，總用時: {total:.2f}s")
