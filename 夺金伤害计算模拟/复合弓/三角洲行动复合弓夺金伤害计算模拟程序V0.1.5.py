from decimal import Decimal, ROUND_HALF_UP

def round_decimal(value, decimals):
    d = Decimal(str(value))
    rounded = d.quantize(Decimal('0.' + '0'*decimals), rounding=ROUND_HALF_UP)
    return float(rounded)

print("本程序由B站繁星攻略组制作")
print("注：受限于数据精度问题，本程序给出的所有时间相关计算仅供参考，与实际存在一定误差")

# 部位倍率字典（基础值）
base_location_multipliers = {
    "头部": 1.7,
    "胸部": 1,
    "腹部": 0.9,
    "下腹部": 0.9,
    "大臂": 0.45,
    "小臂": 0.45,
    "大腿": 0.45,
    "小腿": 0.45
}

# 增强弓弦后的部位倍率
enhanced_location_multipliers = {
    "头部": 2.0,  # 头部倍率提升
    "胸部": 1,
    "腹部": 0.9,
    "下腹部": 0.9,
    "大臂": 0.45,
    "小臂": 0.45,
    "大腿": 0.45,
    "小腿": 0.45
}

# 箭矢参数
arrows = {
    1: {
        "name": "玻纤柳叶箭矢",
        "penetration": 3,
        "damage_multiplier": 1.0,
        "armor_attenuation": [0.9, 0.9, 0.9, 1.0, 0.5, 0.4],
        "armor_multiplier": 1.0
    },
    2: {
        "name": "碳纤维刺骨箭矢",
        "penetration": 4,
        "damage_multiplier": 1.0,
        "armor_attenuation": [1.0, 1.0, 1.0, 1.0, 1.1, 0.6],
        "armor_multiplier": 1.0
    },
    3: {
        "name": "碳纤维穿甲箭矢",
        "penetration": 5,
        "damage_multiplier": 1.0,
        "armor_attenuation": 1.1,  # 恒定值
        "armor_multiplier": 1.0
    }
}

# 护甲类型保护部位
armor_protection = {
    1: ["胸部", "腹部"],         # 半甲
    2: ["胸部", "腹部", "下腹部"], # 全甲
    3: ["胸部", "腹部", "下腹部", "大臂"]  # 重甲
}

def get_float_input(prompt, min_val, max_val, decimals=1):
    while True:
        try:
            value = float(input(prompt))
            value = round_decimal(value, decimals)
            if min_val <= value <= max_val:
                return value
            print(f"输入值必须在 {min_val} 到 {max_val} 之间")
        except ValueError:
            print("请输入有效的数字")

def get_int_input(prompt, min_val, max_val):
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            print(f"输入值必须在 {min_val} 到 {max_val} 之间")
        except ValueError:
            print("请输入有效的整数")

def get_yes_no_input(prompt):
    while True:
        response = input(prompt).strip().lower()
        if response in ["y", "yes", "是", "1"]:
            return True
        elif response in ["n", "no", "否", "0"]:
            return False
        print("请输入 '是' 或 '否'")

def get_arrow_armor_attenuation(arrow_type, armor_level):
    arrow_data = arrows[arrow_type]
    if arrow_type == 3:
        return arrow_data["armor_attenuation"]
    if 1 <= armor_level <= 6:
        return arrow_data["armor_attenuation"][armor_level - 1]
    return 1.0  # 默认值

def calculate_penetration_rate(penetration, armor_level, is_head=False):
    """
    计算穿透伤害倍率
    is_head: 是否命中头部（头部使用不同的计算规则）
    """
    if penetration < armor_level:
        # 穿透等级小于防护等级
        return max(0.16 - (armor_level - penetration) * 0.02, 0.02)
    elif penetration == armor_level:
        # 穿透等级等于防护等级
        return 0.5 if is_head else 0.75
    elif penetration == armor_level + 1:
        # 穿透等级等于防护等级+1
        return 0.75 if is_head else 0.9
    else:  # penetration >= armor_level + 2
        # 穿透等级大于等于防护等级+2
        return 1.0

def main():
    print("===== 弓箭伤害模拟器 =====")
    
    # 玩家初始状态
    health = 100.0
    helmet_durability = get_float_input("输入头盔耐久 (0.0-60.0): ", 0.0, 60.0)
    helmet_level = get_int_input("输入头盔防护等级 (0-6, 0表示无头盔): ", 0, 6)
    armor_durability = get_float_input("输入护甲耐久 (0.0-150.0): ", 0.0, 150.0)
    armor_level = get_int_input("输入护甲防护等级 (0-6, 0表示无护甲): ", 0, 6)
    distance = get_float_input("输入目标距离 (0.0-200.0): ", 0.0, 200.0)
    armor_type = get_int_input("输入护甲类型 (1-半甲, 2-全甲, 3-重甲): ", 1, 3)
    arrow_type = get_int_input("输入箭矢类型 (1-玻纤柳叶, 2-碳纤维刺骨, 3-碳纤维穿甲): ", 1, 3)
    
    # 新增：是否装配增强弓弦
    enhanced_string = get_yes_no_input("是否装配增强弓弦? (是/否): ")
    
    # 根据是否使用增强弓弦选择部位倍率字典
    location_multipliers = enhanced_location_multipliers if enhanced_string else base_location_multipliers
    
    # 武器衰减倍率 - 增强弓弦影响距离阈值
    if enhanced_string:
        weapon_attenuation = 1.0 if distance <= 84.5 else 0.9
    else:
        weapon_attenuation = 1.0 if distance <= 65 else 0.9
    
    shot_interval = 500  # 毫秒（射击间隔）
    
    # 统计信息
    total_damage = 0.0
    total_armor_damage = 0.0
    location_hits = {loc: 0 for loc in location_multipliers}
    location_hits["未命中"] = 0
    total_hits = 0
    total_shots = 0
    total_time_ms = 0  # 总耗时（毫秒）
    shot_type_count = {"瞬发": 0, "满蓄": 0}  # 记录射击方式使用次数
    
    # 显示当前配置
    print("\n===== 当前配置 =====")
    print(f"头盔: {helmet_durability:.1f}耐久, {helmet_level}级防护")
    print(f"护甲: {armor_durability:.1f}耐久, {armor_level}级防护, 类型{armor_type}")
    print(f"距离: {distance:.1f}米")
    print(f"箭矢: {arrows[arrow_type]['name']}")
    print(f"增强弓弦: {'已装配' if enhanced_string else '未装配'}")
    print(f"武器衰减倍率: {weapon_attenuation:.1f} (距离阈值: {'84.5' if enhanced_string else '65'}米)")
    if enhanced_string:
        print("头部倍率提升至2.0")
    print("="*20)
    print("每次攻击前需要选择射击方式：")
    print("1 = 瞬发 (基础伤害76.5, 护甲伤害55.25, 拉弓时间80ms)")
    print("2 = 满蓄 (基础伤害90.0, 护甲伤害65.0, 拉弓时间{}ms)".format(460 if enhanced_string else 540))
    
    # 主循环
    while health > 0:
        # 输入本次射击方式
        shot_mode = ""
        while shot_mode not in ["1", "2"]:
            shot_mode = input("\n输入本次射击方式 (1=瞬发, 2=满蓄): ")
        
        if shot_mode == "1":
            # 瞬发
            base_damage_this = 76.5
            base_armor_damage_this = 55.25
            draw_time_this = 80  # 毫秒（拉弓时间）
            shot_type = "瞬发"
        else:
            # 满蓄
            base_damage_this = 90.0
            base_armor_damage_this = 65.0
            draw_time_this = 460 if enhanced_string else 540  # 毫秒（拉弓时间）
            shot_type = "满蓄"
        
        shot_type_count[shot_type] += 1
        
        location = input("输入命中部位 (头部/胸部/腹部/下腹部/大臂/小臂/大腿/小腿/未命中): ")
        
        # 处理未命中
        if location == "未命中":
            total_shots += 1
            location_hits["未命中"] += 1
            # 更新总时间：本次拉弓时间 + 如果是第一次射击则不加间隔，否则加上间隔
            total_time_ms += draw_time_this
            if total_shots > 1:
                total_time_ms += shot_interval
            print(f"{shot_type}未命中! 耗时: {total_time_ms/1000:.3f}秒")
            continue
        
        # 验证部位输入
        if location not in location_multipliers:
            print("无效部位! 请重新输入")
            continue
        
        total_shots += 1
        total_hits += 1
        location_hits[location] += 1
        
        # 更新总时间：本次拉弓时间 + 如果是第一次射击则不加间隔，否则加上间隔
        total_time_ms += draw_time_this
        if total_shots > 1:
            total_time_ms += shot_interval
        
        # 获取部位倍率
        location_mult = location_multipliers[location]
        
        # 确定保护状态
        protected = False
        armor_damage_taken = 0.0
        penetration_rate = 1.0
        armor_dmg_value = 0.0
        gear_type = ""
        gear_durability = 0.0
        gear_level = 0
        
        # 头部命中处理
        if location == "头部":
            if helmet_level > 0 and helmet_durability > 0:
                protected = True
                gear_type = "头盔"
                gear_durability = helmet_durability
                gear_level = helmet_level
        # 身体部位命中处理
        else:
            if armor_level > 0 and armor_durability > 0 and location in armor_protection[armor_type]:
                protected = True
                gear_type = "护甲"
                gear_durability = armor_durability
                gear_level = armor_level
        
        # 伤害计算
        if not protected or gear_level == 0:  # 未受保护
            damage = base_damage_this * location_mult * weapon_attenuation
            armor_damage_taken = 0.0
        else:
            # 获取箭矢参数
            arrow_data = arrows[arrow_type]
            penetration = arrow_data["penetration"]
            
            # 计算护甲衰减倍率
            armor_attenuation = get_arrow_armor_attenuation(arrow_type, gear_level)
            
            # 计算护甲伤害值
            armor_dmg_value = base_armor_damage_this * arrow_data["armor_multiplier"] * armor_attenuation * weapon_attenuation
            armor_dmg_value = round_decimal(armor_dmg_value, 1)
            
            # 计算穿透倍率 - 头部使用特殊规则
            is_head = (location == "头部")
            penetration_rate = calculate_penetration_rate(penetration, gear_level, is_head)
            
            # 计算实际伤害
            if gear_durability >= armor_dmg_value:
                # 公式a: 护甲完全吸收
                damage = base_damage_this * arrow_data["damage_multiplier"] * location_mult * penetration_rate * weapon_attenuation
                armor_damage_taken = armor_dmg_value
                new_durability = gear_durability - armor_damage_taken
            else:
                # 公式b: 护甲部分击穿
                ratio = gear_durability / armor_dmg_value
                damage_part1 = base_damage_this * arrow_data["damage_multiplier"] * location_mult * penetration_rate * weapon_attenuation
                damage_part2 = base_damage_this * arrow_data["damage_multiplier"] * location_mult * weapon_attenuation
                damage = ratio * damage_part1 + (1 - ratio) * damage_part2
                armor_damage_taken = gear_durability
                new_durability = 0.0
            
            # 更新装备耐久
            if gear_type == "头盔":
                helmet_durability = new_durability
            else:
                armor_durability = new_durability
        
        # 四舍五入伤害值
        damage = round_decimal(damage, 2)
        
        # 更新玩家状态
        health -= damage
        total_damage += damage
        total_armor_damage += armor_damage_taken
        
        # 输出结果
        print(f"\n{shot_type}命中 {location}!")
        print(f"造成伤害: {damage:.2f}")
        
        if protected:
            print(f"{gear_type}损失耐久: {armor_damage_taken:.1f}")
            if gear_durability > 0 and armor_damage_taken >= gear_durability:
                print(f"⚔️ {gear_type}已击碎!")
        
        if health > 0:
            print(f"剩余生命: {round_decimal(health, 1):.1f}")
            print(f"头盔耐久: {round_decimal(helmet_durability, 1):.1f}")
            print(f"护甲耐久: {round_decimal(armor_durability, 1):.1f}")
        else:
            print("💀 你死了!")
            print(f"最终头盔耐久: {round_decimal(helmet_durability, 1):.1f}")
            print(f"最终护甲耐久: {round_decimal(armor_durability, 1):.1f}")
            input("按回车键结束模拟计算")
            break
    
    # 输出统计信息
    print("\n===== 战斗统计 =====")
    print(f"总伤害: {total_damage:.2f}")
    print(f"总护甲伤害: {total_armor_damage:.1f}")
    print(f"总攻击次数: {total_shots}")
    print(f"总命中次数: {total_hits}")
    print(f"总耗时: {total_time_ms/1000:.3f}秒")
    
    print("\n射击方式统计:")
    for shot_type, count in shot_type_count.items():
        if count > 0:
            print(f"{shot_type}: {count}次")
    
    print("\n部位命中统计:")
    for loc, count in location_hits.items():
        if count > 0:
            print(f"{loc}: {count}次")

if __name__ == "__main__":
    main()