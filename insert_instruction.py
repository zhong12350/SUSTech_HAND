import re
import os
import sys

# ===================== 核心配置（无需修改） =====================
# 当前目录（脚本所在目录 = 要替换的stepxx.html所在目录）
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
# 教程文本文件（必须在当前目录）
TEXT_FILE = os.path.join(CURRENT_DIR, "processed_instruction10-19.html")
# 模板文件（必须在当前目录，step00.html）
TEMPLATE_FILE = os.path.join(CURRENT_DIR, "step00.html")

def parse_step_text():
    """解析教程文本，提取Step10-Step19的文本行（保留所有冗余）"""
    step_text = {}
    current_step = None
    lines = []

    # 检查教程文件是否存在
    if not os.path.exists(TEXT_FILE):
        print(f"\n❌ 错误：当前目录未找到 {os.path.basename(TEXT_FILE)}")
        print(f"   当前目录文件列表：{os.listdir(CURRENT_DIR)}")
        sys.exit(1)

    # 读取并拆分步骤文本
    with open(TEXT_FILE, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            # 匹配<!-- Step X -->注释
            step_match = re.match(r'<!-- Step (\d+) -->', line)
            if step_match:
                if current_step is not None and lines:
                    step_text[current_step] = lines.copy()
                current_step = int(step_match.group(1))
                lines = []
                continue
            # 收集当前步骤文本行
            if current_step is not None and 10 <= current_step <= 19:
                lines.append(line)
    # 保存最后一个步骤
    if current_step is not None and lines:
        step_text[current_step] = lines.copy()
    
    if not step_text:
        print("❌ 错误：未从教程文件中提取到Step10-Step19的内容")
        sys.exit(1)
    return step_text

def replace_image_p_content(template_html, step_num, step_lines):
    """仅替换6张图片的<p>内容，用计数器避免正则报错"""
    # 精准匹配image-caption下的<p>标签（适配连续无换行结构）
    p_regex = r'(<div class="image-caption">.*?<h4>.*?</h4>.*?)<p>.*?</p>(.*?</div>.*?</div>)'
    line_iter = iter(step_lines)
    img_counter = 1  # 图片序号计数器（1-6）

    def replace_single_p(match):
        nonlocal img_counter
        prefix = match.group(1)  # 保留<p>前所有内容（img/h4等）
        suffix = match.group(2)  # 保留<p>后所有内容
        try:
            # 取教程文本对应行，处理**加粗**
            text = next(line_iter)
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        except StopIteration:
            # 文本不足时用默认说明
            text = f'Description for step {step_num} image {img_counter}'
        img_counter += 1
        return f'{prefix}<p>{text}</p>{suffix}'

    # 强制替换6张图片的<p>（仅替换6次）
    replaced_html = re.sub(
        p_regex, replace_single_p, template_html,
        count=6, flags=re.DOTALL
    )
    # 替换步骤号（Step10→StepXX、substep_10→substep_XX、Figure10→FigureXX）
    replaced_html = re.sub(r'Step 10', f'Step {step_num}', replaced_html)
    replaced_html = re.sub(r'substep_10_', f'substep_{step_num}_', replaced_html)
    replaced_html = re.sub(r'Figure 10.', f'Figure {step_num}.', replaced_html)
    return replaced_html

def replace_target_files():
    """直接替换当前目录的step10-step19.html（覆盖已有文件）"""
    # 检查模板文件
    if not os.path.exists(TEMPLATE_FILE):
        print(f"\n❌ 错误：当前目录未找到 {os.path.basename(TEMPLATE_FILE)}")
        print(f"   当前目录文件列表：{os.listdir(CURRENT_DIR)}")
        sys.exit(1)
    
    # 读取模板完整内容（保留所有结构：alert、图片路径、样式等）
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template_html = f.read()
    
    # 解析教程文本
    step_text = parse_step_text()

    # 确认覆盖操作（避免误删）
    print("\n⚠️ 警告：即将直接替换当前目录下的 step10.html ~ step19.html")
    print("   已有文件会被覆盖，无法恢复！")
    confirm = input("\n确认执行替换？(输入 y 确认，其他取消)：")
    if confirm.lower() != 'y':
        print("✅ 已取消替换操作")
        sys.exit(0)

    # 逐步骤替换/创建文件（直接覆盖当前目录）
    replaced_count = 0
    for step_num in range(10, 20):
        target_file = os.path.join(CURRENT_DIR, f'step{step_num}.html')
        # 获取当前步骤文本行
        current_lines = step_text.get(step_num, [])
        # 替换图片<p>内容
        final_html = replace_image_p_content(template_html, step_num, current_lines)
        # 直接写入目标文件（覆盖已有内容）
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(final_html)
        replaced_count += 1
        print(f"✅ 已替换：{target_file}")

    print(f"\n🎉 替换完成！共处理 {replaced_count} 个文件（step10-step19.html）")
    print(f"📌 所有文件仅修改了图片的<p>文本，其他内容完全保留")

if __name__ == "__main__":
    print("="*70)
    print(f"📌 操作目录：{CURRENT_DIR}")
    print(f"📌 教程文件：{os.path.basename(TEXT_FILE)}")
    print(f"📌 模板文件：{os.path.basename(TEMPLATE_FILE)}")
    print("="*70)
    replace_target_files()