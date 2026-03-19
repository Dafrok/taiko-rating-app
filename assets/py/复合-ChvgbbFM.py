import math

def calculate_composite_difficulty(an, bn, T):
    """
    计算复合难度和复合难占比（按子数组分割的新逻辑）
    
    参数:
    an: 原始数组 [a0, a1, ..., an]
    bn: 标记数组 [b0, b1, ..., b(n+1)]，仅包含1和2
    
    返回:
    total_difficulty: 复合难度之和
    difficulty_ratio: 复合难占比
    marks: L/R标记数组
    hand_change: 换手标记数组
    sub_array_details: 子数组详细信息列表（包含每个子数组的sync标记）
    """
    # 验证输入
    if len(bn) != len(an) + 1:
        raise ValueError(f"bn数组长度应为{len(an)+1}，实际为{len(bn)}")
    
    for b in bn:
        if b not in [1, 2]:
            raise ValueError(f"bn数组只能包含1和2，发现值: {b}")
    
    # 步骤1: 补0并标记L/R
    a = an.copy()
    a.append(0)  # 补a(n+1)=0
    n = len(a)
    
    # 步骤2: 标记L/R
    marks = [''] * n
    marks[0] = 'R'  # a0标记为R
    
    for i in range(1, n):
        if marks[i-1] == 'R' and a[i-1] < T:
            marks[i] = 'L'
        else:
            marks[i] = 'R'
    
    # 验证标记规则：不可能有连续两个L
    for i in range(1, n):
        if marks[i] == 'L' and marks[i-1] == 'L':
            print(f"警告：在位置{i}发现连续两个L标记，这不符合标记规则")
    
    # 步骤1.1: 标记换手(hand_change)
    hand_change = [None] * n
    
    # 记录每个标记类型上一次出现的位置
    last_R_index = 0
    last_L_index = None
    
    for i in range(1, n):
        if marks[i] == 'R':
            if last_R_index is not None and i != last_R_index:
                if bn[last_R_index] != bn[i]:
                    hand_change[i] = 1
                else:
                    hand_change[i] = 0
            last_R_index = i
        else:  # marks[i] == 'L'
            if last_L_index is not None:
                if bn[last_L_index] != bn[i]:
                    hand_change[i] = 1
                else:
                    hand_change[i] = 0
            last_L_index = i
    
    # 步骤2: 找到所有满足RLRL...循环的子数组
    sub_arrays = []  # 存储子数组的起始和结束索引
    sub_array_marks = []  # 存储子数组的标记模式
    
    i = 0
    while i < n:
        # 找到从i开始的RLRL...循环
        pattern = []
        start = i
        
        # 检查RLRL循环
        j = i
        while j < n:
            expected_mark = 'R' if (j - i) % 2 == 0 else 'L'
            if marks[j] == expected_mark:
                pattern.append(j)
                j += 1
            else:
                break
        
        # 检查是否出现连续两个R
        if j < n and j-1 >= 0 and marks[j-1] == 'R' and marks[j] == 'R':
            # 找到连续两个R，子数组结束
            if len(pattern) >= 6:  # 只记录长度大于等于6的子数组
                sub_arrays.append((start, pattern[-1] + 1))  # 结束索引是包含的
                sub_array_marks.append(marks[start:pattern[-1] + 1])
            i = pattern[-1] + 1  # 从连续R的第一个开始下一个子数组
        else:
            # 没有找到合适的子数组，跳过当前位置
            i += 1
    
    # 步骤3: 计算每个子数组的复合难度
    total_difficulty = 0
    
    def get_interval_coeff(value):
        threshold_low = 15/130 * 1000
        threshold_high = 15/90 * 1000
        
        if value <= threshold_low:
            return 1.0
        elif value >= threshold_high:
            return 0.0
        else:
            return 1.0 - (value - threshold_low) / (threshold_high - threshold_low)
    
    # 存储每个子数组的详细信息
    sub_array_details = []
    
    for sub_idx, (start, end) in enumerate(sub_arrays):
        sub_length = end - start
        
        if sub_length < 6:
            # 子数组长度小于6，跳过
            continue
        
        # 步骤1.2: 在子数组中标记同步(sync) - 简化版本
        sub_sync = [None] * sub_length
        
        # 由于子数组是RLRL循环，同步标记可以简化判断
        # 对于R标记元素，比较当前和前一个R标记的hand_change
        # 对于L标记元素，比较当前和前一个L标记的hand_change
        # 由于RLRL循环，相同标记间隔1个位置
        for i_in_sub in range(sub_length):
            i_in_full = start + i_in_sub
            
            # 子数组内，奇数索引是L，偶数索引是R
            if i_in_sub % 2 == 0:  # R标记元素
                # 找到上上一个R标记（索引差2）
                if i_in_sub >= 2:
                    prev_R_in_sub = i_in_sub - 2
                    prev_R_in_full = start + prev_R_in_sub
                    if hand_change[i_in_full] is not None and hand_change[prev_R_in_full] is not None:
                        if hand_change[i_in_full] == hand_change[prev_R_in_full]:
                            sub_sync[i_in_sub] = 1
                        else:
                            sub_sync[i_in_sub] = 0
            else:  # L标记元素
                # 找到上上一个L标记（索引差2）
                if i_in_sub >= 3:  # 第一个L标记是索引1，需要至少索引3才有前一个L标记
                    prev_L_in_sub = i_in_sub - 2
                    prev_L_in_full = start + prev_L_in_sub
                    if hand_change[i_in_full] is not None and hand_change[prev_L_in_full] is not None:
                        if hand_change[i_in_full] == hand_change[prev_L_in_full]:
                            sub_sync[i_in_sub] = 1
                        else:
                            sub_sync[i_in_sub] = 0
        
        sub_difficulty = 0
        
        # 从子数组的第6个元素开始（索引start+5）
        for i_in_full in range(start + 5, end):
            i_in_sub = i_in_full - start
            
            # 计算基础系数：比较当前元素与上一个元素的同步标记
            if sub_sync[i_in_sub] is not None and sub_sync[i_in_sub-1] is not None:
                if sub_sync[i_in_sub] != sub_sync[i_in_sub-1]:
                    a_coeff = 1
                else:
                    a_coeff = 0
            else:
                a_coeff = 0
            
            # 计算b系数
            if i_in_full >= 2:  # 确保有a(i-1)和a(i-2)
                b_coeff_prev1 = get_interval_coeff(a[i_in_full-1]) if i_in_full-1 >= 0 else 1.0
                b_coeff_prev2 = get_interval_coeff(a[i_in_full-2]) if i_in_full-2 >= 0 else 1.0
                b_coeff = b_coeff_prev1 * b_coeff_prev2
            else:
                b_coeff = 1.0
            
            # 计算当前元素的难度贡献
            element_difficulty = a_coeff * b_coeff
            sub_difficulty += element_difficulty
        
        # 乘上ln(子数组长度)
        if sub_difficulty > 0:
            sub_difficulty *= math.log(sub_length)
        
        total_difficulty += sub_difficulty
        
        # 记录子数组详细信息
        sub_array_details.append({
            'start': start,
            'end': end - 1,  # 包含的结束索引
            'length': sub_length,
            'marks': marks[start:end],
            'sync': sub_sync.copy(),  # 记录子数组的同步标记
            'difficulty': sub_difficulty
        })
    
    # 计算复合难占比
    difficulty_ratio = total_difficulty / len(an) if len(an) > 0 else 0
    
    return total_difficulty, difficulty_ratio, marks, hand_change, sub_array_details


def compute_final_composite_difficulty(an, bn):
    """
    完整的复合难度计算方法（考虑T的选择）
    
    参数:
    an: 原始数组 [a0, a1, ..., an]
    bn: 标记数组 [b0, b1, ..., b(n+1)]，仅包含1和2
    
    返回:
    final_difficulty: 最终复合难度之和
    final_ratio: 最终复合难占比
    T_used: 使用的T值（或计算方法说明）
    marks: L/R标记数组
    hand_change: 换手标记数组
    sub_array_details: 子数组详细信息列表
    """
    # 计算阈值
    t_low = 30/260 * 1000
    t_high = 30/180 * 1000
    t0 = t_high
    tm = t_low
    
    print(f"阈值范围: ({tm:.2f}, {t0:.2f}) 开区间")
    print(f"t0 = {t0:.2f}, tm = {tm:.2f}")
    
    # 检查数组中是否有介于(tm, t0)之间的数
    candidate_values = []
    for value in an:
        if tm < value < t0:
            candidate_values.append(value)
    
    candidate_values = sorted(list(set(candidate_values)), reverse=True)
    
    if not candidate_values:
        print("数组中不存在严格介于(tm, t0)之间的数")
        print(f"使用T = t0 = {t0:.2f}")
        difficulty, ratio, marks, hand_change, sub_arrays = calculate_composite_difficulty(an, bn, t0)
        return difficulty, ratio, t0, marks, hand_change, sub_arrays
    
    print(f"找到严格介于(tm, t0)之间的数: {candidate_values}")
    
    T_values = [t0] + candidate_values
    print(f"T值列表: {[f'{t:.2f}' for t in T_values]}")
    
    difficulties = []
    for i, T in enumerate(T_values):
        difficulty, _, _, _, _ = calculate_composite_difficulty(an, bn, T)
        difficulties.append(difficulty)
        print(f"T={T:.2f}时的复合难度之和: {difficulty:.6f}")
    
    # 步骤3: 计算权重（修改为1/B-1/A的形式）
    weights = []
    for i in range(len(T_values) - 1):
        A = T_values[i]
        B = T_values[i + 1]
        weight = 1/B - 1/A
        weights.append(weight)
    
    # 最后一个权重: 1/tm - 1/tn
    weights.append(1/tm - 1/T_values[-1])
    
    print(f"权重列表: {[f'{w:.6f}' for w in weights]}")
    
    # 验证所有权重之和等于1/tm - 1/t0
    total_weight = sum(weights)
    expected_total = 1/tm - 1/t0
    print(f"权重总和: {total_weight:.6f}, 期望值(1/tm-1/t0): {expected_total:.6f}")
    
    # 步骤4: 计算加权几何平均值
    if total_weight <= 0:
        # 如果所有权重非正，则返回第一个难度值
        weighted_geometric = difficulties[0]
    else:
        # 计算加权几何平均值
        weighted_sum_log = 0
        for i, difficulty in enumerate(difficulties):
            if difficulty > 0:  # 只处理正数
                weighted_sum_log += math.log(difficulty) * weights[i]
            else:
                # 如果难度为0或负数，几何平均数为0
                weighted_geometric = 0
                break
        else:
            # 如果所有难度都为正数
            weighted_geometric = math.exp(weighted_sum_log / total_weight)
    
    # 步骤5: 计算复合难占比
    final_ratio = weighted_geometric / len(an) if len(an) > 0 else 0
    
    print(f"加权几何平均复合难度之和: {weighted_geometric:.6f}")
    print(f"最终复合难占比: {final_ratio:.6f}")
    
    # 使用第一个T值计算详细信息
    T_used = T_values[0]
    difficulty, ratio, marks, hand_change, sub_arrays = calculate_composite_difficulty(an, bn, T_used)
    
    return weighted_geometric, final_ratio, T_used, marks, hand_change, sub_arrays


# 测试函数
def test_composite_difficulty():
    """测试复合难度计算"""
    
    print("复合难度计算测试（新逻辑）")
    print("=" * 60)
    
    # 测试1: 验证标记规则
    print("测试1: 验证标记规则")
    an1 = [100, 120, 80, 150, 90, 110, 130]
    bn1 = [1, 2, 1, 2, 1, 1, 2, 1]
    T1 = 100
    
    difficulty1, ratio1, marks1, hand_change1, sub_arrays1 = calculate_composite_difficulty(an1, bn1, T1)
    
    print(f"an数组: {an1}")
    print(f"T值: {T1}")
    print(f"L/R标记: {marks1}")
    print(f"标记序列: {' '.join(marks1)}")
    
    # 验证标记规则
    print("\n验证标记规则:")
    for i in range(1, len(marks1)):
        if marks1[i] == 'L':
            print(f"  a[{i}]是L，检查a[{i-1}]必须是R且a[{i-1}]<T")
            print(f"  a[{i-1}]={an1[i-1] if i-1 < len(an1) else 0}, 标记:{marks1[i-1]}, 条件: marks[{i-1}]=='R' and a[{i-1}]<{T1}")
            condition_met = marks1[i-1] == 'R' and (an1[i-1] if i-1 < len(an1) else 0) < T1
            print(f"  结果: {'满足' if condition_met else '不满足'}")
    
    print(f"\n子数组信息:")
    for i, sub in enumerate(sub_arrays1):
        print(f"  子数组{i+1}: 起始索引={sub['start']}, 结束索引={sub['end']}, 长度={sub['length']}")
        print(f"          标记序列: {sub['marks']}")
        if 'sync' in sub:
            print(f"          同步标记: {sub['sync']}")
        print(f"          难度: {sub['difficulty']:.6f}")
    
    print(f"\n复合难度之和: {difficulty1:.6f}")
    print(f"复合难占比: {ratio1:.6f}")
    print()
    
    # 测试2: 演示子数组分割
    print("测试2: 演示子数组分割")
    an2 = [50, 120, 80, 150, 90, 110, 130, 70, 140, 85, 95, 105, 115, 125, 135, 145, 155, 165, 175, 185]
    bn2 = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1]
    T2 = 100
    
    difficulty2, ratio2, marks2, hand_change2, sub_arrays2 = calculate_composite_difficulty(an2, bn2, T2)
    
    print(f"an数组长度: {len(an2)}")
    print(f"T值: {T2}")
    print(f"标记序列: {' '.join(marks2)}")
    
    # 分析子数组
    print(f"\n子数组分析:")
    for i, sub in enumerate(sub_arrays2):
        print(f"  子数组{i+1}:")
        print(f"    位置: 索引[{sub['start']}]-[{sub['end']}]，长度={sub['length']}")
        print(f"    标记: {' '.join(sub['marks'])}")
        if 'sync' in sub:
            print(f"    同步标记: {sub['sync']}")
        print(f"    难度: {sub['difficulty']:.6f}")
    
    print(f"\n复合难度之和: {difficulty2:.6f}")
    print(f"复合难占比: {ratio2:.6f}")
    print()
    
    # 测试3: 演示加权几何平均计算
    print("测试3: 演示加权几何平均计算")
    an3 = [120, 140, 160, 180, 200]
    bn3 = [1, 2, 1, 2, 1, 2]
    
    print(f"an数组: {an3}")
    print(f"bn数组: {bn3}")
    
    result3, ratio3, T_used3, marks3, hand_change3, sub_arrays3 = compute_final_composite_difficulty(an3, bn3)
    print(f"最终复合难度之和: {result3:.6f}")
    print(f"最终复合难占比: {ratio3:.6f}")
    print(f"使用的T值: {T_used3}")


# 演示标记规则
def explain_marking_rules():
    """演示标记规则"""
    print("标记规则演示")
    print("=" * 60)
    print("标记规则：")
    print("1. a0标记为'R'")
    print("2. 对于ai(i>=1):")
    print("   - 如果a(i-1)标记为'R'且a(i-1)<T，则ai标记为'L'")
    print("   - 否则标记为'R'")
    print()
    print("子数组提取规则：")
    print("1. 从数组第一个元素（标记为R）开始")
    print("2. 按顺序提取元素形成子数组，要求标记模式为RLRLRL...循环")
    print("3. 当遇到连续两个R标记时，结束当前子数组")
    print("4. 子数组长度必须≥6才参与计算")
    print("5. 从子数组的末尾对应到原数组的下一个元素开始重复上述过程")
    print()
    print("基础系数计算新规则：")
    print("1. 从子数组的第6个元素开始观察")
    print("2. 比较当前观察元素与上一个元素的同步标记")
    print("3. 若同步标记不同，基础系数=1，否则=0")
    print()
    print("复合难度计算：")
    print("1. 对每个子数组从第6个元素开始计算难度")
    print("2. 子数组难度 = Σ(a_coeff * b_coeff)")
    print("3. 最终子数组难度 = 子数组难度 * ln(子数组长度)")
    print("4. 总难度 = 所有子数组难度之和")
    print()


# 演示加权几何平均计算
def explain_weighted_geometric():
    """演示加权几何平均计算"""
    print("加权几何平均计算演示")
    print("=" * 60)
    print("权重计算公式：weight = 1/B - 1/A")
    print("其中A和B是相邻的T值")
    print("最后一个权重：weight = 1/tm - 1/tn")
    print("所有权重之和：sum(weights) = 1/tm - 1/t0")
    print()
    print("加权几何平均值计算公式：")
    print("exp(∑(w_i * log(difficulty_i)) / ∑w_i)")
    print("其中w_i是权重，difficulty_i是对应的复合难度")
    print()
    print("注意：")
    print("1. 加权几何平均值要求所有difficulty_i > 0")
    print("2. 如果任意difficulty_i <= 0，加权几何平均值=0")
    print("3. 如果权重总和<=0，使用第一个难度值")
    print()


if __name__ == "__main__":
    # 演示标记规则
    explain_marking_rules()
    
    # 演示加权几何平均计算
    explain_weighted_geometric()
    
    # 运行测试
    test_composite_difficulty()
    
    # 创建一个简单的交互式测试
    print("\n" + "=" * 60)
    print("简单交互测试")
    print("=" * 60)
    
    # 使用固定的测试数据
    an_test = [50, 120, 80, 150, 90, 110, 130, 70, 140, 85, 95, 105, 115, 125, 135, 145, 155, 165, 175, 185]
    bn_test = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1]
    
    print(f"测试数据：")
    print(f"an = {an_test}")
    print(f"bn长度: {len(bn_test)} (应为{len(an_test)+1})")
    
    try:
        result, ratio, T_used, marks, hand_change, sub_arrays = compute_final_composite_difficulty(an_test, bn_test)
        
        print(f"\n计算结果：")
        print(f"最终复合难度之和: {result:.6f}")
        print(f"最终复合难占比: {ratio:.6f}")
        print(f"使用的T值: {T_used}")
        print(f"L/R标记: {' '.join(marks)}")
        print(f"\n子数组信息:")
        for i, sub in enumerate(sub_arrays):
            print(f"  子数组{i+1}: 长度={sub['length']}, 标记={' '.join(sub['marks'])}")
            if 'sync' in sub:
                print(f"      同步标记: {sub['sync']}")
            print(f"      难度: {sub['difficulty']:.6f}")
        
    except Exception as e:
        print(f"计算错误: {e}")
        import traceback
        traceback.print_exc()
