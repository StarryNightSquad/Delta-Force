import math

print("本程序由B站繁星攻略组与用户Dec128合作制作")

def get_input(prompt, validate_func):
    """通用输入验证函数"""
    while True:
        try:
            value = input(prompt).strip().replace('？', '?')
            result = validate_func(value)
            return result
        except ValueError as e:
            print(f"错误：{e}")

# 输入参数（按验证依赖顺序）
# 1. 初始上限验证
initial_max = get_input(
    "请输入初始上限（1-150整数）: ",
    lambda v: int(v) if v.isdigit() and 1 <= int(v) <= 150 
        else ValueError("必须为1-150的整数")
)

# 2. 当前上限验证
current_max = get_input(
    f"请输入当前上限（一位小数，≤{initial_max}）: ",
    lambda v: round(float(v), 1) if (temp := round(float(v), 1)) <= initial_max 
        else ValueError(f"不得超过{initial_max}且需一位小数")
)

# 3. 剩余耐久验证
remaining_durability = get_input(
    f"请输入剩余耐久（一位小数，≤{current_max}）: ",
    lambda v: round(float(v), 1) if (temp := round(float(v), 1)) <= current_max 
        else ValueError(f"不得超过{current_max}且需一位小数")
)

# 4. 维修损耗验证
repair_loss = get_input(
    "请输入维修损耗（0.01-0.20，两位小数）: ",
    lambda v: round(float(v), 2) if 0.01 <= (temp := round(float(v), 2)) <= 0.20 
        else ValueError("必须为0.01-0.20之间的两位小数")
)

# 5. 维修包效率验证（范围0.01-10）
repair_packages = []
for name in ["自制", "标准", "精密", "高级维修组合"]:
    efficiency = get_input(
        f"请输入{name}维修包效率（0.01-10，两位小数，?代表未知）: ",
        lambda v: None if v == '?' 
            else round(float(v), 2) if 0.01 <= (temp := round(float(v), 2)) <= 10 
            else ValueError("必须为0.01-10之间的两位小数或?")
    )
    repair_packages.append((name, efficiency))

# 计算维修后上限
try:
    # 计算比率
    ratio = (current_max - remaining_durability) / current_max if current_max > 0 else 0
    
    # 计算对数项
    log_term = math.log10(current_max / initial_max) if current_max > 0 and initial_max > 0 else 0
    
    # 计算维修后上限
    repaired_max = current_max - current_max * ratio * (repair_loss - log_term)
    
    # 四舍五入到2位小数用于点数计算
    repaired_max_calculation = round(repaired_max, 2)
    
    # 四舍五入到1位小数用于展示
    repaired_max_display = round(repaired_max, 1)
    
except (ZeroDivisionError, ValueError) as e:
    repaired_max_calculation = 0
    repaired_max_display = 0

# 结果输出
print("\n===== 维修计算结果 =====")
if repaired_max_calculation <= 0:
    print("无法维修（维修后耐久≤0）")
else:
    print(f"维修后上限：{repaired_max_display:.1f}")
    print("消耗维修点数：")
    
    for name, eff in repair_packages:
        if eff is None:
            consumption = "暂无数据"
        else:
            # 计算耐久差
            delta = repaired_max_calculation - remaining_durability
            
            if eff == 0:
                consumption = "无穷大"
            elif delta < 0:
                consumption = "无效值"
            else:
                # 计算点数并去尾取整（向下取整）
                points = delta / eff
                consumption = math.floor(points) if points >= 0 else "无效值"
        
        print(f"- {name}：{consumption}")

input("\n按回车键结束计算...")