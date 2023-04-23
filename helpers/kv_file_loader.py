"""Helper functions for loading .kv files for classes."""
import os
import inspect

from kivy.lang import Builder

def load_kv_file_for_class(kv_filename):
    """Load the .kv file for the calling class and given filename."""
    calling_frame = inspect.stack()[1]
    calling_module = inspect.getmodule(calling_frame[0])
    kv_path = os.path.join(os.path.dirname(calling_module.__file__), kv_filename)
    Builder.load_file(kv_path)
