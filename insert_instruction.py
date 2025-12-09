import re
import os

# ===================== 核心配置（仅改这两个，其他全不动） =====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_FILE = "processed_instruction10-19.html"  # 教程文本文件
TEMPLATE_FILE = "step00.html"                       # 模板文件（完全保留原有结构）

def extract_step_content():
    """提取Step10-Step19的文本内容，按行拆分（保留所有冗余/重复行）"""
    step_content = {}
    current_step = None
    current_lines = []
    
    # 读取处理后的教程文件
    with open(os.path.join(SCRIPT_DIR, PROCESSED_FILE), 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line_stripped = line.strip()
        # 匹配<!-- Step X -->注释，定位步骤
        step_match = re.match(r'<!-- Step (\d+) -->', line_stripped)
        if step_match:
            # 保存上一个步骤的内容
            if current_step is not None and current_lines:
                step_content[current_step] = current_lines.copy()
            current_step = int(step_match.group(1))
            current_lines = []
            continue
        # 仅收集非空行，保留所有重复/冗余行
        if current_step is not None and 10 <= current_step <= 19 and line_stripped:
            current_lines.append(line_stripped)
    
    # 保存最后一个步骤
    if current_step is not None and current_lines:
        step_content[current_step] = current_lines
    return step_content

def replace_image_caption_p(step_num, template_content, content_lines):
    """
    仅替换模板中每个image-item下的<p></p>标签内容，其他所有内容完全不动
    :param step_num: 当前步骤号（10-19）
    :param template_content: 模板完整HTML内容
    :param content_lines: 当前步骤的文本行列表
    :return: 替换后的HTML内容
    """
    # 正则匹配所有image-item下的<p>标签（非贪婪匹配，确保每个<p>独立）
    p_pattern = r'(<div class="image-item">.*?<div class="image-caption">.*?<h4>.*?</h4>.*?)<p>.*?</p>(.*?</div>.*?</div>)'
    
    # 拆分匹配结果，按顺序替换每个<p>的内容
    def replace_p_tag(match, lines=iter(content_lines)):
        """迭代替换每个<p>标签内容"""
        prefix = match.group(1)  # <p>之前的所有内容（图片/标题等，完全保留）
        suffix = match.group(2)  # <p>之后的所有内容（完全保留）
        try:
            # 取当前行文本，处理**加粗**为<strong>
            line = next(lines)
            line_formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            new_p = f'<p>{line_formatted}</p>'
        except StopIteration:
            # 文本行不足时，保留默认说明（可自定义）
            new_p = f'<p>Step {step_num} - Additional assembly notes for this image.</p>'
        # 拼接：保留所有原有内容，仅替换<p>标签内的文本
        return f'{prefix}{new_p}{suffix}'
    
    # 执行替换（全局替换所有image-item下的<p>）
    updated_content = re.sub(
        p_pattern, 
        replace_p_tag, 
        template_content, 
        flags=re.DOTALL | re.IGNORECASE
    )
    return updated_content

def generate_step_files():
    """生成step10-step19.html，仅替换图片<p>标签内容，其他全不动"""
    # 1. 检查关键文件
    if not os.path.exists(os.path.join(SCRIPT_DIR, PROCESSED_FILE)):
        print(f"❌ 错误：未找到 {PROCESSED_FILE}，请确认文件在当前目录！")
        return
    if not os.path.exists(os.path.join(SCRIPT_DIR, TEMPLATE_FILE)):
        print(f"❌ 错误：未找到 {TEMPLATE_FILE}，请确认文件在当前目录！")
        return
    
    # 2. 读取模板文件（完全保留所有原始内容）
    with open(os.path.join(SCRIPT_DIR, TEMPLATE_FILE), 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 3. 提取教程文本内容
    step_content = extract_step_content()
    if not step_content:
        print("❌ 错误：未提取到Step10-Step19的任何内容！")
        return
    
    # 4. 逐步骤生成文件（仅替换图片<p>内容）
    for step_num in range(10, 20):
        # 获取当前步骤的文本行（无内容时用默认）
        content_lines = step_content.get(step_num, [f"Step {step_num} image note {i}" for i in range(1, 7)])
        # 仅替换图片<p>标签内容，其他所有内容完全不动
        final_content = replace_image_caption_p(step_num, template_content, content_lines)
        # 保存到当前目录（覆盖/创建stepXX.html）
        output_path = os.path.join(SCRIPT_DIR, f'step{step_num}.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"✅ 已生成 {output_path}（仅替换图片<p>标签内容，其他全保留）")

if __name__ == "__main__":
    print("📝 开始生成文件，仅替换图片<p>标签内容，其他内容完全不动...")
    generate_step_files()
    print("\n🎉 生成完成！所有文件仅修改图片的<p>说明，图片路径/结构均未改动！")