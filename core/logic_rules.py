# core/logic_rules.py (v2)
# 擴充至涵蓋 40 項屬性連動，模擬賽車因果邏輯變化

def apply_logic_rules(car_state):
    fuel = car_state.get("fuel_module.fuel")
    engine_temp = car_state.get("engine_module.engine_temp")
    overheat = car_state.get("engine_module.overheat_threshold")
    tire_temp = car_state.get("tire_module.surface_temp")
    tire_wear = car_state.get("tire_module.tire_wear")
    tire_pressure = car_state.get("tire_module.tire_pressure")
    grip = car_state.get("tire_module.grip_coefficient")
    drag = car_state.get("aero_module.drag_coefficient")
    downforce = car_state.get("aero_module.downforce")
    slipstream = car_state.get("aero_module.slipstream_bonus")
    brake_eff = car_state.get("brake_module.brake_efficiency")
    brake_wear = car_state.get("brake_module.brake_wear")
    accel = car_state.get("speed_module.acceleration")
    speed = car_state.get("speed_module.speed")
    durability = car_state.get("durability_module.durability")
    chassis = car_state.get("durability_module.chassis_health")
    mech = car_state.get("durability_module.mechanical_integrity")
    laps = car_state.get("race_info_module.laps_completed")

    # 油量變化 → 重量變化 → 加速度變化
    if fuel < 40:
        car_state.apply_change("speed_module.acceleration", "multiply", 1.05)

    # 引擎溫度高於過熱點 → 煞車退化
    if engine_temp > overheat:
        car_state.apply_change("brake_module.brake_efficiency", "multiply", 0.9)

    # 輪胎溫度過熱 → 抓地下降
    if tire_temp > 100:
        car_state.apply_change("tire_module.grip_coefficient", "multiply", 0.95)

    # 輪胎磨損 >80% → 操控 & 耐久下降
    if tire_wear > 80:
        car_state.apply_change("handling_module.handling", "multiply", 0.85)
        car_state.apply_change("durability_module.durability", "add", -3)

    # 輪胎壓過低 → 抓地提升但耐久下降
    if tire_pressure < 28:
        car_state.apply_change("tire_module.grip_coefficient", "multiply", 1.03)
        car_state.apply_change("durability_module.durability", "add", -2)

    # 剎車磨損上升 → 剎車效率下降
    if brake_wear > 60:
        car_state.apply_change("brake_module.brake_efficiency", "multiply", 0.8)

    # 空氣阻力過高 → 速度下降
    if drag > 0.5:
        car_state.apply_change("speed_module.speed", "multiply", 0.92)

    # 高下壓力 → 抓地上升 + 油耗上升
    if downforce > 300:
        car_state.apply_change("tire_module.grip_coefficient", "multiply", 1.08)
        car_state.apply_change("fuel_module.fuel_per_lap", "add", 0.3)

    # 加速度過高 → 引擎溫度上升 + 油耗變快
    if accel > 20:
        car_state.apply_change("engine_module.engine_temp", "add", 4)
        car_state.apply_change("fuel_module.consumption_rate", "multiply", 1.1)

    # 引擎溫度升高 → 冷卻效率下降
    if engine_temp > 90:
        car_state.apply_change("engine_module.cooling_efficiency", "multiply", 0.95)

    # 輪胎抓地係數太低 → 操控性下降
    if grip < 0.85:
        car_state.apply_change("handling_module.handling", "multiply", 0.9)

    # 耐久過低 → 速度下降
    if durability < 50:
        car_state.apply_change("speed_module.speed", "multiply", 0.95)

    # 底盤健康下降 → 剎車熱衰減加速
    if chassis < 60:
        car_state.apply_change("brake_module.brake_fade_rate", "add", 0.02)

    # 機械完整度下降 → 加速度與耐久下降
    if mech < 70:
        car_state.apply_change("speed_module.acceleration", "multiply", 0.95)
        car_state.apply_change("durability_module.durability", "add", -2)

    # 使用尾流加成 → 空氣阻力下降 + 速度上升
    if slipstream:
        car_state.apply_change("aero_module.drag_coefficient", "multiply", 0.9)
        car_state.apply_change("speed_module.speed", "multiply", 1.03)

    # 比賽進行超過 10 圈 → 胎耗與疲勞上升
    if laps > 10:
        car_state.apply_change("tire_module.tire_wear", "add", 5)
        car_state.apply_change("fuel_module.economy_rating", "multiply", 0.98)