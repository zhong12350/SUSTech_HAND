import re
import os

# ===================== 核心配置（仅改这两个，其他全不动） =====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_FILE = "processed_instruction10-19.html"  # 你的教程文本
TEMPLATE_FILE = "step00.html"                       # 你的模板文件（完全保留原有内容）

def extract_step_content():
    """仅提取Step10-Step19的文本内容，按行拆分"""
    step_content = {}
    current_step = None
    current_lines = []
    
    with open(os.path.join(SCRIPT_DIR, PROCESSED_FILE), 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line_stripped = line.strip()
        # 匹配<!-- Step X -->注释
        step_match = re.match(r'<!-- Step (\d+) -->', line_stripped)
        if step_match:
            if current_step is not None and current_lines:
                step_content[current_step] = current_lines.copy()
            current_step = int(step_match.group(1))
            current_lines = []
            continue
        # 仅收集非空行，保留所有冗余/重复行
        if current_step is not None and 10 <= current_step <= 19 and line_stripped:
            current_lines.append(line_stripped)
    
    if current_step is not None and current_lines:
        step_content[current_step] = current_lines
    return step_content

def generate_instruction_only(step_num, content_lines):
    """仅生成instruction部分的HTML，完全匹配模板结构，不碰其他"""
    instruction_html = []
    # 仅替换instruction-grid里的内容，外层结构完全保留模板原样
    instruction_html.append('<!-- Step-by-Step Instructions -->')
    instruction_html.append('<div class="instruction-section">')
    instruction_html.append('''<div class="section-header">
<i class="fas fa-list-ol"></i>
<h3>Step-by-Step Instructions</h3>
</div>''')
    instruction_html.append('<div class="instruction-grid">')
    
    # 每行文本对应一个instruction-item，完全保留你的模板样式
    for idx, line in enumerate(content_lines, 1):
        # 仅处理**加粗**，其他文本原样保留
        line_formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
        instruction_item = f'''<!-- Instruction {idx} -->
<div class="instruction-item">
<div class="instruction-number">{idx}</div>
<div class="instruction-content">
<h4>Step {step_num}.{idx} Operation</h4>
<p>{line_formatted}</p>
<div class="tip-box">
<i class="fas fa-lightbulb"></i>
<strong>Tip:</strong> Ensure proper assembly to avoid functional issues.
                            </div>
</div>
</div>'''
        instruction_html.append(instruction_item)
    
    instruction_html.append('</div>')
    instruction_html.append('</div>')
    return '\n'.join(instruction_html)

def update_only_instruction():
    """仅替换instruction部分，图片/其他所有内容完全保留模板原样"""
    # 1. 读取模板文件（完全保留所有内容）
    template_path = os.path.join(SCRIPT_DIR, TEMPLATE_FILE)
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 2. 提取教程内容
    step_content = extract_step_content()
    if not step_content:
        print("❌ 未提取到任何步骤内容！")
        return
    
    # 3. 仅替换instruction部分，图片部分完全不动
    instruction_marker = '<!-- Step-by-Step Instructions -->'
    # 匹配instruction整个区块（保留其他所有内容）
    instruction_pattern = re.escape(instruction_marker) + r'.*?</div></div>'
    
    # 4. 生成step10-step19.html（仅改instruction，其他全不动）
    for step_num in range(10, 20):
        content_lines = step_content.get(step_num, [f"Step {step_num} instruction line {i}" for i in range(1, 4)])
        # 生成仅instruction的HTML
        new_instruction = generate_instruction_only(step_num, content_lines)
        # 替换模板中的instruction部分，其他内容（包括图片）完全不变
        final_content = re.sub(instruction_pattern, new_instruction, template_content, flags=re.DOTALL)
        
        # 保存到当前目录（step10.html ~ step19.html）
        output_path = os.path.join(SCRIPT_DIR, f'step{step_num}.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"✅ 已生成 {output_path}（仅修改instruction，其他内容完全保留模板原样）")

if __name__ == "__main__":
    # 检查关键文件
    if not os.path.exists(os.path.join(SCRIPT_DIR, PROCESSED_FILE)):
        print(f"❌ 未找到 {PROCESSED_FILE}，请确认文件在当前目录！")
    elif not os.path.exists(os.path.join(SCRIPT_DIR, TEMPLATE_FILE)):
        print(f"❌ 未找到 {TEMPLATE_FILE}，请确认文件在当前目录！")
    else:
        print("📝 开始更新，仅修改instruction部分，其他内容完全不动...")
        update_only_instruction()
        print("\n🎉 全部生成完成！所有文件仅instruction部分更新，图片/结构均未修改！")