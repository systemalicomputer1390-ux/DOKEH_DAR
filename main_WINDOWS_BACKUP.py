import os
import json
import random

from kivy.config import Config
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.core.text import LabelBase
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

# =========================================================
# فارسی
# =========================================================

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_PERSIAN = True
except Exception:
    HAS_PERSIAN = False


def fa(text):
    text = str(text)

    if not HAS_PERSIAN:
        return text

    try:
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


# =========================================================
# تنظیمات اصلی
# =========================================================

# ---------------------------------------------------------
# نمایشگر: دسکتاپ ثابت، Android افقی و responsive
# ---------------------------------------------------------
BASE_WIDTH = 1280
BASE_HEIGHT = 720

# در Android اندازه پنجره را دستی تعیین نمی‌کنیم؛ Kivy اندازه واقعی
# دستگاه را به ما می‌دهد. فقط جهت افقی را مشخص می‌کنیم.
if platform == "android":
    try:
        Config.set("graphics", "orientation", "landscape")
    except Exception:
        pass
else:
    Window.size = (BASE_WIDTH, BASE_HEIGHT)
    Window.minimum_width = 1000
    Window.minimum_height = 600

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FONT_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "fonts",
    "Vazirmatn-Bold.otf"
)

BG_DIR = os.path.join(BASE_DIR, "assets", "backgrounds")
PROD_DIR = os.path.join(BASE_DIR, "assets", "products")
CUST_DIR = os.path.join(BASE_DIR, "assets", "customers")
SND_DIR = os.path.join(BASE_DIR, "assets", "sounds")

MENU_BG = os.path.join(BG_DIR, "menu_background.png")
GAME_BG = os.path.join(BG_DIR, "background.png")

PROGRESS_FILE = os.path.join(BASE_DIR, "progress.json")
LAYOUT_FILE = os.path.join(BASE_DIR, "layout_save.json")
CUSTOMER_LAYOUT_FILE = os.path.join(BASE_DIR, "customer_layout.json")


if os.path.exists(FONT_PATH):
    try:
        LabelBase.register(
            name="GameFont",
            fn_regular=FONT_PATH
        )
        GAME_FONT = "GameFont"
    except Exception:
        GAME_FONT = "Roboto"
else:
    GAME_FONT = "Roboto"


# =========================================================
# صدای بازی
# =========================================================

try:
    import pygame

    pygame.mixer.init()
    HAS_SOUND = True

except Exception:
    HAS_SOUND = False


class SoundManager:

    def __init__(self):
        self.music_on = True
        self.sfx_on = True
        self.click_sound = None

        Clock.schedule_once(
            lambda dt: self.play_music(),
            1
        )

    def play_music(self):

        if not HAS_SOUND:
            return

        if not self.music_on:
            return

        path = os.path.join(
            SND_DIR,
            "bg_music.mp3"
        )

        if not os.path.exists(path):
            return

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def stop_music(self):

        if not HAS_SOUND:
            return

        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def play_click(self):

        if not HAS_SOUND:
            return

        if not self.sfx_on:
            return

        if self.click_sound is None:

            path = os.path.join(
                SND_DIR,
                "click.wav"
            )

            if os.path.exists(path):

                try:
                    self.click_sound = pygame.mixer.Sound(path)
                except Exception:
                    self.click_sound = None

        if self.click_sound:

            try:
                self.click_sound.play()
            except Exception:
                pass


sound_mgr = SoundManager()


# =========================================================
# اطلاعات محصولات
# =========================================================

PRODUCT_DATA = {

    "SHIPAPA.png": {
        "name": "شیپاپا",
        "price": 150,
        "buy_price": 80,
        "scale": 1.0,
        "max": 10
    },

    "PICMAZE.png": {
        "name": "پیک کزه",
        "price": 220,
        "buy_price": 120,
        "scale": 1.0,
        "max": 8
    },

    "TACBERAC.png": {
        "name": "تک",
        "price": 180,
        "buy_price": 95,
        "scale": 1.0,
        "max": 10
    },

    "ALAVIPOOR.png": {
        "name": "علوی پور",
        "price": 250,
        "buy_price": 140,
        "scale": 1.0,
        "max": 10
    },

    "MORTEZA.png": {
        "name": "شیرکاکائو",
        "price": 200,
        "buy_price": 110,
        "scale": 0.95,
        "max": 12
    },

    "BABRI.png": {
        "name": "ادامس ببری",
        "price": 100,
        "buy_price": 50,
        "scale": 0.62,
        "max": 15
    },

    "WATER (1).png": {
        "name": "آب",
        "price": 100,
        "buy_price": 40,
        "scale": 0.85,
        "max": 12
    },

    "DIXFAX.png": {
        "name": "دیکس فکس",
        "price": 180,
        "buy_price": 95,
        "scale": 0.80,
        "max": 8
    },

    "KOACA.png": {
        "name": "کوکا",
        "price": 200,
        "buy_price": 110,
        "scale": 0.80,
        "max": 10
    }
}


# =========================================================
# مراحل
# =========================================================

LEVEL_DATA = {

    1: {"count": 4, "time": 90},
    2: {"count": 6, "time": 85},
    3: {"count": 8, "time": 80},
    4: {"count": 10, "time": 75},
    5: {"count": 12, "time": 70},
    6: {"count": 13, "time": 65},
    7: {"count": 14, "time": 60},
    8: {"count": 15, "time": 55},
    9: {"count": 16, "time": 50},
    10: {"count": 18, "time": 45}
}


CUSTOMER_NAMES = [
    "آقای محمدی",
    "خانم احمدی",
    "آقای رضایی",
    "خانم کریمی",
    "آقای حسینی"
]

CUSTOMER_DEFAULT_LAYOUT = [
    {"x": 145, "y": 140, "w": 180, "h": 270},
    {"x": 360, "y": 140, "w": 180, "h": 270},
    {"x": 575, "y": 140, "w": 180, "h": 270},
    {"x": 790, "y": 140, "w": 180, "h": 270},
    {"x": 1005, "y": 140, "w": 180, "h": 270},
]


# =========================================================
# سیستم پیشرفت
# =========================================================

class ProgressManager:

    def __init__(self):

        self.total_coins = 500

        self.unlocked_level = 1

        self.stars = {
            str(i): 0
            for i in range(1, 11)
        }

        self.load()

    def load(self):

        if not os.path.exists(PROGRESS_FILE):
            return

        try:

            with open(
                PROGRESS_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            self.total_coins = int(
                data.get(
                    "total_coins",
                    500
                )
            )

            self.unlocked_level = int(
                data.get(
                    "unlocked_level",
                    1
                )
            )

            saved_stars = data.get(
                "stars",
                {}
            )

            for i in range(1, 11):

                self.stars[str(i)] = int(
                    saved_stars.get(
                        str(i),
                        0
                    )
                )

        except Exception:
            pass

    def save(self):

        data = {
            "total_coins": self.total_coins,
            "unlocked_level": self.unlocked_level,
            "stars": self.stars
        }

        try:

            with open(
                PROGRESS_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

        except Exception:
            pass

    def add_coins(self, amount):

        self.total_coins += int(amount)

        if self.total_coins < 0:
            self.total_coins = 0

        self.save()

    def set_stars(self, level, stars):

        old = self.stars.get(
            str(level),
            0
        )

        if stars > old:

            self.stars[str(level)] = stars

        if stars >= 2 and level < 10:

            if self.unlocked_level < level + 1:

                self.unlocked_level = level + 1

        self.save()


progress = ProgressManager()


# =========================================================
# دکمه بازی
# =========================================================

class GameButton(Button):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.font_name = GAME_FONT

        self.color = (
            1,
            1,
            1,
            1
        )

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (
            0,
            0,
            0,
            0
        )

        with self.canvas.before:

            Color(
                0.08,
                0.08,
                0.08,
                0.90
            )

            self.rect_bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[18]
            )

            Color(
                0.78,
                0.28,
                0.05,
                1
            )

            self.rect_border = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    18
                ),
                width=2
            )

        self.bind(
            pos=self._update_rects,
            size=self._update_rects
        )

    def _update_rects(self, *args):

        self.rect_bg.pos = self.pos
        self.rect_bg.size = self.size

        self.rect_border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            18
        )


# =========================================================
# محصول داخل دکه
# =========================================================

class ProductItem(FloatLayout):

    def __init__(
        self,
        filename,
        data,
        screen,
        slot_ref,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.filename = filename
        self.name = data["name"]
        self.price = data["price"]
        self.screen = screen
        self.slot_ref = slot_ref

        self.is_selected = False

        self.scale = data["scale"]

        self.min_scale = 0.3
        self.max_scale = 2.0

        self.size_hint = (
            None,
            None
        )

        self._update_size()

        img_path = os.path.join(
            PROD_DIR,
            filename
        )

        self.img = Image(
            source=(
                img_path
                if os.path.exists(img_path)
                else ""
            ),
            size_hint=(1, 1),
            pos_hint={
                "x": 0,
                "y": 0
            },
            allow_stretch=True,
            keep_ratio=True
        )

        self.add_widget(self.img)

        self.highlight = None

    def _update_size(self):

        self.size = (
            58 * self.scale,
            65 * self.scale
        )

    def set_scale(self, scale):

        scale = max(
            self.min_scale,
            min(
                self.max_scale,
                scale
            )
        )

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2

        self.scale = scale

        self._update_size()

        self.pos = (
            cx - self.width / 2,
            cy - self.height / 2
        )

        self.update_highlight()

    def resize(self, direction):

        self.set_scale(
            self.scale +
            (
                0.1
                if direction > 0
                else -0.1
            )
        )

    def add_highlight(self):

        if self.highlight:
            return

        with self.canvas.before:

            Color(
                1,
                0.85,
                0.1,
                1
            )

            self.highlight = Line(
                rounded_rectangle=(
                    self.x - 3,
                    self.y - 3,
                    self.width + 6,
                    self.height + 6,
                    5
                ),
                width=3
            )

    def update_highlight(self):

        if self.highlight:

            self.highlight.rounded_rectangle = (
                self.x - 3,
                self.y - 3,
                self.width + 6,
                self.height + 6,
                5
            )

    def remove_highlight(self):

        if self.highlight:

            try:
                self.canvas.before.remove(
                    self.highlight
                )
            except Exception:
                pass

            self.highlight = None

    def deselect(self):

        self.is_selected = False
        self.remove_highlight()


# =========================================================
# اسلات محصولات
# =========================================================

class ProductSlot(FloatLayout):

    def __init__(
        self,
        fname,
        amount,
        data,
        gs,
        position,
        size,
        columns,
        rows,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.fname = fname
        self.amount = amount
        self.max_amt = amount

        self.data = data
        self.gs = gs

        self.col = columns
        self.row = rows

        self.items = []

        self.sx = (
            position[0] *
            Window.width
        )

        self.sy = (
            position[1] *
            Window.height
        )

        self.sw = size[0]
        self.sh = size[1]

        self.size_hint = (
            None,
            None
        )

        self.size = size
        self.pos = (
            self.sx,
            self.sy
        )

        self._create()

    def _create(self):

        cw = self.sw / self.col
        ch = self.sh / self.row

        for i in range(self.amount):

            r = i // self.col
            c = i % self.col

            item = ProductItem(
                self.fname,
                self.data,
                self.gs,
                self
            )

            ix = (
                self.sx +
                c * cw +
                (cw - item.width) / 2
            )

            iy = (
                self.sy +
                self.sh -
                (r + 1) * ch +
                (ch - item.height) / 2
            )

            item.pos = (
                ix,
                iy
            )

            self.gs.root_layout.add_widget(
                item
            )

            self.items.append(item)

    def remove_item(self, item):

        if item not in self.items:
            return

        if item.parent:

            item.parent.remove_widget(
                item
            )

        self.items.remove(item)
        self.amount -= 1


# =========================================================
# مشتری
# =========================================================

class Customer(FloatLayout):
    def __init__(self, game_screen, index, image_filename=None, layout_index=None, **kwargs):
        super().__init__(**kwargs)

        self.gs = game_screen
        self.index = index
        self.layout_index = index if layout_index is None else int(layout_index)
        self.name = CUSTOMER_NAMES[index % len(CUSTOMER_NAMES)]
        self.patience = 100
        self.is_selected = False
        self.min_width = 80
        self.max_width = 500
        self.min_height = 100
        self.max_height = 600

        product_keys = list(PRODUCT_DATA.keys())
        request_count = random.randint(1, 2)
        self.requests = random.sample(product_keys, request_count)
        self.fulfilled = []

        # جای مشتری از تنظیمات گیم‌پلی
        self.size_hint = (None, None)
        cfg = game_screen.get_customer_config(self.layout_index)
        self.size = (float(cfg["w"]), float(cfg["h"]))
        self.pos = (float(cfg["x"]), float(cfg["y"]))
        self.target_pos = (float(cfg["x"]), float(cfg["y"]))

        # تصویر مشتری: در بازی هر مشتری یک چهره متفاوت می‌گیرد
        if image_filename is None:
            image_filename = game_screen.get_customer_image(index)

        src = os.path.join(CUST_DIR, image_filename) if image_filename else ""

        self.body = Image(
            source=src if os.path.exists(src) else "",
            size_hint=(1, 0.82),
            pos_hint={"x": 0, "y": 0},
            allow_stretch=True,
            keep_ratio=True
        )
        self.add_widget(self.body)

        # کادر درخواست: نام محصول به‌صورت واضح داخل خود بازی نمایش داده می‌شود.
        self.request_box = FloatLayout(size_hint=(None, None), size=(260, 72))
        with self.request_box.canvas.before:
            Color(0.02, 0.02, 0.03, 0.94)
            self.request_bg = RoundedRectangle(pos=self.request_box.pos, size=self.request_box.size, radius=[12])
        self.request_box.bind(pos=self._update_request_box, size=self._update_request_box)

        names = [str(PRODUCT_DATA.get(x, {}).get("name", x)) for x in self.requests]
        request_text = "درخواست شما: " + "، ".join(names) if names else "درخواست: محصول"
        self.lbl_req = Label(
            text=fa(request_text), font_name=GAME_FONT, font_size="18sp",
            color=(1, 1, 1, 1), size_hint=(1, 1),
            halign="center", valign="middle", text_size=(None, None)
        )
        self.request_box.add_widget(self.lbl_req)
        self.add_widget(self.request_box)
        self.bind(pos=self._position_request_box, size=self._position_request_box)

        # نوار صبر
        with self.canvas:
            Color(0.15, 0.15, 0.15, 0.9)
            self.bar_bg = RoundedRectangle(
                pos=(35, 15), size=(150, 9), radius=[4]
            )
            Color(0.2, 0.8, 0.2, 1)
            self.bar_fg = RoundedRectangle(
                pos=(35, 15), size=(150, 9), radius=[4]
            )

        self.move_event = None
        self.highlight = None

    def _update_request_box(self, *args):
        self.request_bg.pos = self.request_box.pos
        self.request_bg.size = self.request_box.size

    def _position_request_box(self, *args):
        if not hasattr(self, "request_box"):
            return
        self.request_box.width = min(320, max(220, self.width * 0.95))
        self.request_box.height = 72
        self.request_box.pos = (
            self.x + (self.width - self.request_box.width) / 2,
            self.y + self.height - self.request_box.height + 6
        )

    def add_highlight(self):
        if self.highlight:
            return
        with self.canvas.after:
            Color(1, 0.85, 0.1, 1)
            self.highlight = Line(
                rounded_rectangle=(self.x - 4, self.y - 4, self.width + 8, self.height + 8, 8),
                width=3
            )

    def update_highlight(self):
        if self.highlight:
            self.highlight.rounded_rectangle = (
                self.x - 4, self.y - 4, self.width + 8, self.height + 8, 8
            )

    def remove_highlight(self):
        if self.highlight:
            try:
                self.canvas.after.remove(self.highlight)
            except Exception:
                pass
            self.highlight = None

    def deselect(self):
        self.is_selected = False
        self.remove_highlight()

    def resize(self, direction):
        factor = 1.05 if direction > 0 else 0.95
        center = self.center
        self.size = (
            max(self.min_width, min(self.max_width, self.width * factor)),
            max(self.min_height, min(self.max_height, self.height * factor))
        )
        self.center = center
        self.target_pos = self.pos
        self.update_highlight()

    # انتقال مستقیم لمس مشتری به ویرایشگر؛ این باعث می‌شود Image/حباب جلوی انتخاب را نگیرد.
    def on_touch_down(self, touch):
        try:
            if self.gs.manager.current == "gameplay_editor":
                editor = self.gs.manager.get_screen("gameplay_editor")
                if editor.customer_touch_down(self, touch):
                    return True
        except Exception:
            pass
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        try:
            if self.gs.manager.current == "gameplay_editor":
                editor = self.gs.manager.get_screen("gameplay_editor")
                if editor.customer_touch_move(self, touch):
                    return True
        except Exception:
            pass
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        try:
            if self.gs.manager.current == "gameplay_editor":
                editor = self.gs.manager.get_screen("gameplay_editor")
                if editor.customer_touch_up(self, touch):
                    return True
        except Exception:
            pass
        return super().on_touch_up(touch)

    def update_patience(self):
        self.patience -= 0.45
        ratio = max(0, self.patience / 100)
        self.bar_fg.size = (150 * ratio, 9)
        return self.patience <= 0


# =========================================================
# منوی اصلی
# =========================================================

class MainMenu(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        root = FloatLayout()

        self.bg = Image(
            source=(
                MENU_BG
                if os.path.exists(MENU_BG)
                else ""
            ),
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1)
        )

        root.add_widget(
            self.bg
        )

        # عنوان

        title_box = FloatLayout(
            size_hint=(
                0.5,
                0.18
            ),
            pos_hint={
                "x": 0.55,
                "top": 0.85
            }
        )

        with title_box.canvas.before:

            Color(
                0,
                0,
                0,
                0.55
            )

            RoundedRectangle(
                pos=title_box.pos,
                size=title_box.size,
                radius=[20]
            )

        title = Label(
            text=fa("دکه دار"),
            font_name=GAME_FONT,
            font_size="90sp",
            color=(
                1,
                0.8,
                0.2,
                1
            ),
            size_hint=(1, 1)
        )

        title_box.add_widget(
            title
        )

        root.add_widget(
            title_box
        )

        buttons = [
            ("شروع بازی", 0.55, "levels"),
            ("فروشگاه", 0.44, "shop"),
            ("تنظیمات", 0.33, "settings"),
            ("سازندگان", 0.22, "creators"),
            ("خروج", 0.11, "exit")
        ]

        for text, y, destination in buttons:

            button = GameButton(
                text=fa(text),
                font_size="32sp",
                size_hint=(
                    0.30,
                    0.085
                ),
                pos_hint={
                    "center_x": 0.80,
                    "center_y": y
                }
            )

            button.destination = destination

            button.bind(
                on_release=self.navigate
            )

            root.add_widget(
                button
            )

        self.add_widget(
            root
        )

    def navigate(self, button):

        sound_mgr.play_click()

        if button.destination == "exit":

            App.get_running_app().stop()

        else:

            self.manager.current = (
                button.destination
            )


# =========================================================
# صفحه مراحل
# =========================================================

class LevelsScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        root = FloatLayout()

        root.add_widget(
            Image(
                source=(
                    MENU_BG
                    if os.path.exists(MENU_BG)
                    else ""
                ),
                allow_stretch=True,
                keep_ratio=False,
                size_hint=(1, 1)
            )
        )

        title = Label(
            text=fa("انتخاب مرحله"),
            font_name=GAME_FONT,
            font_size="55sp",
            color=(
                1,
                0.8,
                0.2,
                1
            ),
            size_hint=(
                0.6,
                0.1
            ),
            pos_hint={
                "center_x": 0.5,
                "top": 0.95
            }
        )

        root.add_widget(
            title
        )

        self.level_buttons = []

        for i in range(10):

            level = i + 1

            row = i // 5
            col = i % 5

            x = 0.10 + col * 0.18
            y = 0.48 - row * 0.30

            locked = level > progress.unlocked_level

            text = (
                f"🔒 مرحله {level}"
                if locked
                else f"مرحله {level}"
            )

            button = GameButton(
                text=fa(text),
                font_size="25sp",
                size_hint=(
                    0.15,
                    0.17
                ),
                pos_hint={
                    "x": x,
                    "y": y
                }
            )

            button.level = level
            button.locked = locked

            button.bind(
                on_release=self.select_level
            )

            root.add_widget(
                button
            )

            stars_count = progress.stars.get(
                str(level),
                0
            )

            stars_text = (
                "★" * stars_count +
                "☆" * (3 - stars_count)
            )

            stars = Label(
                text=stars_text,
                font_name=GAME_FONT,
                font_size="27sp",
                color=(
                    1,
                    0.85,
                    0.2,
                    1
                ),
                size_hint=(
                    0.15,
                    0.05
                ),
                pos_hint={
                    "x": x,
                    "y": y - 0.06
                }
            )

            root.add_widget(
                stars
            )

            self.level_buttons.append(
                button
            )

        back = GameButton(
            text=fa("بازگشت"),
            font_size="26sp",
            size_hint=(
                0.25,
                0.08
            ),
            pos_hint={
                "center_x": 0.5,
                "y": 0.025
            }
        )

        back.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "main"
            )
        )

        root.add_widget(
            back
        )

        self.add_widget(
            root
        )

    def on_enter(self):

        for button in self.level_buttons:

            level = button.level

            locked = (
                level >
                progress.unlocked_level
            )

            button.locked = locked

            button.text = fa(
                f"🔒 مرحله {level}"
                if locked
                else f"مرحله {level}"
            )

    def select_level(self, button):

        sound_mgr.play_click()

        if button.locked:
            return

        game = self.manager.get_screen(
            "game"
        )

        game.current_level = (
            button.level
        )

        self.manager.current = "game"


# =========================================================
# کارت محصول فروشگاه
# =========================================================

class ShopProductCard(FloatLayout):

    def __init__(
        self,
        filename,
        data,
        shop,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.filename = filename
        self.data = data
        self.shop = shop

        self.size_hint = (
            None,
            None
        )

        self.size = (
            285,
            145
        )

        # کادر نیمه شفاف
        with self.canvas.before:

            Color(
                0.04,
                0.04,
                0.04,
                0.86
            )

            self.card_bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[18]
            )

            Color(
                0.78,
                0.28,
                0.05,
                0.65
            )

            self.card_border = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    18
                ),
                width=2
            )

        self.bind(
            pos=self.update_card,
            size=self.update_card
        )

        # تصویر محصول

        image_path = os.path.join(
            PROD_DIR,
            filename
        )

        self.product_image = Image(
            source=(
                image_path
                if os.path.exists(image_path)
                else ""
            ),
            size_hint=(
                None,
                None
            ),
            size=(
                85,
                85
            ),
            pos_hint={
                "x": 0.04,
                "center_y": 0.55
            },
            allow_stretch=True,
            keep_ratio=True
        )

        self.add_widget(
            self.product_image
        )

        # نام محصول

        name = Label(
            text=fa(data["name"]),
            font_name=GAME_FONT,
            font_size="27sp",
            color=(
                1,
                1,
                1,
                1
            ),
            size_hint=(
                0.58,
                0.28
            ),
            pos_hint={
                "right": 0.97,
                "top": 0.94
            },
            halign="right",
            valign="middle"
        )

        self.add_widget(
            name
        )

        # قیمت

        price = Label(
            text=fa(
                f"قیمت: {data['buy_price']} سکه"
            ),
            font_name=GAME_FONT,
            font_size="20sp",
            color=(
                0.8,
                1,
                0.8,
                1
            ),
            size_hint=(
                0.58,
                0.22
            ),
            pos_hint={
                "right": 0.97,
                "center_y": 0.55
            },
            halign="right"
        )

        self.add_widget(
            price
        )

        # موجودی

        stock = Label(
            text=fa("موجودی: آماده"),
            font_name=GAME_FONT,
            font_size="17sp",
            color=(
                0.75,
                0.8,
                0.9,
                1
            ),
            size_hint=(
                0.58,
                0.18
            ),
            pos_hint={
                "right": 0.97,
                "center_y": 0.34
            },
            halign="right"
        )

        self.add_widget(
            stock
        )

        # خرید

        buy_button = GameButton(
            text=fa("خرید"),
            font_size="20sp",
            size_hint=(
                None,
                None
            ),
            size=(
                95,
                42
            ),
            pos_hint={
                "right": 0.95,
                "y": 0.04
            }
        )

        buy_button.bind(
            on_release=self.buy
        )

        self.add_widget(
            buy_button
        )

    def update_card(self, *args):

        self.card_bg.pos = self.pos
        self.card_bg.size = self.size

        self.card_border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            18
        )

    def buy(self, button):

        sound_mgr.play_click()

        price = self.data["buy_price"]

        if progress.total_coins < price:

            self.shop.show_message(
                "سکه کافی نیست!"
            )

            return

        progress.add_coins(
            -price
        )

        self.shop.update_coins()

        self.shop.show_message(
            f"{self.data['name']} خریداری شد"
        )


# =========================================================
# فروشگاه
# =========================================================

class ShopScreen(Screen):

    def on_enter(self):

        self.clear_widgets()

        root = FloatLayout()

        self.root_layout = root

        # بک گراند
        root.add_widget(
            Image(
                source=(
                    MENU_BG
                    if os.path.exists(MENU_BG)
                    else ""
                ),
                allow_stretch=True,
                keep_ratio=False,
                size_hint=(1, 1)
            )
        )

        # عنوان

        title = Label(
            text=fa("فروشگاه"),
            font_name=GAME_FONT,
            font_size="58sp",
            color=(
                1,
                0.8,
                0.2,
                1
            ),
            size_hint=(
                0.35,
                0.10
            ),
            pos_hint={
                "center_x": 0.5,
                "top": 0.96
            }
        )

        root.add_widget(
            title
        )

        # سکه

        self.coins_label = Label(
            text="",
            font_name=GAME_FONT,
            font_size="28sp",
            color=(
                1,
                0.9,
                0.2,
                1
            ),
            size_hint=(
                0.28,
                0.07
            ),
            pos_hint={
                "right": 0.97,
                "top": 0.94
            },
            halign="right"
        )

        root.add_widget(
            self.coins_label
        )

        self.update_coins()

        # -----------------------------------------
        # کارت محصولات
        # -----------------------------------------

        items = list(
            PRODUCT_DATA.items()
        )

        positions = [
            (0.035, 0.60),
            (0.365, 0.60),
            (0.695, 0.60),

            (0.035, 0.40),
            (0.365, 0.40),
            (0.695, 0.40),

            (0.035, 0.20),
            (0.365, 0.20),
            (0.695, 0.20)
        ]

        for i, (filename, data) in enumerate(items):

            x, y = positions[i]

            card = ShopProductCard(
                filename,
                data,
                self
            )

            card.pos = (
                x * Window.width,
                y * Window.height
            )

            root.add_widget(
                card
            )

        # -----------------------------------------
        # خرید سکه - فقط به زودی
        # -----------------------------------------

        coin_card = FloatLayout(
            size_hint=(
                None,
                None
            ),
            size=(
                285,
                70
            ),
            pos_hint={
                "center_x": 0.5,
                "y": 0.085
            }
        )

        with coin_card.canvas.before:

            Color(
                0.04,
                0.04,
                0.04,
                0.88
            )

            RoundedRectangle(
                pos=coin_card.pos,
                size=coin_card.size,
                radius=[16]
            )

        coin_title = Label(
            text=fa(
                "خرید سکه"
            ),
            font_name=GAME_FONT,
            font_size="23sp",
            color=(
                1,
                1,
                1,
                1
            ),
            size_hint=(
                1,
                0.55
            ),
            pos_hint={
                "center_x": 0.5,
                "top": 0.95
            }
        )

        coin_card.add_widget(
            coin_title
        )

        coming = Label(
            text=fa(
                "به‌زودی"
            ),
            font_name=GAME_FONT,
            font_size="18sp",
            color=(
                1,
                0.8,
                0.2,
                1
            ),
            size_hint=(
                1,
                0.45
            ),
            pos_hint={
                "center_x": 0.5,
                "y": 0
            }
        )

        coin_card.add_widget(
            coming
        )

        root.add_widget(
            coin_card
        )

        # -----------------------------------------
        # بازگشت
        # -----------------------------------------

        back = GameButton(
            text=fa("بازگشت"),
            font_size="25sp",
            size_hint=(
                None,
                None
            ),
            size=(
                190,
                52
            ),
            pos_hint={
                "x": 0.025,
                "y": 0.025
            }
        )

        back.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "main"
            )
        )

        root.add_widget(
            back
        )

        self.add_widget(
            root
        )

    def update_coins(self):

        if hasattr(
            self,
            "coins_label"
        ):

            self.coins_label.text = fa(
                f"سکه شما: {progress.total_coins:,}"
            )

    def show_message(self, message):

        label = Label(
            text=fa(message),
            font_name=GAME_FONT,
            font_size="25sp",
            color=(
                1,
                1,
                1,
                1
            )
        )

        popup = Popup(
            title="",
            content=label,
            size_hint=(
                None,
                None
            ),
            size=(
                360,
                150
            ),
            auto_dismiss=True
        )

        popup.open()

        Clock.schedule_once(
            lambda dt:
            popup.dismiss(),
            1.2
        )


# =========================================================
# تنظیمات
# =========================================================

class SettingsScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        root = FloatLayout()
        root.add_widget(Image(source=MENU_BG if os.path.exists(MENU_BG) else "", allow_stretch=True, keep_ratio=False))
        root.add_widget(Label(text=fa("تنظیمات"), font_name=GAME_FONT, font_size="55sp", color=(1,0.8,0.2,1), size_hint=(0.4,0.1), pos_hint={"center_x":0.5,"top":0.95}))
        self.music_button=GameButton(text="",font_size="27sp",size_hint=(0.4,0.1),pos_hint={"center_x":0.5,"top":0.72})
        self.update_music_text(); self.music_button.bind(on_release=self.toggle_music); root.add_widget(self.music_button)
        self.sfx_button=GameButton(text="",font_size="27sp",size_hint=(0.4,0.1),pos_hint={"center_x":0.5,"top":0.57})
        self.update_sfx_text(); self.sfx_button.bind(on_release=self.toggle_sfx); root.add_widget(self.sfx_button)
        gameplay=GameButton(text=fa("تنظیمات گیم پلی"),font_size="27sp",size_hint=(0.4,0.1),pos_hint={"center_x":0.5,"top":0.42})
        gameplay.bind(on_release=self.open_gameplay_editor); root.add_widget(gameplay)
        root.add_widget(Label(text=fa("چیدمان محصولات و مشتری‌ها را از این قسمت تنظیم کنید"),font_name=GAME_FONT,font_size="17sp",color=(0.9,0.9,0.9,1),size_hint=(0.7,0.06),pos_hint={"center_x":0.5,"top":0.35}))
        back=GameButton(text=fa("بازگشت"),font_size="25sp",size_hint=(0.25,0.08),pos_hint={"center_x":0.5,"y":0.03})
        back.bind(on_release=lambda x:setattr(self.manager,"current","main")); root.add_widget(back); self.add_widget(root)
    def open_gameplay_editor(self, button):
        sound_mgr.play_click(); self.manager.current="gameplay_editor"
    def update_music_text(self): self.music_button.text=fa("قطع موسیقی" if sound_mgr.music_on else "پخش موسیقی")
    def update_sfx_text(self): self.sfx_button.text=fa("قطع افکت" if sound_mgr.sfx_on else "پخش افکت")
    def toggle_music(self, button):
        sound_mgr.music_on=not sound_mgr.music_on
        sound_mgr.play_music() if sound_mgr.music_on else sound_mgr.stop_music()
        self.update_music_text(); sound_mgr.play_click()
    def toggle_sfx(self, button):
        sound_mgr.sfx_on=not sound_mgr.sfx_on; self.update_sfx_text()
        if sound_mgr.sfx_on: sound_mgr.play_click()


class GameplayEditorScreen(Screen):
    """Editor مستقل برای چیدمان محصولات و مشتری‌ها.
    ذخیره‌سازی اتمیک است و مشتری‌ها مستقیماً لمس/drag می‌شوند.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = None
        self.products = []
        self.customers = []
        self.selected = None
        self.selected_products = []
        self.mode = "product"
        self.dragging = False
        self.drag_offset = (0, 0)
        # لمس‌های فعال برای ژست دو انگشتی تغییر اندازه در موبایل
        self._active_touches = {}
        self._pinch_start_distance = None
        self._pinch_start_size = None
        self.fields = {}
        self._keyboard_bound = False
        self.status = None
        self.panel = None
        self.root_layout = None

    def on_enter(self):
        self.game = self.manager.get_screen("game")
        self.game.stop_level()
        self.build_editor()
        if not self._keyboard_bound:
            Window.bind(on_key_down=self.on_key_down)
            self._keyboard_bound = True

    def on_leave(self):
        self.dragging = False
        self._active_touches.clear()
        self._pinch_start_distance = None
        self._pinch_start_size = None
        if self._keyboard_bound:
            Window.unbind(on_key_down=self.on_key_down)
            self._keyboard_bound = False

    def build_editor(self):
        self.clear_widgets()
        self.products = []
        self.customers = []
        self.selected = None
        self.selected_products = []
        self.fields = {}

        root = FloatLayout()
        self.root_layout = root
        root.add_widget(Image(source=GAME_BG if os.path.exists(GAME_BG) else "",
                              allow_stretch=True, keep_ratio=False))

        # محصولات را از layout فعلی بازی می‌گیریم.
        source = [c for c in self.game.root_layout.children if isinstance(c, ProductItem)]
        for src in reversed(source):
            obj = ProductItem(src.filename, PRODUCT_DATA[src.filename], self, None)
            obj.scale = src.scale
            obj._update_size()
            obj.pos = src.pos
            root.add_widget(obj)
            self.products.append(obj)

        # مشتری‌ها همیشه از تنظیمات ذخیره‌شده یا پیش‌فرض ساخته می‌شوند.
        for i in range(len(CUSTOMER_DEFAULT_LAYOUT)):
            obj = Customer(self.game, i,
                           image_filename=self.game.get_customer_image(i),
                           layout_index=i)
            root.add_widget(obj)
            self.customers.append(obj)

        # پنل را آخر اضافه می‌کنیم تا روی صحنه قرار بگیرد.
        panel = FloatLayout(size_hint=(None, 1), width=315,
                            pos_hint={"right": 1, "y": 0})
        self.panel = panel
        with panel.canvas.before:
            Color(0.035, 0.035, 0.045, 0.97)
            self.panel_bg = RoundedRectangle(pos=panel.pos, size=panel.size)
        panel.bind(pos=lambda *_: setattr(self.panel_bg, "pos", panel.pos),
                   size=lambda *_: setattr(self.panel_bg, "size", panel.size))
        root.add_widget(panel)

        panel.add_widget(Label(text=fa("تنظیمات گیم پلی"), font_name=GAME_FONT,
                               font_size="28sp", color=(1,0.85,0.25,1),
                               size_hint=(1,None), height=55,
                               pos_hint={"top":0.99}))

        prod_btn = GameButton(text=fa("محصولات"), font_size="20sp",
                              size_hint=(0.42,None), height=42,
                              pos_hint={"x":0.05,"top":0.89})
        prod_btn.bind(on_release=lambda *_: self.set_mode("product"))
        panel.add_widget(prod_btn)

        cust_btn = GameButton(text=fa("مشتری‌ها"), font_size="20sp",
                              size_hint=(0.42,None), height=42,
                              pos_hint={"right":0.95,"top":0.89})
        cust_btn.bind(on_release=lambda *_: self.set_mode("customer"))
        panel.add_widget(cust_btn)

        self.selected_label = Label(text=fa("چیزی انتخاب نشده"), font_name=GAME_FONT,
                                    font_size="17sp", color=(1,1,1,1),
                                    size_hint=(0.9,None), height=40,
                                    pos_hint={"center_x":0.5,"top":0.80}, halign="center")
        panel.add_widget(self.selected_label)

        specs = [("x","X",0.70),("y","Y",0.61),("w","عرض",0.52),
                 ("h","ارتفاع",0.43)]
        for key,title,top in specs:
            panel.add_widget(Label(text=fa(title), font_name=GAME_FONT,
                                   font_size="16sp", color=(0.8,0.85,0.9,1),
                                   size_hint=(0.28,None), height=34,
                                   pos_hint={"x":0.05,"top":top}))
            inp = TextInput(text="", multiline=False, input_filter="float",
                            font_name=GAME_FONT, font_size="16sp",
                            size_hint=(0.55,None), height=34,
                            pos_hint={"right":0.95,"top":top},
                            background_color=(0.12,0.12,0.14,1),
                            foreground_color=(1,1,1,1))
            inp.bind(on_text_validate=self.apply_fields)
            panel.add_widget(inp)
            self.fields[key] = inp

        panel.add_widget(Label(
            text=fa("مشتری را مستقیم لمس و بکشید\n+ / - : بزرگ و کوچک | جهت‌ها: حرکت | Ctrl+S: ذخیره"),
            font_name=GAME_FONT, font_size="14sp", color=(0.65,0.75,0.85,1),
            size_hint=(0.9,None), height=58,
            pos_hint={"center_x":0.5,"top":0.27}, halign="center"))

        save = GameButton(text=fa("ذخیره تغییرات"), font_size="19sp",
                          size_hint=(0.42,None), height=45,
                          pos_hint={"x":0.05,"y":0.13})
        save.bind(on_release=self.save_all)
        panel.add_widget(save)

        reset = GameButton(text=fa("بازنشانی"), font_size="19sp",
                           size_hint=(0.42,None), height=45,
                           pos_hint={"right":0.95,"y":0.13})
        reset.bind(on_release=self.reset_layout)
        panel.add_widget(reset)

        back = GameButton(text=fa("ذخیره و بازگشت"), font_size="19sp",
                          size_hint=(0.90,None), height=48,
                          pos_hint={"center_x":0.5,"y":0.035})
        back.bind(on_release=self.save_and_back)
        panel.add_widget(back)

        self.status = Label(text="", font_name=GAME_FONT, font_size="15sp",
                            color=(0.5,1,0.5,1), size_hint=(0.9,None), height=25,
                            pos_hint={"center_x":0.5,"y":0.205})
        panel.add_widget(self.status)

        self.add_widget(root)
        self.set_mode("product")

    def set_mode(self, mode):
        self.mode = mode
        self.deselect_all()
        self.status.text = fa("حالت محصولات - روی محصول کلیک کنید" if mode == "product"
                              else "حالت مشتری‌ها - روی مشتری کلیک کنید")

    def objects_for_mode(self):
        return self.products if self.mode == "product" else self.customers

    def hit_object(self, pos):
        # از بالا به پایین؛ مشتری‌ها را با ترتیب لایه فعلی بررسی کن.
        objs = self.objects_for_mode()
        for obj in reversed(objs):
            if obj.collide_point(*pos):
                return obj
        return None

    def select_single(self, obj):
        self.deselect_all()
        if obj is None:
            return
        obj.is_selected = True
        obj.add_highlight()
        self.selected = obj
        if self.mode == "product":
            self.selected_products = [obj]
        self.update_selection_label()
        self.update_fields()

    def deselect_all(self):
        for p in self.selected_products:
            p.deselect()
        for c in self.customers:
            c.deselect()
        self.selected_products = []
        self.selected = None
        if self.selected_label:
            self.selected_label.text = fa("چیزی انتخاب نشده")
        for f in self.fields.values():
            f.text = ""

    def update_selection_label(self):
        if self.selected is None:
            self.selected_label.text = fa("چیزی انتخاب نشده")
        elif self.mode == "customer":
            self.selected_label.text = fa("مشتری: " + self.selected.name)
        else:
            self.selected_label.text = fa("محصول: " + self.selected.name)

    def update_fields(self):
        if not self.selected:
            return
        self.fields["x"].text = f"{self.selected.x:.1f}"
        self.fields["y"].text = f"{self.selected.y:.1f}"
        self.fields["w"].text = f"{self.selected.width:.1f}"
        self.fields["h"].text = f"{self.selected.height:.1f}"

    def apply_fields(self, *args):
        if not self.selected:
            self.status.text = fa("اول یک مشتری یا محصول را انتخاب کنید")
            return
        try:
            x = float(self.fields["x"].text)
            y = float(self.fields["y"].text)
            w = max(10.0, float(self.fields["w"].text))
            h = max(10.0, float(self.fields["h"].text))
            x = max(0.0, min(Window.width - w, x))
            y = max(0.0, min(Window.height - h, y))
            self.selected.pos = (x, y)
            self.selected.size = (w, h)
            if hasattr(self.selected, "update_highlight"):
                self.selected.update_highlight()
            self.update_fields()
            self.save_all(silent=True)
            self.status.text = fa("اعمال و ذخیره شد ✓")
        except Exception as e:
            self.status.text = fa("عدد واردشده صحیح نیست")
            print("EDITOR FIELD ERROR:", e)

    # این متد مستقیماً از Customer صدا زده می‌شود و مشکل لمس مشتری را دور می‌زند.
    def customer_touch_down(self, customer, touch):
        if self.mode != "customer" or touch.button != "left":
            return False
        if not customer.collide_point(*touch.pos):
            return False
        self.select_single(customer)
        self.dragging = True
        self.drag_offset = (touch.x - customer.x, touch.y - customer.y)
        return True

    def customer_touch_move(self, customer, touch):
        if not self.dragging or self.selected is not customer:
            return False
        nx = touch.x - self.drag_offset[0]
        ny = touch.y - self.drag_offset[1]
        nx = max(0, min(Window.width - customer.width, nx))
        ny = max(0, min(Window.height - customer.height, ny))
        customer.pos = (nx, ny)
        customer.target_pos = customer.pos
        customer.update_highlight()
        self.update_fields()
        return True

    def customer_touch_up(self, customer, touch):
        if self.dragging and self.selected is customer:
            self.dragging = False
            self.save_all(silent=True)
            self.status.text = fa("موقعیت مشتری ذخیره شد ✓")
            return True
        return False

    def _panel_button_at(self, pos):
        """پیدا کردن دکمه‌های پنل برای لمس موبایل؛ مستقل از ترتیب لایه‌ها."""
        if not self.panel or not self.panel.collide_point(*pos):
            return None
        # آخرین child بالاترین لایه است.
        for child in reversed(self.panel.children):
            if isinstance(child, Button) and child.collide_point(*pos) and not child.disabled:
                return child
        return None

    def on_touch_down(self, touch):
        # اولویت قطعی با کنترل‌های پنل است؛ این بخش جلوی بلعیده‌شدن لمس
        # توسط لایه‌های بازی/مشتری‌ها را می‌گیرد.
        button = self._panel_button_at(touch.pos)
        if button is not None:
            button.trigger_action(duration=0)
            return True

        if touch.is_mouse_scrolling:
            if self.selected:
                self.resize_selected(1 if touch.button == "scrollup" else -1)
                return True
            return False

        self._active_touches[touch.uid] = (touch.x, touch.y)

        # هر لمس روی مشتری/محصول باید مستقیماً قابل انتخاب و جابه‌جایی باشد.
        obj = self.hit_object(touch.pos)
        if obj is not None:
            self.select_single(obj)
            if len(self._active_touches) == 1:
                self.dragging = True
                self.drag_offset = (touch.x - obj.x, touch.y - obj.y)
            elif self.selected is obj:
                self._pinch_start_size = (obj.width, obj.height)
                pts = list(self._active_touches.values())
                if len(pts) >= 2:
                    self._pinch_start_distance = self._distance(pts[-1], pts[-2])
            return True

        # روی پنل یا فضای خالی پنل، انتخاب قبلی را پاک نکن.
        if self.panel and self.panel.collide_point(*touch.pos):
            return False

        self.deselect_all()
        return False

    @staticmethod
    def _distance(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    def on_touch_move(self, touch):
        if touch.uid in self._active_touches:
            self._active_touches[touch.uid] = (touch.x, touch.y)

        # دو انگشت روی آیتم انتخاب‌شده = تغییر همزمان عرض و ارتفاع
        if self.selected is not None and len(self._active_touches) >= 2:
            pts = list(self._active_touches.values())
            if self._pinch_start_distance is None:
                self._pinch_start_distance = self._distance(pts[-1], pts[-2])
                self._pinch_start_size = (self.selected.width, self.selected.height)
            elif self._pinch_start_distance > 1:
                current = self._distance(pts[-1], pts[-2])
                factor = current / self._pinch_start_distance
                o = self.selected
                old_center = o.center
                if isinstance(o, Customer):
                    nw = max(o.min_width, min(o.max_width, self._pinch_start_size[0] * factor))
                    nh = max(o.min_height, min(o.max_height, self._pinch_start_size[1] * factor))
                else:
                    scale = max(o.min_scale, min(o.max_scale, o.scale * factor))
                    o.set_scale(scale)
                    nw, nh = o.size
                if isinstance(o, Customer):
                    o.size = (nw, nh)
                    o.center = old_center
                    o.target_pos = o.pos
                    o.update_highlight()
                self.update_fields()
                return True

        if self.dragging and self.selected:
            o = self.selected
            nx = max(0, min(Window.width-o.width, touch.x-self.drag_offset[0]))
            ny = max(0, min(Window.height-o.height, touch.y-self.drag_offset[1]))
            o.pos = (nx, ny)
            if hasattr(o, "update_highlight"):
                o.update_highlight()
            if hasattr(o, "target_pos"):
                o.target_pos = o.pos
            self.update_fields()
            return True
        return False

    def on_touch_up(self, touch):
        self._active_touches.pop(touch.uid, None)
        if len(self._active_touches) < 2:
            self._pinch_start_distance = None
            self._pinch_start_size = None
        if self.dragging:
            self.dragging = False
            self.save_all(silent=True)
            self.status.text = fa("تغییرات ذخیره شد ✓")
            return True
        if self.selected:
            self.save_all(silent=True)
        return False

    def resize_selected(self, direction):
        if not self.selected:
            return
        if isinstance(self.selected, ProductItem):
            self.selected.resize(direction)
        else:
            self.selected.resize(direction)
        self.update_fields()
        self.save_all(silent=True)

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if not self.selected:
            return False
        if key in (43, 61, 334):
            self.resize_selected(1)
            return True
        if key in (45, 333):
            self.resize_selected(-1)
            return True
        step = 20 if "shift" in modifiers else 5
        dx = dy = 0
        if key == 276: dx = -step
        elif key == 275: dx = step
        elif key == 273: dy = step
        elif key == 274: dy = -step
        elif key == 115 and "ctrl" in modifiers:
            self.save_all()
            return True
        else:
            return False
        self.selected.x = max(0, min(Window.width-self.selected.width, self.selected.x+dx))
        self.selected.y = max(0, min(Window.height-self.selected.height, self.selected.y+dy))
        if hasattr(self.selected, "update_highlight"):
            self.selected.update_highlight()
        self.update_fields()
        self.save_all(silent=True)
        return True

    def _atomic_json(self, path, data):
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def save_all(self, *args, silent=False):
        try:
            product_data = []
            for o in self.products:
                product_data.append({
                    "filename": o.filename,
                    "pos": [round(float(o.x),2), round(float(o.y),2)],
                    "scale": round(float(o.scale),3)
                })
            customer_data = []
            for o in self.customers:
                customer_data.append({
                    "index": int(o.layout_index),
                    "name": o.name,
                    "x": round(float(o.x),2),
                    "y": round(float(o.y),2),
                    "w": round(float(o.width),2),
                    "h": round(float(o.height),2)
                })
            self._atomic_json(LAYOUT_FILE, {"products": product_data})
            self._atomic_json(CUSTOMER_LAYOUT_FILE, {"customers": customer_data})
            # فایل‌ها را همین لحظه دوباره باز می‌کنیم تا مطمئن شویم JSON معتبر است.
            with open(LAYOUT_FILE, "r", encoding="utf-8") as f: json.load(f)
            with open(CUSTOMER_LAYOUT_FILE, "r", encoding="utf-8") as f: json.load(f)
            if not silent and self.status:
                self.status.text = fa("ذخیره شد ✓")
            return True
        except Exception as e:
            print("GAMEPLAY EDITOR SAVE ERROR:", repr(e))
            if self.status:
                self.status.text = fa("خطا در ذخیره: " + str(e))
            return False

    def save_and_back(self, *args):
        if self.save_all():
            self.manager.current = "settings"

    def reset_layout(self, *args):
        try:
            # حذف فایل‌های سفارشی و بازسازی کامل ادیتور با پیش‌فرض‌ها.
            for path in (LAYOUT_FILE, CUSTOMER_LAYOUT_FILE):
                if os.path.exists(path):
                    os.remove(path)
            # بازی را هم از فایل‌های حذف‌شده دوباره بارگذاری می‌کنیم و سپس
            # ادیتور را می‌سازیم تا هیچ وضعیت قدیمی در حافظه باقی نماند.
            self.game.load_layout()
            self.build_editor()
            self.status.text = fa("بازنشانی شد؛ اکنون تنظیمات پیش‌فرض هستند ✓")
        except Exception as e:
            print("RESET ERROR:", repr(e))
            if self.status:
                self.status.text = fa("خطا در بازنشانی")


class CreatorsScreen(Screen):

    def on_enter(self):

        self.clear_widgets()

        root = FloatLayout()

        root.add_widget(
            Image(
                source=(
                    MENU_BG
                    if os.path.exists(MENU_BG)
                    else ""
                ),
                allow_stretch=True,
                keep_ratio=False
            )
        )

        box = FloatLayout(
            size_hint=(
                0.68,
                0.62
            ),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.53
            }
        )

        with box.canvas.before:

            Color(
                0.05,
                0.05,
                0.08,
                0.94
            )

            RoundedRectangle(
                pos=box.pos,
                size=box.size,
                radius=[22]
            )

        title = Label(
            text=fa("سازندگان"),
            font_name=GAME_FONT,
            font_size="45sp",
            color=(
                1,
                0.85,
                0.25,
                1
            ),
            size_hint=(
                1,
                0.18
            ),
            pos_hint={
                "top": 0.97
            }
        )

        box.add_widget(
            title
        )

        creator = Label(
            text=fa(
                "طراح و برنامه‌نویس:\n"
                "سیدعلی علوی"
            ),
            font_name=GAME_FONT,
            font_size="30sp",
            color=(
                1,
                1,
                1,
                1
            ),
            size_hint=(
                1,
                0.28
            ),
            pos_hint={
                "center_y": 0.62
            },
            halign="center",
            valign="middle"
        )

        box.add_widget(
            creator
        )

        company = Label(
            text=fa(
                "شرکت: ALVION"
            ),
            font_name=GAME_FONT,
            font_size="28sp",
            color=(
                1,
                0.85,
                0.3,
                1
            ),
            size_hint=(
                1,
                0.16
            ),
            pos_hint={
                "center_y": 0.38
            },
            halign="center"
        )

        box.add_widget(
            company
        )

        ai = Label(
            text=fa(
                "دستیار هوش مصنوعی:\n"
                "Qwen"
            ),
            font_name=GAME_FONT,
            font_size="22sp",
            color=(
                0.8,
                0.9,
                1,
                1
            ),
            size_hint=(
                1,
                0.20
            ),
            pos_hint={
                "center_y": 0.19
            },
            halign="center"
        )

        box.add_widget(
            ai
        )

        root.add_widget(
            box
        )

        back = GameButton(
            text=fa("بازگشت"),
            font_size="25sp",
            size_hint=(
                0.25,
                0.08
            ),
            pos_hint={
                "center_x": 0.5,
                "y": 0.025
            }
        )

        back.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "main"
            )
        )

        root.add_widget(
            back
        )

        self.add_widget(
            root
        )


# =========================================================
# بازی
# =========================================================

class GameScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.current_level = 1

        self.money = 0

        self.customers = []
        self.current_customer = None

        self.customers_served = 0
        self.customer_spawn_index = 0
        self.prepare_customer_images()
        self.customers_total = 0

        self.level_time = 0

        self.game_active = False

        self.game_timer = None
        self.spawn_event = None

        self.customer_move_events = {}

        # صف تصاویر مشتری‌ها؛ تا وقتی ۵ چهره داریم، تکرار پشت‌سرهم رخ نمی‌دهد.
        self.customer_image_pool = []

        self.start_button_visible = True

        self.selected_products = []

        self.dragging = False
        self.drag_offset = (
            0,
            0
        )

        self.multi_selecting = False
        self.select_box_start = None
        self.select_box = None
        self.select_box_line = None

        # -------------------------------
        # Touch / Gesture state
        # -------------------------------
        self._active_touches = {}
        self._pinch_start_distance = None
        self._pinch_start_scales = {}
        self._touch_drag_last = None

        root = FloatLayout()

        self.root_layout = root

        # -----------------------------------------
        # بک گراند بازی
        # -----------------------------------------

        if os.path.exists(GAME_BG):

            background = Image(
                source=GAME_BG,
                allow_stretch=True,
                keep_ratio=False,
                size_hint=(1, 1)
            )

        else:

            background = FloatLayout(
                size_hint=(1, 1)
            )

            with background.canvas:

                Color(
                    0.18,
                    0.12,
                    0.08,
                    1
                )

                background_rect = RoundedRectangle(
                    pos=(0, 0),
                    size=Window.size
                )

            background.bind(
                pos=lambda obj, value:
                setattr(
                    background_rect,
                    "pos",
                    value
                ),
                size=lambda obj, value:
                setattr(
                    background_rect,
                    "size",
                    value
                )
            )

        root.add_widget(
            background
        )

        # -----------------------------------------
        # HUD
        # -----------------------------------------

        self.level_label = self.make_hud(
            "مرحله: ۱",
            "30sp",
            (
                1,
                0.9,
                0.3,
                1
            ),
            {
                "x": 0.01,
                "top": 0.98
            }
        )

        root.add_widget(
            self.level_label
        )

        self.time_label = self.make_hud(
            "زمان: --",
            "30sp",
            (
                1,
                1,
                1,
                1
            ),
            {
                "center_x": 0.34,
                "top": 0.98
            }
        )

        root.add_widget(
            self.time_label
        )

        self.customer_label = self.make_hud(
            "مشتری: /",
            "30sp",
            (
                0.8,
                1,
                0.8,
                1
            ),
            {
                "center_x": 0.53,
                "top": 0.98
            }
        )

        root.add_widget(
            self.customer_label
        )

        self.money_label = self.make_hud(
            "سکه: ۰",
            "30sp",
            (
                1,
                0.85,
                0.2,
                1
            ),
            {
                "right": 0.16,
                "top": 0.98
            }
        )

        root.add_widget(
            self.money_label
        )

        self.register_label = self.make_hud(
            "صندوق: ۰",
            "24sp",
            (
                0.2,
                1,
                0.35,
                1
            ),
            {
                "right": 0.02,
                "top": 0.98
            }
        )

        root.add_widget(
            self.register_label
        )

        # -----------------------------------------
        # محصولات دکه
        # -----------------------------------------

        self.create_slot(
            "SHIPAPA.png",
            (
                0.195,
                0.285
            ),
            (
                170,
                135
            ),
            5,
            2
        )

        self.create_slot(
            "PICMAZE.png",
            (
                0.335,
                0.285
            ),
            (
                170,
                135
            ),
            4,
            2
        )

        self.create_slot(
            "TACBERAC.png",
            (
                0.475,
                0.285
            ),
            (
                175,
                135
            ),
            5,
            2
        )

        self.create_slot(
            "ALAVIPOOR.png",
            (
                0.620,
                0.285
            ),
            (
                175,
                135
            ),
            5,
            2
        )

        self.create_slot(
            "MORTEZA.png",
            (
                0.205,
                0.095
            ),
            (
                170,
                135
            ),
            6,
            2
        )

        self.create_slot(
            "BABRI.png",
            (
                0.345,
                0.095
            ),
            (
                175,
                135
            ),
            8,
            2
        )

        self.create_slot(
            "WATER (1).png",
            (
                0.485,
                0.095
            ),
            (
                175,
                135
            ),
            6,
            2
        )

        self.create_slot(
            "KOACA.png",
            (
                0.025,
                0.505
            ),
            (
                120,
                90
            ),
            5,
            2
        )

        self.create_slot(
            "DIXFAX.png",
            (
                0.025,
                0.345
            ),
            (
                120,
                90
            ),
            4,
            2
        )

        # -----------------------------------------
        # پنل سایز
        # -----------------------------------------

        self.scale_panel = FloatLayout(
            size_hint=(
                None,
                None
            ),
            size=(
                220,
                50
            ),
            pos_hint={
                "right": 0.98,
                "top": 0.88
            },
            opacity=0
        )

        with self.scale_panel.canvas.before:

            Color(
                0,
                0,
                0,
                0.75
            )

            RoundedRectangle(
                pos=self.scale_panel.pos,
                size=self.scale_panel.size,
                radius=[10]
            )

        self.scale_label = Label(
            text=fa("سایز:"),
            font_name=GAME_FONT,
            font_size="18sp",
            size_hint=(
                None,
                None
            ),
            size=(
                50,
                30
            ),
            pos_hint={
                "x": 0.05,
                "center_y": 0.5
            }
        )

        self.scale_panel.add_widget(
            self.scale_label
        )

        from kivy.uix.textinput import TextInput

        self.scale_input = TextInput(
            text="1.00",
            font_name=GAME_FONT,
            font_size="18sp",
            multiline=False,
            input_filter="float",
            size_hint=(
                None,
                None
            ),
            size=(
                80,
                30
            ),
            pos_hint={
                "center_x": 0.45,
                "center_y": 0.5
            },
            background_color=(
                0.2,
                0.2,
                0.2,
                1
            ),
            foreground_color=(
                1,
                1,
                1,
                1
            )
        )

        self.scale_input.bind(
            on_text_validate=
            self.apply_scale_from_input
        )

        self.scale_panel.add_widget(
            self.scale_input
        )

        apply_button = GameButton(
            text=fa("اعمال"),
            font_size="16sp",
            size_hint=(
                None,
                None
            ),
            size=(
                60,
                30
            ),
            pos_hint={
                "right": 0.95,
                "center_y": 0.5
            }
        )

        apply_button.bind(
            on_release=
            self.apply_scale_from_input
        )

        self.scale_panel.add_widget(
            apply_button
        )

        root.add_widget(
            self.scale_panel
        )

        # -----------------------------------------
        # وضعیت ذخیره
        # -----------------------------------------

        self.save_status_label = Label(
            text="",
            font_name=GAME_FONT,
            font_size="16sp",
            color=(
                0.5,
                1,
                0.5,
                1
            ),
            size_hint=(
                None,
                None
            ),
            size=(
                180,
                30
            ),
            pos_hint={
                "right": 0.98,
                "top": 0.83
            }
        )

        root.add_widget(
            self.save_status_label
        )

        # -----------------------------------------
        # دکمه شروع
        # -----------------------------------------

        self.start_btn = GameButton(
            text=fa("شروع مرحله"),
            font_size="34sp",
            size_hint=(
                None,
                None
            ),
            size=(
                280,
                70
            ),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.50
            }
        )

        self.start_btn.bind(
            on_release=self.start_level
        )

        root.add_widget(
            self.start_btn
        )

        self.add_widget(
            root
        )

        # لمس
        self.bind(
            on_touch_down=self.handle_touch_down
        )

        self.bind(
            on_touch_move=self.handle_touch_move
        )

        self.bind(
            on_touch_up=self.handle_touch_up
        )

        Clock.schedule_once(
            lambda dt:
            self.load_layout(),
            0.5
        )

    # =====================================================
    # HUD
    # =====================================================

    def make_hud(
        self,
        text,
        font_size,
        color,
        pos_hint
    ):

        label = Label(
            text=fa(text),
            font_name=GAME_FONT,
            font_size=font_size,
            color=color,
            size_hint=(
                None,
                None
            ),
            size=(
                190,
                50
            ),
            pos_hint=pos_hint
        )

        with label.canvas.before:

            Color(
                0,
                0,
                0,
                0.45
            )

            RoundedRectangle(
                pos=label.pos,
                size=label.size,
                radius=[10]
            )

        return label

    # =====================================================
    # ورود به صفحه
    # =====================================================

    def on_enter(self):

        self.load_layout()
        self.reset_for_new_level()

    def on_leave(self):

        self.stop_level()
        self._active_touches.clear()
        self.dragging = False
        self._pinch_start_distance = None
        self._pinch_start_scales = {}

    # =====================================================
    # شروع / توقف مرحله
    # =====================================================

    def reset_for_new_level(self):

        self.stop_level()

        self.game_active = False

        self.start_button_visible = True

        self.start_btn.opacity = 1
        self.start_btn.disabled = False

        info = LEVEL_DATA.get(
            self.current_level,
            LEVEL_DATA[1]
        )

        self.customers_total = info["count"]
        self.level_time = info["time"]

        self.customers_served = 0
        self.customer_spawn_index = 0

        self.money = 0

        self.level_label.text = fa(
            f"مرحله: {self.current_level}"
        )

        self.time_label.text = fa(
            "زمان: --"
        )

        self.customer_label.text = fa(
            f"مشتری: 0/{self.customers_total}"
        )

        self.money_label.text = fa(
            "سکه: ۰"
        )

        self.register_label.text = fa(
            "صندوق: ۰"
        )

    def start_level(self, button=None):

        if self.game_active:
            return

        self.start_button_visible = False

        self.start_btn.opacity = 0
        self.start_btn.disabled = True

        self.game_active = True

        self.deselect_all()

        self.time_label.text = fa(
            f"زمان: {self.level_time}"
        )

        # -----------------------------------------
        # تایمر بازی
        # -----------------------------------------

        if self.game_timer:

            try:
                self.game_timer.cancel()
            except Exception:
                pass

        self.game_timer = Clock.schedule_interval(
            self.update_game,
            1
        )

        # -----------------------------------------
        # مشتری اول
        # -----------------------------------------

        if self.spawn_event:

            try:
                self.spawn_event.cancel()
            except Exception:
                pass

        self.spawn_event = Clock.schedule_once(
            lambda dt:
            self.spawn_customer(),
            1.0
        )

        sound_mgr.play_click()

    def stop_level(self):

        self.game_active = False

        if self.game_timer:

            try:
                self.game_timer.cancel()
            except Exception:
                pass

            self.game_timer = None

        if self.spawn_event:

            try:
                self.spawn_event.cancel()
            except Exception:
                pass

            self.spawn_event = None

        # لغو حرکت مشتری‌ها

        for event in list(
            self.customer_move_events.values()
        ):

            try:
                event.cancel()
            except Exception:
                pass

        self.customer_move_events.clear()

        # حذف مشتری‌ها

        for customer in self.customers[:]:

            if customer.parent:

                try:
                    customer.parent.remove_widget(
                        customer
                    )
                except Exception:
                    pass

        self.customers = []

        self.current_customer = None

    # =====================================================
    # تایمر بازی
    # =====================================================

    def update_game(self, dt):

        if not self.game_active:
            return

        self.level_time -= 1

        self.time_label.text = fa(
            f"زمان: {max(0, self.level_time)}"
        )

        if self.current_customer:

            angry = (
                self.current_customer
                .update_patience()
            )

            if angry:

                self.customer_leave_angry()

        if self.level_time <= 0:

            self.end_level()

    def _customer_images(self):
        if not os.path.exists(CUST_DIR):
            return []
        try:
            return sorted(
                f for f in os.listdir(CUST_DIR)
                if f.lower().endswith(".png")
            )
        except Exception:
            return []

    def prepare_customer_images(self):
        images = self._customer_images()
        self.customer_image_pool = images[:]
        random.shuffle(self.customer_image_pool)

    def get_customer_image(self, index):
        # برای ادیتور: هر شماره مشتری یک تصویر متفاوت می‌گیرد.
        images = self._customer_images()
        if not images:
            return ""
        return images[index % len(images)]

    def next_customer_image(self):
        if not self.customer_image_pool:
            self.prepare_customer_images()
        return self.customer_image_pool.pop(0) if self.customer_image_pool else ""

    def get_customer_config(self, index):
        cfg = dict(CUSTOMER_DEFAULT_LAYOUT[index % len(CUSTOMER_DEFAULT_LAYOUT)])
        if not os.path.exists(CUSTOMER_LAYOUT_FILE):
            return cfg
        try:
            with open(CUSTOMER_LAYOUT_FILE, "r", encoding="utf8") as f:
                data = json.load(f)
            saved = data.get("customers", [])
            if saved:
                item = saved[index % len(saved)]
                for k in ("x", "y", "w", "h"):
                    if k in item:
                        cfg[k] = float(item[k])
        except (OSError, ValueError, TypeError, KeyError) as e:
            print("CUSTOMER LAYOUT LOAD ERROR:", e)
        return cfg

    # =====================================================
    # ایجاد مشتری
    # =====================================================

    def spawn_customer(self):

        if not self.game_active:
            return

        if self.current_customer:
            return

        if self.customers_served >= self.customers_total:
            return

        layout_index = self.customer_spawn_index % len(CUSTOMER_DEFAULT_LAYOUT)
        customer = Customer(
            self,
            self.customer_spawn_index,
            image_filename=self.next_customer_image(),
            layout_index=layout_index
        )
        self.customer_spawn_index += 1

        self.root_layout.add_widget(
            customer
        )

        self.customers.append(
            customer
        )

        self.current_customer = customer

        # انیمیشن ورود
        def move_customer(dt):

            if not self.game_active:
                return False

            if not customer.parent:
                return False

            if customer.y < customer.target_pos[1]:

                customer.y += 12

                return True

            customer.y = customer.target_pos[1]

            return False

        event = Clock.schedule_interval(
            move_customer,
            1 / 60
        )

        self.customer_move_events[
            customer
        ] = event

    # =====================================================
    # تحویل محصول
    # =====================================================

    def serve_customer(
        self,
        product_filename
    ):

        customer = self.current_customer

        if not customer:
            return False

        if (
            product_filename
            not in customer.requests
        ):
            return False

        if (
            product_filename
            in customer.fulfilled
        ):
            return False

        # پیدا کردن محصول
        product = None

        for child in self.root_layout.children:

            if (
                isinstance(
                    child,
                    ProductItem
                )
                and child.filename ==
                product_filename
            ):

                product = child
                break

        if not product:
            return False

        # حذف محصول از قفسه

        if product.slot_ref:

            product.slot_ref.remove_item(
                product
            )

        customer.fulfilled.append(
            product_filename
        )

        sound_mgr.play_click()

        remaining = [
            PRODUCT_DATA[x]["name"]
            for x in customer.requests
            if x not in customer.fulfilled
        ]

        if remaining:

            customer.lbl_req.text = fa(
                "درخواست: " + "، ".join(remaining)
            )

        else:

            customer.lbl_req.text = fa(
                "تکمیل شد!"
            )

        if len(
            customer.fulfilled
        ) >= len(
            customer.requests
        ):

            self.customer_leave_happy()

        return True

    # =====================================================
    # مشتری راضی
    # =====================================================

    def customer_leave_happy(self):

        customer = self.current_customer

        if not customer:
            return

        earned = sum(
            PRODUCT_DATA[x]["price"]
            for x in customer.fulfilled
        )

        tip = int(
            earned *
            (
                customer.patience /
                100
            ) *
            0.3
        )

        total = earned + tip

        self.money += total

        self.customers_served += 1

        self.money_label.text = fa(
            f"سکه: {self.money:,}"
        )

        self.register_label.text = fa(
            f"صندوق: {total:,}"
        )

        self.customer_label.text = fa(
            f"مشتری: "
            f"{self.customers_served}/"
            f"{self.customers_total}"
        )

        self.remove_current_customer()

        if (
            self.customers_served
            >= self.customers_total
        ):

            Clock.schedule_once(
                lambda dt:
                self.end_level(),
                0.7
            )

        else:

            Clock.schedule_once(
                lambda dt:
                self.spawn_customer(),
                1.0
            )

    # =====================================================
    # مشتری عصبانی
    # =====================================================

    def customer_leave_angry(self):

        if not self.current_customer:
            return

        self.remove_current_customer()

        if (
            self.customers_served
            < self.customers_total
            and self.game_active
        ):

            Clock.schedule_once(
                lambda dt:
                self.spawn_customer(),
                0.8
            )

    # =====================================================
    # حذف مشتری
    # =====================================================

    def remove_current_customer(self):

        customer = (
            self.current_customer
        )

        if not customer:
            return

        event = self.customer_move_events.pop(
            customer,
            None
        )

        if event:

            try:
                event.cancel()
            except Exception:
                pass

        if customer.parent:

            try:
                customer.parent.remove_widget(
                    customer
                )
            except Exception:
                pass

        if customer in self.customers:

            self.customers.remove(
                customer
            )

        self.current_customer = None

    # =====================================================
    # پایان مرحله
    # =====================================================

    def end_level(self):

        if not self.game_active:
            return

        self.game_active = False

        if self.game_timer:

            try:
                self.game_timer.cancel()
            except Exception:
                pass

            self.game_timer = None

        ratio = (
            self.customers_served /
            self.customers_total
            if self.customers_total
            else 0
        )

        if ratio >= 0.90:
            stars = 3

        elif ratio >= 0.60:
            stars = 2

        elif ratio >= 0.30:
            stars = 1

        else:
            stars = 0

        # ذخیره ستاره

        progress.set_stars(
            self.current_level,
            stars
        )

        # درآمد مرحله

        progress.add_coins(
            self.money
        )

        content = FloatLayout()

        with content.canvas.before:

            Color(
                0.08,
                0.08,
                0.13,
                0.98
            )

            RoundedRectangle(
                pos=content.pos,
                size=content.size,
                radius=[20]
            )

        title = Label(
            text=fa(
                "پایان مرحله!"
            ),
            font_name=GAME_FONT,
            font_size="34sp",
            color=(
                1,
                0.9,
                0.3,
                1
            ),
            size_hint=(
                1,
                0.2
            ),
            pos_hint={
                "top": 1
            }
        )

        content.add_widget(
            title
        )

        stats = Label(
            text=fa(
                f"مشتریان: "
                f"{self.customers_served}/"
                f"{self.customers_total}\n"
                f"درآمد: "
                f"{self.money:,} سکه\n"
                f"ستاره‌ها: "
                f"{'★' * stars}"
                f"{'☆' * (3 - stars)}"
            ),
            font_name=GAME_FONT,
            font_size="23sp",
            color=(
                1,
                1,
                1,
                1
            ),
            size_hint=(
                0.9,
                0.48
            ),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.58
            },
            halign="center",
            valign="middle"
        )

        content.add_widget(
            stats
        )

        next_button = GameButton(
            text=fa("ادامه"),
            font_size="24sp",
            size_hint=(
                0.4,
                0.16
            ),
            pos_hint={
                "center_x": 0.5,
                "y": 0.08
            }
        )

        popup = Popup(
            title="",
            content=content,
            size_hint=(
                None,
                None
            ),
            size=(
                520,
                330
            ),
            auto_dismiss=False
        )

        next_button.bind(
            on_release=lambda x:
            self.close_result_popup(
                popup
            )
        )

        content.add_widget(
            next_button
        )

        popup.open()

    def close_result_popup(self, popup):

        try:
            popup.dismiss()
        except Exception:
            pass

        if self.current_level < 10:

            self.current_level += 1

        self.manager.current = "levels"

    # =====================================================
    # ایجاد اسلات
    # =====================================================

    def create_slot(
        self,
        filename,
        position,
        size,
        columns,
        rows
    ):

        if filename not in PRODUCT_DATA:
            return

        path = os.path.join(
            PROD_DIR,
            filename
        )

        if not os.path.exists(path):

            print(
                "PRODUCT NOT FOUND:",
                path
            )

            return

        ProductSlot(
            filename,
            PRODUCT_DATA[filename]["max"],
            PRODUCT_DATA[filename],
            self,
            position,
            size,
            columns,
            rows
        )

    # =====================================================
    # پیدا کردن محصول
    # =====================================================

    def find_product_at(self, pos):

        for child in reversed(
            self.root_layout.children
        ):

            if (
                isinstance(
                    child,
                    ProductItem
                )
                and child.collide_point(
                    *pos
                )
            ):

                return child

        return None

    # =====================================================
    # انتخاب
    # =====================================================

    def deselect_all(self):

        for product in self.selected_products:

            product.deselect()

        self.selected_products = []

        self.scale_panel.opacity = 0

    # =====================================================
    # لمس
    # =====================================================

    def _is_mouse_event(self, touch):
        return bool(getattr(touch, "is_mouse", False))

    @staticmethod
    def _touch_distance(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    def _toggle_product_selection(self, product):
        if product in self.selected_products:
            product.deselect()
            self.selected_products.remove(product)
        else:
            product.is_selected = True
            product.add_highlight()
            self.selected_products.append(product)
        self.update_scale_panel()

    # =====================================================
    # ورودی یکپارچه Mouse + Touch
    # =====================================================

    def handle_touch_down(self, instance, touch):
        is_mouse = self._is_mouse_event(touch)

        # در Android touch.button وجود ندارد؛ فقط کلیک‌های غیرچپ موس
        # را رد می‌کنیم تا عملکرد Windows کاملاً حفظ شود.
        if self.game_active:
            if is_mouse and touch.button != "left":
                return False

            product = self.find_product_at(touch.pos)
            if product:
                self.serve_customer(product.filename)
                return True
            return False

        # زوم با wheel فقط برای موس
        if touch.is_mouse_scrolling:
            if self.selected_products:
                direction = 1 if touch.button == "scrollup" else -1
                for product in self.selected_products:
                    product.resize(direction)
                self.update_scale_panel()
                return True
            return False

        # Touchهای فعال را ثبت می‌کنیم.
        self._active_touches[touch.uid] = (touch.x, touch.y)

        product = self.find_product_at(touch.pos)

        # -------------------------------
        # Android: لمس دوم برای انتخاب چندتایی
        # -------------------------------
        if not is_mouse and len(self._active_touches) >= 2:
            if product is not None:
                # اگر روی همان محصول لمس دوم باشد، برای pinch نگه می‌داریم.
                if product in self.selected_products and len(self.selected_products) == 1:
                    pts = list(self._active_touches.values())
                    self._pinch_start_distance = self._touch_distance(pts[0], pts[1])
                    self._pinch_start_scales = {p: p.scale for p in self.selected_products}
                    self.dragging = False
                else:
                    # لمس دوم روی محصول دیگر = اضافه/حذف از انتخاب چندتایی
                    self._toggle_product_selection(product)
                return True
            return True

        # -------------------------------
        # انتخاب و Drag
        # -------------------------------
        if product:
            if is_mouse:
                # رفتار قبلی Windows: کلیک چپ محصول را انتخاب و Drag می‌کند.
                if product not in self.selected_products:
                    self.deselect_all()
                    product.is_selected = True
                    self.selected_products.append(product)
                    product.add_highlight()
            else:
                # Touch اول: اگر چیزی انتخاب نشده انتخاب کن؛ اگر انتخاب شده
                # همان گروه را نگه دار تا بتوان چند کالا را جابه‌جا کرد.
                if product not in self.selected_products:
                    self.deselect_all()
                    product.is_selected = True
                    self.selected_products.append(product)
                    product.add_highlight()

            self.dragging = True
            self.drag_offset = (
                touch.pos[0] - product.x,
                touch.pos[1] - product.y
            )
            self._touch_drag_last = touch.pos
            self.update_scale_panel()
            return True

        # -------------------------------
        # Windows: راست‌کلیک = selection box
        # Android: لمس خالی چیزی را انتخاب نمی‌کند
        # -------------------------------
        if is_mouse and touch.button == "right":
            self.multi_selecting = True
            self.select_box_start = touch.pos
            self.create_selection_box(touch.pos)
            return True

        if is_mouse:
            self.deselect_all()
        return False

    # =====================================================
    # حرکت موس
    # =====================================================

    def handle_touch_move(self, instance, touch):
        if touch.uid in self._active_touches:
            self._active_touches[touch.uid] = (touch.x, touch.y)

        if self.game_active:
            return False

        # -------------------------------
        # Pinch: دو انگشت = بزرگ/کوچک
        # -------------------------------
        if len(self._active_touches) >= 2 and self.selected_products:
            pts = list(self._active_touches.values())
            current_distance = self._touch_distance(pts[0], pts[1])

            if self._pinch_start_distance is None and current_distance > 1:
                self._pinch_start_distance = current_distance
                self._pinch_start_scales = {p: p.scale for p in self.selected_products}

            if self._pinch_start_distance and self._pinch_start_distance > 1:
                factor = current_distance / self._pinch_start_distance
                for product in self.selected_products:
                    start_scale = self._pinch_start_scales.get(product, product.scale)
                    product.set_scale(start_scale * factor)
                self.update_scale_panel()
                return True

        # -------------------------------
        # Drag یک انگشتی
        # -------------------------------
        if self.dragging and self.selected_products:
            first = self.selected_products[0]

            nx = touch.pos[0] - self.drag_offset[0]
            ny = touch.pos[1] - self.drag_offset[1]

            dx = nx - first.x
            dy = ny - first.y

            first.pos = (nx, ny)
            first.update_highlight()

            for product in self.selected_products[1:]:
                product.pos = (product.x + dx, product.y + dy)
                product.update_highlight()

            self._touch_drag_last = touch.pos
            return True

        if self.multi_selecting:
            self.update_selection_box(touch.pos)
            return True

        return False

    # =====================================================
    # رها کردن
    # =====================================================

    def handle_touch_up(self, instance, touch):
        self._active_touches.pop(touch.uid, None)

        if len(self._active_touches) < 2:
            self._pinch_start_distance = None
            self._pinch_start_scales = {}

        if self.game_active:
            return False

        if self.dragging:
            # وقتی آخرین انگشت/دکمه رها شد ذخیره می‌کنیم.
            if not self._active_touches:
                self.dragging = False
                self.save_layout()
            return True

        if self.multi_selecting:
            self.multi_selecting = False
            self.finish_selection()
            return True

        return False

    # =====================================================
    # انتخاب چندتایی
    # =====================================================

    def create_selection_box(
        self,
        start_pos
    ):

        with self.root_layout.canvas.after:

            Color(
                0.3,
                0.6,
                1,
                0.25
            )

            self.select_box = RoundedRectangle(
                pos=start_pos,
                size=(
                    0,
                    0
                ),
                radius=[5]
            )

            Color(
                0.3,
                0.6,
                1,
                0.8
            )

            self.select_box_line = Line(
                rectangle=(
                    start_pos[0],
                    start_pos[1],
                    0,
                    0
                ),
                width=2
            )

    def update_selection_box(
        self,
        current_pos
    ):

        if (
            not self.select_box
            or not self.select_box_start
        ):
            return

        x1, y1 = (
            self.select_box_start
        )

        x2, y2 = current_pos

        x = min(
            x1,
            x2
        )

        y = min(
            y1,
            y2
        )

        w = abs(
            x2 - x1
        )

        h = abs(
            y2 - y1
        )

        self.select_box.pos = (
            x,
            y
        )

        self.select_box.size = (
            w,
            h
        )

        self.select_box_line.rectangle = (
            x,
            y,
            w,
            h
        )

        for child in self.root_layout.children:

            if not isinstance(
                child,
                ProductItem
            ):
                continue

            cx = (
                child.x +
                child.width / 2
            )

            cy = (
                child.y +
                child.height / 2
            )

            inside = (
                x <= cx <= x + w
                and
                y <= cy <= y + h
            )

            if inside:

                if child not in self.selected_products:

                    child.is_selected = True

                    child.add_highlight()

                    self.selected_products.append(
                        child
                    )

    def finish_selection(self):

        if self.select_box:

            try:
                self.root_layout.canvas.after.remove(
                    self.select_box
                )
            except Exception:
                pass

            self.select_box = None

        if self.select_box_line:

            try:
                self.root_layout.canvas.after.remove(
                    self.select_box_line
                )
            except Exception:
                pass

            self.select_box_line = None

        self.update_scale_panel()

    # =====================================================
    # سایز
    # =====================================================

    def update_scale_panel(self):

        if not self.selected_products:

            self.scale_panel.opacity = 0

            return

        avg = sum(
            x.scale
            for x in self.selected_products
        ) / len(
            self.selected_products
        )

        self.scale_input.text = (
            f"{avg:.2f}"
        )

        self.scale_panel.opacity = 1

    def apply_scale_from_input(
        self,
        instance
    ):

        if not self.selected_products:
            return

        try:

            scale = float(
                self.scale_input.text
            )

            for product in (
                self.selected_products
            ):

                product.set_scale(
                    scale
                )

            self.scale_input.text = (
                f"{scale:.2f}"
            )

        except Exception:
            pass

    # =====================================================
    # ذخیره چیدمان
    # =====================================================

    def save_layout(self):

        data = []

        for child in self.root_layout.children:

            if isinstance(
                child,
                ProductItem
            ):

                data.append({
                    "filename":
                    child.filename,

                    "pos": [
                        child.x,
                        child.y
                    ],

                    "scale":
                    child.scale
                })

        try:

            with open(
                LAYOUT_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    {
                        "products": data
                    },
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            self.save_status_label.text = (
                fa("ذخیره شد")
            )

            Clock.schedule_once(
                lambda dt:
                setattr(
                    self.save_status_label,
                    "text",
                    ""
                ),
                1.5
            )

        except Exception as e:

            print(
                "SAVE ERROR:",
                e
            )

    # =====================================================
    # بارگذاری چیدمان
    # =====================================================

    def load_layout(self):

        if not os.path.exists(
            LAYOUT_FILE
        ):
            return

        try:

            with open(
                LAYOUT_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            products = data.get(
                "products",
                []
            )

            available = {}

            for child in self.root_layout.children:

                if isinstance(
                    child,
                    ProductItem
                ):

                    available.setdefault(
                        child.filename,
                        []
                    ).append(
                        child
                    )

            count = 0

            for saved in products:

                filename = saved.get(
                    "filename"
                )

                if (
                    filename not in available
                    or
                    not available[filename]
                ):
                    continue

                product = available[
                    filename
                ].pop(0)

                position = saved.get(
                    "pos",
                    [
                        product.x,
                        product.y
                    ]
                )

                scale = saved.get(
                    "scale",
                    1.0
                )

                product.pos = (
                    float(position[0]),
                    float(position[1])
                )

                product.set_scale(
                    float(scale)
                )

                count += 1

            self.save_status_label.text = fa(
                f"بارگذاری شد ({count})"
            )

            Clock.schedule_once(
                lambda dt:
                setattr(
                    self.save_status_label,
                    "text",
                    ""
                ),
                2
            )

        except Exception as e:

            print(
                "LOAD ERROR:",
                e
            )


# =========================================================
# اپلیکیشن
# =========================================================

class DokehDarApp(App):

    def build(self):

        self.title = "دکه دار"

        manager = ScreenManager()

        manager.add_widget(
            MainMenu(
                name="main"
            )
        )

        manager.add_widget(
            LevelsScreen(
                name="levels"
            )
        )

        manager.add_widget(
            GameScreen(
                name="game"
            )
        )

        manager.add_widget(
            ShopScreen(
                name="shop"
            )
        )

        manager.add_widget(
            SettingsScreen(
                name="settings"
            )
        )

        manager.add_widget(
            GameplayEditorScreen(
                name="gameplay_editor"
            )
        )

        manager.add_widget(
            CreatorsScreen(
                name="creators"
            )
        )

        return manager


# =========================================================
# اجرا
# =========================================================

if __name__ == "__main__":

    try:

        DokehDarApp().run()

    except Exception as error:

        print()
        print("=" * 60)
        print("GAME ERROR")
        print("=" * 60)
        print(error)
        print("=" * 60)
