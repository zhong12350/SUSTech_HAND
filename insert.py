import os
import re
from bs4 import BeautifulSoup

# 路径配置（根据你的文件结构修改）
STEPS_DIR = r"./steps"
IMAGES_DIR = r"./assets/images"

# step10.html ~ step19.html
target_steps = list(range(10, 20))

# 模板 - 每个图片块的结构
def generate_image_block(img_path, step, index):
    return f'''
    <div class="image-item">
        <img src="{img_path}" alt="Step {step} - Image {index}" class="step-image" data-image="{index}">
        <div class="image-caption">
            <h4>Figure {step}.{index}: Description</h4>
            <p>Auto-generated image description placeholder.</p>
        </div>
    </div>
    '''

# -------------------------------------------------------------------

for step in target_steps:
    step_file = os.path.join(STEPS_DIR, f"step{step:02d}.html")

    if not os.path.exists(step_file):
        print(f"❌ 文件缺失：{step_file}")
        continue

    print(f"正在处理：{step_file}")

    # 读取 HTML
    with open(step_file, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # 找到 image-gallery div
    gallery = soup.find("div", class_="image-gallery")
    if gallery is None:
        print(f"⚠ 未找到 gallery 区域：{step_file}")
        continue

    # 清空原有占位块
    gallery.clear()

    # 找到本步骤的图片（例如 substep_10_xx.png）
    image_files = []
    for fname in sorted(os.listdir(IMAGES_DIR)):
        if re.match(rf"substep_{step}_\d+.*\.png$", fname):
            image_files.append(fname)

    print(f"  - 找到 {len(image_files)} 张图片")

    # 插入图片块
    for i, img in enumerate(image_files, start=1):
        img_path = f"../assets/images/{img}"
        block_html = generate_image_block(img_path, step, i)
        block = BeautifulSoup(block_html, "html.parser")
        gallery.append(block)

    # 不足 6 张 → 按实际张数即可
    # 超过 6 张 → 上面已自动扩展，无需处理

    # 写回文件
    with open(step_file, "w", encoding="utf-8") as f:
        f.write(str(soup.prettify()))

    print(f"  ✔ 写入完成：step{step:02d}.html")

print("\n🎉 所有页面处理完成！")
