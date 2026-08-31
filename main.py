# -*- coding: utf-8 -*-
"""
24点游戏 (Python + Kivy) - 仅功能三：数字24算法
====================================================
输入 4 个数字(空格分隔)，程序自动判断并显示计算算式

电脑上运行：  pip install kivy  然后  python main.py
打包安卓APK： 见 README.md（buildozer，需在 Linux/WSL 下执行）
"""

import os

# 注意：Android 上必须使用默认的 sdl2 图形后端（APK 中没有 ANGLE 库，
# 且 kivy 2.3.0 也不存在 angle_sdl2 后端）。强制设置会导致应用启动即闪退，
# 因此只在非 Android 平台（如桌面）启用 angle_sdl2。
from kivy.utils import platform as _kivy_platform
if _kivy_platform != "android":
    os.environ["KIVY_GRAPHICS"] = "angle_sdl2"
os.environ["KIVY_TEXT"] = "sdl2"

import random
import traceback
from fractions import Fraction

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput

# ---------------------------------------------------------------- 中文字体注册
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_FONT_PATH = os.path.join(_BASE_DIR, "assets", "fonts", "NotoSansSC-Regular.otf")
FONT = "Roboto"
if os.path.exists(_FONT_PATH):
    try:
        LabelBase.register(name="CJK", fn_regular=_FONT_PATH)
        FONT = "CJK"
    except Exception:
        pass

# ---------------------------------------------------------------- 颜色常量
WINDOW_BG = (0.11, 0.12, 0.16, 1)          # 深色背景
CARD_BG = (0.60, 0.80, 0.95, 1)            # 数字卡片：浅蓝色
TEXT_DARK = (0.10, 0.10, 0.12, 1)
TEXT_LIGHT = (1, 1, 1, 1)
GREEN = (0.30, 0.80, 0.40, 1)              # 成功（绿字）
RED = (0.95, 0.30, 0.30, 1)                # 失败（红字）
GREY = (0.70, 0.72, 0.76, 1)

TITLE_FONT = dp(26)
CARD_FONT = dp(26)
BIG_FONT = dp(22)


def fmt(value):
    """把 Fraction 转成用于显示的字符串：整数直接显示，分数显示为 a/b"""
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        return "%d/%d" % (value.numerator, value.denominator)
    return str(value)


# ================================================================ 卡片控件
class Card(Button):
    """居中显示的卡片：数字卡片"""

    def __init__(self, face, value=None, expr=None, bg=CARD_BG,
                 text_color=TEXT_DARK, font_size=CARD_FONT, **kwargs):
        super(Card, self).__init__(
            text=face, font_name=FONT, font_size=font_size, bold=True,
            color=text_color,
            background_normal="", background_down="",
            background_color=(0, 0, 0, 0), **kwargs)
        self.face = face
        self.value = value
        self.expr = expr if expr is not None else face
        self.bg_normal = bg
        self.selected = False
        self.size_hint = (None, None)

        with self.canvas.before:
            self.rect_color = Color(*bg)
            self.rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# ================================================================ 工具函数
def make_label(text, color=TEXT_LIGHT, font_size=dp(16), bold=False, **kwargs):
    return Label(text=text, font_name=FONT, font_size=font_size, bold=bold,
                 color=color, **kwargs)


def make_button(text, on_press, font_size=dp(18), size_hint=(1, 1),
                bg=(0.30, 0.36, 0.48, 1), **kwargs):
    btn = Button(text=text, font_name=FONT, font_size=font_size, bold=True,
                 color=TEXT_LIGHT, size_hint=size_hint,
                 background_normal="", background_down="",
                 background_color=bg, **kwargs)
    btn.bind(on_press=on_press)
    return btn


# ================================================================ 求解器
def solve24(nums, faces=None):
    """给出 4 个数，用加减乘除算出 24。能算出则返回算式字符串，否则返回 None。
    全程使用 Fraction 精确计算，避免除法舍入误差。"""
    if faces is None:
        faces = [str(n) for n in nums]
    items = [(Fraction(n), f) for n, f in zip(nums, faces)]

    def dfs(items):
        if len(items) == 1:
            if items[0][0] == 24:
                return items[0][1]
            return None
        n = len(items)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                a, ea = items[i]
                b, eb = items[j]
                rest = [items[k] for k in range(n) if k != i and k != j]
                candidates = [
                    (a + b, "(%s+%s)" % (ea, eb)),
                    (a - b, "(%s-%s)" % (ea, eb)),
                    (a * b, "(%s×%s)" % (ea, eb)),
                ]
                if b != 0:
                    candidates.append((a / b, "(%s÷%s)" % (ea, eb)))
                for value, expr in candidates:
                    answer = dfs(rest + [(value, expr)])
                    if answer is not None:
                        return answer
        return None

    answer = dfs(items)
    if answer is None:
        return None
    # 去掉最外层多余的括号
    if answer.startswith("(") and answer.endswith(")"):
        answer = answer[1:-1]
    return answer + " = 24"


# ================================================================ 求解界面
class SolverScreen(Screen):
    """功能三：数字24算法 —— 输入 4 个数字，自动求解"""

    def __init__(self, **kwargs):
        super(SolverScreen, self).__init__(**kwargs)
        self.cards = []

        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))

        self.title_label = make_label("数字24算法", font_size=TITLE_FONT,
                                      bold=True, size_hint=(1, None),
                                      height=dp(38))
        root.add_widget(self.title_label)

        # ---- 输入框
        self.input_box = TextInput(multiline=False, font_name=FONT,
                                   font_size=dp(16), hint_text="输入4个数字，空格分隔，如：10 11 13 2 或 A J Q K",
                                   hint_text_color=GREY, foreground_color=TEXT_DARK,
                                   background_color=(0.95, 0.95, 0.97, 1),
                                   size_hint=(1, None), height=dp(50),
                                   padding=[dp(10), dp(12), dp(10), dp(12)])
        root.add_widget(self.input_box)

        # ---- 3 个按钮并列放在输入框下方（居中对齐）
        button_row = BoxLayout(orientation="horizontal", spacing=dp(8),
                               size_hint=(None, None), width=dp(250), height=dp(50))
        button_row.add_widget(make_button("计算", self.on_solve,
                                          size_hint=(None, 1), width=dp(78),
                                          bg=(0.24, 0.47, 0.85, 1)))
        button_row.add_widget(make_button("重置", self.on_reset,
                                          size_hint=(None, 1), width=dp(78)))
        button_row.add_widget(make_button("退出", self.on_exit,
                                          size_hint=(None, 1), width=dp(78),
                                          bg=(0.70, 0.25, 0.25, 1)))

        button_anchor = AnchorLayout(anchor_x="center", anchor_y="center",
                                     size_hint=(1, None), height=dp(50))
        button_anchor.add_widget(button_row)
        root.add_widget(button_anchor)

        # ---- 中央：4 张数字卡片
        self.card_area = FloatLayout(size_hint=(1, 1))
        self.card_area.bind(size=lambda *a: self.relayout())
        root.add_widget(self.card_area)

        # ---- 卡片下方：结果显示（绿=算式 / 红=不可能）
        self.result_label = make_label("", font_size=dp(20), bold=True,
                                       size_hint=(1, None), height=dp(60))
        root.add_widget(self.result_label)
        self.add_widget(root)

    def relayout(self):
        """4 张卡片显示在屏幕正中央偏上"""
        area = self.card_area
        n = len(self.cards)
        if n == 0:
            return
        cw, ch = dp(80), dp(96)
        for index, card in enumerate(self.cards):
            cx = area.width * (index + 1) / (n + 1)
            card.size = (cw, ch)
            card.pos = (cx - cw / 2.0, area.height * 0.55 - ch / 2.0)

    def _show_cards(self, faces, nums):
        self.card_area.clear_widgets()
        self.cards = []
        for face, n in zip(faces, nums):
            card = Card(face=face, value=Fraction(n), expr=face)
            self.card_area.add_widget(card)
            self.cards.append(card)
        self.relayout()

    def _parse_input(self, parts):
        """解析输入，支持 A/J/Q/K -> 1/11/12/13，返回 (数值列表, 显示列表)"""
        rank_map = {'A': 1, 'J': 11, 'Q': 12, 'K': 13,
                    'a': 1, 'j': 11, 'q': 12, 'k': 13}
        nums = []
        faces = []
        for p in parts:
            if p in rank_map:
                nums.append(rank_map[p])
                faces.append(p.upper())  # 统一大写显示
            else:
                try:
                    n = int(p)
                    nums.append(n)
                    faces.append(str(n))
                except ValueError:
                    return None, None
        return nums, faces

    def on_solve(self, *args):
        text = self.input_box.text.strip()
        parts = text.split()
        if len(parts) != 4:
            self.result_label.color = RED
            self.result_label.text = "请输入 4 个数字，并用空格分隔！"
            self._show_cards([], [])
            return
        nums, faces = self._parse_input(parts)
        if nums is None:
            self.result_label.color = RED
            self.result_label.text = "输入必须是整数或 A/J/Q/K！"
            self._show_cards([], [])
            return
        if any(n < 1 or n > 99 for n in nums):
            self.result_label.color = RED
            self.result_label.text = "每个数字必须是 1~99 之间的整数！"
            self._show_cards([], [])
            return

        self._show_cards(faces, nums)                       # 中央显示 4 张卡片
        answer = solve24(nums, faces)
        if answer is not None:                       # 能算出 24 → 绿字算式
            self.result_label.color = GREEN
            self.result_label.text = answer
        else:                                        # 根本不能得出 → 红字
            self.result_label.color = RED
            self.result_label.text = "这 4 个数根本不可能算出 24"

    def on_reset(self, *args):
        """恢复初始状态：清空输入与显示"""
        self.input_box.text = ""
        self.card_area.clear_widgets()
        self.cards = []
        self.result_label.text = ""
        # 重置后让输入框获得焦点
        Clock.schedule_once(lambda dt: setattr(self.input_box, 'focus', True), 0.1)

    def on_exit(self, *args):
        App.get_running_app().stop()


# ================================================================ App 入口
class Game24App(App):
    title = "24点算法"

    def build(self):
        Window.clearcolor = WINDOW_BG
        self.screen_manager = ScreenManager()
        self.solver_screen = SolverScreen(name="solver")
        self.screen_manager.add_widget(self.solver_screen)
        # 启动后让输入框获取焦点
        Clock.schedule_once(lambda dt: setattr(self.solver_screen.input_box, 'focus', True), 0)
        return self.screen_manager


if __name__ == "__main__":
    try:
        Game24App().run()
    except BaseException:
        # 闪退排查：把异常写进应用私有目录，adb 调试模式下可读取：
        #   adb shell run-as org.example.game24 cat files/game24_crash.log
        traceback.print_exc()
        try:
            from android.storage import app_storage_path
            with open(os.path.join(app_storage_path(), "game24_crash.log"),
                      "w", encoding="utf-8") as _f:
                traceback.print_exc(file=_f)
        except Exception:
            pass
        raise