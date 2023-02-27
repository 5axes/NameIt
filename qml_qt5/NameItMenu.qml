// Copyright (c) 2023 5@xes
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Dialogs 1.2
import QtQuick.Window 2.1

import UM 1.2 as UM
import Cura 1.0 as Cura

Menu
{
    id: base
    
	title: catalog.i18nc("@item:inmenu", "Name It!")
	
	MenuItem
	{
		text: catalog.i18nc("@item:inmenu", "Add Number")
		onTriggered: manager.addPartName("Number")
	}
	MenuItem
	{
		text: catalog.i18nc("@item:inmenu", "Add Number From Part")
		onTriggered: manager.addPartName("NameNumber")
	}		
	MenuItem
	{
		text: catalog.i18nc("@item:inmenu", "Add Name")
		onTriggered: manager.addPartName("Name")
	}
	MenuItem
	{
		text: catalog.i18nc("@item:inmenu", "Add Recycling Symbol")
		onTriggered: manager.addRecyclingSymbol()
	}
	MenuItem
	{
		text: catalog.i18nc("@item:inmenu", "Remove Identifier")
		enabled: UM.Selection.hasSelection
		onTriggered: manager.removeSelectIdMesh()
	}
	MenuItem
	{
		text: catalog.i18nc("@item:inmenu", "Rename models")
		enabled: UM.Selection.hasSelection
		onTriggered: manager.renameMesh()
	}	
	MenuItem
	{
		text: catalog.i18nc("@item:inmenu", "Define Text Parameters")
		onTriggered: manager.defaultSize()
	}
    function moveToContextMenu(contextMenu)
    {
        for(var i in base.items)
        {
            contextMenu.items[0].insertItem(i,base.items[i])
        }
    }

    UM.I18nCatalog { id: catalog; name: "nameit" }
}
