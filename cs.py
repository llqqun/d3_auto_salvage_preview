import pyautogui
import keyboard

def demo():
  print(pyautogui.position())

def main():
    print("🟢 已启动调试工具。请切换到游戏并按下 F5 启动检测。")
    keyboard.add_hotkey('F5', demo)
    keyboard.wait()
main()