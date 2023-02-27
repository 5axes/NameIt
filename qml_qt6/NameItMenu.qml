// Copyright (c) 2023 5@xes
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1

import UM 1.2 as UM
import Cura 1.0 as Cura

Cura.Menu
{
    Cura.Menu
    {
        id: nameITMenu

        title: catalog.i18nc("@title", "Name It !")

        Cura.MenuItem
		{
			text: catalog.i18nc("@item:inmenu", "Add Number")
			onTriggered: manager.addPartName("Number")
		}
        Cura.MenuItem
		{
			text: catalog.i18nc("@item:inmenu", "Add Number From Part")
			onTriggered: manager.addPartName("NameNumber")
		}		
        Cura.MenuItem
        {
            text: catalog.i18nc("@item:inmenu", "Add Name")
            onTriggered: manager.addPartName("Name")
        }
        Cura.MenuItem
        {
            text: catalog.i18nc("@item:inmenu", "Add Recycling Symbol")
            onTriggered: manager.addRecyclingSymbol()
        }
        Cura.MenuItem
        {
            text: catalog.i18nc("@item:inmenu", "Remove Identifier")
            enabled: UM.Selection.hasSelection
            onTriggered: manager.removeSelectIdMesh()
        }
        Cura.MenuItem
        {
            text: catalog.i18nc("@item:inmenu", "Rename models")
            enabled: UM.Selection.hasSelection
            onTriggered: manager.renameMesh()
        }	
        Cura.MenuItem
        {
            text: catalog.i18nc("@item:inmenu", "Define Text Parameters")
            onTriggered: manager.defaultSize()
        }			
    }
    Cura.MenuSeparator
    {
        id: nameITSeparator
    }

    function moveToContextMenu(contextMenu)
    {
        contextMenu.insertItem(0, nameITSeparator)
        contextMenu.insertMenu(0, nameITMenu)
    }

    UM.I18nCatalog { id: catalog; name: "nameit" }
}
