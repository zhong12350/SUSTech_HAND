import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# ========== 仅需修改这2处配置 ==========
TARGET_DIR = r"D\SUSTech_HAND"  # 示例：r"D:\SUSTech_HAND"（必须改）
CHROME_DRIVER_PATH = r"chromedriver.exe"  # 若驱动在同目录则不用改，否则填完整路径

# ========== 固定配置（无需动） ==========
START_STEP = 10
END_STEP = 19
BASE_URL = "https://www.orcahand.com/dashboard"
os.makedirs(TARGET_DIR, exist_ok=True)

def init_browser():
    """初始化浏览器（显示窗口，方便观察步骤切换）"""
    options = webdriver.ChromeOptions()
    # 注释掉无头模式，让你能看到浏览器操作过程
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1200, 800)  # 设置窗口大小，确保步骤标签可见
    driver.implicitly_wait(15)  # 延长隐式等待时间
    return driver

def switch_to_step(driver, step_num):
    """核心：切换到指定步骤（通过标签点击）"""
    try:
        # 尝试1：定位「Step X」文本标签（最常见）
        step_tab = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//*[contains(text(), 'Step {step_num}') or contains(text(), '步骤 {step_num}')]")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView();", step_tab)  # 滚动到标签可见
        step_tab.click()
        print(f"✅ 成功切换到步骤{step_num}")
        
        # 等待该步骤内容加载完成（验证是否激活）
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//div[contains(@class, 'step-panel') and contains(@data-step, '{step_num}') and contains(@class, 'active')]")
            )
        )
        return True
    except:
        try:
            # 尝试2：定位data-step属性标签（备选）
            step_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//*[@data-step='{step_num}']"))
            )
            step_tab.click()
            print(f"✅ 成功切换到步骤{step_num}")
            return True
        except Exception as e:
            print(f"❌ 切换步骤{step_num}失败：{str(e)}")
            return False

def fetch_descriptions(driver, step_num):
    """抓取当前步骤的所有图片描述"""
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    
    # 定位当前步骤的内容容器（精准过滤其他步骤）
    step_container = soup.find(
        "div", 
        attrs={"data-step": str(step_num), "class": lambda c: c and "active" in c.split()}
    )
    if not step_container:
        print(f"❌ 未找到步骤{step_num}的激活容器")
        return []
    
    # 定位所有「图片+描述」组合（通用结构）
    desc_groups = step_container.find_all(
        "div", 
        class_=lambda c: c and any(keyword in c.split() for keyword in ["step-item", "image-item", "img-group"])
    )
    if not desc_groups:
        # 备选：直接找图片的父容器
        desc_groups = step_container.find_all("div", class_=lambda c: c and "desc" not in c.split())
    
    descriptions = []
    for idx, group in enumerate(desc_groups, 1):
        # 找图片（验证是图片组）
        img = group.find("img", class_=lambda c: c and "step-img" in c.split() or True)
        if not img:
            continue
        
        # 找描述文本（多种可能标签）
        desc_tag = group.find(
            lambda tag: tag.name in ["div", "p", "span"] and any(
                kw in tag.get("class", []) for kw in ["step-desc", "description", "desc", "text"]
            )
        )
        if not desc_tag:
            # 备选：取图片后面的所有文本
            desc_text = ""
            for sibling in img.find_next_siblings():
                desc_text += sibling.get_text(strip=True) + "\n"
            desc_text = desc_text.strip()
        else:
            desc_text = desc_tag.get_text(strip=True)
        
        if desc_text:
            descriptions.append((idx, desc_text))
            print(f"  - 找到描述{idx}：{desc_text[:30]}...")  # 打印前30字预览
    
    return descriptions

def generate_html(step_num, descriptions):
    """生成结构化HTML文件"""
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>步骤{step_num} 操作说明</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2d3748; border-bottom: 3px solid #4299e1; padding-bottom: 10px; }}
        .desc-card {{ 
            margin: 20px 0; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
            background: #f8f9fa;
        }}
        .desc-title {{ 
            font-size: 18px; 
            font-weight: 600; 
            color: #4299e1; 
            margin-bottom: 10px; 
            border-left: 4px solid #4299e1; 
            padding-left: 10px;
        }}
        .desc-content {{ 
            font-size: 16px; 
            color: #4a5568; 
            line-height: 1.8; 
        }}
        .empty {{ 
            text-align: center; 
            color: #e53e3e; 
            font-size: 20px; 
            margin: 50px 0; 
            padding: 30px; 
            background: #fef7fb; 
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <h1>步骤 {step_num} 详细操作说明</h1>
"""
    if not descriptions:
        html += '<div class="empty">未抓取到有效描述（请检查步骤切换是否成功）</div>'
    else:
        for idx, text in descriptions:
            html += f"""
    <div class="desc-card">
        <div class="desc-title">step{step_num}_{str(idx).zfill(2)}</div>
        <div class="desc-content">{text}</div>
    </div>
"""
    html += """
</body>
</html>
"""
    filename = f"step{step_num}_instruction.html"
    filepath = os.path.join(TARGET_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"📁 已生成文件：{filepath}（共{len(descriptions)}条描述）\n")

if __name__ == "__main__":
    driver = init_browser()
    try:
        driver.get(BASE_URL)
        print(f"🌐 成功访问网站：{BASE_URL}")
        
        # 先测试步骤10（验证有效后再批量）
        test_step = 10
        print(f"\n===== 开始处理步骤{test_step} =====")
        if switch_to_step(driver, test_step):
            descs = fetch_descriptions(driver, test_step)
            generate_html(test_step, descs)
        
        # 批量处理10-19步（测试通过后取消注释）
        # for step in range(START_STEP, END_STEP + 1):
        #     print(f"\n===== 开始处理步骤{step} =====")
        #     if switch_to_step(driver, step):
        #         descs = fetch_descriptions(driver, step)
        #         generate_html(step, descs)
        
    except Exception as e:
        print(f"\n❌ 全局错误：{str(e)}")
    finally:
        driver.quit()
        print("\n🚀 程序结束！")