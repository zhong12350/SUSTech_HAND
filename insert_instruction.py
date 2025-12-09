import re
import os

# ===================== 强制固定配置（匹配你的目录和文件） =====================
# 当前脚本所在目录（无需修改）
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# 教程文本文件（必须在当前目录）
TEXT_FILE = os.path.join(BASE_DIR, "processed_instruction10-19.html")
# 模板文件（必须在当前目录，即包含alert+image-gallery的step00.html）
TEMPLATE_FILE = os.path.join(BASE_DIR, "step00.html")

def parse_step_text():
    """
    解析processed_instruction10-19.html，提取每个步骤的文本行
    返回：{10: [行1, 行2, ...], 11: [行1, 行2, ...], ..., 19: [...]}
    """
    step_text = {}
    current_step = None
    lines = []

    # 读取教程文件，按Step注释拆分
    with open(TEXT_FILE, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            # 匹配<!-- Step X -->注释（精准定位步骤）
            step_match = re.match(r'<!-- Step (\d+) -->', line)
            if step_match:
                # 保存上一个步骤的文本
                if current_step is not None and lines:
                    step_text[current_step] = lines.copy()
                # 初始化当前步骤
                current_step = int(step_match.group(1))
                lines = []
                continue
            # 收集当前步骤的文本行（保留所有重复/冗余，不做任何过滤）
            if current_step is not None and 10 <= current_step <= 19:
                lines.append(line)
    # 保存最后一个步骤
    if current_step is not None and lines:
        step_text[current_step] = lines.copy()
    
    return step_text

def replace_image_p_content(template_html, step_lines):
    """
    仅替换image-gallery中6个image-item的<p>文本，其他内容完全不动
    :param template_html: 完整的模板HTML（含alert、所有结构）
    :param step_lines: 当前步骤的文本行列表
    :return: 替换后的HTML
    """
    # 正则：精准匹配每个image-item里的<p>标签（适配你的连续无换行结构）
    # 分组说明：
    # group1: <p>之前的所有内容（img、h4等，完全保留）
    # group2: <p>之后的内容（</div></div>等，完全保留）
    p_regex = r'(<div class="image-caption">.*?<h4>.*?</h4>.*?)<p>.*?</p>(.*?</div>.*?</div>)'
    
    # 把文本行转为迭代器，按顺序替换6个image-item的<p>
    line_iter = iter(step_lines)
    
    def replace_single_p(match):
        """替换单个image-item的<p>内容"""
        prefix = match.group(1)  # 保留<p>前的所有内容（img/h4等）
        suffix = match.group(2)  # 保留<p>后的所有内容
        try:
            # 取当前行文本，处理**加粗**为<strong>（仅这一个格式处理）
            text = next(line_iter)
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        except StopIteration:
            # 文本行不足时，保留原有默认格式（仅改步骤号）
            img_num = re.search(r'Image (\d+)', match.group(1)).group(1)
            step_num = re.search(r'Step (\d+)', match.group(1)).group(1)
            text = f'Description for step {step_num} image {img_num}'
        # 仅替换<p>内的文本，其他全保留
        return f'{prefix}<p>{text}</p>{suffix}'
    
    # 全局替换6个image-item的<p>（最多6次，匹配你的6张图片）
    replaced_html = re.sub(
        p_regex,
        replace_single_p,
        template_html,
        count=6,  # 只替换6个（对应6张图片）
        flags=re.DOTALL  # 允许跨换行匹配（适配你的连续结构）
    )
    
    return replaced_html

def generate_step_files():
    """生成step10-step19.html，仅改图片<p>内容，其他全不动"""
    # 1. 检查文件是否存在
    if not os.path.exists(TEXT_FILE):
        print(f"❌ 找不到教程文件：{TEXT_FILE}")
        return
    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ 找不到模板文件：{TEMPLATE_FILE}")
        return
    
    # 2. 读取模板完整内容（保留所有alert、结构、空格、换行）
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template_html = f.read()
    
    # 3. 解析教程文本
    step_text = parse_step_text()
    if not step_text:
        print("❌ 未解析到任何步骤文本！")
        return
    
    # 4. 逐步骤生成文件（step10-step19.html）
    for step_num in range(10, 20):
        # 获取当前步骤的文本行（无内容则用默认）
        current_lines = step_text.get(step_num, [])
        # 替换当前步骤的图片<p>内容（其他全不动）
        final_html = replace_image_p_content(template_html, current_lines)
        # 替换模板中Step 10为当前步骤号（如Step 11）
        final_html = re.sub(r'Step 10', f'Step {step_num}', final_html)
        final_html = re.sub(r'substep_10_', f'substep_{step_num}_', final_html)
        final_html = re.sub(r'Figure 10.', f'Figure {step_num}.', final_html)
        
        # 保存到当前目录
        output_file = os.path.join(BASE_DIR, f'step{step_num}.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"✅ 已生成：{output_file}（仅修改图片<p>内容，其他全保留）")

if __name__ == "__main__":
    print("="*70)
    print("📌 开始生成文件，仅修改图片<p>文本，其他内容完全不动")
    print(f"📌 模板文件：{TEMPLATE_FILE}")
    print(f"📌 教程文件：{TEXT_FILE}")
    print("="*70)
    generate_step_files()
    print("\n🎉 所有文件生成完成！")
    print("✅ 仅修改了image-item下的<p>文本，以下内容完全未动：")
    print("   - Warning Alert区块")
    print("   - 图片的src/alt/class属性")
    print("   - <h4>标题结构（仅替换步骤号）")
    print("   - 所有HTML标签/样式/注释")