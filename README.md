# AssetManager

Asset manager tool for Maya. Based off of: https://www.youtube.com/watch?v=6fZsXhG86mo

To use, run this in Maya script editor:
from conLibrary import libraryUI
import importlib
importlib.reload(libraryUI)
ui = libraryUI.showUI()
