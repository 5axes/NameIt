#----------------------------------------------------------------------------------------------------------------------------------------
# Copyright (c) 2022-2023 5@xes
#
# The NameIt plugin is released under the terms of the AGPLv3 or higher.
# Modifications 5@xes 2022
#----------------------------------------------------------------------------------------------------------------------------------------
# V1.0.0    : First Proof of Concept
# V1.0.1    : Add special type identification_mesh (can be used for automatic supression or not new identification creation)
# V1.1.0    : New function Add Number From Part ( search (X) in the part name )
# V1.1.1    : Fix the last reference number to the biggest value in case of Add Number From Part
# V1.2.0    : Add Prefix and Suffix for Number
# V1.3.0    : Add option to fix a specific Initial Layer Speed
# V1.3.1    : Add message if no identificator created
# V1.3.2    : Clean the code 
# V1.4.0    : Choose Font "Gill Sans MT" / "Arial Rounded MT"
# V1.4.2    : Modification and Test on the Plugin Font NameIt Rounded
# V1.5.0    : Mirror Mode
# V1.5.1    : Mirror Mode Menu direct Switch mode
# V1.6.0    : Add Function Rename Models
# V1.6.1    : Option Middle as ComboBox
# V1.6.2    : Use "grouped" operation for adding text : https://github.com/5axes/NameIt/issues/14
# V1.7.0    : Add Option Front+Base
# V1.8.0    : Two New Font to replace Windows Font with Licence Issue
#             Noto Sans : https://fonts.google.com/noto/specimen/Noto+Sans
#             Odin Rounded : https://www.dafont.com/odin-rounded.font
#             Remove in the final package the Fonts "Gill Sans MT" / "Arial Rounded MT"
# V1.8.1    : Correction On Message for Cura 4.4 to Cura 4.11
# V1.8.2    : Bug correction https://github.com/5axes/NameIt/discussions/18
# V1.8.2    : Add French Translation
# V1.9.0    : Update on Line
# V2.0.0    : Add Recycle Symbol
# V2.0.1    : Update Some Symbol STL files
#----------------------------------------------------------------------------------------------------------------------------------------

VERSION_QT5 = False
try:    
    from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl
    from PyQt6.QtGui import QDesktopServices
except ImportError:
    from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl
    from PyQt5.QtGui import QDesktopServices
    VERSION_QT5 = True
    
# Imports from the python standard library to build the plugin functionality
import re
import os
from os.path import exists
import math
import numpy
import trimesh

from typing import Optional, List

from UM.Math.Vector import Vector
from UM.Extension import Extension
# from UM.PluginRegistry import PluginRegistry
from UM.Application import Application
from cura.CuraApplication import CuraApplication

from UM.Mesh.MeshData import MeshData, calculateNormalsFromIndexedVertices
from UM.Settings.SettingInstance import SettingInstance
from cura.Scene.CuraSceneNode import CuraSceneNode
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection
from cura.Scene.SliceableObjectDecorator import SliceableObjectDecorator
from cura.Scene.BuildPlateDecorator import BuildPlateDecorator
from cura.Operations.SetParentOperation import SetParentOperation
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Operations.GroupedOperation import GroupedOperation
from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation

from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.ContainerRegistry import ContainerRegistry

from collections import OrderedDict

from cura.CuraVersion import CuraVersion  # type: ignore
from UM.Version import Version

from UM.Logger import Logger
from UM.Message import Message
from UM.Resources import Resources

from UM.i18n import i18nCatalog

Resources.addSearchPath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)))
)  # Plugin translation file import

catalog = i18nCatalog("nameit")

if catalog.hasTranslationLoaded():
    Logger.log("i", "Name It Plugin translation loaded!")
    
    
#This class is the extension and doubles as QObject to manage the qml    
class NameIt(QObject, Extension):
    #Create an api
    from cura.CuraApplication import CuraApplication
    api = CuraApplication.getInstance().getCuraAPI()
 
        
    # The QT signal, which signals an update for user information text
    userSizeChanged = pyqtSignal()
    userHeightChanged = pyqtSignal()
    userDistanceChanged = pyqtSignal()
    userKerningChanged = pyqtSignal()
    userPrefixChanged = pyqtSignal()
    userSuffixChanged = pyqtSignal()
    userInfoTextChanged = pyqtSignal()
    userSpeedChanged = pyqtSignal()
    userFontChanged = pyqtSignal()
    userLocationChanged = pyqtSignal()
    
    def __init__(self, parent = None) -> None:
        QObject.__init__(self, parent)
        Extension.__init__(self)
       
        #Initialize variables
        self.userText = ""
        self._continueDialog = None
        self._prefix = ""
        self._suffix = ""
        self._font = "NameIt Rounded"
        self._location = "Front"
        
        # set the preferences to store the default value
        #self._application = CuraApplication.getInstance()
        self._application = Application.getInstance()
        self._i18n_catalog = None
    
        self._preferences = self._application.getPreferences()
        self._preferences.addPreference("NameIt/size", 5)
        self._preferences.addPreference("NameIt/height", 0.2)
        self._preferences.addPreference("NameIt/distance", 1.6)
        self._preferences.addPreference("NameIt/kerning", 0.1)
        self._preferences.addPreference("NameIt/prefix", "")
        self._preferences.addPreference("NameIt/suffix", "")
        self._preferences.addPreference("NameIt/speed_layer_0", 0)
        self._preferences.addPreference("NameIt/font", "NameIt Rounded")
        self._preferences.addPreference("NameIt/location", "Front")
        
        # convert as float to avoid further issue
        self._size = float(self._preferences.getValue("NameIt/size"))
        self._height = float(self._preferences.getValue("NameIt/height"))
        self._distance = float(self._preferences.getValue("NameIt/distance"))
        self._kerning = float(self._preferences.getValue("NameIt/kerning"))
        self._prefix = self._preferences.getValue("NameIt/prefix")
        self._suffix = self._preferences.getValue("NameIt/suffix")     
        self._speed = float(self._preferences.getValue("NameIt/speed_layer_0")) 
        self._font = self._preferences.getValue("NameIt/font") 
        self._location = self._preferences.getValue("NameIt/location")
 
        self.Major=1
        self.Minor=0

        # Logger.log('d', "Info Version CuraVersion --> " + str(Version(CuraVersion)))
        Logger.log('d', "NameIt Info CuraVersion --> " + str(CuraVersion))
        Logger.log('d', "NameIt FontStyle --> " + str(self._font))
        
        # Test version for Cura Master
        # https://github.com/smartavionics/Cura
        if "master" in CuraVersion :
            self.Major=4
            self.Minor=20
        else:
            try:
                self.Major = int(CuraVersion.split(".")[0])
                self.Minor = int(CuraVersion.split(".")[1])
            except:
                pass
 
        # Shortcut
        if VERSION_QT5:
            self._qml_folder = "qml_qt5" 
        else:
            self._qml_folder = "qml_qt6" 

        self._qml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self._qml_folder, "NameIt.qml")
        
        self._controller = CuraApplication.getInstance().getController()
        self._message = None
        
        self.setMenuName(catalog.i18nc("@item:inmenu", "Name It !"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add Number"), lambda: self.addPartName("Number"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add Number From Part"), lambda: self.addPartName("NameNumber"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add Name"), lambda: self.addPartName("Name"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add Recycling Symbol"), lambda: self.addRecyclingSymbol())
        self.addMenuItem("", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Remove Identifier"), self.removeAllIdMesh)
        self.addMenuItem(" ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Rename models"), self.renameMesh)       
        self.addMenuItem("  ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Define Text Parameters"), self.defaultSize)
        self.addMenuItem("   ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Help"), self.gotoHelp)

        # Define a new settings "identification_mesh""
        # V1.8.2 set to enabled = False Issue if the user check this option in a profile
        self._settings_dict = OrderedDict()
        self._settings_dict["identification_mesh"] = {
            "label": "Identification mesh",
            "description": "Mesh used as identification element (Special parameter added for the plugin NameIt!)",
            "type": "bool",
            "default_value": False,
            "enabled": False,
            "settable_per_mesh": True,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False,
            "settable_globally": False
        }
        ContainerRegistry.getInstance().containerLoadComplete.connect(self._onContainerLoadComplete)
        
        self._message = Message(title=catalog.i18nc("@info:title", "Name It!"))
        
        # Stock Data  
        self._all_picked_node = [] 
        self._idcount = 0

    # Source code Origine FieldOfView
    def _getSelectedNodes(self, force_single = False) -> List[SceneNode]:
        self._message.hide()
        selection = Selection.getAllSelectedObjects()[:]
        if force_single:
            if len(selection) == 1:
                return selection[:]

            self._message.setText(catalog.i18nc("@info:status", "Please select a single model first"))
        else:
            if len(selection) >= 1:
                return selection[:]

            self._message.setText(catalog.i18nc("@info:status", "Please select one or more models first"))

        self._message.show()
        return []
        
    # Source code Origine FieldOfView
    # Modified For Multi Selection    
    def renameMesh(self) -> None:
        self._node_queue = self._getSelectedNodes(force_single=False)
        if not self._node_queue:
            return

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self._qml_folder, "RenameDialog.qml")
        self._rename_dialog = self._application.createQmlComponent(path, {"manager": self})
        if not self._rename_dialog:
            return
        self._rename_dialog.show()
        # Use the first Name as reference to rename the Meshs
        self._rename_dialog.setName(self._node_queue[0].getName())

    @pyqtSlot(str)
    def setSelectedMeshName(self, new_name:str) -> None:
        iD = 0
        for node in self._node_queue :
            # Logger.log('d', 'New_name : %s', new_name)
            # node = self._node_queue[0]
            if len(self._node_queue) > 1 :
                _name = new_name
                _name += "({})".format(str(iD))
                iD += 1
            else:
                _name = new_name
                
            node.setName(_name)
            Selection.remove(node)
            Selection.add(node)

        
    def _onContainerLoadComplete(self, container_id):
        if not ContainerRegistry.getInstance().isLoaded(container_id):
            # skip containers that could not be loaded, or subsequent findContainers() will cause an infinite loop
            return

        try:
            container = ContainerRegistry.getInstance().findContainers(id = container_id)[0]

        except IndexError:
            # the container no longer exists
            return

        if not isinstance(container, DefinitionContainer):
            # skip containers that are not definitions
            return
        if container.getMetaDataEntry("type") == "extruder":
            # skip extruder definitions
            return

        blackmagic_category = container.findDefinitions(key="blackmagic")
        identification_mesh = container.findDefinitions(key=list(self._settings_dict.keys())[0])
        
        if blackmagic_category and not identification_mesh:            
            blackmagic_category = blackmagic_category[0]
            for setting_key, setting_dict in self._settings_dict.items():

                definition = SettingDefinition(setting_key, container, blackmagic_category, self._i18n_catalog)
                definition.deserialize(setting_dict)

                # add the setting to the already existing platform adhesion setting definition
                blackmagic_category._children.append(definition)
                container._definition_cache[setting_key] = definition
                container._updateRelations(definition)
                
    # Define the default value for the text element
    def defaultSize(self) -> None:
 
        if self._continueDialog is None:
            self._continueDialog = self._createDialogue()
        
        self._continueDialog.show()
        #self.userSizeChanged.emit()
        

    #====User Input=====================================================================================================
    @pyqtProperty(str, notify= userHeightChanged)
    def heightInput(self):
        return str(self._height)

    @pyqtProperty(str, notify= userKerningChanged)
    def kerningInput(self):
        return str(self._kerning)

    @pyqtProperty(str, notify= userPrefixChanged)
    def prefixInput(self):
        return str(self._prefix)

    @pyqtProperty(str, notify= userSuffixChanged)
    def suffixInput(self):
        return str(self._suffix)
        
    @pyqtProperty(str, notify= userDistanceChanged)
    def distanceInput(self):
        return str(self._distance)
        
    @pyqtProperty(str, notify= userSizeChanged)
    def sizeInput(self):
        return str(self._size)

    @pyqtProperty(str, notify= userSpeedChanged)
    def speedInput(self):
        return str(self._speed)

    @pyqtProperty(str, notify= userFontChanged)
    def fontInput(self):
        return str(self._font)

    @pyqtProperty(str, notify= userLocationChanged)
    def locationInput(self):
        return str(self._location)
 
    #The QT property, which is computed on demand from our userInfoText when the appropriate signal is emitted
    @pyqtProperty(str, notify= userInfoTextChanged)
    def userInfoText(self):
        return self.userText

    #This method builds the dialog from the qml file and registers this class
    #as the manager variable
    def _createDialogue(self):
        #qml_file_path = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "NameIt.qml")
        #Logger.log('d', 'Qml_path : ' + str(self._qml_path)) 
        component_with_context = Application.getInstance().createQmlComponent(self._qml_path, {"manager": self})
        return component_with_context

    def getSize(self) -> float:
    
        return self._size
        
    # is called when a key gets released in the size inputField (twice for some reason)
    @pyqtSlot(str)
    def sizeEntered(self, text):
        # Is the textfield empty ? Don't show a message then
        if text =="":
            #self.writeToLog("size-Textfield: Empty")
            self.userMessage("", "ok")
            return

        #Convert commas to points
        text = text.replace(",",".")

        #self.writeToLog("Size-Textfield: read value "+text)

        #Is the entered Text a number?
        try:
            float(text)
        except ValueError:
            self.userMessage("Entered size invalid : " + text,"wrong")
            return
        self._size = float(text)

        #Check if positive
        if self._size <= 0:
            self.userMessage("Size value must be positive !","wrong")
            self._size = 20
            return

        self.writeToLog("Set NameIt/size to : " + text)
        self._preferences.setValue("NameIt/size", self._size)
        
        #clear the message Field
        self.userMessage("", "ok")
 
    def getHeight(self) -> float:
    
        return self._height
        
    # is called when a key gets released in the height inputField (twice for some reason)
    @pyqtSlot(str)
    def heightEntered(self, text):
        # Is the textfield empty ? Don't show a message then
        if text =="":
            #self.writeToLog("height-Textfield: Empty")
            self.userMessage("", "ok")
            return

        #Convert commas to points
        text = text.replace(",",".")

        #self.writeToLog("height-Textfield: read value "+text)

        #Is the entered Text a number?
        try:
            float(text)
        except ValueError:
            self.userMessage("Entered height invalid : " + text,"wrong")
            return
        self._height = float(text)

        #Check if positive
        if self._height <= 0:
            self.userMessage("Height value must be positive !","wrong")
            self._height = 0.2
            return

        self.writeToLog("Set NameIt/height to : " + text)
        self._preferences.setValue("NameIt/height", self._height)
        
        #clear the message Field
        self.userMessage("", "ok")

    def getSpeed(self) -> float:
    
        return self._speed
        
    # is called when a key gets released in the speed inputField
    @pyqtSlot(str)
    def speedEntered(self, text):
        # Is the textfield empty ? Don't show a message then
        if text =="":
            #self.writeToLog("speed-Textfield: Empty")
            self.userMessage("", "ok")
            return

        #Convert commas to points
        text = text.replace(",",".")

        #self.writeToLog("speed-Textfield: read value "+text)

        #Is the entered Text a number?
        try:
            float(text)
        except ValueError:
            self.userMessage("Speed height invalid : " + text,"wrong")
            return
        self._speed = float(text)

        #Check if positive
        if self._speed < 0:
            self.userMessage("Speed value must be positive !","wrong")
            self._speed = 12
            return

        self.writeToLog("Set NameIt/speed_layer_0 to : " + text)
        self._preferences.setValue("NameIt/speed_layer_0", self._speed)
        
        #clear the message Field
        self.userMessage("", "ok")
        
    def getDistance(self) -> float:
    
        return self._distance
        
    # is called when a key gets released in the distance inputField
    @pyqtSlot(str)
    def distanceEntered(self, text):
        # Is the textfield empty ? Don't show a message then
        if text =="":
            #self.writeToLog("height-Textfield: Empty")
            self.userMessage("", "ok")
            return

        #Convert commas to points
        text = text.replace(",",".")

        #self.writeToLog("distance-Textfield: read value "+text)

        #Is the entered Text a number?
        try:
            float(text)
        except ValueError:
            self.userMessage("Entered distance invalid : " + text,"wrong")
            return
        self._distance = float(text)

        self.writeToLog("Set NameIt/distance to : " + text)
        self._preferences.setValue("NameIt/distance", self._distance)
        
        #clear the message Field
        self.userMessage("", "ok")


    def getKerning(self) -> float:
    
        return self._kerning
        
    # is called when a key gets released in the kerning inputField
    @pyqtSlot(str)
    def kerningEntered(self, text):
        # Is the textfield empty ? Don't show a message then
        if text =="":
            #self.writeToLog("kerning-Textfield: Empty")
            self.userMessage("", "ok")
            return

        #Convert commas to points
        text = text.replace(",",".")

        #self.writeToLog("distance-Textfield: read value "+text)

        #Is the entered Text a number?
        try:
            float(text)
        except ValueError:
            self.userMessage("Entered kerning invalid : " + text,"wrong")
            return
        self._kerning = float(text)

        self.writeToLog("Set NameIt/kerning to : " + text)
        self._preferences.setValue("NameIt/kerning", self._kerning)
        
        #clear the message Field
        self.userMessage("", "ok")

    def getPrefix(self) -> str:
    
        return self._prefix
        
    # is called when a key gets released in the prefix inputField
    @pyqtSlot(str)
    def prefixEntered(self, text):

        self._prefix = str(text)

        self.writeToLog("Set NameIt/Prefix to : " + text)
        self._preferences.setValue("NameIt/prefix", self._prefix)
        
        #clear the message Field
        self.userMessage("", "ok")

    def getSuffix(self) -> str:
    
        return self._suffix
        
    # is called when a key gets released in the suffix inputField
    @pyqtSlot(str)
    def suffixEntered(self, text):
            
        self._suffix= str(text)

        self.writeToLog("Set NameIt/Suffix to : " + text)
        self._preferences.setValue("NameIt/suffix", self._suffix)
        
        #clear the message Field
        self.userMessage("", "ok")

       
    def getFont(self) -> str:
    
        return self._font
        
    # is called when a CurrentIndexChanged in the font combobox
    @pyqtSlot(str)
    def fontEntered(self, text):

        self._font = str(text)

        self.writeToLog("Set NameIt/Font : " + text)
        self._preferences.setValue("NameIt/font", self._font)
        
        # Logger.log("d", "fontEntered = %s", self._font) 
        
        # clear the message Field
        self.userMessage("", "ok")

    def getLocation(self) -> str:
    
        return self._location
        
    # is called when a CurrentIndexChanged in the location combobox
    @pyqtSlot(str)
    def locationEntered(self, text):

        self._location = str(text)

        self.writeToLog("Set NameIt/Location : " + text)
        self._preferences.setValue("NameIt/location", self._location)
        
        # Logger.log("d", "locationEntered = %s", self._location) 
        
        # clear the message Field
        self.userMessage("", "ok")
        
    #===== Text Output ===================================================================================================
    #writes the message to the log, includes timestamp, length is fixed
    def writeToLog(self, str):
        Logger.log("d", "Debug NameIt = %s", str)

    #Sends an user message to the Info Textfield, color depends on status (prioritized feedback)
    # Red wrong for Errors and Warnings
    # Grey for details and messages that aren't interesting for advanced users
    def userMessage(self, message, status):
        if status is "wrong":
            #Red
            self.userText = "<font color='#a00000'>" + message + "</font>"
        else:
            # Grey
            if status is "ok":
                self.userText = "<font color='#9fa4b0'>" + message + "</font>"
            else:
                self.writeToLog("Error: Invalid status: "+status)
                return
        #self.writeToLog("User Message: "+message)
        self.userInfoTextChanged.emit()
     
    def gotoHelp(self) -> None:
        QDesktopServices.openUrl(QUrl("https://github.com/5axes/NameIt/wiki"))
       
 
    # Source code from MeshTools Plugin 
    # Copyright (c) 2020 Aldo Hoeben / fieldOfView
    def _getAllSelectedNodes(self) -> List[SceneNode]:
        selection = Selection.getAllSelectedObjects()[:]
        if selection:
            deep_selection = []  # type: List[SceneNode]
            for selected_node in selection:
                if selected_node.hasChildren():
                    deep_selection = deep_selection + selected_node.getAllChildren()
                if selected_node.getMeshData() != None:
                    deep_selection.append(selected_node)
            if deep_selection:
                return deep_selection

        Message(catalog.i18nc("@info:status", "Please select one or more models first"))

        return []
    
    def _checkSettings(self) -> None:
        # V1.8.2 set to enabled = False Issue if the user check this option in a profile
        global_container_stack = CuraApplication.getInstance().getGlobalContainerStack()
        extruder_stack = CuraApplication.getInstance().getExtruderManager().getActiveExtruderStacks()[0] 
        extruder = global_container_stack.extruderList[0]        
        type_identification_mesh = bool(extruder.getProperty("identification_mesh", "value"))
        if type_identification_mesh :
            Logger.log('d', "type_identification_mesh : {}".format(type_identification_mesh))              
            extruder.setProperty("identification_mesh", "value", False)

    def get_mat_number(self, word):
        # https://en.wikipedia.org/wiki/Recycling_codes
        word_number_mapping = {"PLA": 92, "TPU": 113, "TPU 95A": 113, "ABS": 121, "PLA+": 92, "PETG": 1, "PA": 43, "PC": 58, "HIPS" :108 , "PEEK": 68 , "PVA" : 114 , "ASA" : 13 , "PA" : 43, "Nylon" : 43}
        return word_number_mapping.get(word, -1)
      
    def getMaterial(self, IdM) -> str:
        # Logger.log('d', "Material : {}".format(IdM))
        extruder_stack = CuraApplication.getInstance().getExtruderManager().getActiveExtruderStacks()       
        M_Name = "PLA"
        for Extrud in extruder_stack:
            M_GUID = Extrud.material.getMetaData().get("GUID", "")
            if M_GUID ==  IdM :
                M_Name = Extrud.material.getMetaData().get("material", "")
                number = self.get_mat_number(M_Name)
                # Logger.log('d', "M_Name : {} - {}".format(number ,M_Name))
            # Logger.log('d', "M_GUID : {}".format(M_GUID))
        
        return str(number)+"-"+M_Name
            

    #===== Recycling Symbol Creation ==============================================================================
    # Add Recycling Symbol
    #========================================================================================================
    def addRecyclingSymbol(self) -> None:
        nbMod=0
        nbNum=0
        
        # V1.8.2 set to enabled = False
        self._checkSettings()
        
        nodes_list = self._getAllSelectedNodes()
        if not nodes_list:
            nodes_list = DepthFirstIterator(self._application.getController().getScene().getRoot())
        
        self._op = GroupedOperation()
        # Logger.log('d', "nodes_list : {}".format(nodes_list))
        for node in nodes_list:
            if node.callDecoration("isSliceable"):           
                # Logger.log('d', "isSliceable : {}".format(node.getName()))
                node_stack=node.callDecoration("getStack")           
                if node_stack: 
                    type_infill_mesh = bool(node_stack.getProperty("infill_mesh", "value"))
                    type_cutting_mesh = bool(node_stack.getProperty("cutting_mesh", "value"))
                    type_support_mesh = bool(node_stack.getProperty("support_mesh", "value"))
                    type_anti_overhang_mesh = bool(node_stack.getProperty("anti_overhang_mesh", "value")) 
                    type_identification_mesh = bool(node_stack.getProperty("identification_mesh", "value"))
                    # Logger.log('d', "type_identification_mesh : {}".format(type_identification_mesh))
                    
                    if not type_infill_mesh and not type_support_mesh and not type_anti_overhang_mesh and not type_cutting_mesh and not type_identification_mesh :
                        nbMod+=1
                        name = self.getMaterial(node_stack.getProperty("material_guid", "value"))
                        Logger.log('d', "Material : {}".format(self.getMaterial(node_stack.getProperty("material_guid", "value"))))
                        # Logger.log('d', "Mesh : {}".format(name))
                        
                        # Add RecyclingSymbol 
                        nbNum+=1
                        self._createRecyclingSymbol(node, name)
        
        self._op.push()        
        # Informations at the end of the creation Routine
        # message_type only available from Cura 4.11
        if self.Major == 4 and self.Minor < 11 :
            if nbNum == 0 :                                
                Message(text = "No Recycling Symbol created for %s element(s)" % (nbMod), title = catalog.i18nc("@info:title", "Warning ! Name It")).show()
            elif nbNum < nbMod :
                Message(text = "Recycling Symbol creation : %d / %d" % (nbNum,nbMod), title = catalog.i18nc("@info:title", "Info ! Name It")).show()    
            elif nbNum == nbMod :
                Message(text = "Recycling Symbol creation : %d / %d" % (nbNum,nbMod), title = catalog.i18nc("@info:title", "Info ! Name It")).show()    
        else :
            if nbNum == 0 :                                
                Message(text = "No Recycling Symbol created for %s element(s)" % (nbMod), title = catalog.i18nc("@info:title", "Warning ! Name It"), message_type = Message.MessageType.ERROR).show()
            elif nbNum < nbMod :
                Message(text = "Recycling Symbol creation : %d / %d" % (nbNum,nbMod), title = catalog.i18nc("@info:title", "Info ! Name It"), message_type = Message.MessageType.WARNING).show()    
            elif nbNum == nbMod :
                Message(text = "Recycling Symbol creation : %d / %d" % (nbNum,nbMod), title = catalog.i18nc("@info:title", "Info ! Name It"), message_type = Message.MessageType.POSITIVE).show()    
  
    #===== Identifier Creation ==============================================================================
    # Add Part Name  as text
    #  Option :
    #           -   "Number"        : Incremental Number + Prefix & Suffix
    #           -   "NameNumber"    : Number present in the object number + Prefix & Suffix
    #           -   "Name"          : Name of the Object
    #========================================================================================================
    def addPartName(self, option) -> None:
        nbMod=0
        nbNum=0
        # Logger.log('d', "Type : {}".format(option))
        
        # V1.8.2 set to enabled = False
        self._checkSettings()
        
        nodes_list = self._getAllSelectedNodes()
        if not nodes_list:
            nodes_list = DepthFirstIterator(self._application.getController().getScene().getRoot())
        
        self._op = GroupedOperation()
        # Logger.log('d', "nodes_list : {}".format(nodes_list))
        for node in nodes_list:
            if node.callDecoration("isSliceable"):           
                # Logger.log('d', "isSliceable : {}".format(node.getName()))
                node_stack=node.callDecoration("getStack")           
                if node_stack: 
                    type_infill_mesh = bool(node_stack.getProperty("infill_mesh", "value"))
                    type_cutting_mesh = bool(node_stack.getProperty("cutting_mesh", "value"))
                    type_support_mesh = bool(node_stack.getProperty("support_mesh", "value"))
                    type_anti_overhang_mesh = bool(node_stack.getProperty("anti_overhang_mesh", "value")) 
                    type_identification_mesh = bool(node_stack.getProperty("identification_mesh", "value"))
                    # Logger.log('d', "type_identification_mesh : {}".format(type_identification_mesh))
                    
                    if not type_infill_mesh and not type_support_mesh and not type_anti_overhang_mesh and not type_cutting_mesh and not type_identification_mesh :
                        nbMod+=1
                        name = node.getName()
                        Logger.log('d', "Mesh : {}".format(name))
                        # Add Part Name as text 
                        if option == "Name" :
                            nbNum+=1
                            self._createNameMesh(node, name)
                        # Add Number as text  
                        if option == "Number" :
                            nbNum+=1
                            self._idcount += 1
                            # Logger.log("d", "name= %s", name)
                            
                            # filename = node.getMeshData().getFileName() 
                            # Logger.log("d", "Ident = %s", Ident)
                            Ident=self._prefix + str(self._idcount) + self._suffix
                            self._createNameMesh(node, Ident)
                        # Add Number as text from (number in Part  IE : Disque.stl(1) -> use 1 )
                        if option == "NameNumber" :
                            SearchId = re.findall(r"(\([0-9]*\d+[0-9]*\))", name)
                            # Logger.log("d", "SearchId= %s", SearchId)                         
                            if SearchId is not None: 
                                indice=len(SearchId) 
                                # Logger.log("d", "SearchId = %s", indice) 
                                if indice > 0 :
                                    nbNum+=1                               
                                    Ident=SearchId[len(SearchId)-1] 
                                    Id = re.search(r"(\d+)", Ident)
                                    Id_temp = int(Id.group())
                                    Id_total = self._prefix + str(Id_temp) + self._suffix
                                    self._createNameMesh(node, Id_total)
                                    if Id_temp > self._idcount :
                                        self._idcount = Id_temp   
        
        self._op.push()        
        # Informations at the end of the creation Routine
        # message_type only available from Cura 4.11
        if self.Major == 4 and self.Minor < 11 :
            if nbNum == 0 :                                
                Message(text = "No Identifier created for %s element(s)" % (nbMod), title = catalog.i18nc("@info:title", "Warning ! Name It")).show()
            elif nbNum < nbMod :
                Message(text = "Identifier creation : %d / %d" % (nbNum,nbMod), title = catalog.i18nc("@info:title", "Info ! Name It")).show()    
            elif nbNum == nbMod :
                Message(text = "Identifier creation : %d / %d" % (nbNum,nbMod), title = catalog.i18nc("@info:title", "Info ! Name It")).show()    
        else :
            if nbNum == 0 :                                
                Message(text = "No Identifier created for %s element(s)" % (nbMod), title = catalog.i18nc("@info:title", "Warning ! Name It"), message_type = Message.MessageType.ERROR).show()
            elif nbNum < nbMod :
                Message(text = "Identifier creation : %d / %d" % (nbNum,nbMod), title = catalog.i18nc("@info:title", "Info ! Name It"), message_type = Message.MessageType.WARNING).show()    
            elif nbNum == nbMod :
                Message(text = "Identifier creation : %d / %d" % (nbNum,nbMod), title = catalog.i18nc("@info:title", "Info ! Name It"), message_type = Message.MessageType.POSITIVE).show()    
 
    #----------------------------------------
    # Initial Source code from  fieldOfView
    #----------------------------------------  
    def _toMeshData(self, tri_node: trimesh.base.Trimesh) -> MeshData:
        # Rotate the part to laydown on the build plate
        # Modification from 5@xes
        tri_node.apply_transform(trimesh.transformations.rotation_matrix(math.radians(90), [-1, 0, 0]))
        tri_faces = tri_node.faces
        tri_vertices = tri_node.vertices

        # Following Source code from  fieldOfView
        # https://github.com/fieldOfView/Cura-SimpleShapes/blob/bac9133a2ddfbf1ca6a3c27aca1cfdd26e847221/SimpleShapes.py#L45
        indices = []
        vertices = []

        index_count = 0
        face_count = 0
        for tri_face in tri_faces:
            face = []
            for tri_index in tri_face:
                vertices.append(tri_vertices[tri_index])
                face.append(index_count)
                index_count += 1
            indices.append(face)
            face_count += 1

        vertices = numpy.asarray(vertices, dtype=numpy.float32)
        indices = numpy.asarray(indices, dtype=numpy.int32)
        normals = calculateNormalsFromIndexedVertices(vertices, indices, face_count)

        mesh_data = MeshData(vertices=vertices, indices=indices, normals=normals)

        return mesh_data              

    #----------------------------------------
    # Create RecyclingSymbol
    #----------------------------------------
    def _createRecyclingSymbol(self, parent: CuraSceneNode, name):
        node = CuraSceneNode()

        # Logger.log("d", "_createNameMesh= %s", "Id-"+name)

        node_bounds = parent.getBoundingBox()
        # Logger.log("d", "width= %s", str(node_bounds.width))
        # Logger.log("d", "depth= %s", str(node_bounds.depth))
        # Logger.log("d", "Center X= %s", str(node_bounds.center.x))
        # Logger.log("d", "Center Y= %s", str(node_bounds.center.z))
        if self._location == "Front" or self._location == "Front+Base" :
            PosX = node_bounds.center.x
            PosY = node_bounds.center.z+0.5*node_bounds.depth + self._distance + self._size         
        else :
            PosX = node_bounds.center.x
            PosY = node_bounds.center.z + (self._size * 0.5)

        # Logger.log("d", "Pos X= %s", str(PosX))
        # Logger.log("d", "Pos Y= %s", str(PosY))
        
        position = Vector(PosX, 0, PosY)
                        
        node.setSelectable(True)
        node.setName("Id-"+name)   
        
        if self._location == "Front+Base" :
            base = True
        else :
            base = False
        # Create texte
        createMesh = self._createSymbol(parent,name,base)
        
        mesh =  self._toMeshData(createMesh)
        node.setMeshData(mesh)

        active_build_plate = CuraApplication.getInstance().getMultiBuildPlateModel().activeBuildPlate
        node.addDecorator(BuildPlateDecorator(active_build_plate))
        node.addDecorator(SliceableObjectDecorator())

        stack = node.callDecoration("getStack") # created by SettingOverrideDecorator that is automatically added to CuraSceneNode
        settings = stack.getTop()

        # identification_mesh type
        definition = stack.getSettingDefinition("identification_mesh")
        new_instance = SettingInstance(definition, settings)
        new_instance.setProperty("value", True)
        new_instance.resetState()  # Ensure that the state is not seen as a user state.
        settings.addInstance(new_instance)

        if self._speed > 0 :
            # identification_mesh type
            definition = stack.getSettingDefinition("speed_layer_0")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", self._speed)
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance)
        
        if self._location != "Front" and self._location != "Front+Base" :
            # meshfix_union_all false
            definition = stack.getSettingDefinition("meshfix_union_all")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", False)
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance)
            
        if self._location == "Center (not filled)"  :
            # infill_sparse_density 0
            definition = stack.getSettingDefinition("infill_sparse_density")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", 0)
            new_instance.resetState()  
            settings.addInstance(new_instance)

            # wall_line_count 0
            definition = stack.getSettingDefinition("wall_line_count")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", 0)
            new_instance.resetState()  
            settings.addInstance(new_instance)

            # top_bottom_thickness 0
            definition = stack.getSettingDefinition("top_bottom_thickness")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", 0)
            new_instance.resetState()  
            settings.addInstance(new_instance)

            
        #op = GroupedOperation()
        # First add node to the scene at the correct position/scale, before parenting, so the support mesh does not get scaled with the parent
        self._op.addOperation(AddSceneNodeOperation(node, self._controller.getScene().getRoot()))
        self._op.addOperation(SetParentOperation(node, parent))
        #op.push()
        node.setPosition(position, CuraSceneNode.TransformSpace.World)
 
        CuraApplication.getInstance().getController().getScene().sceneChanged.emit(node)
        self._all_picked_node.append(node)
        
        Logger.log('d', '_createRecyclingSymbol')
        
        
    #----------------------------------------
    # Create Name Mesh
    #----------------------------------------
    def _createNameMesh(self, parent: CuraSceneNode, name):
        node = CuraSceneNode()

        # Logger.log("d", "_createNameMesh= %s", "Id-"+name)

        node_bounds = parent.getBoundingBox()
        # Logger.log("d", "width= %s", str(node_bounds.width))
        # Logger.log("d", "depth= %s", str(node_bounds.depth))
        # Logger.log("d", "Center X= %s", str(node_bounds.center.x))
        # Logger.log("d", "Center Y= %s", str(node_bounds.center.z))
        if self._location == "Front" or self._location == "Front+Base" :
            PosX = node_bounds.center.x
            PosY = node_bounds.center.z+0.5*node_bounds.depth + self._distance + self._size         
        else :
            PosX = node_bounds.center.x
            PosY = node_bounds.center.z + (self._size * 0.5)

        # Logger.log("d", "Pos X= %s", str(PosX))
        # Logger.log("d", "Pos Y= %s", str(PosY))
        
        position = Vector(PosX, 0, PosY)
                        
        node.setSelectable(True)
        node.setName("Id-"+name)   
        
        if self._location == "Front+Base" :
            base = True
        else :
            base = False
        # Create texte
        createMesh = self._createText(parent,name,base)
        
        mesh =  self._toMeshData(createMesh)
        node.setMeshData(mesh)

        active_build_plate = CuraApplication.getInstance().getMultiBuildPlateModel().activeBuildPlate
        node.addDecorator(BuildPlateDecorator(active_build_plate))
        node.addDecorator(SliceableObjectDecorator())

        stack = node.callDecoration("getStack") # created by SettingOverrideDecorator that is automatically added to CuraSceneNode
        settings = stack.getTop()

        # identification_mesh type
        definition = stack.getSettingDefinition("identification_mesh")
        new_instance = SettingInstance(definition, settings)
        new_instance.setProperty("value", True)
        new_instance.resetState()  # Ensure that the state is not seen as a user state.
        settings.addInstance(new_instance)

        if self._speed > 0 :
            # identification_mesh type
            definition = stack.getSettingDefinition("speed_layer_0")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", self._speed)
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance)
        
        if self._location != "Front" and self._location != "Front+Base" :
            # meshfix_union_all false
            definition = stack.getSettingDefinition("meshfix_union_all")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", False)
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance)
            
        if self._location == "Center (not filled)"  :
            # infill_sparse_density 0
            definition = stack.getSettingDefinition("infill_sparse_density")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", 0)
            new_instance.resetState()  
            settings.addInstance(new_instance)

            # wall_line_count 0
            definition = stack.getSettingDefinition("wall_line_count")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", 0)
            new_instance.resetState()  
            settings.addInstance(new_instance)

            # top_bottom_thickness 0
            definition = stack.getSettingDefinition("top_bottom_thickness")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", 0)
            new_instance.resetState()  
            settings.addInstance(new_instance)

            
        #op = GroupedOperation()
        # First add node to the scene at the correct position/scale, before parenting, so the support mesh does not get scaled with the parent
        self._op.addOperation(AddSceneNodeOperation(node, self._controller.getScene().getRoot()))
        self._op.addOperation(SetParentOperation(node, parent))
        #op.push()
        node.setPosition(position, CuraSceneNode.TransformSpace.World)
 
        CuraApplication.getInstance().getController().getScene().sceneChanged.emit(node)
        self._all_picked_node.append(node)
        
        Logger.log('d', '_createNameMesh')

    #----------------------------------------
    # Remove All Id Mesh
    #----------------------------------------
    def removeAllIdMesh(self):
        self._idcount = 0
        if self._all_picked_node:
            for node in self._all_picked_node:
                self._removeIdMesh(node)
            self._all_picked_node = []
            self.propertyChanged.emit()
        else:        
            for node in DepthFirstIterator(self._application.getController().getScene().getRoot()):
                if node.callDecoration("isSliceable"):
                    # N_Name=node.getName()
                    # Logger.log('d', 'isSliceable : ' + str(N_Name))
                    node_stack=node.callDecoration("getStack")           
                    if node_stack:        
                        if node_stack.getProperty("identification_mesh", "value"):
                            # N_Name=node.getName()
                            # Logger.log('d', 'cutting_mesh : ' + str(N_Name)) 
                            self._removeIdMesh(node)


    def _removeIdMesh(self, node: CuraSceneNode):
        parent = node.getParent()
        if parent == self._controller.getScene().getRoot():
            parent = None

        op = RemoveSceneNodeOperation(node)
        op.push()

        if parent and not Selection.isSelected(parent):
            Selection.add(parent)

        CuraApplication.getInstance().getController().getScene().sceneChanged.emit(node)

    #--------------------------------------------------------------------------------------
    # Text Creation
    #  Use the 'character'.stl file present in the models directory
    #  If the 'character' cannot be use as a file name then use the unicode number (ord())
    #  And if this character doesn't exists then replace it by ?
    #--------------------------------------------------------------------------------------
    def _createText(self, node: CuraSceneNode, name, base):
        meshes = []
        offsetX=0
        
        Logger.log("d", "Node name= %s", name)

        Ident = name.upper()

        Ind = 0
        for cch in Ident:
            # Space Char
            if ord(cch) == 32:
                # 1 = one space size will be set at the end
                offsetX += 1
            # Tabulation Char
            elif ord(cch) == 9:
                offsetX += 2
            else:
                #Logger.log("d", "Char= %s",cch)        
                Filename = cch + ".stl"
                Folder = os.path.join("models",self._font)
                # Logger.log("d", "Folder= %s",Folder) 
                
                model_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), Folder, Filename)
                if not exists(model_definition_path) :
                    Filename = "{}.stl".format(ord(cch))
                    model_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), Folder, Filename)
                    # Logger.log("d", "Code = %s - > %s",ord(cch),Filename)
                    # Logger.log("d", "Filename Code = %s",Filename)
                
                # Use ? (Unicode 63) if the character is not defined. Must have a look to the log file to list the missing letter
                if not exists(model_definition_path) :  
                    Filename = "63.stl"
                    model_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), Folder, Filename)
                    Logger.log("d", "Unknow Recycling Code= %s",Ident)
                    
                # Logger.log("d", "Filename= %s",Filename)
                # Logger.log("d", "model_definition_path= %s",model_definition_path)
                mesh = trimesh.load(model_definition_path) 
                # Logger.log("d", "offsetX = {}",format(offsetX))            
                mesh.apply_transform(trimesh.transformations.translation_matrix([offsetX, 0, 0]))
                # Logger.log("d", "Mesh bounds = %s",str(mesh.bounds[1, 0]))            
                offsetX = mesh.bounds[1, 0]+self._kerning
            
                meshes.append(mesh)
                
                Ind += 1
                # Logger.log("d", "Ident= %s",str(Ind))

        origin = [0, 0, 0]
        DirX = [1, 0, 0]
        DirY = [0, 1, 0]
        DirZ = [0, 0, 1]
        
        if base :
            Ind += 1
            Filename = "base.stl"
            model_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), Folder, Filename)
            mesh = trimesh.load(model_definition_path) 
            mesh.apply_transform(trimesh.transformations.scale_matrix(offsetX, origin, DirX))
            meshes.append(mesh)
            
        if Ind == 1 :
            combined = mesh           
        else :
            # Logger.log("d", "model_definition_path= %s",str(meshes))
            combined = trimesh.util.concatenate(meshes) 
        
        if base :
            combined.apply_transform(trimesh.transformations.translation_matrix([0, 0, 1]))
        
        # Logger.log("d", "Combined bounds = %s",str(combined.bounds))
        median = -(0.5*(combined.bounds[1, 0]-combined.bounds[0, 0])+combined.bounds[0, 0])
        #Logger.log("d", "combined= %s",str(median))
        combined.apply_transform(trimesh.transformations.translation_matrix([median, 0, 0]))            
        

        combined.apply_transform(trimesh.transformations.scale_matrix(self._size, origin, DirX))
        combined.apply_transform(trimesh.transformations.scale_matrix(self._size, origin, DirY))
        combined.apply_transform(trimesh.transformations.scale_matrix(self._height, origin, DirZ))
        
        # Mirror the text for option Middle
        if self._location != "Front" and self._location != "Front+Base" :
            combined.apply_transform(trimesh.transformations.reflection_matrix(origin, DirX))
            
        return combined
        
    #--------------------------------------------------------------------------------------
    # Symbol Creation
    #  Use the 'character'.stl file present in the models directory
    #  If the 'character' cannot be use as a file name then use the unicode number (ord())
    #  And if this character doesn't exists then replace it by ?
    #--------------------------------------------------------------------------------------
    def _createSymbol(self, node: CuraSceneNode, name, base):
        meshes = []
        offsetX=0
        
        Logger.log("d", "Symbol name= %s", name)

        Ident = name.upper()

        Ind = 0

        #Logger.log("d", "Char= %s",cch)        
        Filename = Ident + ".stl"
        Folder = os.path.join("models","Recyling Symbol")

        model_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), Folder, Filename)
        Logger.log("d", "Folder= %s",model_definition_path) 
        
        # Use ? (Unicode 63) if the character is not defined. Must have a look to the log file to list the missing letter
        if not exists(model_definition_path) :  
            Filename = "63.stl"
            model_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), Folder, Filename)
            
        # Logger.log("d", "Filename= %s",Filename)
        # Logger.log("d", "model_definition_path= %s",model_definition_path)
        mesh = trimesh.load(model_definition_path) 
        # Logger.log("d", "offsetX = {}",format(offsetX))            
        mesh.apply_transform(trimesh.transformations.translation_matrix([offsetX, 0, 0]))
        # Logger.log("d", "Mesh bounds = %s",str(mesh.bounds[1, 0]))            
        offsetX = mesh.bounds[1, 0]+self._kerning
    
        meshes.append(mesh)
            
        Ind += 1
        # Logger.log("d", "Ident= %s",str(Ind))

        origin = [0, 0, 0]
        DirX = [1, 0, 0]
        DirY = [0, 1, 0]
        DirZ = [0, 0, 1]
        
        if base :
            Ind += 1
            Filename = "base.stl"
            model_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), Folder, Filename)
            mesh = trimesh.load(model_definition_path) 
            mesh.apply_transform(trimesh.transformations.scale_matrix(offsetX, origin, DirX))
            meshes.append(mesh)
            
        if Ind == 1 :
            combined = mesh           
        else :
            # Logger.log("d", "model_definition_path= %s",str(meshes))
            combined = trimesh.util.concatenate(meshes) 
        
        if base :
            combined.apply_transform(trimesh.transformations.translation_matrix([0, 0, 1]))
        
        # Logger.log("d", "Combined bounds = %s",str(combined.bounds))
        median = -(0.5*(combined.bounds[1, 0]-combined.bounds[0, 0])+combined.bounds[0, 0])
        #Logger.log("d", "combined= %s",str(median))
        combined.apply_transform(trimesh.transformations.translation_matrix([median, 0, 0]))            
        

        combined.apply_transform(trimesh.transformations.scale_matrix(self._size, origin, DirX))
        combined.apply_transform(trimesh.transformations.scale_matrix(self._size, origin, DirY))
        combined.apply_transform(trimesh.transformations.scale_matrix(self._height, origin, DirZ))
        
        # Mirror the text for option Middle
        if self._location != "Front" and self._location != "Front+Base" :
            combined.apply_transform(trimesh.transformations.reflection_matrix(origin, DirX))
            
        return combined