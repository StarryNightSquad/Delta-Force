import math
import decimal
from decimal import Decimal, ROUND_HALF_UP

print("本程序由B站繁星攻略组制作")

def input_float_with_decimal(prompt, min_val, max_val, decimal_places):
    while True:
        s = input(prompt)
        if not s.replace('.', '', 1).lstrip('-').isdigit():
            print("输入的不是有效的数字，请重新输入。")
            continue
        try:
            # 使用 Decimal 进行精确计算
            value = Decimal(s)
        except decimal.InvalidOperation:
            print("输入的不是有效的数字，请重新输入。")
            continue
        if value < min_val or value > max_val:
            print(f"数值必须在{min_val}到{max_val}之间，请重新输入。")
            continue
        # 四舍五入到指定小数位
        value = value.quantize(Decimal('1.' + '0'*decimal_places), rounding=ROUND_HALF_UP)
        return value

def input_integer(prompt, min_val, max_val):
    while True:
        s = input(prompt)
        if not s.isdigit():
            print("输入的不是有效的整数，请重新输入。")
            continue
        value = int(s)
        if value < min_val or value > max_val:
            print(f"请输入{min_val}到{max_val}之间的整数。")
            continue
        return value

def input_fire_mode():
    while True:
        mode = input("请输入射击模式（1=全自动，2=半自动）：").strip()
        if mode in ['1', '2']:
            return int(mode)
        print("请输入有效的选项（1或2）")

# 输入武器参数
base_damage = input_integer("请输入武器的基础伤害（0-150的整数）：", 0, 150)
rpm = input_integer("请输入武器的每分钟射速（1-1500的整数）：", 1, 1500)
decay_multiplier = input_float_with_decimal("请输入衰减倍率（0-1，两位小数）：", Decimal('0.0'), Decimal('1.0'), 2)
trigger_delay = input_integer("请输入扳机延迟（0-200ms的整数）：", 0, 200)
fire_mode = input_fire_mode()

# 计算射击间隔（使用 Decimal）
shooting_interval = (Decimal('60000') / Decimal(rpm)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

# 输入部位倍率（新顺序，下腹部自动继承腹部数值）
body_parts = ['头部', '胸部', '腹部', '大臂', '小臂', '大腿', '小腿']
multipliers = {}
for part in body_parts:
    prompt = f"请输入{part}的倍率（0-3，最多三位小数）："
    multipliers[part] = input_float_with_decimal(prompt, Decimal('0.0'), Decimal('3.0'), 3)

# 下腹部继承腹部倍率
multipliers['下腹部'] = multipliers['腹部']

# 处理各部位（排除下腹部）
parts_to_output = ['头部', '胸部', '腹部', '大臂', '小臂', '大腿', '小腿']
results = []
for part in parts_to_output:
    multiplier = multipliers[part]
    # 使用 Decimal 计算伤害
    dmg_per_shot = Decimal(base_damage) * multiplier * decay_multiplier
    
    # 四舍五入到小数点后两位
    dmg_per_shot = dmg_per_shot.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    
    if dmg_per_shot <= Decimal('0'):
        hits_str = "无法致死"
        time_str = "无法计算"
    else:
        # 计算致死次数（向上取整）
        hits = math.ceil(Decimal('100') / dmg_per_shot)
        
        # 根据射击模式计算耗时
        if fire_mode == 1:  # 全自动模式
            time_ms = Decimal(trigger_delay) + shooting_interval * (Decimal(hits) - Decimal('1'))
        else:  # 半自动模式
            time_ms = (Decimal(trigger_delay) * Decimal(hits)) + shooting_interval * (Decimal(hits) - Decimal('1'))
        
        # 四舍五入到小数点后两位
        time_ms = time_ms.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        
        hits_str = f"{hits}次"
        time_str = f"{time_ms}ms"
    
    results.append((part, hits_str, time_str))

# 输出结果
print("\n各部位致死次数及耗时：")
for part, hits, time in results:
    print(f"{part}：{hits}，耗时{time}")

# 结束提示
input("按回车键结束模拟计算")