print("本程序由B站繁星攻略组制作，感谢B站用户Dec128与乂丶z提供的数据支持")

from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_CEILING
import math
import re
import openpyxl
import os

# 设置Decimal上下文精度
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP

def round_to_two(x):
    """四舍五入到小数点后两位"""
    return x.quantize(Decimal('0.01'))

def parse_efficiency(value):
    """解析维修效率值，返回Decimal类型"""
    if value is None:
        return Decimal('0')
    
    if isinstance(value, str):
        # 处理单个值
        try:
            return Decimal(value.strip())
        except:
            return Decimal('0')
    
    # 处理数字类型
    try:
        return Decimal(str(value))
    except:
        return Decimal('0')

def load_armor_data(file_path):
    """从Excel文件加载护甲和头盔数据"""
    wb = openpyxl.load_workbook(file_path)
    sheet = wb['护甲数据']
    
    # 支持1-6级装备
    armors = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    helmets = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    
    # 从第4行开始读取数据（跳过前3行标题）
    for row_idx, row in enumerate(sheet.iter_rows(min_row=4, values_only=True), start=4):
        # 提取基本数据
        name = row[0]  # A列
        if not name:
            continue
            
        level = row[1]  # B列
        armor_type = row[2]  # C列
        
        # 处理所有1-6级装备
        if not isinstance(level, (int, float)) or level < 1 or level > 6:
            continue
        
        level = int(level)
        
        # 转换数值类型为Decimal
        try:
            max_durability = Decimal(str(row[6])) if row[6] is not None else Decimal('0')  # G列
            repair_loss = Decimal(str(row[8])) if row[8] is not None else Decimal('0')      # I列
        except:
            continue
        
        # 只读取K、M、O、Q四列的维修效率数据
        efficiency_self = row[10]  # K列 (自制)
        efficiency_std = row[12]   # M列 (标准)
        efficiency_prec = row[14]  # O列 (精密)
        efficiency_adv = row[16]   # Q列 (高级)
        
        # 创建装备数据字典
        equipment = {
            'name': name,
            'level': level,
            'type': armor_type,
            'max_durability': max_durability,
            'repair_loss': repair_loss,
            'efficiencies': {
                '1': parse_efficiency(efficiency_self),  # 自制
                '2': parse_efficiency(efficiency_std),   # 标准
                '3': parse_efficiency(efficiency_prec),  # 精密
                '4': parse_efficiency(efficiency_adv)    # 高级
            }
        }
        
        # 分类到护甲或头盔
        if armor_type in ['半甲', '全甲', '重甲']:
            armors[level].append(equipment)
        elif armor_type in ['无', '有']:
            helmets[level].append(equipment)
    
    return armors, helmets

def validate_input(prompt, input_type, min_val=None, max_val=None, decimal_places=None, reference=None, reference_desc=None):
    """
    验证用户输入
    :param prompt: 提示信息
    :param input_type: 'int' 或 'decimal'
    :param min_val: 最小值
    :param max_val: 最大值
    :param decimal_places: 允许的小数位数
    :param reference: 参考值（用于上限验证）
    :param reference_desc: 参考值的描述（用于错误提示）
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
                if reference is not None:
                    if value > reference:
                        ref_desc = reference_desc if reference_desc else f"{reference}"
                        raise ValueError(f"值不能大于 {ref_desc}")
                
                if decimal_places > 0:
                    return value.quantize(Decimal('1.' + '0' * decimal_places))
                else:
                    return value
            
        except ValueError as e:
            print(f"输入错误: {e}，请重新输入")

def main():
    # 加载护甲数据
    file_path = "S5护甲数据.xlsx"
    if not os.path.exists(file_path):
        print(f"错误: 找不到数据文件 {file_path}")
        return
    
    try:
        armors, helmets = load_armor_data(file_path)
    except Exception as e:
        print(f"加载护甲数据失败: {e}")
        return
    
    # 显示装备统计信息
    print("成功加载装备数据:")
    
    # 护甲统计
    armor_counts = []
    for level in range(1, 7):
        count = len(armors[level])
        armor_counts.append(f"{level}级({count})")
    print(f"护甲: {' '.join(armor_counts)}")
    
    # 头盔统计
    helmet_counts = []
    for level in range(1, 7):
        count = len(helmets[level])
        helmet_counts.append(f"{level}级({count})")
    print(f"头盔: {' '.join(helmet_counts)}")
    
    print("\n=== 装备维修计算模拟 ===")
    
    # 选择装备类型（调整顺序：1头盔 2护甲）
    print("\n请选择装备类型:")
    print("1. 头盔")
    print("2. 护甲")
    equip_type = input("请输入选择(1-2): ")
    
    if equip_type not in ['1', '2']:
        print("无效的选择")
        return
    
    # 选择装备等级（1-6级）
    print("\n请选择装备等级:")
    
    # 根据装备类型获取统计信息
    if equip_type == '1':  # 头盔
        equipment_dict = helmets
        equip_type_name = "头盔"
    else:  # 护甲
        equipment_dict = armors
        equip_type_name = "护甲"
    
    # 显示每个等级可用的装备数量
    for level in range(1, 7):
        count = len(equipment_dict[level])
        print(f"{level}. {level}级装备 ({count}件可用)")
    
    equip_level = input(f"请输入选择(1-6): ")
    
    if equip_level not in ['1', '2', '3', '4', '5', '6']:
        print("无效的选择")
        return
    
    equip_level = int(equip_level)
    
    # 获取该等级装备列表
    equipment_list = equipment_dict[equip_level]
    
    if not equipment_list:
        print(f"没有找到{equip_level}级的{equip_type_name}")
        return
    
    print(f"\n请选择{equip_level}级{equip_type_name}:")
    
    # 显示装备列表，包含初始上限和维修损耗
    for i, equip in enumerate(equipment_list, 1):
        print(f"{i}. {equip['name']} (初始上限: {equip['max_durability']}, 维修损耗: {equip['repair_loss']})")
    
    try:
        choice = int(input(f"请输入选择(1-{len(equipment_list)}): "))
        if choice < 1 or choice > len(equipment_list):
            raise ValueError
    except ValueError:
        print("无效的选择")
        return
    
    selected_equip = equipment_list[choice - 1]
    
    # 显示装备详细信息
    print("\n=== 装备详细信息 ===")
    print(f"装备名称: {selected_equip['name']}")
    print(f"装备类型: {selected_equip['type']}")
    print(f"防护等级: {selected_equip['level']}级")
    print(f"初始上限: {selected_equip['max_durability']}")
    print(f"维修损耗: {selected_equip['repair_loss']}")
    print("维修效率:")
    print(f"  1. 自制维修包: {selected_equip['efficiencies']['1']}")
    print(f"  2. 标准维修包: {selected_equip['efficiencies']['2']}")
    print(f"  3. 精密维修包: {selected_equip['efficiencies']['3']}")
    print(f"  4. 高级维修组合: {selected_equip['efficiencies']['4']}")
    
    # 设置基础参数
    initial_max = selected_equip['max_durability']
    repair_loss = selected_equip['repair_loss']
    efficiencies = selected_equip['efficiencies']
    
    # 输入当前状态 - 添加严格的验证
    print("\n请输入装备当前状态:")
    
    # 当前上限验证：不得高于初始上限
    current_max = validate_input(
        f"当前上限(1-{initial_max}最多一位小数): ",
        'decimal',
        1,
        150,
        1,
        reference=initial_max,
        reference_desc=f"装备的初始上限({initial_max})"
    )
    
    # 剩余耐久验证：不得高于当前上限
    current_durability = validate_input(
        f"剩余耐久(0-{current_max}最多一位小数): ",
        'decimal',
        0,
        150,
        1,
        reference=current_max,
        reference_desc=f"当前上限({current_max})"
    )
    
    # 维修循环
    repair_count = 0
    
    while True:
        repair_count += 1
        print(f"\n=== 第 {repair_count} 次维修 ===")
        print(f"当前状态: 上限={current_max.quantize(Decimal('0.1'))} 耐久={current_durability.quantize(Decimal('0.1'))}")
        
        # 输入本次使用的维修工具
        while True:
            print("\n请选择维修工具:")
            print("1. 自制维修包")
            print("2. 标准维修包")
            print("3. 精密维修包")
            print("4. 高级维修组合")
            
            choice = input("请输入维修工具编号(1-4): ")
            if choice in efficiencies:
                tool_name = {
                    '1': '自制维修包',
                    '2': '标准维修包',
                    '3': '精密维修包',
                    '4': '高级维修组合'
                }[choice]
                efficiency = efficiencies[choice]
                print(f"已选择: {tool_name} (效率={efficiency})")
                break
            print("错误: 无效的选择，请输入1-4之间的数字")
        
        # 根据装备类型和维修工具设置维修点数上限
        if equip_type == '2':  # 护甲
            max_points = {
                '1': 50,   # 自制维修包
                '2': 75,   # 标准维修包
                '3': 120,  # 精密维修包
                '4': 200   # 高级维修组合
            }[choice]
        else:  # 头盔
            max_points = {
                '1': 30,   # 自制维修包
                '2': 50,   # 标准维修包
                '3': 75,   # 精密维修包
                '4': 100   # 高级维修组合
            }[choice]
        
        # 输入维修点数
        repair_points = validate_input(f"维修点数(1-{max_points}整数): ", 'int', 1, max_points)
        
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
    
    # 等待用户按Enter键结束程序
    input("\n计算完成，按Enter键结束程序...")

if __name__ == "__main__":
    main()
