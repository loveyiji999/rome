import os
import yaml

# 對應字串關鍵字 → mutex 群組名稱
mutex_map = {
    "engine": ["engine_misfire", "engine_overheat", "cooling_system", "misfire"],
    "tire": ["tire_pressure", "tire_compound", "tire_temp", "grip"],
    "brake": ["brake_fade", "brake_fluid", "brake_pad"],
    "pit": ["pit_entry", "pit_stop", "early_pit"],
    "ai_attack": ["dive_bomb", "inside_dive", "block_maneuver", "overtake_attempt"],
    "strategy_slot": ["fuel_mode", "battery_save", "drs_available", "push_to_pass"]
}

def match_mutex(event_id):
    for mutex, keywords in mutex_map.items():
        for kw in keywords:
            if kw in event_id:
                return mutex
    return None

def apply_mutex_to_events(event_dir):
    for fname in os.listdir(event_dir):
        if fname.endswith(".yaml"):
            full_path = os.path.join(event_dir, fname)
            with open(full_path, "r", encoding="utf-8") as f:
                events = yaml.safe_load(f)

            modified = False
            for event in events:
                if "mutex" not in event:
                    mutex = match_mutex(event["id"])
                    if mutex:
                        event["mutex"] = mutex
                        modified = True

            if modified:
                with open(full_path, "w", encoding="utf-8") as f:
                    yaml.dump(events, f, allow_unicode=True, sort_keys=False)
                print(f"已加入 mutex 至：{fname}")

if __name__ == "__main__":
    apply_mutex_to_events("data/events")