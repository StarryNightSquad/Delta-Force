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
    
    # 创建1-6级的存储结构
    armors = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    helmets = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    
    # 从第3行开始读取数据（跳过前2行标题）
    for row_idx, row in enumerate(sheet.iter_rows(min_row=3, values_only=True), start=3):
        # 检查是否是有效行
        if not row[0] or row[0] == "听力范围" or not isinstance(row[1], (int, float)):
            continue
            
        name = row[0]
        armor_class = int(row[1])
        armor_type = row[2]
        
        # 只处理1-6级装备
        if armor_class < 1 or armor_class > 6:
            continue
            
        # 获取关键数据
        initial_max = row[6] if isinstance(row[6], (int, float)) else 0
        repair_loss = row[8] if isinstance(row[8], (int, float)) else 0
        
        # 获取四种维修包效率
        efficiencies = []
        for col_idx in [10, 12, 14, 16]:  # K, M, O, Q列
            eff_value = row[col_idx]
            if isinstance(eff_value, (int, float)):
                efficiencies.append(eff_value)
            else:
                # 尝试转换字符串值
                try:
                    if isinstance(eff_value, str):
                        eff_value = float(eff_value)
                    efficiencies.append(eff_value)
                except:
                    efficiencies.append(None)
        
        # 创建装备数据对象
        item = {
            'name': name,
            'class': armor_class,
            'type': armor_type,
            'initial_max': initial_max,
            'repair_loss': repair_loss,
            'efficiencies': efficiencies,
            'row': row_idx  # 记录行号用于调试
        }
        
        # 分类存储
        if armor_type in ['半甲', '全甲', '重甲']:
            armors[armor_class].append(item)
        elif armor_type in ['无', '有']:
            helmets[armor_class].append(item)
    
    return armors, helmets

# 加载数据并显示统计信息
try:
    armors, helmets = load_armor_data('S5护甲数据.xlsx')
    
    # 显示装备统计信息
    print("成功加载装备数据:")
    
    # 护甲统计
    armor_counts = []
    for level in range(1, 7):
        count = len(armors.get(level, []))
        armor_counts.append(f"{level}级({count})")
    print(f"护甲: {' '.join(armor_counts)}")
    
    # 头盔统计
    helmet_counts = []
    for level in range(1, 7):
        count = len(helmets.get(level, []))
        helmet_counts.append(f"{level}级({count})")
    print(f"头盔: {' '.join(helmet_counts)}")
    
except Exception as e:
    print(f"加载Excel文件时出错: {e}")
    armors, helmets = {1:[],2:[],3:[],4:[],5:[],6:[]}, {1:[],2:[],3:[],4:[],5:[],6:[]}
    print("护甲: 1级(0) 2级(0) 3级(0) 4级(0) 5级(0) 6级(0)")
    print("头盔: 1级(0) 2级(0) 3级(0) 4级(0) 5级(0) 6级(0)")

def select_item(item_type, item_class, items_dict):
    """选择具体装备"""
    items = items_dict.get(item_class, [])
    if not items:
        print(f"未找到{item_type}{item_class}级装备")
        return None
        
    print(f"\n请选择{item_class}级{item_type}:")
    for i, item in enumerate(items, 1):
        # 显示装备名称、初始上限和维修损耗
        print(f"{i}. {item['name']} (初始上限: {item['initial_max']}, 维修损耗: {item['repair_loss']:.2f})")
    
    while True:
        try:
            choice = int(input("请输入选择(1-{len(items)}): "))
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
    print("\n=== 装备维修计算器 ===")
    print("\n请选择装备类型:")
    print("1. 护甲")
    print("2. 头盔")
    
    # 选择装备类型
    while True:
        try:
            type_choice = int(input("请输入选择(1-2): "))
            if type_choice in [1, 2]:
                break
            print("编号无效，请重新输入")
        except ValueError:
            print("请输入有效数字")
    
    # 选择装备等级
    print("\n请选择装备等级:")
    for level in range(1, 7):
        item_type = "护甲" if type_choice == 1 else "头盔"
        items_dict = armors if type_choice == 1 else helmets
        count = len(items_dict.get(level, []))
        print(f"{level}. {level}级{item_type} ({count}件可用)")
    
    while True:
        try:
            class_choice = int(input("请输入选择(1-6): "))
            if 1 <= class_choice <= 6:
                break
            print("编号无效，请重新输入 (1-6)")
        except ValueError:
            print("请输入有效数字")
    
    # 选择具体装备
    item_type = "护甲" if type_choice == 1 else "头盔"
    items_dict = armors if type_choice == 1 else helmets
    item = select_item(item_type, class_choice, items_dict)
    
    if not item:
        print(f"未找到{item_type}{class_choice}级装备，请检查Excel数据")
        input("\n按回车键结束...")
        return
        
    # 显示装备详细信息
    print("\n=== 装备详细信息 ===")
    print(f"装备名称: {item['name']}")
    print(f"装备类型: {item['type']}")
    print(f"防护等级: {item['class']}级")
    print(f"初始上限: {item['initial_max']}")
    print(f"维修损耗: {item['repair_loss']:.4f}")
    
    # 获取维修效率
    repair_packages = []
    package_names = ["自制", "标准", "精密", "高级维修组合"]
    
    if not item['efficiencies']:
        print("警告: 未找到维修效率数据")
    
    for i, eff in enumerate(item['efficiencies']):
        if eff is None or eff == '':
            repair_packages.append((package_names[i], None))
        else:
            try:
                # 将效率值转换为Decimal
                repair_packages.append((package_names[i], Decimal(str(eff))))
            except:
                repair_packages.append((package_names[i], None))
                print(f"警告: {package_names[i]}维修包效率值无效: {eff}")
    
    # 输入当前状态 - 添加严格验证
    initial_max = item['initial_max']
    
    # 输入当前上限（验证不超过初始上限）
    current_max_float = get_float_input(
        f"\n请输入当前上限(≤{initial_max}): ", 
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
        print(f"计算错误: {e}")
        repaired_max_calculation = Decimal(0)
        repaired_max_display = Decimal(0)
    
    # 结果输出
    print("\n=== 维修计算结果 ===")
    if repaired_max_calculation <= 0:
        print("无法维修（维修后耐久≤0）")
    else:
        print(f"维修后上限: {repaired_max_display:.1f}")
        print("消耗维修点数:")
        
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
                    try:
                        # 计算点数并去尾取整（向下取整）
                        points = delta / d_eff
                        # 使用向下取整（ROUND_FLOOR）
                        consumption = points.quantize(Decimal('1'), rounding=ROUND_FLOOR)
                    except Exception as e:
                        consumption = f"计算错误: {e}"
            
            print(f"- {name}: {consumption}")

    input("\n按回车键结束计算...")

if __name__ == "__main__":
    main()
