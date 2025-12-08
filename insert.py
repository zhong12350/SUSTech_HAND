import os
import re
from bs4 import BeautifulSoup

# 路径配置
STEPS_DIR = "./steps"
IMAGES_DIR = "./assets/images"

# 处理步骤 10-19
target_steps = list(range(10, 20))

# 图片块模板
def generate_image_block(img_path, step, index):
    return f'''<div class="image-item">
        <img src="{img_path}" alt="Step {step} - Image {index}" class="step-image" data-image="{index}">
        <div class="image-caption">
            <h4>Figure {step}.{index}: Image {index}</h4>
            <p>Description for step {step} image {index}</p>
        </div>
    </div>'''

print(f"处理步骤: {target_steps[0]} ~ {target_steps[-1]}")
print("-" * 50)

for step in target_steps:
    step_file = f"{STEPS_DIR}/step{step:02d}.html"
    
    if not os.path.exists(step_file):
        print(f"❌ 文件不存在: {step_file}")
        continue

    print(f"处理: step{step:02d}.html")

    try:
        # 读取HTML
        with open(step_file, "r", encoding="utf-8") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")

        # 找到image-gallery区域
        gallery = soup.find("div", class_="image-gallery")
        if not gallery:
            print(f"⚠ 未找到image-gallery区域")
            continue

        # 清空gallery中的所有内容
        for child in list(gallery.children):
            child.decompose()

        # 查找该步骤的所有图片
        image_files = []
        if os.path.exists(IMAGES_DIR):
            for filename in os.listdir(IMAGES_DIR):
                # 匹配 substep_10_01.jpg 或 substep_10_01.png 等格式
                if filename.startswith(f"substep_{step}_") and filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    image_files.append(filename)
        
        # 按数字排序 (substep_10_01, substep_10_02, ...)
        image_files.sort(key=lambda x: int(re.search(r'substep_\d+_(\d+)', x).group(1)) if re.search(r'substep_\d+_(\d+)', x) else 0)
        
        print(f"  找到 {len(image_files)} 张图片: {image_files}")

        # 插入图片块
        for i, img_filename in enumerate(image_files, 1):
            # 使用正确的路径格式: ../assets/images/substep_10_01.jpg
            img_path = f"../assets/images/{img_filename}"
            block_html = generate_image_block(img_path, step, i)
            block_soup = BeautifulSoup(block_html, "html.parser")
            gallery.append(block_soup)

        # 写入文件 - 保持原格式，不使用prettify
        with open(step_file, "w", encoding="utf-8") as f:
            # 直接写入原始的HTML字符串，保持格式
            output = str(soup)
            f.write(output)
        
        print(f"  ✓ 更新完成")

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

print("\n✅ 所有步骤处理完成!")
print("\n检查生成的图片路径:")
for step in target_steps:
    step_file = f"{STEPS_DIR}/step{step:02d}.html"
    if os.path.exists(step_file):
        with open(step_file, "r", encoding="utf-8") as f:
            content = f.read()
            # 统计image-item数量
            count = content.count('class="image-item"')
            # 查找图片路径
            img_paths = re.findall(r'src="(\.\./assets/images/substep_\d+_\d+\.\w+)"', content)
            print(f"Step {step:02d}: {count} 张图片")
            if img_paths:
                print(f"  示例路径: {img_paths[0]}")