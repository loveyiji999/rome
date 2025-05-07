# condition_parser.py

def evaluate_condition(cond: dict, car_state, context: dict) -> bool:
    """
    根據條件名稱與參數，回傳 True / False 判定是否滿足
    :param cond: e.g. { name: "FuelBelow", params: { threshold: 20 } }
    :param car_state: CarState 物件
    :param context: 額外參數，例如 current_lap, distance_to_ai, slipstream_status
    """
    name = cond["name"]
    params = cond.get("params", {})

    if name == "Always":
        return True

    elif name == "FuelBelow":
        fuel = car_state.get("fuel_module.fuel")
        return fuel < params.get("threshold", 20)

    elif name == "TireWearAbove":
        wear = car_state.get("tire_module.tire_wear")
        return wear > params.get("threshold", 60)

    elif name == "DistanceLessThan":
        return context.get("distance_to_ai", 999) < params.get("threshold", 2.0)

    elif name == "LapsCompletedOver":
        return car_state.get("race_info_module.laps_completed") > params.get("count", 3)

    elif name == "InSlipstream":
        return context.get("slipstream_active", False)

    else:
        # 其他未實作條件，預設為不滿足
        return False
