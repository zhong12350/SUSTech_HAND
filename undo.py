import os
import shutil
import time
import datetime
from collections import defaultdict

# ===================== 核心配置 =====================
# 备份目录（隐藏目录，避免干扰）
BACKUP_DIR = ".file_backup"
# 脚本自身文件名（排除备份/检测）
SCRIPT_NAME = os.path.basename(__file__)
# 批量修改时间阈值（秒）：同一批次修改的文件时间差不超过此值
BATCH_THRESHOLD = 300  # 5分钟，可根据需要调整
# 排除的文件/目录（无需检测/备份）
EXCLUDE_LIST = [BACKUP_DIR, SCRIPT_NAME, "output_steps"]

# ===================== 工具函数 =====================
def get_file_mtime(file_path):
    """获取文件最后修改时间（时间戳+格式化字符串）"""
    try:
        mtime = os.path.getmtime(file_path)
        mtime_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        return mtime, mtime_str
    except Exception as e:
        print(f"⚠️ 获取{file_path}修改时间失败：{e}")
        return None, None

def init_backup_dir():
    """初始化备份目录"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"✅ 创建备份目录：{os.path.abspath(BACKUP_DIR)}")
    # 为备份目录添加时间戳子目录（区分不同批次备份）
    backup_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_backup_dir = os.path.join(BACKUP_DIR, backup_timestamp)
    os.makedirs(batch_backup_dir)
    return batch_backup_dir

def backup_files(file_list, backup_dir):
    """备份指定文件到备份目录（保留目录结构）"""
    backup_log = []
    for file_path in file_list:
        try:
            # 构建备份路径（保留相对路径）
            rel_path = os.path.relpath(file_path)
            backup_file_path = os.path.join(backup_dir, rel_path)
            # 创建备份目录（如果有子目录）
            os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
            # 备份文件（保留元数据）
            shutil.copy2(file_path, backup_file_path)
            backup_log.append({
                "original": file_path,
                "backup": backup_file_path,
                "mtime": get_file_mtime(file_path)[0]
            })
            print(f"📁 已备份：{file_path} → {backup_file_path}")
        except Exception as e:
            print(f"⚠️ 备份{file_path}失败：{e}")
    # 保存备份日志（用于撤销）
    log_path = os.path.join(backup_dir, "backup_log.txt")
    with open(log_path, 'w', encoding='utf-8') as f:
        for item in backup_log:
            f.write(f"{item['original']}|{item['backup']}|{item['mtime']}\n")
    return backup_log, log_path

def scan_current_files():
    """扫描当前目录所有文件（排除指定项）"""
    file_list = []
    for root, dirs, files in os.walk("."):
        # 排除不需要的目录
        dirs[:] = [d for d in dirs if d not in EXCLUDE_LIST]
        for file in files:
            file_path = os.path.join(root, file)
            # 排除不需要的文件
            if os.path.basename(file_path) in EXCLUDE_LIST:
                continue
            # 排除隐藏文件（可选）
            if file.startswith(".") and file != ".file_backup":
                continue
            file_list.append(file_path)
    return file_list

def detect_recent_batch_changes(file_list):
    """检测最近一次批量修改的文件（按修改时间聚类）"""
    # 1. 收集所有文件的修改时间
    file_mtime_dict = {}
    for file_path in file_list:
        mtime, _ = get_file_mtime(file_path)
        if mtime:
            file_mtime_dict[file_path] = mtime

    if not file_mtime_dict:
        print("❌ 未检测到任何可分析的文件")
        return []

    # 2. 按修改时间排序，取最近的时间作为基准
    sorted_files = sorted(file_mtime_dict.items(), key=lambda x: x[1], reverse=True)
    latest_mtime = sorted_files[0][1]
    latest_time_str = datetime.datetime.fromtimestamp(latest_mtime).strftime("%Y-%m-%d %H:%M:%S")

    # 3. 找出同一批次（时间差≤BATCH_THRESHOLD）的文件
    batch_files = []
    for file_path, mtime in sorted_files:
        if abs(mtime - latest_mtime) <= BATCH_THRESHOLD:
            batch_files.append(file_path)
        else:
            # 时间差超过阈值，停止（因为已按时间排序）
            break

    # 4. 输出检测结果
    print(f"\n📊 检测到最近一次批量修改（基准时间：{latest_time_str}）：")
    print(f"   共 {len(batch_files)} 个文件被修改：")
    for idx, file in enumerate(batch_files, 1):
        _, mtime_str = get_file_mtime(file)
        print(f"   {idx}. {file} (修改时间：{mtime_str})")

    return batch_files

def load_backup_log(log_path):
    """加载备份日志，返回文件映射"""
    backup_map = {}
    if not os.path.exists(log_path):
        print(f"❌ 备份日志不存在：{log_path}")
        return backup_map
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            original, backup, mtime = line.split("|")
            backup_map[original] = {
                "backup_path": backup,
                "mtime": float(mtime) if mtime else None
            }
    return backup_map

def undo_recent_changes():
    """撤销最近一次批量修改（恢复备份）"""
    # 1. 检查备份目录
    if not os.path.exists(BACKUP_DIR):
        print("❌ 无备份目录，无法撤销！")
        return False

    # 2. 获取最新的备份批次（按时间戳排序）
    backup_batches = [d for d in os.listdir(BACKUP_DIR) if os.path.isdir(os.path.join(BACKUP_DIR, d))]
    if not backup_batches:
        print("❌ 无备份批次，无法撤销！")
        return False

    # 按时间戳降序排序，取最新的批次
    backup_batches.sort(reverse=True)
    latest_batch = backup_batches[0]
    latest_batch_dir = os.path.join(BACKUP_DIR, latest_batch)
    log_path = os.path.join(latest_batch_dir, "backup_log.txt")

    # 3. 加载备份日志
    backup_map = load_backup_log(log_path)
    if not backup_map:
        print("❌ 备份日志为空，无法撤销！")
        return False

    # 4. 确认撤销操作
    print(f"\n⚠️ 即将撤销最近一次批量修改（备份批次：{latest_batch}）")
    print(f"   共将恢复 {len(backup_map)} 个文件到修改前状态！")
    confirm = input("   确认撤销？(y/n)：")
    if confirm.lower() != "y":
        print("✅ 已取消撤销操作")
        return True

    # 5. 恢复文件
    success_count = 0
    fail_count = 0
    for original_path, backup_info in backup_map.items():
        backup_path = backup_info["backup_path"]
        try:
            # 恢复文件（覆盖当前文件）
            shutil.copy2(backup_path, original_path)
            print(f"✅ 已恢复：{original_path}")
            success_count += 1
        except Exception as e:
            print(f"❌ 恢复{original_path}失败：{e}")
            fail_count += 1

    # 6. 输出撤销结果
    print(f"\n📊 撤销完成！")
    print(f"   成功恢复：{success_count} 个文件")
    print(f"   恢复失败：{fail_count} 个文件")
    return success_count > 0

# ===================== 主逻辑 =====================
if __name__ == "__main__":
    print("="*60)
    print("📌 文件变化检测与撤销工具")
    print(f"   当前目录：{os.path.abspath('.')}")
    print(f"   批量修改时间阈值：{BATCH_THRESHOLD}秒（{BATCH_THRESHOLD/60}分钟）")
    print("="*60)

    # 1. 扫描当前文件
    print("\n🔍 正在扫描当前目录文件...")
    current_files = scan_current_files()
    print(f"✅ 扫描完成，共检测到 {len(current_files)} 个文件（排除{EXCLUDE_LIST}）")

    # 2. 备份当前文件状态（撤销的基础）
    print("\n📁 正在备份当前文件状态（用于撤销）...")
    batch_backup_dir = init_backup_dir()
    backup_log, log_path = backup_files(current_files, batch_backup_dir)
    print(f"✅ 备份完成，备份日志：{log_path}")

    # 3. 检测最近一次批量修改
    batch_files = detect_recent_batch_changes(current_files)

    # 4. 提供撤销选项
    if batch_files:
        print("\n" + "="*60)
        undo_choice = input("是否需要撤销本次批量修改？(y/n)：")
        if undo_choice.lower() == "y":
            undo_recent_changes()
        else:
            print("✅ 无需撤销，操作结束！")
    else:
        print("\n✅ 未检测到批量修改文件，无需撤销！")

    print("\n" + "="*60)
    print("🎉 工具运行结束！")
    print("="*60)