import re
import os

# ===================== 适配你当前目录的配置（和截图100%匹配） =====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 你的教程文件（截图里已存在）
PROCESSED_FILE_NAME = "processed_instruction10-19.html"
# 你的模板文件（用截图里的step00.html）
TEMPLATE_FILE_NAME = "step00.html"

def extract_step_content(processed_file_path):
    """提取Step10-Step19的文本内容（保留所有行，不删冗余）"""
    step_content = {}
    current_step = None
    current_lines = []
    try:
        with open(processed_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ 读取教程文件失败：{e}")
        return step_content

    for line in lines:
        line_stripped = line.strip()
        # 匹配<!-- Step 10 -->这类注释
        step_match = re.match(r'<!-- Step (\d+) -->', line_stripped)
        if step_match:
            # 保存上一个步骤的内容
            if current_step is not None and current_lines:
                step_content[current_step] = current_lines.copy()
            current_step = int(step_match.group(1))
            current_lines = []
            continue
        # 收集当前步骤的非空行
        if current_step is not None and 10 <= current_step <= 19:
            if line_stripped:
                current_lines.append(line_stripped)
    # 保存最后一个步骤
    if current_step is not None and current_lines:
        step_content[current_step] = current_lines
    return step_content

def generate_image_html(step_num, img_count=6):
    """生成步骤对应的图片画廊HTML（适配模板格式）"""
    image_html = []
    image_html.append('<!-- Image Gallery Section - 6 Images with Captions -->')
    image_html.append('<div class="image-gallery">')
    for img_idx in range(1, img_count+1):
        img_item = f'''<div class="image-item">
<img alt="Step {step_num} - Image {img_idx}" class="step-image" data-image="{img_idx}" src="assets/images/substep_{step_num:02d}_{img_idx:02d}.png"/>
<div class="image-caption">
<h4>Figure {step_num}.{img_idx}: Image {img_idx}</h4>
<p>Description for step {step_num} image {img_idx}</p>
</div>
</div>'''
        image_html.append(img_item)
    image_html.append('</div>')
    return '\n'.join(image_html)

def generate_instruction_html(step_num, content_lines):
    """生成步骤说明HTML（每行对应一个instruction-item）"""
    instruction_html = []
    instruction_html.append('<!-- Step-by-Step Instructions -->')
    instruction_html.append('<div class="instruction-section">')
    instruction_html.append('''<div class="section-header">
<i class="fas fa-list-ol"></i>
<h3>Step-by-Step Instructions</h3>
</div>''')
    instruction_html.append('<div class="instruction-grid">')
    
    # 每行文本对应一个instruction-item
    for idx, line in enumerate(content_lines, 1):
        # 处理**加粗**为HTML标签
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

def replace_step_content(template_file_path, step_content):
    """直接在当前目录生成/覆盖step10.html ~ step19.html"""
    # 读取模板文件
    try:
        with open(template_file_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except Exception as e:
        print(f"❌ 读取模板文件失败：{e}")
        return

    # 定位模板中需要替换的区块
    gallery_start_marker = '<!-- Image Gallery Section - 6 Images with Captions -->'
    gallery_end_pattern = re.escape(gallery_start_marker) + r'.*?</div></div>'
    instruction_start_marker = '<!-- Step-by-Step Instructions -->'
    instruction_end_pattern = re.escape(instruction_start_marker) + r'.*?</div></div>'

    # 为Step10-Step19生成文件（直接写到当前目录）
    for step_num in range(10, 20):
        # 获取当前步骤的文本行
        current_lines = step_content.get(step_num, [f"Default instruction for step {step_num}, line {i}" for i in range(1, 4)])
        
        # 生成图片画廊和步骤说明HTML
        gallery_html = generate_image_html(step_num)
        instruction_html = generate_instruction_html(step_num, current_lines)

        # 替换模板内容
        new_content = re.sub(gallery_end_pattern, gallery_html, template, flags=re.DOTALL)
        new_content = re.sub(instruction_end_pattern, instruction_html, new_content, flags=re.DOTALL)

        # 输出路径：当前目录/stepXX.html（直接覆盖/创建）
        output_file_path = os.path.join(SCRIPT_DIR, f'step{step_num}.html')
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ 已生成/覆盖：{output_file_path} (包含{len(current_lines)}个步骤项)")
        except Exception as e:
            print(f"❌ 保存step{step_num}.html失败：{e}")

def check_file_exists(file_path, file_desc):
    """检查文件是否存在"""
    if not os.path.exists(file_path):
        print(f"\n❌ 未找到【{file_desc}】：{file_path}")
        print(f"📂 当前目录文件列表：{os.listdir(SCRIPT_DIR)}")
        return False
    print(f"✅ 找到【{file_desc}】：{file_path}")
    return True

if __name__ == "__main__":
    # 拼接文件完整路径
    processed_file_path = os.path.join(SCRIPT_DIR, PROCESSED_FILE_NAME)
    template_file_path = os.path.join(SCRIPT_DIR, TEMPLATE_FILE_NAME)

    # 打印目录信息（方便核对）
    print("="*60)
    print("📌 目录与文件信息")
    print(f"   脚本所在目录：{SCRIPT_DIR}")
    print(f"   教程文件路径：{processed_file_path}")
    print(f"   模板文件路径：{template_file_path}")
    print("="*60)

    # 检查关键文件
    processed_ok = check_file_exists(processed_file_path, "教程文件 processed_instruction10-19.html")
    template_ok = check_file_exists(template_file_path, "模板文件 step00.html")
    if not (processed_ok and template_ok):
        print("\n❌ 关键文件缺失！请确认文件在当前目录后重试。")
        exit(1)

    # 解析教程内容
    print("\n🔍 正在解析教程文件中的步骤内容...")
    step_content_dict = extract_step_content(processed_file_path)
    if not step_content_dict:
        print("❌ 未提取到任何步骤内容！请检查教程文件是否包含<!-- Step 10 -->等注释。")
        exit(1)
    print(f"✅ 解析完成！提取到的步骤：{list(step_content_dict.keys())}")

    # 生成/覆盖step10-step19.html（直接写到当前目录）
    print("\n📝 开始生成/覆盖step10.html ~ step19.html（当前目录）...")
    replace_step_content(template_file_path, step_content_dict)

    # 完成提示
    print("\n🎉 操作完成！")
    print(f"   当前目录已生成/更新：step10.html ~ step19.html")
    print(f"   可直接在当前目录查看这些文件。")
    print("="*60)