import pyautogui
import keyboard
import time
import cv2
import numpy as np
from PIL import ImageGrab, Image

# ========= 配置项 =========
GRID_START = (1400, 555)
GRID_SIZE = (51, 51)
GRID_COLS, GRID_ROWS = 10, 6
CAPTURE_WIDTH, CAPTURE_HEIGHT = 520, 312  # 10×52, 6×52

# ========= 坐标计算 =========
def get_inventory_slots():
    slots = []
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = GRID_START[0] + col * GRID_SIZE[0]
            y = GRID_START[1] + row * GRID_SIZE[1]
            slots.append((x, y))
    return slots

# ========= 图像识别 =========
def load_templates():
    return {
        "legend": cv2.imread("legend_star.png", 0),
        "set": cv2.imread("set_star.png", 0)
    }

def match_star(img, template, threshold=0.6):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    return len(list(zip(*loc[::-1]))) > 0

def is_target_item(img, templates):
    if match_star(img, templates["legend"]):
        return "legend"
    elif match_star(img, templates["set"]):
        return "set"
    return None

def right_click_item(x, y):
    pyautogui.moveTo(x + 25, y + 25, duration=0.05)  # 移动到格子中心
    pyautogui.rightClick()
    time.sleep(0.1)

def decompose_items(slots, item_types, salvage_button_pos=(170, 290)):
    print(f"[分解] 开始操作 {len(slots)} 件装备...")
    # 步骤 1：点击分解按钮
    pyautogui.moveTo(salvage_button_pos[0], salvage_button_pos[1], duration=0.05)
    pyautogui.click()

    for (x, y), item_type in zip(slots, item_types):
        if item_type in ("legend", "set"):
            # 步骤 2：点击目标装备
            pyautogui.moveTo(x + 25, y + 25, duration=0.05)
            pyautogui.click()
            time.sleep(0.1)

            # 步骤 3：确认分解（按回车）
            pyautogui.press('enter')
            print(f" → 分解 {item_type} 装备 @ ({x},{y})")

            # 步骤 4：等待动画（可调）
            time.sleep(0.1)

    print("[分解] 全部完成 ✅")
# ========= 主逻辑 =========
def scan_and_visualize():
    print("[工具] 截图中...")
    full_img = ImageGrab.grab(bbox=(GRID_START[0], GRID_START[1], 
                                    GRID_START[0] + CAPTURE_WIDTH, 
                                    GRID_START[1] + CAPTURE_HEIGHT))
    full_cv = cv2.cvtColor(np.array(full_img), cv2.COLOR_RGB2BGR)

    slots = get_inventory_slots()
    templates = load_templates()
    found = 0
    matched_slots = []
    matched_types = []

    for (x, y) in slots:
        offset_x = x - GRID_START[0]
        offset_y = y - GRID_START[1]
        slot_img = full_cv[offset_y:offset_y + 51, offset_x:offset_x + 51]

        item_type = is_target_item(slot_img, templates)
        if item_type == "legend":
            color = (0, 165, 255)
            found += 1
            matched_slots.append((x, y))
            matched_types.append(item_type)
        elif item_type == "set":
            color = (0, 255, 0)
            found += 1
            matched_slots.append((x, y))
            matched_types.append(item_type)
        else:
            color = (255, 255, 255)

        cv2.rectangle(full_cv, (offset_x, offset_y), 
                      (offset_x + 51, offset_y + 51), color, 2)

    cv2.imwrite("debug_result.png", full_cv)
    print(f"[工具] 扫描完成，共识别到 {found} 件装备，输出：debug_result.png")

    if found:
        decompose_items(matched_slots, matched_types)
    else:
        print("[分解] 无可操作物品")

# ========= 快捷键触发 =========
def main():
    print("🟢 已启动调试工具。请切换到游戏并按下 F5 启动检测。")
    keyboard.add_hotkey('F5', scan_and_visualize)
    keyboard.wait()

if __name__ == "__main__":
    main()
