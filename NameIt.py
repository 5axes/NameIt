#-----------------------------------------------------------------------------------
# Copyright (c) 2022 5@xes
#
# The NameIt plugin is released under the terms of the AGPLv3 or higher.
# Modifications 5@xes 2020-2022
#-----------------------------------------------------------------------------------
# V1.0.0    : First Proof
#
#-----------------------------------------------------------------------------------

VERSION_QT5 = False
try:
    from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl
    from PyQt6.QtGui import QDesktopServices
except ImportError:
    from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl
    from PyQt5.QtGui import QDesktopServices
    VERSION_QT5 = True
    
# Imports from the python standard library to build the plugin functionality
import os
import sys
import re
import math
import numpy
import trimesh
import shutil
from shutil import copyfile

from typing import Optional, List

from UM.Math.Vector import Vector

from UM.Extension import Extension
from UM.PluginRegistry import PluginRegistry
from UM.Application import Application
from cura.CuraApplication import CuraApplication

from UM.Mesh.MeshData import MeshData, calculateNormalsFromIndexedVertices
from UM.Resources import Resources
from UM.Settings.SettingInstance import SettingInstance
from cura.Scene.CuraSceneNode import CuraSceneNode
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection
from cura.Scene.SliceableObjectDecorator import SliceableObjectDecorator
from cura.Scene.BuildPlateDecorator import BuildPlateDecorator
from cura.Scene.CuraSceneNode import CuraSceneNode
from cura.Operations.SetParentOperation import SetParentOperation
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Operations.GroupedOperation import GroupedOperation
from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation
from UM.Operations.SetTransformOperation import SetTransformOperation
from UM.Mesh.MeshBuilder import MeshBuilder

from cura.CuraVersion import CuraVersion  # type: ignore
from UM.Version import Version

from UM.Logger import Logger
from UM.Message import Message

from UM.i18n import i18nCatalog

catalog = i18nCatalog("cura")

#This class is the extension and doubles as QObject to manage the qml    
class NameIt(QObject, Extension):
    #Create an api
    from cura.CuraApplication import CuraApplication
    api = CuraApplication.getInstance().getCuraAPI()
    
    # The QT signal, which signals an update for user information text
    userInfoTextChanged = pyqtSignal()
    userSizeChanged = pyqtSignal()
    userHeightChanged = pyqtSignal()
    userDistanceChanged = pyqtSignal()
    
    def __init__(self, parent = None) -> None:
        QObject.__init__(self, parent)
        Extension.__init__(self)
       

        # Stock Data  
        self._all_picked_node = []
        
        
        #Inzialize varables
        self.userText = ""
        self._continueDialog = None
        
        # set the preferences to store the default value
        self._application = CuraApplication.getInstance()
        self._preferences = self._application.getPreferences()
        self._preferences.addPreference("NameIt/size", 10)
        self._preferences.addPreference("NameIt/height", 0.2)
        self._preferences.addPreference("NameIt/distance", 3)
        
        # convert as float to avoid further issue
        self._size = float(self._preferences.getValue("NameIt/size"))
        self._height = float(self._preferences.getValue("NameIt/height"))
        self._distance = float(self._preferences.getValue("NameIt/distance"))
        
        # Suggested solution from fieldOfView . in this discussion solved in Cura 4.9
        # https://github.com/5axes/Calibration-Shapes/issues/1
        # Cura are able to find the scripts from inside the plugin folder if the scripts are into a folder named resources
        Resources.addSearchPath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources"))
 
        self.Major=1
        self.Minor=0

        # Logger.log('d', "Info Version CuraVersion --> " + str(Version(CuraVersion)))
        Logger.log('d', "Info CuraVersion --> " + str(CuraVersion))
        
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
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add Number"), self.addNumber)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Add Name"), self.addPartName)
        self.addMenuItem(" ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Remove All"), self.removeAllIdMesh)
        self.addMenuItem("  ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Define default size"), self.defaultSize)
        self.addMenuItem("   ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Help"), self.gotoHelp)
  
        #Inzialize varables
        self.userText = ""
        self._continueDialog = None
        
    # Define the default value pour the standard element
    def defaultSize(self) -> None:
 
        if self._continueDialog is None:
            self._continueDialog = self._createDialogue()
        self._continueDialog.show()
        #self.userSizeChanged.emit()

    #====User Input=====================================================================================================
    @pyqtProperty(str, notify= userHeightChanged)
    def heightInput(self):
        return str(self._height)
        
    @pyqtProperty(str, notify= userDistanceChanged)
    def distanceInput(self):
        return str(self._distance)
        
    @pyqtProperty(str, notify= userSizeChanged)
    def sizeInput(self):
        return str(self._size)
        
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
            self.userMessage("Entered size invalid: " + text,"wrong")
            return
        self._size = float(text)

        #Check if positive
        if self._size <= 0:
            self.userMessage("Size value must be positive !","wrong")
            self._size = 20
            return

        self.writeToLog("Set NameIt/size printFromHeight to : " + text)
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
            self.userMessage("Entered height invalid: " + text,"wrong")
            return
        self._height = float(text)

        #Check if positive
        if self._height <= 0:
            self.userMessage("Height value must be positive !","wrong")
            self._height = 0.2
            return

        self.writeToLog("Set NameIt/height printFromHeight to : " + text)
        self._preferences.setValue("NameIt/height", self._height)
        
        #clear the message Field
        self.userMessage("", "ok")

    def getDistance(self) -> float:
    
        return self._distance
        
    # is called when a key gets released in the distance inputField (twice for some reason)
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
            self.userMessage("Entered distance invalid: " + text,"wrong")
            return
        self._distance = float(text)

        self.writeToLog("Set NameIt/distance printFromDistance to : " + text)
        self._preferences.setValue("NameIt/distance", self._distance)
        
        #clear the message Field
        self.userMessage("", "ok")
        
    #===== Text Output ===================================================================================================
    #writes the message to the log, includes timestamp, length is fixed
    def writeToLog(self, str):
        Logger.log("d", "Debug calibration shapes = %s", str)

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
     
    # Add Part Name  as text  
    def addPartName(self) -> None:
 
        nodes_list = self._getAllSelectedNodes()
        if not nodes_list:
            nodes_list = DepthFirstIterator(self._application.getController().getScene().getRoot())
        
        for node in nodes_list:
            if node.callDecoration("isSliceable"):           
                Logger.log('d', "isSliceable : {}".format(node.getName()))
                node_stack=node.callDecoration("getStack")           
                if node_stack: 
                    type_infill_mesh = node_stack.getProperty("infill_mesh", "value")
                    type_cutting_mesh = node_stack.getProperty("cutting_mesh", "value")
                    type_support_mesh = node_stack.getProperty("support_mesh", "value")
                    type_anti_overhang_mesh = node_stack.getProperty("anti_overhang_mesh", "value") 
                    
                    if not type_infill_mesh and not type_support_mesh and not type_anti_overhang_mesh :
                        # and Selection.isSelected(node)
                        Logger.log('d', "Mesh : {}".format(node.getName()))

                        self._createNameMesh(node, node.getName())
                  
    # Add Number  as text     
    def addNumber(self) -> None:
        
        nodes_list = self._getAllSelectedNodes()
        if not nodes_list:
            nodes_list = DepthFirstIterator(self._application.getController().getScene().getRoot())
        
        Id = 0
        for node in nodes_list:
            if node.callDecoration("isSliceable"):
                node_stack=node.callDecoration("getStack")           
                if node_stack: 
                    type_infill_mesh = node_stack.getProperty("infill_mesh", "value")
                    type_cutting_mesh = node_stack.getProperty("cutting_mesh", "value")
                    type_support_mesh = node_stack.getProperty("support_mesh", "value")
                    type_anti_overhang_mesh = node_stack.getProperty("anti_overhang_mesh", "value") 
                    
                    if not type_infill_mesh and not type_support_mesh and not type_anti_overhang_mesh :            
                        name = node.getName()
                        Id += 1
                        Logger.log("d", "name= %s", name)
                        
                        # filename = node.getMeshData().getFileName() 
                        # Logger.log("d", "filename= %s", name)

                        
                        self._createNameMesh(node, Ident)
                    
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

    def _createNameMesh(self, parent: CuraSceneNode, name):
        node = CuraSceneNode()

        Logger.log("d", "_createNameMesh= %s", "Id-"+name)


        node_bounds = parent.getBoundingBox()
        Logger.log("d", "width= %s", str(node_bounds.width))
        Logger.log("d", "depth= %s", str(node_bounds.depth))
        Logger.log("d", "Center X= %s", str(node_bounds.center.x))
        Logger.log("d", "Center Y= %s", str(node_bounds.center.z))

        PosX = node_bounds.center.x
        PosY = node_bounds.center.z+0.5*node_bounds.depth

        Logger.log("d", "Pos X= %s", str(PosX))
        Logger.log("d", "Pos Y= %s", str(PosY))
        
        position = Vector(PosX, 0, PosY)
                        
        node.setSelectable(True)
        node.setName("Id-"+name)   
        
        # Create texte
        createMesh = self._createText(parent,name)
        
        mesh =  self._toMeshData(createMesh)
        node.setMeshData(mesh)

        active_build_plate = CuraApplication.getInstance().getMultiBuildPlateModel().activeBuildPlate
        node.addDecorator(BuildPlateDecorator(active_build_plate))
        node.addDecorator(SliceableObjectDecorator())

        stack = node.callDecoration("getStack") # created by SettingOverrideDecorator that is automatically added to CuraSceneNode
        settings = stack.getTop()

        # cutting_mesh type
        #definition = stack.getSettingDefinition("cutting_mesh")
        #new_instance = SettingInstance(definition, settings)
        #new_instance.setProperty("value", True)
        #new_instance.resetState()  # Ensure that the state is not seen as a user state.
        #settings.addInstance(new_instance)


        op = GroupedOperation()
        # First add node to the scene at the correct position/scale, before parenting, so the support mesh does not get scaled with the parent
        op.addOperation(AddSceneNodeOperation(node, self._controller.getScene().getRoot()))
        op.addOperation(SetParentOperation(node, parent))
        op.push()
        node.setPosition(position, CuraSceneNode.TransformSpace.World)
 
        CuraApplication.getInstance().getController().getScene().sceneChanged.emit(node)
        self._all_picked_node.append(node)
        
        Logger.log('d', '_createNameMesh')

    def removeAllIdMesh(self):
        if self._all_picked_node:
            for node in self._all_picked_node:
                self._removeSupportMesh(node)
            self._all_picked_node = []
            self.propertyChanged.emit()
        else:        
            for node in DepthFirstIterator(self._application.getController().getScene().getRoot()):
                if node.callDecoration("isSliceable"):
                    # N_Name=node.getName()
                    # Logger.log('d', 'isSliceable : ' + str(N_Name))
                    node_stack=node.callDecoration("getStack")           
                    if node_stack:        
                        if node_stack.getProperty("cutting_mesh", "value"):
                            # N_Name=node.getName()
                            # Logger.log('d', 'cutting_mesh : ' + str(N_Name)) 
                            self._removeSupportMesh(node)


    def _removeSupportMesh(self, node: CuraSceneNode):
        parent = node.getParent()
        if parent == self._controller.getScene().getRoot():
            parent = None

        op = RemoveSceneNodeOperation(node)
        op.push()

        if parent and not Selection.isSelected(parent):
            Selection.add(parent)

        CuraApplication.getInstance().getController().getScene().sceneChanged.emit(node)
        
    # Text Creation
    def _createText(self, node: CuraSceneNode, name):
        meshes = []
        
        Logger.log("d", "name= %s", name)
        
        # filename = node.getMeshData().getFileName() 
        # Logger.log("d", "filename= %s", name)

        node_bounds = node.getBoundingBox()
        Logger.log("d", "width= %s", str(node_bounds.width))
        Logger.log("d", "depth= %s", str(node_bounds.depth))
        Logger.log("d", "Center X= %s", str(node_bounds.center.x))
        Logger.log("d", "Center Y= %s", str(node_bounds.center.z))
        
        Ident = name.upper()

        PosX = node_bounds.center.x
        PosY = node_bounds.center.z+0.5*node_bounds.depth

        Logger.log("d", "Pos X= %s", str(PosX))
        Logger.log("d", "Pos Y= %s", str(PosY))
        
        Ind = 0
        for chiffre in Ident:          
            Filename = chiffre + ".stl"
            Logger.log("d", "Filename= %s",Filename) 
            model_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", Filename)
            # Logger.log("d", "model_definition_path= %s",model_definition_path)
            mesh = trimesh.load(model_definition_path)
                       
            mesh.apply_transform(trimesh.transformations.translation_matrix([(1.1*Ind), 0, 0]))
            meshes.append(mesh)
                
            Ind += 1
            Logger.log("d", "Ident= %s",str(Ind))
        
        if Ind == 1 :
            combined = mesh           
        else :
            Logger.log("d", "model_definition_path= %s",str(meshes))
            combined = trimesh.util.concatenate(meshes)  

        Logger.log("d", "combined= %s",str(combined.bounds))
        median = -(0.5*(combined.bounds[1, 0]-combined.bounds[0, 0])+combined.bounds[0, 0])
        Logger.log("d", "combined= %s",str(combined.bounds[0, 0]))
        Logger.log("d", "combined= %s",str(combined.bounds[1, 0]))
        Logger.log("d", "combined= %s",str(median))
        combined.apply_transform(trimesh.transformations.translation_matrix([median, 0, 0]))            
        
        origin = [0, 0, 0]
        DirX = [1, 0, 0]
        DirY = [0, 1, 0]
        DirZ = [0, 0, 1]
        combined.apply_transform(trimesh.transformations.scale_matrix(self._size, origin, DirX))
        combined.apply_transform(trimesh.transformations.scale_matrix(self._size, origin, DirY))
        combined.apply_transform(trimesh.transformations.scale_matrix(self._height, origin, DirZ))
        
        combined.apply_transform(trimesh.transformations.translation_matrix([PosX, -(PosY+self._distance), 0]))
        
        return combined