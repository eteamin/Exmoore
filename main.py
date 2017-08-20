from functools import partial
from queue import Queue, Empty as QueueEmpty

from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
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
            Color(1, 0.1, 1, 0.1)
            self.rect = Rectangle(size=(Window.width, Window.height), pos=self.pos)

        self.url_input = TextInput(pos_hint={'center_y': 0.5}, size_hint=(None, None), size=(1000, 50))
        self.start = Button(text='Start', size_hint=(None, None), size=(100, 50))
        self.report_queue = Queue()

        self.start.bind(on_release=partial(self.on_start_press))

        self.add_widget(self.url_input)
        self.add_widget(self.start)

    def on_start_press(self, *args):
        DownloadTask(self.url_input.text, 2, self.report_queue)
        self.add_widget(progress_bar)
    #     Clock.schedule_interval(self.update_progress_bar, 0.5)
    #
    # def update_progress_bar(self, *args):
    #     try:
    #         total = self.report_queue.get()
    #     except QueueEmpty:
    #         total = 0
    #     progress_bar.value = total


class Exmoore(App):
    def build(self):
        screen_manager.add_widget(MainScreen())
        return screen_manager


if __name__ == '__main__':
    Exmoore().run()
