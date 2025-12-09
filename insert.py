import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

# ========== 核心路径配置（无需修改） ==========
PROJECT_ROOT = Path(__file__).parent  # 脚本所在目录 = HTML文件所在目录
HTML_TARGET_DIR = PROJECT_ROOT        # HTML文件根目录
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"  # 图片存储目录
# =============================================

# 处理步骤范围（10-19）
TARGET_STEPS = list(range(10, 20))
# 支持的图片格式
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif')
# 强制图片自适应样式（!important确保优先级最高，放大后必生效）
IMG_ADAPTIVE_STYLE = "max-width: 100% !important; height: auto !important; object-fit: contain !important; display: block !important; margin: 0 auto !important;"


def get_sorted_step_images(step: int) -> list:
    """获取指定步骤的图片文件，按序号升序排序（substep_10_01.png → substep_10_02.png）"""
    image_files = []
    if not IMAGES_DIR.exists():
        print(f"⚠ 图片目录不存在：{IMAGES_DIR}")
        return image_files
    
    # 匹配step对应的图片文件（substep_XX_YY格式）
    for filename in os.listdir(IMAGES_DIR):
        match = re.match(rf'substep_{step}_(\d+)\.\w+', filename, re.IGNORECASE)
        if match and filename.lower().endswith(IMAGE_EXTENSIONS):
            image_files.append(filename)
    
    # 按图片序号排序（确保1、2、3...顺序）
    def sort_key(filename: str) -> int:
        return int(re.search(rf'substep_{step}_(\d+)', filename).group(1))
    
    return sorted(image_files, key=sort_key)


def force_adaptive_style(img_tag):
    """强制给图片添加自适应样式，覆盖所有冲突样式"""
    # 直接替换style属性（确保自适应样式100%生效）
    img_tag['style'] = IMG_ADAPTIVE_STYLE
    # 追加专属class，双重保障（可配合全局CSS）
    img_tag_classes = img_tag.get('class', [])
    if isinstance(img_tag_classes, str):
        img_tag_classes = img_tag_classes.split()
    img_tag_classes.append('adaptive-step-image')
    img_tag['class'] = ' '.join(list(set(img_tag_classes)))  # 去重


def update_image_attributes(img_tag, img_relative_path: str, step: int, index: int):
    """仅更新图片核心属性+强制自适应样式，不修改其他内容"""
    # 更新图片路径（关键：确保路径正确）
    img_tag['src'] = img_relative_path
    # 更新辅助属性
    img_tag['alt'] = f"Step {step} - Image {index}"
    img_tag['data-image'] = str(index)
    # 强制添加自适应样式（解决放大后失效问题）
    force_adaptive_style(img_tag)


def update_single_step(step: int) -> bool:
    """
    处理单个步骤的图片：
    1. 仅更新图片路径/样式，保留所有<p>说明文本
    2. 删多余图片框，新增不足的图片框
    3. 不修改任何非图片相关内容（alert/样式/注释等）
    """
    # 目标HTML文件路径（step10.html → step19.html）
    step_file = HTML_TARGET_DIR / f"step{step:02d}.html"
    if not step_file.exists():
        print(f"❌ 步骤{step}：文件不存在 → {step_file}")
        return False

    # 读取HTML文件（保留所有原有内容）
    try:
        with open(step_file, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        print(f"❌ 步骤{step}：读取文件失败 → {str(e)}")
        return False

    # 解析HTML（使用内置html.parser，无需额外安装依赖）
    soup = BeautifulSoup(html_content, "html.parser")
    # 定位图片画廊区域（仅处理该区域内的图片）
    gallery = soup.find("div", class_="image-gallery")
    if not gallery:
        print(f"⚠ 步骤{step}：未找到image-gallery区域，跳过")
        return False

    # 获取当前步骤的图片列表（按序号排序）
    step_images = get_sorted_step_images(step)
    actual_img_count = len(step_images)
    print(f"📸 步骤{step}：检测到 {actual_img_count} 张图片")

    # 获取现有图片框列表
    existing_items = gallery.find_all("div", class_="image-item")
    existing_count = len(existing_items)

    # ========== 核心逻辑1：更新现有图片框的图片（保留<p>文本） ==========
    for idx in range(min(existing_count, actual_img_count)):
        # 现有图片框
        img_item = existing_items[idx]
        # 当前图片文件
        img_file = step_images[idx]
        img_index = idx + 1  # 图片序号从1开始

        # 计算图片相对路径（适配Windows/Linux路径分隔符）
        img_absolute_path = IMAGES_DIR / img_file
        img_relative_path = os.path.relpath(img_absolute_path, HTML_TARGET_DIR).replace("\\", "/")

        # 找到图片标签，更新属性+样式
        img_tag = img_item.find("img")
        if img_tag:
            update_image_attributes(img_tag, img_relative_path, step, img_index)

    # ========== 核心逻辑2：删除多余的图片框（现有 > 实际图片数） ==========
    if existing_count > actual_img_count:
        del_count = existing_count - actual_img_count
        # 删除超出数量的图片框
        for img_item in existing_items[actual_img_count:]:
            img_item.decompose()
        print(f"🗑️ 步骤{step}：删除 {del_count} 个多余图片框")

    # ========== 核心逻辑3：新增不足的图片框（现有 < 实际图片数） ==========
    if existing_count < actual_img_count:
        add_count = actual_img_count - existing_count
        # 新增图片框（保留默认<p>文本，后续可被说明脚本覆盖）
        for idx in range(existing_count, actual_img_count):
            img_file = step_images[idx]
            img_index = idx + 1

            # 计算图片相对路径
            img_absolute_path = IMAGES_DIR / img_file
            img_relative_path = os.path.relpath(img_absolute_path, HTML_TARGET_DIR).replace("\\", "/")

            # 生成新图片框（结构与原有一致）
            new_item_html = f'''<div class="image-item">
                <img src="{img_relative_path}" alt="Step {step} - Image {img_index}" class="step-image adaptive-step-image" data-image="{img_index}" style="{IMG_ADAPTIVE_STYLE}">
                <div class="image-caption">
                    <h4>Figure {step}.{img_index}: Image {img_index}</h4>
                    <p>Description for step {step} image {img_index}</p>
                </div>
            </div>'''
            # 解析并添加到画廊
            new_item = BeautifulSoup(new_item_html, "html.parser")
            gallery.append(new_item)

        print(f"➕ 步骤{step}：新增 {add_count} 个图片框")

    # ========== 写入文件（仅修改图片部分，保留所有原有内容） ==========
    try:
        with open(step_file, "w", encoding="utf-8") as f:
            # 保留HTML结构和缩进，避免格式混乱
            f.write(soup.prettify())
        print(f"✅ 步骤{step}：图片更新完成（保留所有<p>说明文本）\n")
        return True
    except Exception as e:
        print(f"❌ 步骤{step}：写入文件失败 → {str(e)}\n")
        return False


def main():
    """主函数：批量处理10-19步骤的图片"""
    print("="*80)
    print(f"📌 开始处理图片（仅修改图片路径/样式，保留所有说明文本）")
    print(f"📌 操作目录：{PROJECT_ROOT}")
    print(f"📌 图片目录：{IMAGES_DIR}")
    print("="*80)

    # 统计成功/失败数量
    success_count = 0
    fail_count = 0

    # 批量处理10-19步骤
    for step in TARGET_STEPS:
        if update_single_step(step):
            success_count += 1
        else:
            fail_count += 1

    # 输出最终统计
    print("="*80)
    print(f"🎉 处理完成！")
    print(f"✅ 成功更新：{success_count} 个文件")
    print(f"❌ 处理失败：{fail_count} 个文件")
    print("📌 说明：仅修改图片相关内容，<p>说明文本/HTML结构均未改动")
    print("="*80)


if __name__ == "__main__":
    main()