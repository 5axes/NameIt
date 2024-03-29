// Copyright (c) 2023 5@xes

import QtQuick 2.2
import QtQuick.Controls 2.0

import UM 1.2 as UM

UM.Dialog
{
    minimumWidth: 550
    minimumHeight: 60
    function boolCheck(value) //Hack to ensure a good match between python and qml.
    {
        if(value == "True")
        {
            return true
        }else if(value == "False" || value == undefined)
        {
            return false
        }
        else
        {
            return value
        }
    }

    property variant i18n_catalog: UM.I18nCatalog { name: "nameit" }
	
    title: i18n_catalog.i18nc("@title", "Name It plugin settings")

    CheckBox
    {
        checked: boolCheck(UM.Preferences.getValue("NameIt/context_menu"))
        onClicked: UM.Preferences.setValue("NameIt/context_menu", checked)

        text: i18n_catalog.i18nc("@label", "Add Name It as context menu (restart Cura to apply change)")
    }
}