from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_CEILING
import math
import re

print("本程序由B站繁星攻略组与用户Dec128合作制作")

# 设置Decimal上下文精度
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP

def round_to_two(x):
    """四舍五入到小数点后两位"""
    return x.quantize(Decimal('0.01'))

def validate_input(prompt, input_type, min_val=None, max_val=None, decimal_places=None, reference=None):
    """
    验证用户输入
    :param prompt: 提示信息
    :param input_type: 'int' 或 'decimal'
    :param min_val: 最小值
    :param max_val: 最大值
    :param decimal_places: 允许的小数位数
    :param reference: 参考值（用于上限验证）
    """
    while True:
        try:
            value_str = input(prompt)
            
            # 检查空输入
            if not value_str:
                raise ValueError("输入不能为空")
            
            # 整数验证
            if input_type == 'int':
                value = int(value_str)
                if min_val is not None and value < min_val:
                    raise ValueError(f"值不能小于 {min_val}")
                if max_val is not None and value > max_val:
                    raise ValueError(f"值不能大于 {max_val}")
                return Decimal(value)
            
            # 小数验证
            elif input_type == 'decimal':
                # 验证小数格式
                if decimal_places > 0:
                    pattern = r'^\d+(\.\d{1,' + str(decimal_places) + r'})?$'
                else:
                    pattern = r'^\d+$'
                
                if not re.match(pattern, value_str):
                    raise ValueError(f"最多允许 {decimal_places} 位小数")
                
                value = Decimal(value_str)
                
                # 检查小数位数
                if '.' in value_str:
                    decimals = len(value_str.split('.')[1])
                    if decimals > decimal_places:
                        raise ValueError(f"最多允许 {decimal_places} 位小数")
                
                # 范围验证
                if min_val is not None and value < min_val:
                    raise ValueError(f"值不能小于 {min_val}")
                if max_val is not None and value > max_val:
                    raise ValueError(f"值不能大于 {max_val}")
                
                # 参考值验证
                if reference is not None and value > reference:
                    raise ValueError(f"值不能大于 {reference}")
                
                if decimal_places > 0:
                    return value.quantize(Decimal('1.' + '0' * decimal_places))
                else:
                    return value
            
        except ValueError as e:
            print(f"输入错误: {e}，请重新输入")

def main():
    print("===== 装备维修计算器 =====")
    
    # 输入基础参数
    initial_max = validate_input("初始上限(1-150整数): ", 'int', 1, 150)
    current_max = validate_input("当前上限(1-150最多一位小数): ", 'decimal', 1, 150, 1, initial_max)
    current_durability = validate_input("剩余耐久(0-150最多一位小数): ", 'decimal', 0, 150, 1, current_max)
    repair_loss = validate_input("维修损耗(0-1最多两位小数): ", 'decimal', 0, 1, 2)
    
    # 输入四种维修工具的维修效率
    tools = {
        "1": "自制维修包",
        "2": "标准维修包",
        "3": "精密维修包",
        "4": "高级维修组合"
    }
    
    efficiencies = {}
    print("\n请设置各种维修工具的维修效率:")
    for num, tool in tools.items():
        eff = validate_input(f"{num}. {tool}的维修效率(0.01-10最多两位小数): ", 'decimal', Decimal('0.01'), Decimal('10'), 2)
        efficiencies[num] = eff
    
    # 维修循环
    repair_count = 0
    
    while True:
        repair_count += 1
        print(f"\n=== 第 {repair_count} 次维修 ===")
        print(f"当前状态: 上限={current_max.quantize(Decimal('0.1'))} 耐久={current_durability.quantize(Decimal('0.1'))}")
        
        # 输入本次使用的维修工具
        while True:
            print("\n请选择维修工具:")
            for num, tool in tools.items():
                print(f"{num}. {tool} (效率={efficiencies[num]})")
            
            choice = input("请输入维修工具编号(1-4): ")
            if choice in efficiencies:
                tool_name = tools[choice]
                efficiency = efficiencies[choice]
                break
            print("错误: 无效的选择，请输入1-4之间的数字")
        
        # 输入维修点数
        repair_points = validate_input("维修点数(1-200整数): ", 'int', 1, 200)
        
        # 计算修复耐久
        repair_durability = repair_points * efficiency
        
        # 计算维修后上限
        try:
            # 计算对数项，处理当前上限等于初始上限的情况
            ratio = current_max / initial_max
            if ratio == 1:
                log_term = Decimal(0)
            else:
                log_term = Decimal(math.log10(float(ratio)))
        except (ValueError, OverflowError):
            log_term = Decimal(0)
        
        # 计算耐久损失比例
        durability_loss_ratio = (current_max - current_durability) / current_max
        
        # 计算上限减少量
        max_reduction = current_max * durability_loss_ratio * (repair_loss - log_term)
        new_max = current_max - max_reduction
        
        # 四舍五入到小数点后两位
        new_max = round_to_two(new_max)
        
        # 计算维修后耐久
        new_durability = current_durability + repair_durability
        new_durability = round_to_two(new_durability)
        
        # 检查是否修满
        if new_durability >= new_max:
            # 计算实际需要的耐久修复量
            required_repair = new_max - current_durability
            
            # 计算实际消耗的维修点数
            consumed_points = required_repair / efficiency
            
            # 计算剩余维修点数（进一取整）
            remaining_points = repair_points - consumed_points
            remaining_points = remaining_points.to_integral_value(rounding=ROUND_CEILING)
            
            # 输出结果
            print("\n===== 修理完成 =====")
            print(f"维修后上限: {new_max.quantize(Decimal('0.1'))}")
            print(f"维修后耐久: {new_max.quantize(Decimal('0.1'))}")
            print(f"剩余维修点数: {remaining_points}")
            break
        
        # 检查是否不可维修
        if new_max < Decimal('1'):
            print("\n===== 不可维修 =====")
            print("原因: 维修后上限小于1")
            break
        
        # 更新状态
        current_max = new_max
        current_durability = new_durability
        
        # 输出本次维修结果
        print("\n维修结果:")
        print(f"维修后上限: {new_max.quantize(Decimal('0.1'))}")
        print(f"维修后耐久: {new_durability.quantize(Decimal('0.1'))}")
        print(f"本次消耗维修点数: {repair_points}")

if __name__ == "__main__":
    main()
