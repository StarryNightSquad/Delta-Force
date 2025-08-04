print("本程序由B站繁星攻略组制作")

import openpyxl
import time
from itertools import product
import heapq

# 读取武器数据
def read_weapons(file_path):
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb["夺金模式"]
    except Exception as e:
        print(f"读取武器数据时出错: {e}")
        return [], [], []
    
    weapons = []  # 所有武器
    rifles = []   # 非手枪武器
    pistols = []  # 手枪
    
    current_category = None
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if row[0] is not None:  # 分类行
            current_category = row[0]
            continue
            
        if row[1] is None:  # 空行
            continue
            
        name = row[1]
        market = row[2]
        battle = row[3]
        
        # 处理空白或无效值 - 不在此处排除，在后续过滤中处理
        item = {
            "name": name,
            "market": market,
            "battle": battle,
            "type": "weapon" if current_category != "手枪" else "pistol",
            "category": current_category
        }
        
        weapons.append(item)
        
        if current_category != "手枪":
            rifles.append(item)
        else:
            pistols.append(item)
    
    return weapons, rifles, pistols

# 读取装备数据
def read_equipments(file_path):
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb["护甲数据"]
    except Exception as e:
        print(f"读取装备数据时出错: {e}")
        return [], [], [], []
    
    armors = []    # 护甲
    helmets = []   # 头盔
    chests = []    # 胸挂/弹挂
    backpacks = [] # 背包
    
    current_category = None
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if row[0] is not None:  # 主分类
            current_category = row[0]
            continue
            
        if row[1] is None:  # 空行
            continue
            
        name = row[1]
        market = row[2]
        battle = row[3]
        quality = row[6]  # G列是品质列
        
        # 处理空白或无效值 - 不在此处排除，在后续过滤中处理
        item = {
            "name": name,
            "market": market,
            "battle": battle,
            "quality": quality,
            "category": current_category
        }
        
        if current_category == "护甲":
            armors.append(item)
        elif current_category == "头盔":
            helmets.append(item)
        elif current_category == "胸挂":
            chests.append(item)
        elif current_category == "背包":
            backpacks.append(item)
    
    return armors, helmets, chests, backpacks

# 筛选物品
def filter_items(items, min_battle_value, exclude_high_value=False, is_specified=False):
    valid_items = [{"name": "空", "market": 0, "battle": 0, "quality": 0}]
    
    for item in items:
        # 对于用户指定的装备，跳过所有过滤条件
        if is_specified:
            valid_items.append(item)
            continue
            
        # 处理市场价值为/或空的情况 - 在非指定时排除
        if item["market"] in [None, "/", ""]:
            continue
            
        # 处理战备价值为/或空的情况 - 在非指定时排除
        if item["battle"] in [None, "/", ""]:
            continue
            
        # 尝试转换为数值
        try:
            market = float(item["market"]) if item["market"] not in [None, "/", ""] else 0
            battle = float(item["battle"]) if item["battle"] not in [None, "/", ""] else 0
        except (ValueError, TypeError):
            continue
            
        # 跳过市场价值过高的物品
        if exclude_high_value and market >= battle + 2000:
            continue
            
        # 跳过市场价值超过目标战备值的物品
        if market >= min_battle_value:
            continue
            
        # 添加有效物品
        valid_items.append({
            "name": item["name"],
            "market": market,
            "battle": battle,
            "quality": item.get("quality", 0)
        })
    
    return valid_items

# 获取品质名称
def get_quality_name(quality_num):
    qualities = {
        0: "无",
        1: "1级",
        2: "2级",
        3: "3级",
        4: "4级",
        5: "5级",
        6: "6级"
    }
    return qualities.get(quality_num, f"未知({quality_num})")

# 统计品阶装备数量
def count_equipment_by_quality(items, quality_range=(1, 6)):
    quality_count = {}
    for q in range(quality_range[0], quality_range[1] + 1):
        count = sum(1 for item in items 
                   if item.get("quality") == q 
                   and item["market"] not in [None, "/", ""]  # 只统计有效物品
                   and item["battle"] not in [None, "/", ""])
        quality_count[q] = count
    return quality_count

# 主程序
def main():
    print("=" * 50)
    print("战备价值计算器")
    print("=" * 50)
    
    # 读取数据
    try:
        weapons, rifles, pistols = read_weapons("S5武器价格.xlsx")
        armors, helmets, chests, backpacks = read_equipments("S5装备价格.xlsx")
        print("数据读取成功!")
        
        # 打印一些统计数据
        print(f"读取到 {len(rifles)} 件武器, {len(pistols)} 件手枪")
        print(f"读取到 {len(armors)} 件护甲, {len(helmets)} 件头盔")
        print(f"读取到 {len(chests)} 件胸挂, {len(backpacks)} 件背包")
    except Exception as e:
        print(f"读取数据时出错: {e}")
        input("按 Enter 键退出程序...")
        return
    
    # 用户选择是否指定携行具
    while True:
        spec = input("\n是否指定携行具? (是/否): ").strip()
        if spec in ["是", "否"]:
            specify_gear = (spec == "是")
            break
        else:
            print("请输入'是'或'否'")
    
    selected_chest = None
    selected_backpack = None
    
    # 统计品阶装备数量
    chest_quality_count = count_equipment_by_quality(chests)
    backpack_quality_count = count_equipment_by_quality(backpacks)
    
    if specify_gear:
        # 胸挂选择
        print("\n选择胸挂等级:")
        print(f"0: 无 ({chest_quality_count.get(0, 0)}件)")
        for q in range(1, 7):
            count = chest_quality_count.get(q, 0)
            print(f"{q}: {get_quality_name(q)} ({count}件)")
        
        while True:
            try:
                chest_quality = int(input("请输入等级编号 (0-6): "))
                if 0 <= chest_quality <= 6:
                    break
                else:
                    print("请输入0-6之间的数字")
            except ValueError:
                print("请输入有效的数字")
        
        if chest_quality > 0:
            # 按等级筛选胸挂 - 用户指定时不过滤
            quality_chests = [c for c in chests if c.get("quality") == chest_quality]
            quality_name = get_quality_name(chest_quality)
            
            if not quality_chests:
                print(f"\n{quality_name}的胸挂没有可选项")
            else:
                print(f"\n可选的胸挂 ({quality_name}, 共{len(quality_chests)}件):")
                for i, chest in enumerate(quality_chests, 1):
                    # 显示市场价值，即使为/或空
                    market_display = chest["market"] if chest["market"] not in [None, "/", ""] else "无市场价值"
                    battle_display = chest["battle"] if chest["battle"] not in [None, "/", ""] else "无战备价值"
                    print(f"{i}: {chest['name']} (市场:{market_display}, 战备:{battle_display})")
                
                while True:
                    try:
                        chest_choice = int(input(f"请选择胸挂编号 (1-{len(quality_chests)}): "))
                        if 1 <= chest_choice <= len(quality_chests):
                            selected_chest = quality_chests[chest_choice - 1]
                            print(f"已选择: {selected_chest['name']}")
                            break
                        else:
                            print(f"请输入1-{len(quality_chests)}之间的数字")
                    except ValueError:
                        print("请输入有效的数字")
        else:
            print("未选择胸挂")
        
        # 背包选择
        print("\n选择背包等级:")
        print(f"0: 无 ({backpack_quality_count.get(0, 0)}件)")
        for q in range(1, 7):
            count = backpack_quality_count.get(q, 0)
            print(f"{q}: {get_quality_name(q)} ({count}件)")
        
        while True:
            try:
                backpack_quality = int(input("请输入等级编号 (0-6): "))
                if 0 <= backpack_quality <= 6:
                    break
                else:
                    print("请输入0-6之间的数字")
            except ValueError:
                print("请输入有效的数字")
        
        if backpack_quality > 0:
            # 按等级筛选背包 - 用户指定时不过滤
            quality_backpacks = [b for b in backpacks if b.get("quality") == backpack_quality]
            
            if not quality_backpacks:
                quality_name = get_quality_name(backpack_quality)
                print(f"\n{quality_name}的背包没有可选项")
            else:
                quality_name = get_quality_name(backpack_quality)
                print(f"\n可选的背包 ({quality_name}, 共{len(quality_backpacks)}件):")
                for i, backpack in enumerate(quality_backpacks, 1):
                    # 显示市场价值，即使为/或空
                    market_display = backpack["market"] if backpack["market"] not in [None, "/", ""] else "无市场价值"
                    battle_display = backpack["battle"] if backpack["battle"] not in [None, "/", ""] else "无战备价值"
                    print(f"{i}: {backpack['name']} (市场:{market_display}, 战备:{battle_display})")
                
                while True:
                    try:
                        backpack_choice = int(input(f"请选择背包编号 (1-{len(quality_backpacks)}): "))
                        if 1 <= backpack_choice <= len(quality_backpacks):
                            selected_backpack = quality_backpacks[backpack_choice - 1]
                            print(f"已选择: {selected_backpack['name']}")
                            break
                        else:
                            print(f"请输入1-{len(quality_backpacks)}之间的数字")
                    except ValueError:
                        print("请输入有效的数字")
        else:
            print("未选择背包")
    
    # 用户输入目标战备价值
    while True:
        try:
            min_battle_value = int(input("\n请输入目标战备价值: "))
            if min_battle_value > 0:
                break
            else:
                print("请输入大于0的整数")
        except ValueError:
            print("请输入有效的整数")
    
    start_time = time.time()
    
    print("\n正在计算最优组合...")
    
    # 筛选各槽位物品
    filtered_rifles = filter_items(rifles, min_battle_value, specify_gear)
    filtered_pistols = filter_items(pistols, min_battle_value, specify_gear)
    filtered_armors = filter_items(armors, min_battle_value, specify_gear)
    filtered_helmets = filter_items(helmets, min_battle_value, specify_gear)
    
    # 处理用户指定的携行具 - 使用特殊过滤函数
    chest_items = [selected_chest] if selected_chest else filter_items(chests, min_battle_value, specify_gear)
    backpack_items = [selected_backpack] if selected_backpack else filter_items(backpacks, min_battle_value, specify_gear)
    
    # 生成所有可能的组合
    combinations = []
    
    # 计算总组合数
    total_combinations = len(filtered_rifles) * len(filtered_pistols) * len(filtered_helmets) * len(filtered_armors) * len(chest_items) * len(backpack_items)
    if total_combinations > 0:
        print(f"共有 {total_combinations} 种可能的装备组合...")
    else:
        print("没有有效的装备组合，请检查输入条件")
        input("\n按 Enter 键退出程序...")
        return
    
    count = 0
    last_update = time.time()
    
    # 使用笛卡尔积生成所有组合
    for combo in product(
        filtered_rifles, 
        filtered_pistols, 
        filtered_helmets, 
        filtered_armors, 
        chest_items, 
        backpack_items
    ):
        count += 1
        rifle, pistol, helmet, armor, chest, backpack = combo
        
        # 处理市场价值为/或空的情况 - 视为0
        def safe_value(val):
            if val in [None, "/", ""]:
                return 0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0
        
        # 计算总价值
        total_battle = (
            safe_value(rifle["battle"]) + 
            safe_value(pistol["battle"]) + 
            safe_value(helmet["battle"]) + 
            safe_value(armor["battle"]) + 
            safe_value(chest["battle"]) + 
            safe_value(backpack["battle"])
        )
        
        total_market = (
            safe_value(rifle["market"]) + 
            safe_value(pistol["market"]) + 
            safe_value(helmet["market"]) + 
            safe_value(armor["market"]) + 
            safe_value(chest["market"]) + 
            safe_value(backpack["market"])
        )
        
        # 只保留满足战备要求的组合
        if total_battle >= min_battle_value:
            # 使用堆来维护最小的3个组合
            if len(combinations) < 3:
                heapq.heappush(combinations, (-total_market, total_battle, total_market, combo))
            else:
                heapq.heappushpop(combinations, (-total_market, total_battle, total_market, combo))
        
        # 每10万次显示一次进度
        if time.time() - last_update > 5 and count % 100000 == 0 and total_combinations > 100000:
            progress = count / total_combinations * 100
            print(f"计算进度: {progress:.2f}% ({count}/{total_combinations})")
            last_update = time.time()
    
    # 转换堆为有序列表
    top_combinations = []
    while combinations:
        neg_market, battle, market, combo = heapq.heappop(combinations)
        top_combinations.append((market, battle, combo))
    
    top_combinations.sort(key=lambda x: x[0])  # 按市场价值从低到高排序
    
    # 输出结果
    print("\n" + "=" * 50)
    print(f"计算完成! 耗时: {time.time() - start_time:.2f}秒")
    print(f"找到 {len(top_combinations)} 个满足条件的组合:")
    
    slot_names = ["武器", "手枪", "头盔", "护甲", "胸挂", "背包"]
    
    for idx, (total_market, total_battle, combo) in enumerate(top_combinations, 1):
        print("\n" + "-" * 50)
        print(f"组合 #{idx} (总市场价值: {total_market}, 总战备价值: {total_battle}):")
        
        for slot, item in zip(slot_names, combo):
            if item:  # 确保item不为空
                quality_name = get_quality_name(item.get("quality", 0))
                
                # 处理市场价值显示
                market_display = item["market"]
                if market_display in [None, "/", ""]:
                    market_display = "无市场价值"
                
                # 处理战备价值显示
                battle_display = item["battle"]
                if battle_display in [None, "/", ""]:
                    battle_display = "无战备价值"
                
                print(f"  {slot}: {item['name']} ({quality_name}, 市场: {market_display}, 战备: {battle_display})")
            else:
                print(f"  {slot}: 空")
    
    input("\n按 Enter 键退出程序...")

if __name__ == "__main__":
    main()
