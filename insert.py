import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

# ========== 路径配置 ==========
PROJECT_ROOT = Path(__file__).parent
HTML_TARGET_DIR = PROJECT_ROOT
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
# ==============================

TARGET_STEPS = list(range(10, 20))
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif')
IMG_ADAPTIVE_STYLE = "max-width: 100%; height: auto; object-fit: contain;"

def get_sorted_step_images(step: int) -> list:
    """获取指定步骤的图片文件，按序号排序"""
    image_files = []
    if not IMAGES_DIR.exists():
        return image_files
    
    for filename in os.listdir(IMAGES_DIR):
        match = re.match(rf'substep_{step}_(\d+)\.\w+', filename, re.IGNORECASE)
        if match and filename.lower().endswith(IMAGE_EXTENSIONS):
            image_files.append(filename)
    
    def sort_key(filename: str) -> int:
        return int(re.search(rf'substep_{step}_(\d+)', filename).group(1))
    
    return sorted(image_files, key=sort_key)

def update_image_attrs(img_tag, img_relative_path: str, step: int, index: int):
    """仅更新图片属性，添加自适应样式，不碰其他内容"""
    img_tag['src'] = img_relative_path
    img_tag['alt'] = f"Step {step} - Image {index}"
    img_tag['data-image'] = str(index)
    img_tag['class'] = "step-image"
    if 'style' in img_tag.attrs:
        img_tag['style'] = f"{img_tag['style']}; {IMG_ADAPTIVE_STYLE}"
    else:
        img_tag['style'] = IMG_ADAPTIVE_STYLE

def update_single_step(step: int):
    """仅处理图片，完全保留<p>说明文本"""
    step_file = HTML_TARGET_DIR / f"step{step:02d}.html"
    if not step_file.exists():
        print(f"❌ 步骤{step}：文件不存在 {step_file}")
        return False

    try:
        with open(step_file, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        print(f"❌ 步骤{step}：读取失败 - {str(e)}")
        return False

    # 使用内置解析器，无需额外安装
    soup = BeautifulSoup(html_content, "html.parser")
    gallery = soup.find("div", class_="image-gallery")
    if not gallery:
        print(f"⚠ 步骤{step}：未找到image-gallery")
        return False

    image_files = get_sorted_step_images(step)
    actual_img_count = len(image_files)
    print(f"📸 步骤{step}：找到{actual_img_count}张图片")

    existing_items = gallery.find_all("div", class_="image-item")
    existing_count = len(existing_items)

    # 1. 更新现有图片（保留<p>文本）
    for idx in range(min(existing_count, actual_img_count)):
        item = existing_items[idx]
        img_file = image_files[idx]
        img_index = idx + 1
        
        img_absolute_path = IMAGES_DIR / img_file
        img_relative_path = os.path.relpath(img_absolute_path, HTML_TARGET_DIR).replace("\\", "/")
        
        img_tag = item.find("img")
        if img_tag:
            update_image_attrs(img_tag, img_relative_path, step, img_index)

    # 2. 删除多余图片框
    if existing_count > actual_img_count:
        for item in existing_items[actual_img_count:]:
            item.decompose()
        print(f"🗑️ 步骤{step}：删除{existing_count - actual_img_count}个多余图片框")

    # 3. 新增图片框（保留默认<p>文本，后续可被说明脚本覆盖）
    if existing_count < actual_img_count:
        for idx in range(existing_count, actual_img_count):
            img_file = image_files[idx]
            img_index = idx + 1
            img_absolute_path = IMAGES_DIR / img_file
            img_relative_path = os.path.relpath(img_absolute_path, HTML_TARGET_DIR).replace("\\", "/")
            
            new_item_html = f'''<div class="image-item">
                <img src="{img_relative_path}" alt="Step {step} - Image {img_index}" class="step-image" data-image="{img_index}" style="{IMG_ADAPTIVE_STYLE}">
                <div class="image-caption">
                    <h4>Figure {step}.{img_index}: Image {img_index}</h4>
                    <p>Description for step {step} image {img_index}</p>
                </div>
            </div>'''
            new_item = BeautifulSoup(new_item_html, "html.parser")
            gallery.append(new_item)
        print(f"➕ 步骤{step}：新增{actual_img_count - existing_count}个图片框")

    # 写入文件（保留所有<p>文本）
    try:
        with open(step_file, "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print(f"✅ 步骤{step}：图片更新完成（保留<p>文本）\n")
        return True
    except Exception as e:
        print(f"❌ 步骤{step}：写入失败 - {str(e)}\n")
        return False

def main():
    print(f"===== 开始处理步骤 {TARGET_STEPS[0]}~{TARGET_STEPS[-1]} =====")
    print("📌 仅处理图片（路径/数量/自适应），完全保留<p>说明文本")
    success_count = 0

    for step in TARGET_STEPS:
        if update_single_step(step):
            success_count += 1

    print(f"===== 处理结束：成功更新{success_count}/{len(TARGET_STEPS)}个文件 =====")

if __name__ == "__main__":
    main()