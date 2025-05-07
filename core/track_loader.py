import yaml
from enum import Enum

# --- 切片類型列舉 ---
class TrackType(Enum):
    STRAIGHT = "Straight"
    LONG_STRAIGHT = "Long Straight"
    MEDIUM_CORNER = "Medium Corner"
    SLOW_CORNER = "Slow Corner"
    CHICANE = "Chicane"
    UPHILL = "Uphill"
    DOWNHILL = "Downhill"
    ROUGH_PATCH = "Rough Patch"
    WET_SECTION = "Wet Section"
    PIT_ENTRY = "Pit Entry"
    CROSSWIND_ZONE = "Crosswind Zone"
    HAIRPIN_RETURN = "Hairpin Return"

# --- 賽道切片資料類別 ---
class TrackSegment:
    def __init__(self, segment_id, track_type: TrackType, attributes: dict):
        self.id = segment_id
        self.track_type = track_type
        self.attributes = attributes
        self.base_event_chance = attributes.get("base_event_chance", 0.05)
        self.recommended_speed = attributes.get("recommended_speed", None)
        self.avg_time = attributes.get("estimated_avg_time", None)

    def __repr__(self):
        return f"<Segment {self.id} - {self.track_type.value}>"

# --- 讀取 YAML 檔並建立切片列表 ---
def load_track_segments(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    segments = []
    for entry in data:
        track_type = TrackType(entry['track_type'])  # 字串轉 Enum
        segment = TrackSegment(entry['id'], track_type, entry['attributes'])
        segments.append(segment)
    return segments

if __name__ == "__main__":
    segments = load_track_segments("track_config.yaml")
    for seg in segments:
        print(seg)
        print("  屬性：", seg.attributes)
