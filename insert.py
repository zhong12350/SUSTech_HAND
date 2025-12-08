import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

# ===================== 配置区 =====================
STEPS_DIR = Path("./steps")
IMAGES_DIR = Path("./assets/images")
TARGET_STEPS = list(range(10, 20))
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif')
# ================================================================

def generate_image_block(img_path: str, step: int, index: int) -> str:
    return f'''<div class="image-item">
        <img src="{img_path}" alt="Step {step} - Image {index}" class="step-image" data-image="{index}">
        <div class="image-caption">
            <h4>Figure {step}.{index}: Image {index}</h4>
            <p>Description for step {step} image {index}</p>
        </div>
    </div>'''

def get_sorted_step_images(step: int, img_dir: Path) -> list:
    """改回匹配substep_xx_xx格式（和你的图片命名一致）"""
    image_files = []
    if not img_dir.exists():
        return image_files
    
    for filename in os.listdir(img_dir):
        # 关键：匹配substep_<步骤>_<序号>（和你的图片命名一致）
        match = re.match(rf'substep_{step}_(\d+)\.\w+', filename, re.IGNORECASE)
        if match and filename.lower().endswith(IMAGE_EXTENSIONS):
            image_files.append(filename)
    
    # 按序号排序
    def sort_key(filename: str) -> int:
        match = re.search(rf'substep_{step}_(\d+)', filename)
        return int(match.group(1)) if match else 0
    
    return sorted(image_files, key=sort_key)

def update_step_html(step: int, steps_dir: Path, img_dir: Path) -> bool:
    step_file = steps_dir / f"step{step:02d}.html"
    if not step_file.exists():
        print(f"❌ 跳过：文件不存在 {step_file}")
        return False
    
    try:
        with open(step_file, "r", encoding="utf-8") as f:
            html = f.read()
    except UnicodeDecodeError:
        try:
            with open(step_file, "r", encoding="gbk") as f:
                html = f.read()
        except Exception as e:
            print(f"❌ 读取失败 {step_file}：{str(e)}")
            return False
    
    soup = BeautifulSoup(html, "html.parser")
    gallery = soup.find("div", class_="image-gallery")
    if not gallery:
        print(f"⚠ 跳过 {step_file}：未找到image-gallery")
        return False
    
    gallery.clear()
    image_files = get_sorted_step_images(step, img_dir)
    print(f"  📸 找到 {len(image_files)} 张图片：{image_files}")
    
    for idx, img_filename in enumerate(image_files, 1):
        img_path = os.path.join("..", img_dir.name, img_filename).replace("\\", "/")
        gallery.append(BeautifulSoup(generate_image_block(img_path, step, idx), "html.parser"))
    
    with open(step_file, "w", encoding="utf-8") as f:
        f.write(str(soup))
    print(f"  ✅ 更新完成 {step_file}")
    return True

def verify_update_results(steps_dir: Path, target_steps: list):
    print("\n" + "="*50 + "\n📋 验证结果\n" + "="*50)
    for step in target_steps:
        step_file = steps_dir / f"step{step:02d}.html"
        if not step_file.exists():
            print(f"Step {step:02d}：文件不存在")
            continue
        
        with open(step_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        count = content.count('class="image-item"')
        img_paths = re.findall(r'src="(\.\./assets/images/substep_\d+_\d+\.\w+)"', content)
        print(f"Step {step:02d}：{count} 张图片")
        if img_paths:
            print(f"  示例路径：{img_paths[0]}")

if __name__ == "__main__":
    print(f"🚀 处理步骤：{TARGET_STEPS[0]} ~ {TARGET_STEPS[-1]}")
    print("-" * 50)
    
    if not STEPS_DIR.exists():
        print(f"❌ 错误：步骤目录不存在 {STEPS_DIR}")
        exit(1)
    if not IMAGES_DIR.exists():
        print(f"⚠ 警告：图片目录不存在 {IMAGES_DIR}")
    
    success_count = 0
    for step in TARGET_STEPS:
        if update_step_html(step, STEPS_DIR, IMAGES_DIR):
            success_count += 1
    
    verify_update_results(STEPS_DIR, TARGET_STEPS)
    print(f"\n🎉 完成！成功更新 {success_count}/{len(TARGET_STEPS)} 个文件")