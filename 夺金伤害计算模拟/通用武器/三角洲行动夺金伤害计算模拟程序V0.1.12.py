import sys
from decimal import Decimal, ROUND_HALF_UP

print("本程序由B站繁星攻略组制作")

def get_decimal_input(prompt, min_val, max_val, decimal_places):
    while True:
        try:
            value = input(prompt)
            # 使用 Decimal 进行精确处理
            decimal_value = Decimal(value)
            
            # 四舍五入到指定小数位
            quantized = decimal_value.quantize(
                Decimal('1.' + '0' * decimal_places), 
                rounding=ROUND_HALF_UP
            )
            
            # 转换为浮点数进行范围检查
            float_val = float(quantized)
            if min_val <= float_val <= max_val:
                return quantized
            else:
                print(f"输入错误，范围{min_val}到{max_val}，请重新输入。")
        except Exception as e:
            print(f"输入错误: {str(e)}，请输入有效的数字。")

def get_int_input(prompt, min_val, max_val):
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"输入错误，范围{min_val}到{max_val}，请重新输入。")
        except ValueError:
            print("输入错误，请输入整数。")

# 初始化参数
print("=== 初始化参数 ===")
helmet_durability = get_decimal_input("请输入头盔耐久（0.0-60.0）：", 0.0, 60.0, 1)
armor_durability = get_decimal_input("请输入护甲耐久（0.0-150.0）：", 0.0, 150.0, 1)
helmet_level = get_int_input("请输入头盔防护等级（0-6）：", 0, 6)
armor_level = get_int_input("请输入护甲防护等级（0-6）：", 0, 6)
armor_type = get_int_input("\n请输入护甲类型（1-半甲，2-全甲，3-重甲）：", 1, 3)

# 子弹参数
print("\n=== 子弹参数 ===")
bullet_level = get_int_input("请输入穿透等级（0-6）：", 0, 6)
base_damage_multiplier = get_decimal_input("请输入基础伤害倍率（0.10-5.00）：", 0.10, 5.00, 2)
base_armor_multiplier = get_decimal_input("请输入基础护甲倍率（0.10-5.00）：", 0.10, 5.00, 2)
armor_decay_multiplier = get_decimal_input("请输入护甲衰减倍率（0.00-1.20）：", 0.00, 1.20, 2)

# 武器参数
print("\n=== 武器参数 ===")
weapon_damage = get_int_input("请输入武器基础伤害（0-150）：", 0, 150)
weapon_armor_damage = get_int_input("请输入武器护甲伤害（0-100）：", 0, 100)
fire_rate = get_int_input("请输入每分钟射速（1-1500）：", 1, 1500)
weapon_decay_multiplier = get_decimal_input("请输入武器衰减倍率（0.00-1.00）：", 0.00, 1.00, 2)
trigger_delay = get_int_input("请输入扳机延迟（0-300ms）：", 0, 300)
fire_mode = get_int_input("请输入射击模式（1-全自动，2-半自动）：", 1, 2)

# 部位倍率参数
body_parts = ['头部', '胸部', '腹部', '大臂', '小臂', '大腿', '小腿']
body_part_multipliers = {}
print("\n=== 输入部位倍率 ===")
for part in body_parts:
    multiplier = get_decimal_input(f"请输入{part}的倍率（0.000-3.000）：", 0.000, 3.000, 3)
    body_part_multipliers[part] = multiplier
body_part_multipliers['下腹部'] = body_part_multipliers['腹部']

# 计算射击间隔 (使用 Decimal 计算)
shot_interval = (Decimal('60000') / Decimal(str(fire_rate))).quantize(
    Decimal('0.01'), rounding=ROUND_HALF_UP
)

# 初始化状态 (全部使用 Decimal)
player_health = Decimal('100.0')
current_helmet_durability = helmet_durability
current_armor_durability = armor_durability
protected_areas = {
    1: ['胸部', '腹部'],
    2: ['胸部', '腹部', '下腹部'],
    3: ['胸部', '腹部', '下腹部', '大臂']
}[armor_type]
valid_parts = ['头部', '胸部', '腹部', '大臂', '小臂', '大腿', '小腿', '下腹部', '未命中']

hit_count = 0
total_time = Decimal('0.0')
total_damage = Decimal('0.0')
total_armor_damage = Decimal('0.0')
hit_statistics = {part: 0 for part in valid_parts}

print("\n=== 开始模拟计算 ===")
while True:
    # 输入命中部位
    while True:
        hit_part = input("\n请输入命中部位（或输入'未命中'/exit）：").strip()
        if hit_part.lower() == 'exit':
            sys.exit()
        if hit_part in valid_parts:
            hit_statistics[hit_part] += 1
            hit_count += 1
            break
        print("无效输入，请重新输入。")

    # 计算总耗时 (使用 Decimal 计算)
    trigger_delay_dec = Decimal(str(trigger_delay))
    if fire_mode == 1:  # 全自动
        total_time = trigger_delay_dec + shot_interval * Decimal(str(hit_count - 1))
    else:  # 半自动
        total_time = (trigger_delay_dec * Decimal(str(hit_count))) + (shot_interval * Decimal(str(hit_count - 1)))
    
    # 四舍五入总耗时
    total_time = total_time.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # 处理未命中
    if hit_part == '未命中':
        print("\n=== 计算结果 ===")
        print("本次攻击未命中")
        print(f"累计耗时：{total_time} ms")
        continue

    # 伤害计算逻辑
    is_protected = False
    protector_level = 0
    protector_type = None
    current_protector_durability = Decimal('0.0')

    # 判断保护状态
    if hit_part == '头部':
        if helmet_level > 0 and current_helmet_durability > Decimal('0'):
            is_protected = True
            protector_level = helmet_level
            protector_type = 'helmet'
            current_protector_durability = current_helmet_durability
    else:
        if armor_level > 0 and current_armor_durability > Decimal('0') and hit_part in protected_areas:
            is_protected = True
            protector_level = armor_level
            protector_type = 'armor'
            current_protector_durability = current_armor_durability

    # 计算穿透倍率
    penetration_multiplier = Decimal('0.0')
    if is_protected:
        diff = bullet_level - protector_level
        if diff < 0:
            penetration_multiplier = Decimal('0.0')
        elif diff == 0:
            penetration_multiplier = Decimal('0.5')
        elif diff == 1:
            penetration_multiplier = Decimal('0.75')
        else:
            penetration_multiplier = Decimal('1.0')

    # 计算护甲伤害 (使用 Decimal 计算)
    weapon_armor_damage_dec = Decimal(str(weapon_armor_damage))
    armor_damage_value = weapon_armor_damage_dec * base_armor_multiplier * armor_decay_multiplier * weapon_decay_multiplier
    final_damage = Decimal('0.0')
    protector_destroyed = False
    armor_damage_dealt = Decimal('0.0')

    if is_protected:
        # 计算剩余耐久 (使用 Decimal 四舍五入)
        remaining_durability = current_protector_durability - armor_damage_value
        if remaining_durability <= Decimal('0'):
            protector_destroyed = True
            remaining_durability = Decimal('0.0')
        else:
            # 四舍五入到1位小数
            remaining_durability = remaining_durability.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

        # 累计护甲伤害
        armor_damage_dealt = current_protector_durability - remaining_durability
        total_armor_damage += armor_damage_dealt

        # 计算伤害 (使用 Decimal 计算)
        part_multiplier = body_part_multipliers[hit_part]
        denominator = weapon_armor_damage_dec * base_armor_multiplier * armor_decay_multiplier * weapon_decay_multiplier
        
        if denominator == Decimal('0'):
            ratio = Decimal('0.0')
        else:
            ratio = current_protector_durability / denominator

        weapon_damage_dec = Decimal(str(weapon_damage))
        
        if current_protector_durability >= armor_damage_value:
            final_damage = weapon_damage_dec * base_damage_multiplier * part_multiplier * penetration_multiplier * weapon_decay_multiplier
        else:
            part1 = ratio * weapon_damage_dec * base_damage_multiplier * part_multiplier * penetration_multiplier * weapon_decay_multiplier
            part2 = (Decimal('1') - ratio) * weapon_damage_dec * base_damage_multiplier * part_multiplier * weapon_decay_multiplier
            final_damage = part1 + part2
        
        # 四舍五入伤害值
        final_damage = final_damage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # 更新耐久
        if protector_type == 'helmet':
            current_helmet_durability = remaining_durability
        else:
            current_armor_durability = remaining_durability
    else:
        # 未受保护 (使用 Decimal 计算)
        part_multiplier = body_part_multipliers[hit_part]
        weapon_damage_dec = Decimal(str(weapon_damage))
        final_damage = weapon_damage_dec * base_damage_multiplier * part_multiplier * weapon_decay_multiplier
        # 四舍五入伤害值
        final_damage = final_damage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    total_damage += final_damage
    player_health -= final_damage

    # 输出结果
    print("\n=== 计算结果 ===")
    if is_protected:
        if protector_type == 'helmet':
            print("头盔被击碎！" if protector_destroyed else "头盔未被击碎。")
            print(f"头盔损失耐久：{armor_damage_dealt.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}")
        else:
            print("护甲被击碎！" if protector_destroyed else "护甲未被击碎。")
            print(f"护甲损失耐久：{armor_damage_dealt.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}")
    elif hit_part == '头部' and helmet_level > 0:
        print("（未受头盔保护）")

    print(f"受到伤害：{final_damage}")
    print(f"剩余生命值：{player_health.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}")
    print(f"剩余头盔耐久：{current_helmet_durability}")
    print(f"剩余护甲耐久：{current_armor_durability}")
    print(f"累计耗时：{total_time} ms")

    # 死亡处理
    if player_health <= Decimal('0'):
        print("\n=== 最终统计 ===")
        print(f"射击模式：{'全自动' if fire_mode == 1 else '半自动'}")
        print(f"总造成伤害：{total_damage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}")
        print(f"总护甲伤害：{total_armor_damage.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}")
        
        print("\n命中统计：")
        total_shots = sum(hit_statistics.values())
        valid_hits = total_shots - hit_statistics['未命中']
        display_order = ['未命中', '头部', '胸部', '腹部', '下腹部', '大臂', '小臂', '大腿', '小腿']
        for part in display_order:
            count = hit_statistics.get(part, 0)
            if count > 0:
                print(f"{part.ljust(5)}：{count}次")
        
        print(f"\n有效命中次数：{valid_hits}次")
        print(f"总攻击次数：{total_shots}次")
        print(f"击杀耗时：{total_time} ms")
        
        input("\n按回车键结束模拟计算...")
        break