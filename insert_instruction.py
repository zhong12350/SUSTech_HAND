import re
import os
import sys

# ===================== 核心配置（无需修改） =====================
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
TEXT_FILE = os.path.join(CURRENT_DIR, "processed_instruction10-19.html")
TEMPLATE_FILE = os.path.join(CURRENT_DIR, "step00.html")

def parse_step_text():
    """解析教程文本，提取Step10-Step19的文本行（保留所有冗余）"""
    step_text = {}
    current_step = None
    lines = []

    if not os.path.exists(TEXT_FILE):
        print(f"\n❌ 错误：未找到 {os.path.basename(TEXT_FILE)}")
        print(f"   当前目录文件：{os.listdir(CURRENT_DIR)}")
        sys.exit(1)

    with open(TEXT_FILE, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            step_match = re.match(r'<!-- Step (\d+) -->', line)
            if step_match:
                if current_step is not None and lines:
                    step_text[current_step] = lines.copy()
                current_step = int(step_match.group(1))
                lines = []
                continue
            if current_step is not None and 10 <= current_step <= 19:
                lines.append(line)
    if current_step is not None and lines:
        step_text[current_step] = lines.copy()
    
    if not step_text:
        print("❌ 错误：未提取到Step10-Step19内容")
        sys.exit(1)
    return step_text

def replace_only_p_content(template_html, step_num, step_lines):
    """仅替换<p>文本，不碰任何图片相关内容（src/alt/数量）"""
    # 仅匹配<p>标签，不修改其他内容
    p_regex = r'(<div class="image-caption">.*?<h4>.*?</h4>.*?)<p>.*?</p>(.*?</div>.*?</div>)'
    line_iter = iter(step_lines)
    img_counter = 1

    def replace_single_p(match):
        nonlocal img_counter
        prefix = match.group(1)
        suffix = match.group(2)
        try:
            text = next(line_iter)
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        except StopIteration:
            text = f'Description for step {step_num} image {img_counter}'
        img_counter += 1
        return f'{prefix}<p>{text}</p>{suffix}'

    # 只替换<p>文本，不修改步骤号/图片路径
    replaced_html = re.sub(
        p_regex, replace_single_p, template_html,
        count=6, flags=re.DOTALL
    )
    return replaced_html

def replace_target_files():
    """仅替换<p>文本，直接覆盖当前目录step10-step19.html"""
    if not os.path.exists(TEMPLATE_FILE):
        print(f"\n❌ 错误：未找到 {os.path.basename(TEMPLATE_FILE)}")
        print(f"   当前目录文件：{os.listdir(CURRENT_DIR)}")
        sys.exit(1)
    
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template_html = f.read()
    
    step_text = parse_step_text()

    print("\n⚠️ 警告：仅替换<p>说明文本，覆盖step10-step19.html")
    confirm = input("确认执行？(y/n)：")
    if confirm.lower() != 'y':
        print("✅ 已取消")
        sys.exit(0)

    replaced_count = 0
    for step_num in range(10, 20):
        target_file = os.path.join(CURRENT_DIR, f'step{step_num}.html')
        current_lines = step_text.get(step_num, [])
        final_html = replace_only_p_content(template_html, step_num, current_lines)
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(final_html)
        replaced_count += 1
        print(f"✅ 已替换<p>文本：{target_file}")

    print(f"\n🎉 完成！共处理 {replaced_count} 个文件，仅修改<p>文本")

if __name__ == "__main__":
    print("="*70)
    print(f"📌 操作目录：{CURRENT_DIR}")
    print("📌 仅修改图片<p>说明文本，不碰任何图片内容")
    print("="*70)
    replace_target_files()