# core/map_loader.py

import yaml
from core.track_loader import load_track_segments

def load_track_map(map_path, segment_db):
    """
    根據 track_map.yaml 載入賽道地圖，轉換為 TrackSegment 實體清單
    :param map_path: str, 地圖檔案路徑
    :param segment_db: list[TrackSegment], 所有可用切片
    :return: (map_info, segments)
    """
    with open(map_path, "r", encoding="utf-8") as f:
        map_data = yaml.safe_load(f)

    id_to_segment = {seg.id: seg for seg in segment_db}
    segment_ids = map_data["segments"]
    lap_count = map_data.get("lap_count", 1)

    full_track = []
    for _ in range(lap_count):
        for seg_id in segment_ids:
            if seg_id in id_to_segment:
                full_track.append(id_to_segment[seg_id])
            else:
                raise ValueError(f"track_map 中找不到切片 ID: {seg_id}")

    return map_data, full_track