// Import the standard GUI elements from QTQuick
import QtQuick 6.0
import QtQuick.Controls 6.0

// Imports the Uranium GUI elements, which are themed for Cura.
import UM 1.6 as UM

// Imports the Cura GUI elements.
import Cura 1.7 as Cura


// UM.Dialog
UM.Dialog
{
    id: base
	
	property variant catalog: UM.I18nCatalog { name: "nameit" }

    title: catalog.i18nc("@title", "Name It ! Parameters")

    // Setting the dimensions of the dialog window
    width: 300
    height: 300
    minimumWidth: 300
    minimumHeight: 300

    // Position of the window
    x: Screen.width*0.5 - width - 50
    y: 400 

    // Connecting our variable to the computed property of the manager
    property string userInfoText: manager.userInfoText
	
	property string sizeInput: manager.sizeInput
	property string heightInput: manager.heightInput
	property string distanceInput: manager.distanceInput
	property string kerningInput: manager.kerningInput
	property string prefixInput: manager.prefixInput
	property string suffixInput: manager.suffixInput
	property string speedInput: manager.speedInput
	property string fontInput: manager.fontInput
	property string locationInput: manager.locationInput

    // Button for closing the dialogbox
    // Text userInfoText for notification
    Text
    {
        id: user_text
		width:280
        text: userInfoText
        font.family: "Arial"
        font.pointSize: 10
        color: "black"

        anchors.top: close_button.top
        anchors.topMargin: 1
        anchors.left: parent.left
        anchors.leftMargin: 10
    }
	
    // Label "Size : "
    UM.Label
    {
        id: label_size
		width: 150
        text: catalog.i18nc("@label", "Size :")
        font: UM.Theme.getFont("default")
        color: UM.Theme.getColor("text")

        anchors.top: close_button.top
        anchors.topMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 10
    }

    // User input of Size
    UM.TextFieldWithUnit
    {
        id: size_input
        width: 90
        text: sizeInput
		// "ie. 20.0"

        anchors.top: label_size.top
        anchors.topMargin: -2
        anchors.left: label_size.right
        anchors.leftMargin: 10

		font: UM.Theme.getFont("default")
		
		unit: "mm"
		
        // Validate entered value
        Keys.onReturnPressed:
        {
			event.accepted = true
        }

        // Return the new entered value
        Keys.onReleased:
        {
            manager.sizeEntered(size_input.text)
        }
    }

    // Label "Height: "
    UM.Label
    {
        id: label_height
		width: 150
        text: catalog.i18nc("@label", "Height :")
        font: UM.Theme.getFont("default")
        color: UM.Theme.getColor("text")

        anchors.top: size_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }

    // User input of height
    UM.TextFieldWithUnit
    {
        id: height_input
        width: 90
        text: heightInput
		// "ie. 20.0"

        anchors.top: label_height.top
        anchors.topMargin: -2
        anchors.left: label_height.right
        anchors.leftMargin: 10

		font: UM.Theme.getFont("default")
		
		unit: "mm"
		
        // Validate entered value
        Keys.onReturnPressed:
        {
			event.accepted = true
        }

        // Return the new entered value
        Keys.onReleased:
        {
            manager.heightEntered(height_input.text)
        }
    }
	
	// Label "Distance : "
    UM.Label
    {
        id: label_distance
		width: 150
        text: catalog.i18nc("@label", "Distance :")
        font: UM.Theme.getFont("default")
        color: UM.Theme.getColor("text")

        anchors.top: height_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }

    // User input of distance
    UM.TextFieldWithUnit
    {
        id: distance_input
        width: 90
        text: distanceInput

        anchors.top: label_distance.top
        anchors.topMargin: -2
        anchors.left: label_distance.right
        anchors.leftMargin: 10

		font: UM.Theme.getFont("default")
		
		unit: "mm"
		
        // Validate entered value
        Keys.onReturnPressed:
        {
			event.accepted = true
        }

        // Return the new entered value
        Keys.onReleased:
        {
            manager.distanceEntered(distance_input.text)
        }
    }
	
	// Label "Kerning : "
    UM.Label
    {
        id: label_kerning
		width: 150
        text: catalog.i18nc("@label", "Kerning :")
        font: UM.Theme.getFont("default")
        color: UM.Theme.getColor("text")

        anchors.top: distance_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }

    // User input of kerning
    UM.TextFieldWithUnit
    {
        id: kerning_input
        width: 90
        text: kerningInput

        anchors.top: label_kerning.top
        anchors.topMargin: -2
        anchors.left: label_kerning.right
        anchors.leftMargin: 10

		font: UM.Theme.getFont("default")
		
		unit: "mm"
		
        // Validate entered value
        Keys.onReturnPressed:
        {
			event.accepted = true
        }

        // Return the new entered value
        Keys.onReleased:
        {
            manager.kerningEntered(kerning_input.text)
        }
    }

    // Label "Prefix :"
    UM.Label
    {
        id: label_prefix
		width: 150
        text: catalog.i18nc("@label", "Number Prefix :")
        font: UM.Theme.getFont("default")
        color: UM.Theme.getColor("text")

        anchors.top: kerning_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }
	
	// Text prefix_input
    UM.TextFieldWithUnit
    {
        id: prefix_input
		width: 90
        text: prefixInput
        font: UM.Theme.getFont("default")
		unit: ""

        anchors.top: label_prefix.top
        anchors.topMargin: -2
        anchors.left: label_prefix.right
        anchors.leftMargin: 10

        // Validate entered value
        Keys.onReturnPressed:
        {
			event.accepted = true
        }

        // Return the new entered value
        Keys.onReleased:
        {
            manager.prefixEntered(prefix_input.text)
        }		
    }

    // Label "Suffix :"
    UM.Label
    {
        id: label_suffix
		width: 150
        text: catalog.i18nc("@label", "Number Suffix :")
        font: UM.Theme.getFont("default")
        color: UM.Theme.getColor("text")

        anchors.top: prefix_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }
	
	// Text suffix_text
    UM.TextFieldWithUnit
    {
        id: suffix_input
		width: 90
        text: suffixInput
        font: UM.Theme.getFont("default")
		unit: ""

        anchors.top: label_suffix.top
        anchors.topMargin: -2
        anchors.left: label_suffix.right
        anchors.leftMargin: 10

        // Validate entered value
        Keys.onReturnPressed:
        {
			event.accepted = true
        }

        // Return the new entered value
        Keys.onReleased:
        {
            manager.suffixEntered(suffix_input.text)
        }			
    }	

    // Label "Initial Layer Speed :"
    UM.Label
    {
        id: label_speed
		width: 150
        text: catalog.i18nc("@label", "Initial Layer Speed :")
        font: UM.Theme.getFont("default")
        color: UM.Theme.getColor("text")

        anchors.top: suffix_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }
	
	// Text speed_input
    UM.TextFieldWithUnit
    {
        id: speed_input
		width: 90
        text: speedInput
        font: UM.Theme.getFont("default")
		unit: "mm/s"

        anchors.top: label_speed.top
        anchors.topMargin: -2
        anchors.left: label_speed.right
        anchors.leftMargin: 10

        // Validate entered value
        Keys.onReturnPressed:
        {
			event.accepted = true
        }

        // Return the new entered value
        Keys.onReleased:
        {
            manager.speedEntered(speed_input.text)
        }			
    }	
	
    // Label "Font :"
    UM.Label
    {
        id: label_font
		width: 150
        text: catalog.i18nc("@label", "Font :")
        font: UM.Theme.getFont("default")
        color: UM.Theme.getColor("text")

        anchors.top: speed_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }	
	
	Cura.ComboBox {
		id: fontComboType
		width: 120
		height: UM.Theme.getSize("setting_control").height
		objectName: "Font_Type"
		visible:true
        anchors.top: label_font.top
        anchors.topMargin: -2
        anchors.left: label_font.right
		anchors.leftMargin: 10
		textRole: "text"
		model: ListModel {
		   id: cbItems
		   // ListElement { text: "Arial Rounded MT"}
		   // ListElement { text: "Gill Sans MT"}
		   ListElement { text: "NameIt Rounded"}
		   ListElement { text: "Noto Sans"}
		   ListElement { text: "Odin Rounded"}
		}

		Component.onCompleted: currentIndex = find(fontInput)
		
		onCurrentIndexChanged: 
		{ 
			manager.fontEntered(cbItems.get(currentIndex).text)
		}
	}	

    // Label "Location :"
    UM.Label
    {
        id: label_location
		width: 150
        text: catalog.i18nc("@label", "Location :")
        font: UM.Theme.getFont("default")
        color: UM.Theme.getColor("text")

        anchors.top: label_font.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }	
	
	Cura.ComboBox {
		id: locationComboType
		width: 120
		height: UM.Theme.getSize("setting_control").height
		objectName: "Location_Type"
		visible:true
        anchors.top: label_location.top
        anchors.topMargin: -2
        anchors.left: label_location.right
		anchors.leftMargin: 10
		textRole: "text"
		model: ListModel {
		   id: locItems
		   ListElement { text: "Front"}
		   ListElement { text: "Front+Base"}
		   ListElement { text: "Center"}
		   ListElement { text: "Center (not filled)"}
		}

		Component.onCompleted: currentIndex = find(locationInput)
		
		onCurrentIndexChanged: 
		{ 
			manager.locationEntered(locItems.get(currentIndex).text)
		}
	}		
}
