print("本程序由繁星攻略组制作，已适配2026年1月29日更新后损耗算法")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
三角洲行动 - 局内维修损耗计算器 V1.6
基于新算法（TRD→MDP曲线查表）
全程 Decimal 高精度计算
消耗点数显示小数，剩余点数向上取整显示
数据来源：S6护甲数据.xlsx（外部表格）
"""

import math
import openpyxl
from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_CEILING, ROUND_FLOOR

# ===== 设置 Decimal 精度（50位，足够覆盖游戏计算） =====
getcontext().prec = 50

# ===== 调试开关 =====
DEBUG = False

# ===== 维修工具配置（使用 Decimal） =====
REPAIR_TOOLS = {
    "蓝": {"点数": Decimal("50")},
    "紫": {"点数": Decimal("75")},
    "金": {"点数": Decimal("120")},
    "红": {"点数": Decimal("200")},
}
HELMET_REPAIR_TOOLS = {
    "蓝": {"点数": Decimal("30")},
    "紫": {"点数": Decimal("50")},
    "金": {"点数": Decimal("75")},
    "红": {"点数": Decimal("100")},
}

# ============================================================
# 工具函数：Decimal 对数（以10为底）
# ============================================================
def decimal_log10(x):
    """计算 Decimal 的以10为底的对数"""
    if x <= 0:
        return Decimal("-inf")
    # 使用 Decimal 的 ln 方法计算
    return x.ln() / Decimal("10").ln()

# ============================================================
# 数据加载
# ============================================================
def parse_efficiency(val):
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return Decimal(str(val))
    if isinstance(val, str):
        val = val.strip()
        if not val or val == "-" or val == "":
            return None
        try:
            return Decimal(val)
        except:
            return None
    return None

def load_armor_data(filepath):
    wb = openpyxl.load_workbook(filepath, data_only=True)
    sheet = wb['护甲数据']
    
    armors = []
    helmets = []
    current_section = None
    
    for row_idx, row in enumerate(sheet.iter_rows(min_row=1, values_only=True), start=1):
        if not row or not row[0]:
            continue
        name = str(row[0]).strip()
        
        if name == "护甲":
            current_section = "armor"
            continue
        elif name == "头盔":
            current_section = "helmet"
            continue
        
        if name in ["防护等级", "护甲类型", "瞄准负面", "移动负面", "装备重量", "初始上限", "首次碎甲维修上限", "维修损耗", "维修单价"]:
            continue
        
        if current_section is None:
            continue
        
        level_cell = row[1]
        if level_cell is None:
            continue
        try:
            level = int(float(level_cell))
        except (ValueError, TypeError):
            continue
        
        armor_type = row[2] if len(row) > 2 else None
        initial_max = Decimal(str(row[6])) if row[6] is not None else Decimal("0")
        loss = Decimal(str(row[8])) if row[8] is not None else Decimal("0")
        
        # K(10)=蓝, L(11)=紫, M(12)=金, N(13)=红
        eff = {
            '蓝': parse_efficiency(row[10]) if len(row) > 10 else None,
            '紫': parse_efficiency(row[11]) if len(row) > 11 else None,
            '金': parse_efficiency(row[12]) if len(row) > 12 else None,
            '红': parse_efficiency(row[13]) if len(row) > 13 else None,
        }
        
        item = {
            'name': name,
            'level': level,
            'type': armor_type,
            'initial_max': initial_max,
            'loss': loss,
            'efficiencies': eff,
        }
        
        if current_section == "armor":
            armors.append(item)
        elif current_section == "helmet":
            helmets.append(item)
    
    return armors, helmets

# ============================================================
# 曲线生成与插值（Decimal 版本）
# ============================================================
def generate_curve_from_key_points(key_points, step=Decimal("0.1")):
    """根据关键点生成步长 step 的密集插值曲线（Decimal）"""
    dense = []
    for i in range(len(key_points)-1):
        x0, y0 = key_points[i]
        x1, y1 = key_points[i+1]
        x = x0
        while x < x1 - Decimal("1e-9"):
            if x1 != x0:
                t = (x - x0) / (x1 - x0)
            else:
                t = Decimal("0")
            y = y0 + t * (y1 - y0)
            dense.append((x, y))
            x += step
    dense.append(key_points[-1])
    return dense

def find_intersection(trd, curve):
    """线性插值查找 MDP（Decimal）"""
    if not curve:
        return Decimal("1")
    if trd <= curve[0][0]:
        return curve[0][1]
    if trd >= curve[-1][0]:
        return max(Decimal("0"), curve[-1][1])
    for i in range(len(curve)-1):
        x0, y0 = curve[i]
        x1, y1 = curve[i+1]
        if x0 <= trd <= x1:
            if x1 != x0:
                t = (trd - x0) / (x1 - x0)
            else:
                t = Decimal("0")
            return y0 + t * (y1 - y0)
    return curve[-1][1]

def reverse_trd(mdp, curve):
    """根据 MDP 反推 TRD（Decimal）"""
    if not curve:
        return Decimal("0")
    if mdp >= curve[0][1]:
        return curve[0][0]
    if mdp <= curve[-1][1]:
        return curve[-1][0]
    for i in range(len(curve)-1):
        x0, y0 = curve[i]
        x1, y1 = curve[i+1]
        if y0 >= mdp >= y1:
            if y1 != y0:
                t = (mdp - y0) / (y1 - y0)
            else:
                t = Decimal("0")
            return x0 + t * (x1 - x0)
    return curve[-1][0]

def build_curve_for_armor(armor):
    """根据装备的 initial_max 和 loss 动态生成曲线关键点（Decimal）"""
    initial_max = armor['initial_max']
    loss = armor['loss']
    key_points = [(Decimal("0"), Decimal("1"))]
    cm = Decimal(str(initial_max))
    rem = Decimal("0")
    cum_trd = Decimal("0")
    while cm > Decimal("0.1"):
        ratio_full = (cm - rem) / cm if cm > 0 else Decimal("0")
        log_term_full = decimal_log10(cm / initial_max) if cm > 0 else Decimal("0")
        new_cm = cm * (Decimal("1") - ratio_full * (loss - log_term_full))
        if new_cm < 0:
            new_cm = Decimal("0")
        actual_repair = new_cm - rem
        cum_trd += actual_repair * (Decimal("1") - loss)
        mdp = new_cm / initial_max if initial_max > 0 else Decimal("0")
        key_points.append((cum_trd, mdp))
        cm = new_cm
        rem = Decimal("0")
        if cm <= Decimal("0.1"):
            break
    return key_points

# ============================================================
# 核心计算（全程 Decimal，不取整）
# ============================================================
def calculate_repair(armor, current_max, remaining, tool_color, points_used=None, prev_trd=None):
    # 确保输入为 Decimal
    if not isinstance(current_max, Decimal):
        current_max = Decimal(str(current_max))
    if not isinstance(remaining, Decimal):
        remaining = Decimal(str(remaining))
    
    initial_max = armor['initial_max']
    loss = armor['loss']
    efficiency = armor['efficiencies'].get(tool_color)
    
    if efficiency is None or efficiency <= 0:
        return {'success': False, 'message': f'该装备无法使用{tool_color}色维修工具'}
    
    is_helmet = armor.get('is_helmet', False)
    tool_max_points = HELMET_REPAIR_TOOLS.get(tool_color, {}).get('点数', Decimal("0")) if is_helmet else REPAIR_TOOLS.get(tool_color, {}).get('点数', Decimal("0"))
    if points_used is None:
        points_used = tool_max_points
    else:
        if not isinstance(points_used, Decimal):
            points_used = Decimal(str(points_used))
        points_used = min(points_used, tool_max_points)
    if points_used <= 0:
        return {'success': False, 'message': '无效的维修点数'}
    
    if current_max <= 0:
        return {'success': False, 'message': '装备已报废'}
    
    # 预判新上限（旧公式）
    ratio = (current_max - remaining) / current_max if current_max > 0 else Decimal("0")
    log_term = decimal_log10(current_max / initial_max) if current_max > 0 else Decimal("0")
    pre_new_max = current_max * (Decimal("1") - ratio * (loss - log_term))
    if pre_new_max < 0:
        pre_new_max = Decimal("0")
    if pre_new_max < Decimal("1"):
        return {'success': False, 'message': f'不可维修（预判新上限 {pre_new_max:.2f} < 1）', 'is_repairable': False}
    
    # 生成曲线关键点（动态）
    if 'curve_key_points' not in armor:
        armor['curve_key_points'] = build_curve_for_armor(armor)
    curve = generate_curve_from_key_points(armor['curve_key_points'], step=Decimal("0.1"))
    
    # 获取或反推当前 TRD
    if prev_trd is None:
        mdp = current_max / initial_max if initial_max > 0 else Decimal("0")
        prev_trd = reverse_trd(mdp, curve)
    else:
        if not isinstance(prev_trd, Decimal):
            prev_trd = Decimal(str(prev_trd))
        mdp_check = find_intersection(prev_trd, curve)
        expected_max = initial_max * mdp_check
        if abs(expected_max - current_max) > Decimal("0.5"):
            mdp = current_max / initial_max if initial_max > 0 else Decimal("0")
            prev_trd = reverse_trd(mdp, curve)
    
    # 需要修复的量（修到预判新上限）
    need = pre_new_max - remaining
    if need <= 0:
        return {
            'success': True,
            'new_max': current_max,
            'new_remaining': remaining,
            'new_trd': prev_trd,
            'consumed_points': Decimal("0"),
            'remaining_points': points_used,
            'actual_repair': Decimal("0"),
            'is_full': True,
            'mdp': find_intersection(prev_trd, curve),
            'pre_new_max': pre_new_max,
        }
    
    # 需要的点数（不取整）
    required_points = need / efficiency
    if required_points <= 0:
        required_points = Decimal("0")
    
    # 实际消耗点数（不取整）
    actual_points = min(required_points, points_used)
    
    # 实际修复量
    actual_repair = actual_points * efficiency
    
    # TRD 增量
    trd_increment = actual_repair * (Decimal("1") - loss)
    new_trd = prev_trd + trd_increment
    
    # 查曲线得 MDP
    mdp = find_intersection(new_trd, curve)
    new_max = initial_max * mdp
    new_remaining = remaining + actual_repair
    if new_remaining > new_max:
        new_remaining = new_max
    is_full = new_remaining >= new_max - Decimal("0.001")
    
    return {
        'success': True,
        'new_max': new_max,
        'new_remaining': new_remaining,
        'new_trd': new_trd,
        'consumed_points': actual_points,
        'remaining_points': points_used - actual_points,
        'actual_repair': actual_repair,
        'is_full': is_full,
        'mdp': mdp,
        'pre_new_max': pre_new_max,
    }

# ============================================================
# 交互部分
# ============================================================
def get_int(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = int(input(prompt))
            if min_val is not None and val < min_val:
                print(f"不能小于 {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"不能大于 {max_val}")
                continue
            return val
        except ValueError:
            print("请输入有效整数")

def get_float(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = float(input(prompt))
            if min_val is not None and val < min_val:
                print(f"不能小于 {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"不能大于 {max_val}")
                continue
            return val
        except ValueError:
            print("请输入有效数字")

def get_choice(prompt, options):
    while True:
        val = input(prompt).strip()
        if val in options:
            return val
        print(f"请输入 {', '.join(options)}")

def main():
    print("=" * 60)
    print("  三角洲行动 - 局内维修损耗计算器 V1.6")
    print("  算法：TRD→MDP 曲线查表（Decimal 高精度）")
    print("  数据来源：S6护甲数据.xlsx")
    print("=" * 60)
    
    try:
        armors, helmets = load_armor_data("S6护甲数据.xlsx")
        print(f"加载成功：护甲 {len(armors)} 件，头盔 {len(helmets)} 件")
        if not armors and not helmets:
            print("错误：未读取到任何装备数据，请检查 Excel 文件格式。")
            input("按回车键退出...")
            return
    except FileNotFoundError:
        print("错误：找不到 S6护甲数据.xlsx，请将该文件放在程序同一目录下。")
        input("按回车键退出...")
        return
    except Exception as e:
        print(f"加载失败：{e}")
        input("按回车键退出...")
        return
    
    for h in helmets:
        h['is_helmet'] = True
    
    # 选择装备类型
    print("\n请选择装备类型：")
    print("1. 护甲")
    print("2. 头盔")
    type_choice = get_choice("请输入(1-2)：", ["1", "2"])
    items = armors if type_choice == "1" else helmets
    type_name = "护甲" if type_choice == "1" else "头盔"
    tool_config = REPAIR_TOOLS if type_choice == "1" else HELMET_REPAIR_TOOLS
    
    if not items:
        print(f"错误：没有可用的{type_name}数据")
        input("按回车键退出...")
        return
    
    # 按等级分组
    levels = sorted(set(item['level'] for item in items))
    items_by_level = {lv: [i for i in items if i['level'] == lv] for lv in levels}
    
    print(f"\n请选择{type_name}等级：")
    for lv in levels:
        print(f"{lv}. {lv}级 ({len(items_by_level[lv])}件)")
    level_choice = get_choice(f"请输入({levels[0]}-{levels[-1]})：", [str(l) for l in levels])
    level = int(level_choice)
    items_level = items_by_level[level]
    
    print(f"\n请选择{level}级{type_name}：")
    for i, item in enumerate(items_level, 1):
        print(f"{i}. {item['name']} (上限:{item['initial_max']:.1f}, 损耗:{item['loss']*100:.0f}%)")
    item_choice = get_int(f"请输入(1-{len(items_level)})：", 1, len(items_level))
    armor = items_level[item_choice - 1]
    
    print(f"\n已选择：{armor['name']}")
    print(f"  初始上限：{armor['initial_max']:.1f}")
    print(f"  损耗率：{armor['loss']*100:.0f}%")
    print("  维修效率：")
    for color in ['蓝', '紫', '金', '红']:
        eff = armor['efficiencies'].get(color)
        if eff and eff > 0:
            print(f"    {color}：{eff:.3f}")
        else:
            print(f"    {color}：不可用")
    
    current_max = Decimal(str(get_float(f"\n当前上限(≤{armor['initial_max']:.1f})：", 0, float(armor['initial_max']))))
    remaining = Decimal(str(get_float(f"剩余耐久(≤{current_max:.1f})：", 0, float(current_max))))
    
    state = {'current_max': current_max, 'remaining': remaining, 'trd': None}
    tool_colors = ['蓝', '紫', '金', '红']
    count = 0
    
    while True:
        count += 1
        print(f"\n{'='*60}")
        print(f"第 {count} 次维修")
        print(f"当前状态：上限={state['current_max']:.2f}，耐久={state['remaining']:.2f}")
        
        print("\n请选择维修工具：")
        for i, color in enumerate(tool_colors, 1):
            eff = armor['efficiencies'].get(color)
            if eff and eff > 0:
                max_pts = tool_config.get(color, {}).get('点数', Decimal("0"))
                print(f"{i}. {color}色维修包 ({max_pts}点, 效率{eff:.3f})")
            else:
                print(f"{i}. {color}色维修包 (不可用)")
        tool_choice = get_choice("请输入(1-4)：", ["1", "2", "3", "4"])
        tool_color = tool_colors[int(tool_choice)-1]
        eff = armor['efficiencies'].get(tool_color)
        if not eff or eff <= 0:
            print(f"该装备无法使用{tool_color}色维修工具")
            continue
        max_pts = tool_config.get(tool_color, {}).get('点数', Decimal("0"))
        use_full = get_choice("使用全部点数？(y/n)：", ["y", "Y", "n", "N"])
        if use_full.lower() == 'y':
            points_used = None
        else:
            points_used = Decimal(str(get_int(f"请输入点数(1-{max_pts})：", 1, int(max_pts))))
        
        result = calculate_repair(armor, state['current_max'], state['remaining'],
                                  tool_color, points_used, state['trd'])
        if not result.get('success'):
            print(f"错误：{result.get('message')}")
            if result.get('is_repairable') is False:
                break
            continue
        
        state['current_max'] = result['new_max']
        state['remaining'] = result['new_remaining']
        state['trd'] = result['new_trd']
        
        # 显示结果（消耗点数显示小数，剩余点数向上取整）
        consumed_display = result['consumed_points']
        remaining_display = result['remaining_points'].to_integral_value(rounding=ROUND_CEILING)
        
        print(f"\n【维修结果】")
        print(f"  预判新上限：{result['pre_new_max']:.2f}")
        print(f"  消耗点数：{consumed_display:.2f}")
        print(f"  剩余点数：{remaining_display}（游戏内以整数保存）")
        print(f"  实际修复量：{result['actual_repair']:.2f}")
        print(f"  新TRD：{result['new_trd']:.2f}")
        print(f"  MDP：{result['mdp']:.4f} ({result['mdp']*100:.2f}%)")
        print(f"  维修后上限：{result['new_max']:.2f}")
        print(f"  维修后耐久：{result['new_remaining']:.2f}")
        print(f"  状态：{'✅ 修满' if result['is_full'] else '❌ 未修满'}")
        
        if result['is_full']:
            print("\n===== 修理完成 =====")
            break
        if result['new_max'] < Decimal("1"):
            print("\n===== 不可维修 =====")
            break
        cont = get_choice("\n继续维修？(y/n)：", ["y", "Y", "n", "N"])
        if cont.lower() != 'y':
            break
    
    print(f"\n最终状态：")
    print(f"  上限：{state['current_max']:.2f}")
    print(f"  耐久：{state['remaining']:.2f}")
    if state['trd'] is not None:
        print(f"  累计TRD：{state['trd']:.2f}")
    input("\n按回车键结束...")

if __name__ == "__main__":
    main()
