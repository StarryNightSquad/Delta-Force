from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_CEILING
import math

# 设置Decimal上下文精度
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP

def round_to_two(x):
    """四舍五入到小数点后两位"""
    return x.quantize(Decimal('0.01'))

def main():
    # 输入基础参数
    initial_max = Decimal(input("初始上限(1-150整数): "))
    current_max = Decimal(input("当前上限(1-150最多一位小数): ")).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    current_durability = Decimal(input("剩余耐久(0-150最多一位小数): ")).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    repair_loss = Decimal(input("维修损耗(0-1最多两位小数): ")).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # 输入四种维修工具的维修效率
    tools = ["自制维修包", "标准维修包", "精密维修包", "高级维修组合"]
    efficiencies = {}
    for tool in tools:
        eff = Decimal(input(f"{tool}的维修效率(0.01-10最多两位小数): ")).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        efficiencies[tool] = eff
    
    # 维修循环
    while True:
        # 输入本次使用的维修工具和维修点数
        tool = input("请选择维修包(自制维修包/标准维修包/精密维修包/高级维修组合): ")
        if tool not in efficiencies:
            print("无效的维修包选择，请重新输入")
            continue
        
        repair_points = Decimal(input("维修点数(1-200整数): "))
        efficiency = efficiencies[tool]
        
        # 计算修复耐久
        repair_durability = repair_points * efficiency
        
        # 计算维修后上限
        try:
            log_value = math.log10(float(current_max / initial_max))
        except ValueError:
            log_value = 0
        log_term = Decimal(str(log_value))
        ratio = (current_max - current_durability) / current_max
        factor = repair_loss - log_term
        delta = current_max * ratio * factor
        new_max = current_max - delta
        new_max = round_to_two(new_max)
        
        # 计算维修后耐久
        new_durability = current_durability + repair_durability
        new_durability = round_to_two(new_durability)
        
        # 检查是否修满
        if new_durability >= new_max:
            required_repair = new_max - current_durability
            consumed_points = required_repair / efficiency
            remaining_points = repair_points - consumed_points
            remaining_points = remaining_points.to_integral_value(rounding=ROUND_CEILING)
            
            # 输出结果（展示时保留一位小数）
            print(f"修理完成，维修后上限: {new_max.quantize(Decimal('0.1'))}, "
                  f"维修后耐久: {new_max.quantize(Decimal('0.1'))}, "
                  f"剩余维修点数: {remaining_points}")
            break
        
        # 检查是否不可维修
        if new_max < Decimal('1'):
            print("不可维修")
            break
        
        # 更新状态并继续
        current_max = new_max
        current_durability = new_durability
        
        # 输出本次维修结果（展示时保留一位小数）
        print(f"维修后上限: {new_max.quantize(Decimal('0.1'))}, "
              f"维修后耐久: {new_durability.quantize(Decimal('0.1'))}, "
              f"剩余维修点数: 0")

if __name__ == "__main__":
    main()
