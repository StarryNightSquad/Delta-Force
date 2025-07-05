import math
import re

print("本程序由B站繁星攻略组与用户Dec128合作制作")

def validate_float_input(prompt, min_val, max_val, decimal_places, value_name):
    """验证浮点数输入，确保格式、范围和精度"""
    while True:
        value = input(prompt)
        try:
            # 格式校验（最多指定小数位）
            pattern = rf'^\d+(\.\d{{0,{decimal_places}}})?$'
            if not re.match(pattern, value):
                raise ValueError(f"最多允许{decimal_places}位小数")
            
            num = float(value)
            if num < min_val:
                raise ValueError(f"不能小于{min_val}")
            if num > max_val:
                raise ValueError(f"不能大于{max_val}")
            
            # 规范小数位数（不四舍五入，仅截断）
            num = float(f"{num:.{decimal_places}f}")
            return num
        except ValueError as e:
            print(f"{value_name}输入错误：{e}，请重新输入")

def validate_int_input(prompt, min_val, max_val, value_name):
    """验证整数输入，确保范围和格式"""
    while True:
        value = input(prompt)
        try:
            num = int(value)
            if num < min_val:
                raise ValueError(f"不能小于{min_val}")
            if num > max_val:
                raise ValueError(f"不能大于{max_val}")
            return num
        except ValueError:
            print(f"{value_name}输入错误：必须为整数，请重新输入")

def main():
    print("=== 装备维修计算器 ===")
    
    # 输入物品类别
    item_type = input("请输入物品类别（头盔/护甲）：").strip()
    while item_type not in ["头盔", "护甲"]:
        print("错误：物品类别只能是'头盔'或'护甲'")
        item_type = input("请重新输入物品类别（头盔/护甲）：").strip()

    # 输入各项参数（带严格校验）
    current_upper = validate_float_input(
        "请输入当前上限（1-150，最多1位小数）：",
        1, 150, 1, "当前上限"
    )
    
    initial_upper = validate_int_input(
        "请输入初始上限（1-150整数）：",
        1, 150, "初始上限"
    )
    
    remaining_durability = validate_float_input(
        "请输入剩余耐久（0-150，最多1位小数）：",
        0, 150, 1, "剩余耐久"
    )
    
    repair_loss = validate_float_input(
        "请输入维修损耗（0-0.2，最多2位小数）：",
        0, 0.2, 2, "维修损耗"
    )
    
    repair_price = validate_int_input(
        "请输入维修单价（大于0的整数）：",
        1, 1000000000, "维修单价"
    )

    # 处理当前上限（去尾法取整）
    current_upper_processed = int(current_upper)

    # 维修可行性判定（严格遵循要求）
    print("\n=== 维修可行性判定 ===")
    if item_type == "护甲" and current_upper_processed < 10:
        print(f"当前护甲上限({current_upper_processed})小于10，不可维修")
    elif item_type == "头盔" and current_upper_processed < 5:
        print(f"当前头盔上限({current_upper_processed})小于5，不可维修")
    else:
        print("装备符合维修条件，开始计算...")
        
        try:
            # 计算公式组件
            term1 = (current_upper_processed - remaining_durability) / current_upper_processed
            
            # 对数计算安全校验
            if current_upper_processed <= 0 or initial_upper <= 0:
                raise ValueError("对数计算参数必须大于0")
                
            log_value = current_upper_processed / initial_upper
            term2 = repair_loss - math.log10(log_value)
            
            # 计算维修后上限
            repaired_upper = current_upper_processed - current_upper_processed * term1 * term2 * 1.25
        except Exception as e:
            print(f"\n计算错误：{e}")
            input("\n按回车结束程序")
            return

        # 结果处理（严格遵循要求）
        # 1. 去尾法精确到个位数
        final_upper = int(repaired_upper)  # 去尾取整
        
        # 2. 若小于1则强制为1
        if final_upper < 1:
            final_upper = 1
        
        # 计算维修花费（剩余耐久取整）
        remaining_int = int(remaining_durability)
        repair_cost = (final_upper - remaining_int + 1) * repair_price * 1.25
        
        # 花费不能为负
        if repair_cost < 0:
            repair_cost = 0

        print("\n=== 计算结果 ===")
        print(f"维修后耐久上限：{final_upper}")
        print(f"维修花费：{repair_cost:,}")  # 千位分隔符格式化

    input("\n按回车结束程序")

if __name__ == "__main__":
    main()