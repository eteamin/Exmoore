from functools import partial

from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.network.urlrequest import UrlRequest

screen_manager = ScreenManager(transition=FadeTransition())
progress_bar = ProgressBar()


class MainScreen(Screen):
    def __init__(self):
        super(MainScreen, self).__init__()

        self.url_input = TextInput(pos_hint={'center_y': 0.5}, size_hint=(None, None), size=(1000, 50))
        self.start = Button(text='Start', size_hint=(None, None), size=(100, 50))

        self.start.bind(on_release=partial(self.on_start_press))

        self.add_widget(self.url_input)
        self.add_widget(self.start)
        UrlRequest('http://pushyab.com/css/style.css', on_success=self.on_start_press)

    def on_start_press(self, *args):
        """Get the headers to know the content-length"""
        pass


class Exmoore(App):
    def build(self):
        screen_manager.add_widget(MainScreen())
        return screen_manager


if __name__ == '__main__':
    Exmoore().run()
