import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

# ========== 路径配置（完全匹配你的当前结构） ==========
PROJECT_ROOT = Path(__file__).parent  # 项目根目录（脚本所在位置）
HTML_TARGET_DIR = PROJECT_ROOT        # HTML文件在根目录
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"  # 图片目录
# ======================================================

TARGET_STEPS = list(range(10, 20))
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif')
# 图片自适应样式（确保放大后适配屏幕）
IMG_ADAPTIVE_STYLE = "max-width: 100%; height: auto; object-fit: contain;"


def get_sorted_step_images(step: int) -> list:
    """获取指定步骤的图片文件，按序号排序"""
    image_files = []
    if not IMAGES_DIR.exists():
        return image_files
    
    for filename in os.listdir(IMAGES_DIR):
        # 匹配substep_XX_YY格式的图片（XX=步骤号，YY=图片序号）
        match = re.match(rf'substep_{step}_(\d+)\.\w+', filename, re.IGNORECASE)
        if match and filename.lower().endswith(IMAGE_EXTENSIONS):
            image_files.append(filename)
    
    # 按图片序号排序
    def sort_key(filename: str) -> int:
        return int(re.search(rf'substep_{step}_(\d+)', filename).group(1))
    
    return sorted(image_files, key=sort_key)


def update_image_item(img_tag, img_relative_path: str, step: int, index: int):
    """仅更新图片标签的属性（保留其他所有内容），添加自适应样式"""
    # 更新核心属性（路径、alt、data-image）
    img_tag['src'] = img_relative_path
    img_tag['alt'] = f"Step {step} - Image {index}"
    img_tag['data-image'] = str(index)
    img_tag['class'] = "step-image"  # 保留原有class
    # 添加自适应样式（确保放大后适配屏幕）
    if 'style' in img_tag.attrs:
        # 保留原有样式，追加自适应样式
        img_tag['style'] = f"{img_tag['style']}; {IMG_ADAPTIVE_STYLE}"
    else:
        img_tag['style'] = IMG_ADAPTIVE_STYLE


def update_single_step(step: int):
    """仅更新图片路径和数量，保留所有原有HTML内容（包括<p>说明、h4等）"""
    step_file = HTML_TARGET_DIR / f"step{step:02d}.html"
    if not step_file.exists():
        print(f"❌ 步骤{step}：文件不存在 {step_file}")
        return False

    # 读取HTML（保留所有原有内容）
    try:
        with open(step_file, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        print(f"❌ 步骤{step}：读取失败 - {str(e)}")
        return False

    # 解析HTML（用html5lib避免标签解析异常）
    soup = BeautifulSoup(html_content, "html5lib")
    gallery = soup.find("div", class_="image-gallery")
    if not gallery:
        print(f"⚠ 步骤{step}：未找到image-gallery区域")
        return False

    # 获取实际图片列表
    image_files = get_sorted_step_images(step)
    actual_img_count = len(image_files)
    print(f"📸 步骤{step}：找到{actual_img_count}张图片")

    # 获取现有image-item列表
    existing_items = gallery.find_all("div", class_="image-item")
    existing_count = len(existing_items)

    # ========== 核心逻辑1：处理现有image-item（仅更新图片属性，保留其他内容） ==========
    for idx in range(min(existing_count, actual_img_count)):
        item = existing_items[idx]
        img_file = image_files[idx]
        img_index = idx + 1  # 图片序号从1开始
        
        # 计算图片相对路径（确保路径正确）
        img_absolute_path = IMAGES_DIR / img_file
        img_relative_path = os.path.relpath(img_absolute_path, HTML_TARGET_DIR).replace("\\", "/")
        
        # 找到item内的img标签，仅更新属性
        img_tag = item.find("img")
        if img_tag:
            update_image_item(img_tag, img_relative_path, step, img_index)
        
        # 可选：更新h4标题的序号（保留标题其他内容）
        h4_tag = item.find("h4")
        if h4_tag:
            # 替换序号，保留标题文本结构（比如Figure 10.1 → Figure 10.2）
            h4_tag.string = re.sub(
                rf'Figure {step}\.\d+', 
                f'Figure {step}.{img_index}', 
                h4_tag.get_text()
            )

    # ========== 核心逻辑2：删除多余的image-item（现有数量 > 实际图片数） ==========
    if existing_count > actual_img_count:
        for item in existing_items[actual_img_count:]:
            item.decompose()  # 删除多余的图片框
        print(f"🗑️ 步骤{step}：删除{existing_count - actual_img_count}个多余图片框")

    # ========== 核心逻辑3：新增不足的image-item（现有数量 < 实际图片数） ==========
    if existing_count < actual_img_count:
        for idx in range(existing_count, actual_img_count):
            img_file = image_files[idx]
            img_index = idx + 1
            # 计算图片相对路径
            img_absolute_path = IMAGES_DIR / img_file
            img_relative_path = os.path.relpath(img_absolute_path, HTML_TARGET_DIR).replace("\\", "/")
            
            # 生成新的image-item（保留和原有一致的结构）
            new_item_html = f'''<div class="image-item">
                <img src="{img_relative_path}" alt="Step {step} - Image {img_index}" class="step-image" data-image="{img_index}" style="{IMG_ADAPTIVE_STYLE}">
                <div class="image-caption">
                    <h4>Figure {step}.{img_index}: Image {img_index}</h4>
                    <p>Description for step {step} image {img_index}</p>
                </div>
            </div>'''
            new_item = BeautifulSoup(new_item_html, "html5lib")
            gallery.append(new_item)
        print(f"➕ 步骤{step}：新增{actual_img_count - existing_count}个图片框")

    # ========== 写入文件（仅修改图片相关内容，其他完全保留） ==========
    try:
        with open(step_file, "w", encoding="utf-8") as f:
            # 格式化输出，保留原有缩进
            f.write(soup.prettify())
        print(f"✅ 步骤{step}：更新完成（仅修改图片路径/数量，保留所有原有内容）\n")
        return True
    except Exception as e:
        print(f"❌ 步骤{step}：写入失败 - {str(e)}\n")
        return False


def main():
    print(f"===== 开始处理步骤 {TARGET_STEPS[0]}~{TARGET_STEPS[-1]} =====")
    print(f"📌 仅修改图片路径/数量，保留所有原有HTML内容")
    print(f"📌 图片添加自适应样式：{IMG_ADAPTIVE_STYLE}\n")
    success_count = 0

    for step in TARGET_STEPS:
        if update_single_step(step):
            success_count += 1

    print(f"===== 处理结束：成功更新{success_count}/{len(TARGET_STEPS)}个文件 =====")


if __name__ == "__main__":
    main()