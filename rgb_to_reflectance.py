# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RGBToReflectance
                                 A QGIS plugin
 Converts RGB values to reflectance
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2025-02-11
        git sha              : $Format:%H$
        copyright            : (C) 2025 by Kaden Patten, Alexander Hernandez, USDA ARS FRR
        email                : kaden.patten@usda.gov
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.core import Qgis, QgsTask, QgsApplication
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, pyqtSignal, QObject
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox, QListWidgetItem, QApplication
import subprocess, platform, re

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .rgb_to_reflectance_dialog import RGBToReflectanceDialog
import os.path

def showDialog(window_title, dialog_text, icon_level):
    dialog = QMessageBox()
    dialog.setSizeGripEnabled(True)
    dialog.setWindowTitle(window_title)
    dialog.setText(dialog_text)
    dialog.setIcon(icon_level)
    dialog.exec_()

class RGBToReflectance(QObject):
    finished_signal = pyqtSignal(int,object)
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        super().__init__()
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RGBToReflectance_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&RGB To Reflectance')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        self.tm = QgsApplication.taskManager()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RGBToReflectance', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/rgb_to_reflectance/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Convert RGB to reflectance'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        #self.first_start = True

        self.location = os.path.dirname(__file__)
        if platform.system() == "Windows":
            self.exec = os.path.join(self.location,"rrenv/Scripts/python.exe")
        else:
            self.exec = os.path.join(self.location,"rrenv/bin/python")
        self.script = os.path.join(self.location,"rgb2reflectance.py")
        self.log = os.path.join(self.location,"rr_log.txt")

        self.dlg = RGBToReflectanceDialog()

        self.img_folder = ""

        self.dlg.input_folder.textChanged.connect(self.onInputFolderChanged)
        self.dlg.input_button.clicked.connect(self.onSelectPhotoFolder)
        self.dlg.close_button.clicked.connect(self.onClose)
        self.dlg.ok_button.clicked.connect(self.onExecute)
        self.finished_signal.connect(self.completed)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        import inspect
        curframe = inspect.currentframe()
        frames = inspect.getouterframes(curframe)
        for frame in frames:
            if frame.function == "uninstallPlugin":
                if platform.system() == "Linux" or platform.system() == "Darwin":
                    bin_folder = os.path.dirname(self.exec)
                    for i in os.listdir(bin_folder):
                        if "python" in str(i).lower():
                            os.unlink(os.path.join(bin_folder,i))
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&RGB To Reflectance'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = RGBToReflectanceDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    # UI Functions
    def onInputFolderChanged(self):
        self.img_folder = self.dlg.input_folder.text()
        #self.onClearAdjacentPhotos()
        self.dlg.progress_bar.setValue(0)

    def onSelectPhotoFolder(self):
        folder = QFileDialog.getExistingDirectory(self.dlg, "Select folder ")
        # if user do not select any folder, then don't change folder_name
        if len(folder) > 1:
            self.dlg.input_folder.setText(folder)

    def onClose(self):
        """Close plugin."""
        self.dlg.close()

    def onExecute(self):
        if self.img_folder == "" or not os.path.isdir(self.img_folder):
            showDialog(window_title="Error: Invalid Input",
                       dialog_text="Please enter a valid input folder",
                       icon_level=QMessageBox.Critical)
            return

        args = [self.exec, self.script, self.img_folder]
        
        self.dlg.progress_bar.setValue(0)
        try:
            #pre_count = self.tm.countActiveTasks()
            ntask = QgsTask.fromFunction("rgb2reflectance_run",self.sub_wrapper,args)
            self.tm.addTask(ntask)
            task_count = self.tm.countActiveTasks()
            #print(task_count)
            #print("run")

        except Exception as e:
            showDialog(window_title="Error!",
                       dialog_text=e,
                       icon_level=QMessageBox.Critical)

    def completed(self,exception,result=None):
        #print("done")
        if result.returncode != 0:
            showDialog(window_title="Error!",
                       dialog_text=result.stderr.decode(),
                       icon_level=QMessageBox.Critical)
            with open(self.log,"w+") as f:
                f.write(result.stdout.decode())
                f.write(result.stderr.decode())
            return
        with open(self.log,"w+") as f:
            f.write(result.stdout.decode())
            f.write(result.stderr.decode())
        self.dlg.progress_bar.setValue(100)

    def sub_wrapper(self,task,args):
        if platform.system() == "Windows":
            res = subprocess.run(args, capture_output=True, shell=True)
        else:
            res = subprocess.run(args, capture_output=True)
        self.finished_signal.emit(res.returncode,res)
        return res