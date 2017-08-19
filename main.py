from functools import partial
from os import path
from tempfile import mkdtemp

from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.network.urlrequest import UrlRequest

screen_manager = ScreenManager(transition=FadeTransition())


class MainScreen(Screen):
    def __init__(self):
        super(MainScreen, self).__init__()

        self.url_input = TextInput(pos_hint={'center_y': 0.5}, size_hint=(None, None), size=(1000, 50))
        self.start = Button(text='Start', size_hint=(None, None), size=(100, 50))
        """binding start button release"""
        self.start.bind(on_release=partial(self.on_start_press))

        self.add_widget(self.url_input)
        self.add_widget(self.start)

    def on_start_press(self, *args):
        """Get the headers to know the content-length"""
        UrlRequest(url=self.url_input.text, on_success=self.on_head_req_success, method='HEAD')

    def on_head_req_success(self, req, resp):
        """Headers are here!"""
        if resp:
            raise
        content_length = int(req.resp_headers.get('Content-Length'))
        chunks = content_length / 2

    def generate_tmp_storage(self):
        return path.join(mkdtemp(), '1.tmp')








class Exmoore(App):
    def build(self):
        screen_manager.add_widget(MainScreen())
        return screen_manager


if __name__ == '__main__':
    Exmoore().run()
