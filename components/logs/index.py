from kivy.uix.boxlayout import BoxLayout

from helpers import load_kv_file_for_class

load_kv_file_for_class("index.kv")

class LogsUI(BoxLayout):
    """LogsUI class is a BoxLayout that displays the logs page 
    of the application."""
