from random import randint

from PySide2.QtCore import QEvent
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QLineEdit, QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QMessageBox
from maya import cmds
import pprint
from conLibrary.controllerLibrary import ControllerLibrary
import importlib
from PySide2 import QtWidgets, QtCore, QtGui
import os

USERAPPDIR = cmds.internalVar(userAppDir=True)
DIRECTORY = os.path.join(USERAPPDIR, 'controllerLibrary')

#get projects from directory
def getProjects(directory=DIRECTORY):
    """
    Gets a list of project folders in a directory
    :param directory:
    :return:
    """
    directory_list = list()
    directory_list.clear()

    files = [f for f in os.listdir(directory)]
    for f in files:
        directory_list.append(f)

    return directory_list

#get tabs from a directory/project directory
def getTabs(projectName, directory=DIRECTORY):
    """
    Gets a list of sub-directories in a project directory
    :param projectName:
    :param directory:
    :return:
    """
    LIBRARYDIRECTORY = os.path.join(DIRECTORY, projectName)
    directory_list = list()
    for root, dirs, files in os.walk(LIBRARYDIRECTORY, topdown=False):
        for name in dirs:
            directory_list.append(name)

    return directory_list

class ControllerLibraryUI(QtWidgets.QDialog):
    """
    import importlib
from conLibrary import libraryUI
importlib.reload(libraryUI)

ui = libraryUI.showUI()
    """
    def __init__(self):
        super(ControllerLibraryUI, self).__init__()
        self.w = None
        self.addAsset = None
        self.newProject = None
        self.setWindowTitle('Asset Manager')
        self.library = ControllerLibrary()
        self.buildUI()

    def buildUI(self):
        print("Building UI")
        #setting up layouts
        windowLayout = QtWidgets.QHBoxLayout(self)
        projectLayout = QtWidgets.QVBoxLayout(self)
        assetsLayout = QtWidgets.QVBoxLayout(self)
        newProjectButtonLayout = QtWidgets.QHBoxLayout(self)
        newTabButtonLayout = QtWidgets.QHBoxLayout(self)

        #projectLayout - layout with a list that allows users to select a project from a list and a search bar that allows users to look up a project name
        #project search bar
        self.projectsLabel = QtWidgets.QLabel("Projects")
        self.projectSearch = QtWidgets.QLineEdit()
        self.projectSearch.setPlaceholderText("Search for a project...")
        self.projectSearch.setMinimumSize(40, 40)
        projectLayout.addWidget(self.projectsLabel)
        projectLayout.addWidget(self.projectSearch)
        self.projectSearch.textChanged.connect(self.searchProjects)

        #allow users to create a new project directory + project in list with an inputted name
        self.projectNameField = QtWidgets.QLineEdit()
        self.projectNameField.setPlaceholderText("New project name")
        self.projectNameField.setMinimumSize(40, 40)
        #saveLayout.addWidget(self.saveNameField)
        self.addProjectBtn = QtWidgets.QPushButton('+')
        #adding some css to the button
        self.addProjectBtn.setStyleSheet('''
                QPushButton{
                                            font-weight: bold;
                                            color: #ffffff;
                                            background-color:#4287f5;
                                            border-color: #4287f5;
                                        }''')
        self.addProjectBtn.clicked.connect(self.createProject)
        newProjectButtonLayout.addWidget(self.projectNameField)
        newProjectButtonLayout.addWidget(self.addProjectBtn)
        projectLayout.addLayout(newProjectButtonLayout)

        #projectsList - users can select a project from list
        self.projectsList = QtWidgets.QListWidget()
        self.projectsList.setViewMode(QtWidgets.QListWidget.ListMode)
        self.projectsList.setResizeMode(QtWidgets.QListWidget.Adjust)
        projectLayout.addWidget(self.projectsList)

        #populate the project list with project directories from script directory
        self.populateProjectsList(self.projectsList)
        self.projectsList.itemClicked.connect(self.projectClicked)

        #assetsLayout - allows users to select assets from different categories
        #search bar that allows users to search an asset by name
        self.assetsLabel = QtWidgets.QLabel("Assets")
        self.assetSearch = QtWidgets.QLineEdit()
        self.assetSearch.setPlaceholderText("Search for an asset...")
        self.assetSearch.setMinimumSize(40, 40)
        assetsLayout.addWidget(self.assetsLabel)
        assetsLayout.addWidget(self.assetSearch)

        #button that allows user to add a new asset in a pop up
        self.addAssetBtn = QtWidgets.QPushButton('+ Add Asset')
        self.addAssetBtn.setStyleSheet('''
                QPushButton{
                                            font-weight: bold;
                                            color: #ffffff;
                                            background-color:#4287f5;
                                            border-color: #4287f5;
                                        }''')
        self.addAssetBtn.clicked.connect(self.newAsset)
        assetsLayout.addWidget(self.addAssetBtn)

        #allows users to add a new category tab with a custom name
        self.tabNameField = QtWidgets.QLineEdit()
        self.tabNameField.setPlaceholderText("New tab name")
        self.tabNameField.setMinimumSize(40, 40)
        # saveLayout.addWidget(self.saveNameField)
        self.addTabBtn = QtWidgets.QPushButton('+')
        #adding some css to button
        self.addTabBtn.setStyleSheet('''
                QPushButton{
                                            font-weight: bold;
                                            color: #ffffff;
                                            background-color:#4287f5;
                                            border-color: #4287f5;
                                        }''')
        self.addTabBtn.clicked.connect(self.createTab)
        newTabButtonLayout.addWidget(self.tabNameField)
        newTabButtonLayout.addWidget(self.addTabBtn)
        assetsLayout.addLayout(newTabButtonLayout)
        self.assetsTabs = QtWidgets.QTabWidget()
        assetsLayout.addWidget(self.assetsTabs)
        #self.assetsTabs.tabBarClicked.connect(self.tabClicked)


        windowLayout.addLayout(projectLayout)
        windowLayout.addLayout(assetsLayout)
        self.setLayout(windowLayout)

    def populateProjectsList(self, projectsList):
        """
        Populates the projectsList widget with project directories in the script directory
        :param projectsList:
        :return:
        """
        projectsList.clear()
        projects = getProjects()
        for project in projects:
            projectsList.addItem(project)


    def searchProjects(self, text):
        """
        Searches for a project based on user input/text in the project search bar
        :param projectsList:
        :return:
        """
        self.projectsList.clear()
        projects = getProjects()
        for project in projects:
            if text.lower() in project.lower():
                projectItem = QtWidgets.QListWidgetItem(project)
                self.projectsList.addItem(projectItem)

    def projectClicked(self, clickedProjectName):
        """
        Creates and populates tabs with subdirectories from a selected project directory
        :param projectsList:
        :return:
        """
        self.assetsTabs.clear()
        tabs = getTabs(clickedProjectName.text())
        for tab in tabs:
            self.assetsListWidget = QtWidgets.QListWidget()
            self.assetsListWidget.clear()
            self.assetsListWidget.setViewMode(QtWidgets.QListWidget.IconMode)
            self.assetsListWidget.setIconSize(QtCore.QSize(64, 64))
            self.assetsListWidget.setResizeMode(QtWidgets.QListWidget.Adjust)
            self.assetsListWidget.setGridSize(QtCore.QSize(12+64, 12+64))
            self.assetsTabs.addTab(self.assetsListWidget, tab)
            self.populateAssetsTab(clickedProjectName.text(), tab)
        print(tabs)

    def refresh(self, clickedProjectName):
        """
        Refreshes the list of assets in a tab
        :param projectsList:
        :return:
        """
        self.assetsTabs.clear()
        tabs = getTabs(clickedProjectName)
        for tab in tabs:
            self.assetsListWidget = QtWidgets.QListWidget()
            self.assetsListWidget.clear()
            self.assetsListWidget.setViewMode(QtWidgets.QListWidget.IconMode)
            self.assetsListWidget.setIconSize(QtCore.QSize(64, 64))
            self.assetsListWidget.setResizeMode(QtWidgets.QListWidget.Adjust)
            self.assetsListWidget.setGridSize(QtCore.QSize(12+64, 12+64))
            self.assetsTabs.addTab(self.assetsListWidget, tab)
            self.populateAssetsTab(clickedProjectName, tab)
        print(tabs)


    def eventFilter(self, source, event):

        if event.type() == QEvent.ContextMenu and source is self.assetsListWidget:
            print(event)
            print(source)
            return True
        return super().eventFilter(source, event)

    def tabClicked(self, clickedTabName):

        print(clickedTabName)
        print(self.assetsTabs.tabText(clickedTabName))
        self.populateAssetsTab()

    def populateAssetsTab(self, project, tab):
        """
        Populates tabs with a list of the assets in the tab directory
        :param projectsList:
        :return:
        """
        self.assetsListWidget.itemClicked.connect(self.assetClicked)
        self.library.clear()
        self.library.ye(project, tab)
        for name, info in self.library.items():
            file = QtWidgets.QListWidgetItem(name)
            self.assetsListWidget.addItem(file)
            screenshot = info.get('screenshot')
            if screenshot:
                icon = QtGui.QIcon(screenshot)
                file.setIcon(icon)

            file.setToolTip(pprint.pformat(info))
            print(name)

    def assetClicked(self, assetClickedName):
        """
        Opens up an item details pop up if an asset is clicked
        :param projectsList:
        :return:
        """
        print("assetClicked: ", assetClickedName.text())
        selectedProject =""
        for item in self.projectsList.selectedItems():
            selectedProject = item.text()
        selectedTab = self.assetsTabs.tabText(self.assetsTabs.currentIndex())
        if self.w is None:
            self.w = ItemDetails(assetClickedName.text(), selectedProject, selectedTab)

        self.w.showDetails(assetClickedName.text(), selectedProject, selectedTab)
        self.w.show()

    def newAsset(self):
        """
        Allows user to create a new asset in a popup window
        :param projectsList:
        :return:
        """
        selectedProject =""
        for item in self.projectsList.selectedItems():
            selectedProject = item.text()
        selectedTab = self.assetsTabs.tabText(self.assetsTabs.currentIndex())
        if self.addAsset is None:
            self.addAsset = NewAsset(selectedProject, selectedTab)
        self.addAsset.show()




    def createProject(self):
        """
        Allows user to create a new project directory with a custom name
        :return:
        """
        name = self.projectNameField.text()
        LIBRARYDIRECTORY = os.path.join(DIRECTORY, name)
        if not os.path.exists(LIBRARYDIRECTORY):
            os.mkdir(LIBRARYDIRECTORY)
        self.populateProjectsList(self.projectsList)
        self.projectNameField.clear()

    def createTab(self):
        """
        Allows user to create a new tab category with a custom name
        :return:
        """
        name = self.tabNameField.text()
        USERAPPDIR = cmds.internalVar(userAppDir=True)
        DIRECTORY = os.path.join(USERAPPDIR, 'controllerLibrary')
        selectedProject =""
        for item in self.projectsList.selectedItems():
            selectedProject = item.text()
            LIBRARYDIRECTORY = os.path.join(DIRECTORY, item.text())
            TABDIRECTORY = os.path.join(LIBRARYDIRECTORY, name)
            if not os.path.exists(TABDIRECTORY):
                os.mkdir(TABDIRECTORY)
            self.refresh(selectedProject)
        self.tabNameField.clear()


class ItemDetails(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, selectedAsset, selectedProject, selectedTab):
        super().__init__()
        self.mainUI = ControllerLibraryUI()
        self.setWindowTitle('Asset Details')
        self.library = ControllerLibrary()
        self.layout = QVBoxLayout()
        self.icon = QLabel()
        self.layout.addWidget(self.icon)
        self.nameTitle = QLabel("Asset Name")
        self.layout.addWidget(self.nameTitle)
        self.nameLabel = QtWidgets.QLabel(selectedAsset)
        self.layout.addWidget(self.nameLabel)
        self.pathTitle = QLabel("Path")
        self.layout.addWidget(self.pathTitle)
        self.pathLabel = QtWidgets.QLabel("")
        self.layout.addWidget(self.pathLabel)
        self.descTitle = QLabel("Asset Notes")
        self.layout.addWidget(self.descTitle)
        self.descLabel = QtWidgets.QLabel("")
        self.layout.addWidget(self.descLabel)
        self.showDetails(selectedAsset, selectedProject, selectedTab)
        self.importAssetBtn = QtWidgets.QPushButton('Import Asset')
        self.importAssetBtn.clicked.connect(self.load)
        self.importAssetBtn.setStyleSheet('''
                QPushButton{
                                            font-weight: bold;
                                            color: #ffffff;
                                            background-color:#4287f5;
                                            border-color: #4287f5;
                                        }''')
        self.layout.addWidget(self.importAssetBtn)
        self.buildUI(selectedAsset, selectedProject)
        self.setLayout(self.layout)

    def buildUI(self, selectedAsset, selectedProject):
        """
        Build UI with buttons
        :param selectedAsset:
        :param selectedProject:
        :return:
        """
        self.deleteAssetBtn = QtWidgets.QPushButton('Delete Asset')
        self.deleteAssetBtn.clicked.connect(self.deleteAsset)
        self.layout.addWidget(self.deleteAssetBtn)
        self.deleteAssetBtn.setStyleSheet('''
                QPushButton{
                                            font-weight: bold;
                                            color: #ffffff;
                                            background-color:#FF6157;
                                            border-color: #FF6157;
                                        }''')

    def showDetails(self, selectedAsset, selectedProject, selectedTab):
        """
        Show details of selected asset
        :param selectedAsset:
        :param selectedProject:
        :param selectedTab:
        :return:
        """
        self.library.ye(selectedProject, selectedTab)
        for name, info in self.library.items():
            if selectedAsset in name:
                screenshot = info.get('screenshot')
                path = info.get('path')
                desc = info.get('note')
                if screenshot:
                    pixmap = QPixmap(screenshot)
                    self.icon.setPixmap(pixmap)
                self.nameLabel.setText(selectedAsset)
                self.pathLabel.setText(path)
                if desc is None:
                    self.descLabel.setText("No note")
                else:
                    self.descLabel.setText(desc)

    def load(self):
        """
        Import/load asset into scene
        :return:
        """
        self.library.load(self.nameLabel.text())

    def deleteAsset(self):
        """
        Delete selected asset from directory
        :return:
        """
        self.library.delete(self.nameLabel.text())
        self.close()
        #self.mainUI.refresh(selectedProject)


class NewAsset(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, selectedProject, selectedTab):
        super().__init__()
        self.mainUI = ControllerLibraryUI()
        self.setWindowTitle('New Asset')
        self.library = ControllerLibrary()
        self.layout = QVBoxLayout()
        self.buildUI(selectedProject, selectedTab)


    def buildUI(self, selectedProject, selectedTab):
        self.nameLabel = QLabel("Asset Name")
        self.layout.addWidget(self.nameLabel)
        self.nameEdit = QLineEdit()
        self.nameEdit.setPlaceholderText("Enter asset name")
        self.layout.addWidget(self.nameEdit)

        self.projectLabel = QLabel("Project")
        self.layout.addWidget(self.projectLabel)
        self.comboProjects = QComboBox()
        self.layout.addWidget(self.comboProjects)
        self.populateComboProjects(selectedProject)
        self.comboProjects.currentIndexChanged.connect(self.updateComboTabs)

        self.categoryLabel = QLabel("Category")
        self.layout.addWidget(self.categoryLabel)
        self.comboTabs = QComboBox()
        self.layout.addWidget(self.comboTabs)
        self.populateComboTabs(selectedTab)

        self.notesLabel = QLabel("Asset Notes")
        self.layout.addWidget(self.notesLabel)
        self.noteEdit = QLineEdit()
        self.noteEdit.setPlaceholderText("Enter asset note")
        self.layout.addWidget(self.noteEdit)

        self.saveAssetBtn = QtWidgets.QPushButton('Save Asset')
        self.layout.addWidget(self.saveAssetBtn)
        self.saveAssetBtn.clicked.connect(self.saveAsset)
        self.saveAssetBtn.setStyleSheet('''
                QPushButton{
                                            font-weight: bold;
                                            color: #ffffff;
                                            background-color:#4287f5;
                                            border-color: #4287f5;
                                        }''')
        self.saveAsset()

        self.setLayout(self.layout)

    def populateComboProjects(self, selectedProject):
        """
        Populate the projects dropdown with all the projects and set the selected project
        :param selectedProject:
        :return:
        """
        projects = getProjects()
        for project in projects:
            self.comboProjects.addItem(project)
        self.comboProjects.setCurrentText(selectedProject)

    def populateComboTabs(self, selectedTab):
        """
        Populate the tab dropdown based on the selected project
        :param selectedTab:
        :return:
        """
        self.comboTabs.clear()
        current = self.comboProjects.currentText()
        tabs = getTabs(current)
        for tab in tabs:
            self.comboTabs.addItem(tab)
        self.comboTabs.setCurrentText(selectedTab)

    def updateComboTabs(self):
        """
        Update viable tabs based on selected project
        :return:
        """
        self.comboTabs.clear()
        current = self.comboProjects.currentText()
        tabs = getTabs(current)
        for tab in tabs:
            self.comboTabs.addItem(tab)

    def saveAsset(self):
        """
        Save asset to desired path
        :return:
        """
        print("save asset")
        name = self.nameEdit.text()
        note = self.noteEdit.text()
        folder = self.comboProjects.currentText()
        tab = self.comboTabs.currentText()
        if not name.strip():
            cmds.warning("Enter a name")
            return
        self.library.saveAssetFile(name, note, folder, tab)
        #self.populate()
        self.nameEdit.setText('')
        self.noteEdit.setText('')
        self.mainUI.refresh(folder)
        self.mainUI.projectsList.setCurrentIndex(self.mainUI.projectsList.currentIndex())
        self.close()










def showUI():
    """from conLibrary import libraryUI
from conLibrary import controllerLibrary
import importlib
importlib.reload(libraryUI)
importlib.reload(controllerLibrary)
ui = libraryUI.showUI()"""
    ui = ControllerLibraryUI()
    ui.show()
    return ui
