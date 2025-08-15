print("本程序由B站繁星攻略组制作")

import decimal
import math
from decimal import Decimal, ROUND_HALF_UP

# 设置decimal上下文环境
decimal.getcontext().rounding = ROUND_HALF_UP

# 常量定义
MAX_HEALTH = 100
BASE_DAMAGE = Decimal('112')
SHOOT_INTERVAL = Decimal('500')  # ms
BODY_PARTS = {
    "头部": Decimal('1.9'),
    "胸部": Decimal('1.125'),
    "腹部": Decimal('1'),
    "大臂": Decimal('1'),
    "小臂": Decimal('1'),
    "大腿": Decimal('0.9'),
    "小腿": Decimal('0.9')
}
TRIGGER_DELAY = {
    "速射": Decimal('80'),
    "满蓄": Decimal('540')
}
SHOOT_MODE_FACTOR = {
    "速射": Decimal('0.7'),
    "满蓄": Decimal('1.0')
}

def get_attenuation(distance):
    """根据距离计算衰减倍率"""
    if distance <= 10:
        return Decimal('1.0')
    elif distance <= 30:
        return Decimal('0.9')
    elif distance <= 50:
        return Decimal('0.8')
    else:
        return Decimal('0.7')

def validate_distance(value):
    """验证距离输入是否有效"""
    try:
        distance = Decimal(value)
        if distance < 0 or distance > 200:
            return False
        # 检查是否为一位小数
        if abs(distance * 10 - int(distance * 10)) > 0:
            return False
        return True
    except:
        return False

def calculate_damage(attenuation, body_multiplier, shoot_mode_factor):
    """计算单次伤害值"""
    damage = BASE_DAMAGE * attenuation * body_multiplier * shoot_mode_factor
    return damage.quantize(Decimal('0.00'))

def calculate_shots_needed(damage):
    """计算致死所需攻击次数"""
    if damage >= MAX_HEALTH:
        return 1
    return math.ceil(MAX_HEALTH / damage)

def calculate_total_time(attack_count, trigger_delay):
    """计算总耗时（毫秒）"""
    if attack_count == 0:
        return Decimal('0')
    return (trigger_delay * attack_count + 
            SHOOT_INTERVAL * (attack_count - 1))

def main():
    print("复合弓模拟计算器")
    print("=" * 50)
    
    # 获取有效距离输入
    while True:
        distance = input("请输入目标距离(0-200米，一位小数): ").strip()
        if validate_distance(distance):
            distance = Decimal(distance)
            break
        print("无效输入! 请输入0-200范围内的一位小数")
    
    # 获取有效射击方式输入
    while True:
        shoot_mode = input("请输入射击方式(速射/满蓄): ").strip()
        if shoot_mode in TRIGGER_DELAY:
            break
        print("无效输入! 请输入'速射'或'满蓄'")
    
    # 计算衰减倍率
    attenuation = get_attenuation(distance)
    
    # 获取射击模式因子
    shoot_mode_factor = SHOOT_MODE_FACTOR[shoot_mode]
    
    # 计算并显示各部位结果
    body_parts = ["头部", "胸部", "腹部", "大臂", "小臂", "大腿", "小腿"]
    
    print("\n各部位致死次数及耗时:")
    print("-" * 50)
    
    for part in body_parts:
        # 计算伤害
        multiplier = BODY_PARTS[part]
        damage = calculate_damage(attenuation, multiplier, shoot_mode_factor)
        
        # 计算攻击次数
        attacks = calculate_shots_needed(float(damage))
        
        # 计算总耗时（毫秒）
        time_ms = calculate_total_time(attacks, TRIGGER_DELAY[shoot_mode])
        time_ms = time_ms.quantize(Decimal('1'))  # 取整毫秒值
        
        # 格式化输出
        hits_str = f"{attacks}次"
        time_str = f"{time_ms}ms"
        
        print(f"{part.ljust(4)}：{hits_str.ljust(8)}，耗时{time_str}")
    
    print("=" * 50)
    
    # 结束程序
    input("\n按回车键结束模拟计算")

if __name__ == "__main__":
    main()
