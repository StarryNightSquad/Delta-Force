print("本程序由B站繁星攻略组制作，感谢B站用户Dec128与乂丶z提供的数据支持")

import math
import openpyxl
from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR, getcontext

# 设置Decimal精度环境
getcontext().prec = 20  # 设置高精度计算环境

# 加载Excel数据
def load_armor_data(file_path):
    wb = openpyxl.load_workbook(file_path)
    sheet = wb['护甲数据']
    
    armors = {3: [], 4: [], 5: [], 6: []}
    helmets = {3: [], 4: [], 5: [], 6: []}
    
    # 从第3行开始读取数据（跳过前2行标题）
    for row in sheet.iter_rows(min_row=3, values_only=True):
        # 检查是否是有效行
        if not row[0] or row[0] == "听力范围":
            continue
            
        name = row[0]
        armor_class = row[1]
        armor_type = row[2]
        
        # 只处理3-6级装备
        if armor_class not in [3, 4, 5, 6]:
            continue
            
        # 获取关键数据
        initial_max = row[6] if isinstance(row[6], (int, float)) else 0
        repair_loss = row[8] if isinstance(row[8], (int, float)) else 0
        
        # 获取四种维修包效率
        efficiencies = [
            row[10],  # 自制维修包效率 (K列)
            row[12],  # 标准维修包效率 (M列)
            row[14],  # 精密维修包效率 (O列)
            row[16]   # 高级维修组合效率 (Q列)
        ]
        
        # 创建装备数据对象
        item = {
            'name': name,
            'class': armor_class,
            'type': armor_type,
            'initial_max': initial_max,
            'repair_loss': repair_loss,
            'efficiencies': efficiencies
        }
        
        # 分类存储
        if armor_type in ['半甲', '全甲', '重甲']:
            armors[armor_class].append(item)
        elif armor_type in ['无', '有']:
            helmets[armor_class].append(item)
    
    return armors, helmets

# 加载数据
armors, helmets = load_armor_data('S5护甲数据.xlsx')

def select_item(item_type, item_class, items_dict):
    """选择具体装备"""
    items = items_dict.get(item_class, [])
    if not items:
        print(f"未找到{item_type}{item_class}级装备")
        return None
        
    print(f"\n请选择{item_type}{item_class}级装备:")
    for i, item in enumerate(items, 1):
        print(f"{i}. {item['name']}")
    
    while True:
        try:
            choice = int(input("请输入编号选择装备: "))
            if 1 <= choice <= len(items):
                return items[choice-1]
            print("编号无效，请重新输入")
        except ValueError:
            print("请输入有效数字")

def get_float_input(prompt, max_value=None):
    """获取浮点数输入并进行验证"""
    while True:
        try:
            value = float(input(prompt))
            if max_value is not None and value > max_value:
                print(f"输入值不能超过{max_value}，请重新输入")
                continue
            return value
        except ValueError:
            print("请输入有效数字")

def main():
    print("===== 护甲维修计算器 =====")
    print("请选择装备类型:")
    print("1. 护甲")
    print("2. 头盔")
    
    # 选择装备类型
    while True:
        try:
            type_choice = int(input("请输入类型编号: "))
            if type_choice in [1, 2]:
                break
            print("编号无效，请重新输入")
        except ValueError:
            print("请输入有效数字")
    
    # 选择装备等级
    print("\n请选择装备等级:")
    print("3. 3级")
    print("4. 4级")
    print("5. 5级")
    print("6. 6级")
    
    while True:
        try:
            class_choice = int(input("请输入等级编号: "))
            if 3 <= class_choice <= 6:
                break
            print("编号无效，请重新输入")
        except ValueError:
            print("请输入有效数字")
    
    # 选择具体装备
    item_type = "护甲" if type_choice == 1 else "头盔"
    items_dict = armors if type_choice == 1 else helmets
    item = select_item(item_type, class_choice, items_dict)
    
    if not item:
        return
        
    print(f"\n已选择: {item['name']}")
    print(f"初始上限: {item['initial_max']}")
    print(f"维修损耗: {item['repair_loss']:.2f}")
    
    # 获取维修效率
    repair_packages = []
    package_names = ["自制", "标准", "精密", "高级维修组合"]
    for i, eff in enumerate(item['efficiencies']):
        if eff is None or eff == '':
            repair_packages.append((package_names[i], None))
        else:
            # 将效率值转换为Decimal
            repair_packages.append((package_names[i], Decimal(str(eff))))
    
    # 输入当前状态 - 添加严格验证
    initial_max = item['initial_max']
    
    # 输入当前上限（验证不超过初始上限）
    current_max_float = get_float_input(
        f"请输入当前上限(≤{initial_max}): ", 
        max_value=initial_max
    )
    
    # 输入剩余耐久（验证不超过当前上限）
    remaining_durability_float = get_float_input(
        f"请输入剩余耐久(≤{current_max_float}): ", 
        max_value=current_max_float
    )
    
    # 将输入值转换为Decimal
    d_initial_max = Decimal(str(item['initial_max']))
    d_repair_loss = Decimal(str(item['repair_loss']))
    d_current_max = Decimal(str(current_max_float))
    d_remaining_durability = Decimal(str(remaining_durability_float))
    
    # 计算维修后上限
    try:
        # 计算比率
        if d_current_max == 0:
            ratio = Decimal(0)
        else:
            ratio = (d_current_max - d_remaining_durability) / d_current_max
        
        # 计算对数项（使用浮点数计算后再转换为Decimal）
        if d_current_max > 0 and d_initial_max > 0:
            log_val = math.log10(float(d_current_max / d_initial_max))
            log_term = Decimal(str(log_val))
        else:
            log_term = Decimal(0)
        
        # 计算维修后上限（使用Decimal精确计算）
        repaired_max = d_current_max - d_current_max * ratio * (d_repair_loss - log_term)
        
        # 四舍五入到2位小数用于点数计算
        repaired_max_calculation = repaired_max.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # 四舍五入到1位小数用于展示
        repaired_max_display = repaired_max.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        
    except (ZeroDivisionError, ValueError) as e:
        repaired_max_calculation = Decimal(0)
        repaired_max_display = Decimal(0)
    
    # 结果输出
    print("\n===== 维修计算结果 =====")
    if repaired_max_calculation <= 0:
        print("无法维修（维修后耐久≤0）")
    else:
        print(f"维修后上限：{repaired_max_display:.1f}")
        print("消耗维修点数：")
        
        for name, d_eff in repair_packages:
            if d_eff is None:
                consumption = "暂无数据"
            else:
                # 计算耐久差
                delta = repaired_max_calculation - d_remaining_durability
                
                if d_eff == 0:
                    consumption = "无穷大"
                elif delta < 0:
                    consumption = "无效值"
                else:
                    # 计算点数并去尾取整（向下取整）
                    points = delta / d_eff
                    # 使用向下取整（ROUND_FLOOR）
                    consumption = points.quantize(Decimal('1'), rounding=ROUND_FLOOR)
            
            print(f"- {name}：{consumption}")

    input("\n按回车键结束计算...")

if __name__ == "__main__":
    main()
