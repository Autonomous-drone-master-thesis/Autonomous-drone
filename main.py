from kivy.app import App
from kivy.uix.label import Label


class HelloWorldApp(App):
    """
    A Kivy application that displays "Hello, World!" in a Label widget.
    """
    def build(self) -> Label:
        return Label(text="Hello, World!")


if __name__ == "__main__":
    HelloWorldApp().run()
