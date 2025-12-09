import re

def process_robot_hand_instructions(file_path):
    """
    处理机器人灵巧手组装教程文本：
    1. 按/分割步骤并标注step10-step19
    2. 彻底删除相邻重复行（包含全空白行去重）
    3. 润色语言使其更专业
    """
    # 读取文件内容（保留原始换行符）
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ========== 核心修复：彻底删除相邻重复行 ==========
    lines = content.split('\n')
    cleaned_lines = []
    prev_line = None  # 记录上一行（去除首尾空白后的值）
    for raw_line in lines:
        # 处理当前行：去除首尾空白（统一比对标准）
        current_stripped = raw_line.strip()
        
        # 仅当当前行与上一行不同时，才保留原始行
        if current_stripped != prev_line:
            cleaned_lines.append(raw_line)  # 保留原始格式（含缩进/空格）
            prev_line = current_stripped    # 更新上一行比对值
        # 重复行则直接跳过
    
    # 重新拼接为文本（保留原始换行结构）
    cleaned_content = '\n'.join(cleaned_lines)
    
    # ========== 步骤标注（step10-step19） ==========
    step_num = 10
    # 分割步骤：处理/前后的任意空白（换行/空格/制表符）
    steps = re.split(r'\s*/\s*', cleaned_content)
    processed_steps = []
    for step in steps:
        step_stripped = step.strip()
        if step_stripped:  # 跳过空步骤
            # 添加HTML注释标注，保持格式整洁
            step_label = f"<!-- Step {step_num} -->"
            processed_steps.append(f"{step_label}\n{step_stripped}")
            step_num += 1
            if step_num > 19:
                break  # 仅处理10-19步
    
    # 合并步骤（步骤间用空行分隔）
    processed_content = '\n\n'.join(processed_steps)
    
    # ========== 专业语言润色 ==========
    polish_rules = {
        # 拼写错误修正
        r'scrwews\b': 'screws',
        r'thay\b': 'they',
        # 口语化表达→专业表达
        r'wiggling it around while pushing it in can help': 'gently wiggle and push the tube to facilitate insertion',
        r'It might be easier to first': 'It is recommended to first',
        r'Press firmly': 'Apply firm pressure',
        r'pull them and bring the carpal on to': 'pull the tendons taut and mount the carpal onto',
        r'significant amount of tension': 'sufficient tension',
        r'tighten very securely': 'tighten the fastener securely to specification',
        r'trying to apply tension later will be significantly harder': 'subsequent tension adjustment will be substantially more difficult',
        # 专业术语标准化
        r'teflon tubing\b': 'PTFE tubing',
        r'finger assembly\b': 'finger subassembly',
        r'carpal holes\b': 'carpal apertures',
        r'tower holes\b': 'tower bores',
        r'rod\b': 'guide rod',
        r'washers\b': 'flat washers',
        r'groove\b': 'machined groove',
        r'motor teeth\b': 'motor gear teeth',
        r'belt\b(?!\s+sanitizer)': 'timing belt',  # 避免误匹配其他belt
        r'wrist gear\b': 'wrist drive gear',
        r'bearing covers\b': 'bearing retainer plates',
        # 关键步骤优化
        r'Follow the color coding to route the tendons through the carpal holes\. They should not cross each other': 
        'Route the tendons through the carpal apertures in accordance with the color-coding scheme; ensure no tendon crossover occurs',
        r'Note: The holes the tendons come out from at the other side of the carpal may appear random due to internal routing':
        'Note: The exit apertures of the tendons on the distal side of the carpal may appear irregular due to internal routing paths',
        r'Be extra careful with the routing as it\'s not as straightforward as the other fingers':
        'Exercise additional caution during tendon routing, as this process is less intuitive compared to the other digits',
        r'Reminder: If the tubing gets compressed or squished during cutting, use a thin round tool \(e\.g\., awl or screwdriver\) to reopen it for tendon passage':
        'Caution: If the PTFE tubing becomes compressed or deformed during cutting, ream the bore with a thin cylindrical tool (e.g., an awl or precision screwdriver) to ensure unobstructed tendon passage'
    }
    
    polished_content = processed_content
    for pattern, replacement in polish_rules.items():
        polished_content = re.sub(pattern, replacement, polished_content, flags=re.IGNORECASE)
    
    # ========== 保存结果 ==========
    output_path = 'processed_instruction10-19.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(polished_content)
    
    # 验证结果（输出去重前后行数对比）
    original_line_count = len(lines)
    cleaned_line_count = len(cleaned_lines)
    duplicate_count = original_line_count - cleaned_line_count
    print(f"✅ 处理完成！生成文件：{output_path}")
    print(f"📊 去重统计：原始行数 {original_line_count} → 处理后行数 {cleaned_line_count}，删除重复行 {duplicate_count} 行")
    return output_path

# 测试用例（可直接运行验证）
def test_duplicate_removal():
    """测试重复行删除功能"""
    test_text = """Cross them as shown in the image.
Cross them as shown in the image.
Image 3
Image 3

Attach the 2 M4x16 screws with washers on the side of the tower.

Image 2
Image 2"""
    lines = test_text.split('\n')
    cleaned_lines = []
    prev_line = None
    for raw_line in lines:
        current_stripped = raw_line.strip()
        if current_stripped != prev_line:
            cleaned_lines.append(raw_line)
            prev_line = current_stripped
    cleaned_text = '\n'.join(cleaned_lines)
    print("\n=== 重复行删除测试结果 ===")
    print("原始文本：")
    print(test_text)
    print("\n处理后文本：")
    print(cleaned_text)

# 执行处理
if __name__ == "__main__":
    # 先运行测试用例验证去重功能
    test_duplicate_removal()
    
    # 处理目标文件
    input_file = "instruction10-19.html"
    try:
        process_robot_hand_instructions(input_file)
    except FileNotFoundError:
        print(f"\n❌ 错误：未找到文件 {input_file}，请确认文件路径正确")
    except Exception as e:
        print(f"\n❌ 处理出错：{str(e)}")