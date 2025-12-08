import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

# ========== 路径配置（和你的项目结构完全一致） ==========
# 项目根目录（脚本insert.py所在的位置）
PROJECT_ROOT = Path(__file__).parent  # 自动获取脚本所在目录
STEPS_DIR = PROJECT_ROOT / "steps"     # 根目录下的steps文件夹
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"  # 根目录下的assets/images
# ======================================================

TARGET_STEPS = list(range(10, 20))
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif')


def generate_image_block(img_path: str, step: int, index: int) -> str:
    return f'''<div class="image-item">
        <img src="{img_path}" alt="Step {step} - Image {index}" class="step-image" data-image="{index}">
        <div class="image-caption">
            <h4>Figure {step}.{index}: Image {index}</h4>
            <p>Description for step {step} image {index}</p>
        </div>
    </div>'''


def get_sorted_step_images(step: int) -> list:
    """获取当前步骤对应的图片（substep_xx_xx格式）"""
    image_files = []
    if not IMAGES_DIR.exists():
        return image_files
    
    for filename in os.listdir(IMAGES_DIR):
        # 严格匹配：substep_<步骤>_<序号>.<后缀>（比如substep_10_01.png）
        match = re.match(rf'substep_{step}_(\d+)\.\w+', filename, re.IGNORECASE)
        if match and filename.lower().endswith(IMAGE_EXTENSIONS):
            image_files.append(filename)
    
    # 按序号排序（01、02、03...）
    def sort_key(filename: str) -> int:
        return int(re.search(rf'substep_{step}_(\d+)', filename).group(1))
    
    return sorted(image_files, key=sort_key)


def update_single_step(step: int):
    """更新单个stepxx.html文件"""
    step_file = STEPS_DIR / f"step{step:02d}.html"
    if not step_file.exists():
        print(f"❌ 步骤{step}：文件不存在 {step_file}")
        return False

    # 读取HTML文件
    try:
        with open(step_file, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        print(f"❌ 步骤{step}：读取失败 - {str(e)}")
        return False

    # 解析并定位image-gallery区域
    soup = BeautifulSoup(html_content, "html.parser")
    gallery = soup.find("div", class_="image-gallery")
    if not gallery:
        print(f"⚠ 步骤{step}：未找到image-gallery区域")
        return False

    # 清空原有内容 + 插入新图片块
    gallery.clear()
    image_files = get_sorted_step_images(step)
    print(f"📸 步骤{step}：找到{len(image_files)}张图片")

    for idx, img_file in enumerate(image_files, 1):
        # 图片路径：相对于steps文件夹的路径（steps/step10.html → ../../assets/images/xxx）
        img_relative_path = os.path.relpath(IMAGES_DIR / img_file, STEPS_DIR).replace("\\", "/")
        gallery.append(BeautifulSoup(generate_image_block(img_relative_path, step, idx), "html.parser"))

    # 写入修改后的HTML
    try:
        with open(step_file, "w", encoding="utf-8") as f:
            f.write(str(soup))
        print(f"✅ 步骤{step}：更新完成\n")
        return True
    except Exception as e:
        print(f"❌ 步骤{step}：写入失败 - {str(e)}\n")
        return False


def main():
    print(f"===== 开始处理步骤 {TARGET_STEPS[0]}~{TARGET_STEPS[-1]} =====")
    success_count = 0

    for step in TARGET_STEPS:
        if update_single_step(step):
            success_count += 1

    print(f"===== 处理结束：成功更新{success_count}/{len(TARGET_STEPS)}个文件 =====")


if __name__ == "__main__":
    main()