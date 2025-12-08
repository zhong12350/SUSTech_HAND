import os
import re
from pathlib import Path

# 项目根目录（脚本所在位置）
PROJECT_ROOT = Path(__file__).parent
# 目标HTML文件：根目录下的step00.html~step29.html
HTML_FILES = [PROJECT_ROOT / f"step{i:02d}.html" for i in range(30)]

# 要替换的旧CSS（图片自适应相关）
OLD_CSS_PATTERNS = [
    # 匹配旧的.image-item样式
    re.compile(r'\.image-item\s*\{[^}]*\}', re.DOTALL),
    # 匹配旧的.step-image样式
    re.compile(r'\.step-image\s*\{[^}]*\}', re.DOTALL),
    # 匹配旧的.image-caption样式
    re.compile(r'\.image-caption\s*\{[^}]*\}', re.DOTALL)
]

# 新的自适应样式（只修改这部分）
NEW_CSS = """
.image-item {
    background-color: white;
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: var(--box-shadow);
    transition: var(--transition);
    display: flex;
    flex-direction: column;
    height: 100%;
}

.step-image {
    width: 100%;
    height: 100%;
    max-height: 300px;
    object-fit: contain;
    cursor: pointer;
    transition: transform 0.3s ease;
    background-color: #f8f9fa;
}

.image-caption {
    padding: 15px 20px;
    background-color: #f8f9fa;
    border-top: 1px solid #eee;
    flex-shrink: 0;
}
"""


def update_html_file(file_path):
    """修改单个HTML文件的图片自适应样式"""
    if not file_path.exists():
        print(f"❌ 跳过：文件不存在 {file_path.name}")
        return False

    try:
        # 读取HTML内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取失败 {file_path.name}：{str(e)}")
        return False

    # 替换旧CSS为新样式
    # 先删除所有旧样式，再插入新样式
    for pattern in OLD_CSS_PATTERNS:
        content = pattern.sub("", content)
    
    # 将新样式插入到<style>标签内（放在原有CSS之后）
    content = re.sub(
        r'(<style>.*?)(</style>)',
        lambda m: f"{m.group(1)}\n{NEW_CSS}\n{m.group(2)}",
        content,
        flags=re.DOTALL
    )

    # 写入修改后的内容
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 已更新 {file_path.name}")
        return True
    except Exception as e:
        print(f"❌ 写入失败 {file_path.name}：{str(e)}")
        return False


def main():
    print("===== 开始批量修改图片自适应样式 =====")
    success_count = 0

    for html_file in HTML_FILES:
        if update_html_file(html_file):
            success_count += 1

    print(f"\n===== 处理完成：成功更新 {success_count}/{len(HTML_FILES)} 个文件 =====")


if __name__ == "__main__":
    main()