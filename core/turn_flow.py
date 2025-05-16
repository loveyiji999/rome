import random
from core.logic_rules import apply_logic_rules

class TurnFlow:
    def __init__(self, car_state, segments, seed=None, events=None, is_player=False, personality='balanced'):
        self.car_state = car_state
        self.segments = segments
        self.current_turn = 0
        self.current_lap_time = 0.0
        self.total_time = 0.0
        self.log = []
        self.seed = seed or random.randint(1000, 999999)
        self.random = random.Random(self.seed)
        self.all_events = events or []
        self.is_player = is_player
        self.personality = personality

    def get_current_segment(self):
        index = self.current_turn % len(self.segments)
        return self.segments[index]

    def choose_option_for_ai(self, event):
        # 根據 AI 性格與隨機性決定選項，可擴充為 weighted/softmax
        keys = [opt['key'] for opt in event.options]
        return self.random.choice(keys)

    def choose_numeric_for_ai(self, mu):
        # 使用高斯分布模擬 AI 回應值
        sigma_map = {'conservative': 1, 'balanced': 2, 'aggressive': 3}
        sigma = sigma_map.get(self.personality, 2)
        val = self.random.gauss(mu, sigma)
        return max(1, min(10, round(val)))

    def simulate_turn(self):
        self.current_turn += 1
        segment = self.get_current_segment()
        pre_state = self.car_state.summary()

        # 初始化 context，包含所有會在 Expression 中使用到的欄位
        context = {
            'fuel': self.car_state.get('fuel_module.fuel') or 0,
            'tire_wear': self.car_state.get('tire_module.tire_wear') or 0,
            'distance_to_ai': 1.5,
            'slipstream_active': True,
            'laps_completed': self.car_state.get('race_info_module.laps_completed') or 0,
            'last_lap_time': getattr(self, 'current_lap_time', 0.0),
            'target_lap_time': getattr(self, 'target_lap_time', 0.0),
            'gap_to_trailer': self.car_state.get('race_info_module.gap_to_leader') or 0,
            'num_ai_adjacent': getattr(self, 'num_ai_adjacent', 0)
        }

        triggered_event = None
        option_key = None
        feedback = None
        triggered_name = 'None'
        candidates = []
        triggered_mutex = set()

        # 事件檢測與套用
        for event in self.all_events:
            if event.mutex and event.mutex in triggered_mutex:
                continue
            if event.is_triggered(segment, self.car_state, self.random, context):
                candidates.append(event.name)
                if not triggered_event:
                    triggered_event = event
                    triggered_name = event.name
                    # 玩家或 AI 選擇
                    if self.is_player:
                        option_key = 'A'  # TODO: 等待玩家輸入
                    else:
                        option_key = self.choose_option_for_ai(event)
                    feedback = event.apply_option(option_key, self.car_state)
                    event.cooldown_remaining = event.cooldown
                    if event.mutex:
                        triggered_mutex.add(event.mutex)

        # 計算段落用時（單位轉換：速度 km/h → m/s，長度 m）
        speed_kmh = self.car_state.get('speed_module.speed') or 1
        # km/h → m/s：除以 3.6
        speed_mps = speed_kmh / 3.6
        length_m = getattr(segment, 'length', 1)   # 賽道切片長度單位為公尺 :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
        # 避免除以零
        if speed_mps <= 0:
            base_time = float('inf')
        else:
            base_time = length_m / speed_mps

        segment_time = base_time
        self.current_lap_time += segment_time
        self.total_time += segment_time

        # 記錄日誌
        post_state = self.car_state.summary()
        self.log.append({
            'turn': self.current_turn,
            'segment': getattr(segment, 'id', None),
            'segment_type': segment.track_type.value,
            'event': triggered_name,
            'option': option_key,
            'pre_state': pre_state,
            'post_state': post_state,
            'time': segment_time
        })

        print(f"第 {self.current_turn} 回合 - 區段：{segment.track_type.value} - 可觸發事件：{candidates}")
        if triggered_event:
            print(f"→ 實際觸發事件：{triggered_event.name}，選擇：{option_key}，反饋：{feedback}")

        # 更新冷卻與邏輯規則
        for event in self.all_events:
            if event.cooldown_remaining > 0:
                event.cooldown_remaining -= 1
        apply_logic_rules(self.car_state)

        return segment_time

    def print_log(self):
        print("\n===== 回合事件紀錄 =====")
        for entry in self.log:
            print(f"【第 {entry['turn']} 回合】{entry['segment_type']} → 事件：{entry['event']} 用時：{entry['time']:.2f}s")
            print(f"  前：{entry['pre_state']}")
            print(f"  後：{entry['post_state']}\n")
