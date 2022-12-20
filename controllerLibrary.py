from maya import cmds
import os
import json
import pprint
print("I am the controller library")

USERAPPDIR = cmds.internalVar(userAppDir=True)
DIRECTORY = os.path.join(USERAPPDIR, 'controllerLibrary')

def createDirectory(directory = DIRECTORY):
    """
    import importlib
from conLibrary import controllerLibrary
importlib.reload(controllerLibrary)

lib = controllerLibrary.ControllerLibrary()
lib.save('test')
    Creates the given directory
    :param directory: the directory to create
    """
    if not os.path.exists(directory):
        os.mkdir(directory)

def createAssetLibrary(name):
    """
from conLibrary import libraryUI
import importlib
importlib.reload(libraryUI)
ui = libraryUI.showUI()
    :param name:
    :return:
    """
    LIBRARYDIRECTORY = os.path.join(DIRECTORY, name)
    if not os.path.exists(LIBRARYDIRECTORY):
        os.mkdir(LIBRARYDIRECTORY)


class ControllerLibrary(dict):
    def save(self, name, directory=DIRECTORY, screenshot=True, **info):
        createDirectory(directory)
        path=os.path.join(directory, '%s.ma' % name)
        infoFile = os.path.join(directory, '%s.json' % name)

        info['name'] = name
        info['path'] = path

        cmds.file(rename=path)

        if cmds.ls(selection=True):
            cmds.file(force=True, type='mayaAscii', exportSelected=True)
        else:
            cmds.file(save=True, type='mayaAscii', force=True)

        if screenshot:
            info['screenshot'] = self.saveScreenshot(name, directory=directory)

        with open(infoFile, 'w') as f:
            json.dump(info, f, indent=4)

        self[name] = info

    def find(self, directory=DIRECTORY):
        if not os.path.exists(directory):
            return
        files = os.listdir(directory)
        mayaFiles = [f for f in files if f.endswith('.ma')]

        for ma in mayaFiles:
            name, ext = os.path.splitext(ma)
            path = os.path.join(directory, ma)

            infoFile = '%s.json' % name
            if infoFile in files:
                infoFile = os.path.join(directory, infoFile)

                with open(infoFile, 'r') as f:
                    info = json.load(f)
            else:
                info = {}

            screenshot = '%s.jpg' % name
            if screenshot in files:
                info['screenshot'] = os.path.join(directory, name)

            info['name'] = name
            info['path'] = path

            self[name] = info
        pprint.pprint(self)

    def saveAssetFile(self, name, note, folderName, tabName, directory=DIRECTORY, screenshot=True, **info):
        createDirectory(directory)
        folderPath = os.path.join(directory, folderName)
        tabPath = os.path.join(folderPath, tabName)
        path=os.path.join(tabPath, '%s.ma' % name)
        infoFile = os.path.join(tabPath, '%s.json' % name)

        info['name'] = name
        info['path'] = path
        info['note'] = note

        cmds.file(rename=path)

        if cmds.ls(selection=True):
            cmds.file(force=True, type='mayaAscii', exportSelected=True)
        else:
            cmds.file(save=True, type='mayaAscii', force=True)

        if screenshot:
            info['screenshot'] = self.saveScreenshot(name, tabPath)

        with open(infoFile, 'w') as f:
            json.dump(info, f, indent=4)

        self[name] = info

    def ye(self, folderName, tabName, directory=DIRECTORY):
        self.clear()
        print(folderName)
        LIBRARYDIRECTORY = os.path.join(directory, folderName)
        TABDIRECTORY = os.path.join(LIBRARYDIRECTORY, tabName)
        if not os.path.exists(TABDIRECTORY):
            return
        files = os.listdir(TABDIRECTORY)
        mayaFiles = [f for f in files if f.endswith('.ma')]
        for ma in mayaFiles:
            name, ext = os.path.splitext(ma)
            path = os.path.join(TABDIRECTORY, ma)

            infoFile = '%s.json' % name
            if infoFile in files:
                infoFile = os.path.join(TABDIRECTORY, infoFile)

                with open(infoFile, 'r') as f:
                    info = json.load(f)
            else:
                info = {}

            screenshot = '%s.jpg' % name
            if screenshot in files:
                info['screenshot'] = os.path.join(TABDIRECTORY, name)

            info['name'] = name
            info['path'] = path

            self[name] = info
        pprint.pprint(self)



    def load(self, name):
        path = self[name]['path']
        cmds.file(path, i=True, usingNamespaces=False)


    def delete(self, name):
        path = self[name]['path']
        os.remove(path)

    def saveScreenshot(self, name, directory):
        print(directory)
        path = os.path.join(directory, '%s.jpg' % name)

        cmds.viewFit()
        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
        cmds.playblast(completeFilename=path, forceOverwrite=True, format='image', width=200, height=200,
                       showOrnaments=False, startTime=1, endTime=1, viewer=False)
        return path