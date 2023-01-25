// Import the standard GUI elements from QTQuick
import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.1
import QtQuick.Window 2.2

// Import the Uranium GUI elements, which are themed for Cura
import UM 1.1 as UM
import Cura 1.0 as Cura

// Dialog
Window
{
    id: base
	UM.I18nCatalog { id: catalog; name: "nameit"}

    title: "Name It ! Parameters"

    color: "#fafafa" //Background color of cura: #fafafa

    // NonModal like that the dialog to block input in the main window
    modality: Qt.NonModal

    // WindowStaysOnTopHint to stay on top
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint

    // Setting the dimensions of the dialog window
    width: 320
    height: 330
    minimumWidth: 320
    minimumHeight: 330

    // Position of the window
    x: Screen.width*0.5 - width - 50
    y: 400 

    // Define a Window a border (Red for) and a background color
    Rectangle {
        id: bg_rect
        width: 320
        height: 330
        color: "#fff"
        border.color: "#D22"
        border.width: 3
        radius: 4
    }

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
    Button
    {
        id: close_button
        text: "<font color='#ffffff'>" + "x" + "</font>"
        width: 25
        height: 25

        anchors.top: parent.top
        anchors.topMargin: 10
        anchors.right: parent.right
        anchors.rightMargin: 10

        tooltip: catalog.i18nc("@tooltip", "Close this dialog box")

        style: ButtonStyle{
            background: Rectangle {
                implicitWidth: 100
                implicitHeight: 25
                radius: 3
                color: "#D22"
            }
        }

        onClicked:
        {
            base.close();
        }
    }

    //Textfield for User Messages
    Text
    {
        id: user_text

        width: 300
        anchors.top: parent.top
        anchors.topMargin: 2
        anchors.left: parent.left
        anchors.leftMargin: 10

        text: userInfoText

        font.family: "Arial"
        font.pointSize: 10
        //The color gets overwritten by the html tags added to the text
        color: "black"

        wrapMode: Text.Wrap
    }
	
    //Text "Size: "
    Text
    {
        id: label_size
		width: 150
        text: catalog.i18nc("@label", "Size :")
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: close_button.top
        anchors.topMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 10
    }

    //User input of height
    TextField
    {
        id: size_input
        width: 80
        text: sizeInput
		// "ie. 20.0"

        anchors.top: label_size.top
        anchors.topMargin: -2
        anchors.left: label_size.right
        anchors.leftMargin: 10

		font.family: "Arial"
        font.pointSize: 12

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

    // Text: "mm"
    Text
    {
        id: text_unit_1
        text: "mm"
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.bottom: size_input.bottom
        anchors.bottomMargin: 0
        anchors.left: size_input.right
        anchors.leftMargin: 5
    }

    //Text "Height: "
    Text
    {
        id: label_height
		width: 150
        text: catalog.i18nc("@label", "Height :")
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: size_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }

    //User input of height
    TextField
    {
        id: height_input
        width: 80
        text: heightInput
		// "ie. 0.4"

        anchors.top: label_height.top
        anchors.topMargin: -2
        anchors.left: label_height.right
        anchors.leftMargin: 10

		font.family: "Arial"
        font.pointSize: 12

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

    // Text: "mm"
    Text
    {
        id: text_unit_2
        text: "mm"
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.bottom: height_input.bottom
        anchors.bottomMargin: 0
        anchors.left: height_input.right
        anchors.leftMargin: 5
    }
	
    //Text "Distance: "
    Text
    {
        id: label_distance
		width: 150
        text: catalog.i18nc("@label", "Distance :")
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: height_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }

    //User input of distance
    TextField
    {
        id: distance_input
        width: 80
        text: distanceInput
		// "ie. 20.0"

        anchors.top: label_distance.top
        anchors.topMargin: -2
        anchors.left: label_distance.right
        anchors.leftMargin: 10

		font.family: "Arial"
        font.pointSize: 12

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

    // Text: "mm"
    Text
    {
        id: text_unit_3
        text: "mm"
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.bottom: distance_input.bottom
        anchors.bottomMargin: 0
        anchors.left: distance_input.right
        anchors.leftMargin: 5
    }

    //Text "Kerning: "
    Text
    {
        id: label_kerning
		width: 150
        text: catalog.i18nc("@label", "Kerning :")
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: distance_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }

    //User input of kerning
    TextField
    {
        id: kerning_input
        width: 80
        text: kerningInput
		// "ie. 2.0"

        anchors.top: label_kerning.top
        anchors.topMargin: -2
        anchors.left: label_kerning.right
        anchors.leftMargin: 10

		font.family: "Arial"
        font.pointSize: 12

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

    // Text: "mm"
    Text
    {
        id: text_unit_4
        text: "mm"
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.bottom: kerning_input.bottom
        anchors.bottomMargin: 0
        anchors.left: kerning_input.right
        anchors.leftMargin: 5
    }
	
    // Label "Suffix :"
    Text
    {
        id: label_prefix
		width: 150
        text: catalog.i18nc("@label", "Number Prefix :")
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: kerning_input.bottom
        anchors.topMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 10
    }
	
	//Text prefix_input
    TextField
    {
        id: prefix_input
		width: 100
        text: prefixInput
        font.family: "Arial"
        font.pointSize: 12

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
    Text
    {
        id: label_suffix
		width: 150
        text: catalog.i18nc("@label", "Number Suffix :")
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: label_prefix.bottom
        anchors.topMargin: 8
        anchors.left: parent.left
        anchors.leftMargin: 10
    }
	
	//Text suffix_input
    TextField
    {
        id: suffix_input
		width: 100
        text: suffixInput
        font.family: "Arial"
        font.pointSize: 12

        anchors.top: label_suffix.top
        anchors.topMargin: 8
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

    //Text "Initial Layer Speed : "
    Text
    {
        id: label_speed
		width: 150
        text: catalog.i18nc("@label", "Initial Layer Speed :")
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: suffix_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }

    //User input of kerning
    TextField
    {
        id: speed_input
        width: 80
        text: speedInput
		// "ie. 12"

        anchors.top: label_speed.top
        anchors.topMargin: -2
        anchors.left: label_speed.right
        anchors.leftMargin: 10

		font.family: "Arial"
        font.pointSize: 12

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

    // Text: "mm/s"
    Text
    {
        id: text_unit_5
        text: "mm/s"
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.bottom: speed_input.bottom
        anchors.bottomMargin: 0
        anchors.left: speed_input.right
        anchors.leftMargin: 5
    }

    //Text "Initial Layer Speed : "
    Text
    {
        id: label_font
		width: 150
        text: catalog.i18nc("@label", "Font :")
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: speed_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }	
	
	ComboBox {
		id: fontComboType
		width: 130
		height: UM.Theme.getSize("setting_control").height
		objectName: "Font_Type"
		visible:true
        anchors.top: label_font.top
        anchors.topMargin: -2
        anchors.left: label_font.right
		anchors.leftMargin: 10
		
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

    //Text "Location :"
    Text
    {
        id: label_location
		width: 150
        text: catalog.i18nc("@label", "Location :")
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: label_font.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }	
	
	ComboBox {
		id: locationComboType
		width: 130
		height: UM.Theme.getSize("setting_control").height
		objectName: "Location_Type"
		visible:true
        anchors.top: label_location.top
        anchors.topMargin: -2
        anchors.left: label_location.right
		anchors.leftMargin: 10
		
		model: ListModel {
		   id: locItems
		   ListElement { text: catalog.i18nc("@option", "Front")}
		   ListElement { text: catalog.i18nc("@option", "Front+Base")}
		   ListElement { text: catalog.i18nc("@option", "Center")}
		   ListElement { text: catalog.i18nc("@option", "Center (not filled)")}
		}

		Component.onCompleted: currentIndex = find(locationInput)
		
		onCurrentIndexChanged: 
		{ 
			manager.locationEntered(locItems.get(currentIndex).text)
		}
	}
}
