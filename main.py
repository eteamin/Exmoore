from functools import partial
from queue import Queue, Empty as QueueEmpty

from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.clock import Clock
from kivy.core.window import Window

from models.task import DownloadTask


screen_manager = ScreenManager(transition=FadeTransition())
progress_bar = ProgressBar()


class MainScreen(Screen):
    def __init__(self):
        super(MainScreen, self).__init__()
        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 0.3)
            self.rect = Rectangle(size=(Window.width, Window.height), pos=self.pos)

        self.exmoore = Label(
            text='Exmoore',
            font_size=dp(45),
            font_name='statics/Pasajero.otf',
            pos_hint={'center_x': 0.5, 'center_y': 0.95},
        )
        self.beta = Label(
            text='beta',
            font_size=dp(16),
            font_name='statics/Pasajero.otf',
            pos_hint={'center_x': 0.65, 'center_y': 0.93},
        )

        self.url_input = TextInput(
            hint_text='Type in the URL',
            pos_hint={'center_x': 0.5, 'center_y': 0.85},
            size_hint=(None, None),
            size=(Window.width / 1.5, Window.width / 20),
            background_color=(1, 1, 1, 1),
            opacity=0.9
        )
        self.start = Button(
            text='Download',
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            background_normal='',
            background_color=(0, 0.9, 0.3, 0.8),
            opacity=0.9
        )
        self.settings = Button(
            text='Settings',
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={'center_x': 0.1, 'center_y': 0.1},
            background_normal='',
            background_color=(0.3, 0.6, 0.8, 0.8),
            opacity=0.9
        )
        self.settings.bind(on_release=partial(switch_to, SettingsScreen))
        self.report_queue = Queue()

        self.start.bind(on_release=partial(self.on_start_press))

        self.add_widget(self.url_input)
        self.add_widget(self.start)
        self.add_widget(self.settings)
        self.add_widget(self.exmoore)
        self.add_widget(self.beta)

    def on_start_press(self, *args):
        self.task = DownloadTask(self.url_input.text, 2, self.report_queue)
        self.add_widget(progress_bar)
        Clock.schedule_interval(self.update_progress_bar, 0.5)

    def update_progress_bar(self, *args):
        try:
            downloaded, total = self.report_queue.get(timeout=0.1)
        except QueueEmpty:
            return
        if not progress_bar.max:
            progress_bar.max = total
        progress_bar.value = downloaded


class SettingsScreen(Screen):
    def __init__(self):
        super(SettingsScreen, self).__init__()
        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 0.3)
            self.rect = Rectangle(size=(Window.width, Window.height), pos=self.pos)

        self.exmoore = Label(
            text='Exmoore',
            font_size=dp(45),
            font_name='statics/Pasajero.otf',
            pos_hint={'center_x': 0.5, 'center_y': 0.95},
        )

        downloads_location = Button(
            text='Choose Location',
            size_hint=(None, None),
            size=(150, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            background_normal='',
            background_color=(0, 0.9, 0.3, 0.8),
            opacity=0.9
        )
        self.main = Button(
            text='Return',
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={'center_x': 0.1, 'center_y': 0.1},
            background_normal='',
            background_color=(0.3, 0.6, 0.8, 0.8),
            opacity=0.9
        )
        self.main.bind(on_release=partial(switch_to, MainScreen))
        current_location = Label(
            text='',
            font_size=dp(22),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
        )
        self.add_widget(self.exmoore)
        self.add_widget(downloads_location)
        self.add_widget(current_location)
        self.add_widget(self.main)


def switch_to(*args):
    screen = args[0]
    screen_manager.switch_to(screen())


class Exmoore(App):
    def build(self):
        screen_manager.add_widget(MainScreen())
        return screen_manager


if __name__ == '__main__':
    Exmoore().run()
