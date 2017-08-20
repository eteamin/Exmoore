import os
from functools import partial
from queue import Queue, Empty as QueueEmpty

from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.clock import Clock
from kivy.core.window import Window

from models.task import DownloadTask


def touch_move(instance, touch):
    instance.center = touch.pos


class Settings:
    pass


settings = Settings()
settings.threads = 2
settings.download_path = os.path.join(os.environ['HOME'], 'Downloads')
screen_manager = ScreenManager(transition=FadeTransition())
progress_bar = ProgressBar(max=0)


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
        self.task = DownloadTask(
            url=self.url_input.text,
            threads=settings.threads,
            download_report=self.report_queue,
            download_path=settings.download_path
        )
        self.add_widget(progress_bar)
        self.event = Clock.schedule_interval(self.update_progress_bar, 1)

    def update_progress_bar(self, *args):
        try:
            downloaded, total = self.report_queue.get(block=False)
        except QueueEmpty:
            return
        if not progress_bar.max:
            progress_bar.max = total
        progress_bar.value = downloaded
        if downloaded == total:
            Clock.unschedule(self.event)


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

        self.choose_downloads_location = Button(
            text='Choose Location',
            size_hint=(None, None),
            size=(150, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            background_normal='',
            background_color=(0, 0.9, 0.3, 0.8),
            opacity=0.9
        )
        self.return_to_main = Button(
            text='Return',
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={'center_x': 0.1, 'center_y': 0.1},
            background_normal='',
            background_color=(0.3, 0.6, 0.8, 0.8),
            opacity=0.9
        )
        self.return_to_main.bind(on_release=partial(switch_to, MainScreen))
        self.current_location = Label(
            text=settings.download_path,
            font_size=dp(22),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
        )

        self.file_chooser = FileChooserListView()
        self.file_chooser.dirselect = True

        self.submit_dir_selection = Button(
            text='Select',
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={'center_x': 0.9, 'center_y': 0.9},
            background_normal='',
            background_color=(0.3, 0.6, 0.8, 0.8),
            opacity=0.9
        )
        self.submit_dir_selection.bind(on_release=partial(self.on_location_submit))
        self.choose_downloads_location.bind(on_release=partial(self.on_location_clicked))

        self.thread_show_button = Button(text='Threads', size_hint=(None, None), pos=(300, 200))
        self.thread_show_button.bind(on_release=self.show_drop_down, on_touch_move=touch_move)

        self.add_widget(self.exmoore)
        self.add_widget(self.choose_downloads_location)
        self.add_widget(self.current_location)
        self.add_widget(self.return_to_main)
        self.add_widget(self.thread_show_button)

    def show_drop_down(self, button, *largs):
        self.threads_selection = DropDown(
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.1},
        )
        self.add_widget(self.threads_selection)
        self.threads_selection.bind(on_select=lambda instance, x: setattr(settings, 'threads', int(x)))
        for i in range(1, 5):
            item = Button(text=str(i), size_hint=(None, None), size=(100, 50))
            item.bind(on_release=lambda btn: self.threads_selection.select(btn.text))
            self.threads_selection.add_widget(item)

        self.threads_selection.open(button)

    def on_location_submit(self, *args):
        self.update_location(self.file_chooser.selection[0])
        self.remove_widget(self.file_chooser)
        self.remove_widget(self.submit_dir_selection)
        self.add_widget(self.choose_downloads_location)

    def on_location_clicked(self, *args):
        self.remove_widget(self.choose_downloads_location)
        self.add_widget(self.file_chooser)
        self.add_widget(self.submit_dir_selection)

    def update_location(self, location):
        self.current_location.text = location
        settings.download_path = location


def switch_to(*args):
    screen = args[0]
    screen_manager.switch_to(screen())


class Exmoore(App):
    def build(self):
        screen_manager.add_widget(MainScreen())
        return screen_manager


if __name__ == '__main__':
    Exmoore().run()
