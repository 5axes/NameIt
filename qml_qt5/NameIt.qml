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

    title: "Name It ! Parameters"

    color: "#fafafa" //Background color of cura: #fafafa

    // NonModal like that the dialog to block input in the main window
    modality: Qt.NonModal

    // WindowStaysOnTopHint to stay on top
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint

    // Setting the dimensions of the dialog window
    width: 250
    height: 230
    minimumWidth: 250
    minimumHeight: 230

    // Position of the window
    x: Screen.width*0.5 - width - 50
    y: 400 

    // Define a Window a border (Red for) and a background color
    Rectangle {
        id: bg_rect
        width: 250
        height: 230
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

        tooltip: "Close this dialog box"

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

        width: 280
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
        id: text_size
		width:90
        text: "Size:"
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

        anchors.top: text_size.top
        anchors.topMargin: -2
        anchors.left: text_size.right
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
        id: text_height
		width:90
        text: "Height:"
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
		// "ie. 20.0"

        anchors.top: text_height.top
        anchors.topMargin: -2
        anchors.left: text_height.right
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
        id: text_distance
		width:90
        text: "Distance:"
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

        anchors.top: text_distance.top
        anchors.topMargin: -2
        anchors.left: text_distance.right
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
        id: text_kerning
		width:90
        text: "Kerning:"
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

        anchors.top: text_kerning.top
        anchors.topMargin: -2
        anchors.left: text_kerning.right
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
		width: 90
        text: "Prefix :"
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: kerning_input.bottom
        anchors.topMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 10
    }
	
	//Text prefix_text
    TextField
    {
        id: prefix_text
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
            manager.prefixEntered(prefix_text.text)
        }		
    }

    // Label "Suffix :"
    Text
    {
        id: label_suffix
		width: 90
        text: "Suffix :"
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: label_prefix.bottom
        anchors.topMargin: 8
        anchors.left: parent.left
        anchors.leftMargin: 10
    }
	
	//Text userInfoText
    TextField
    {
        id: suffix_text
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
            manager.suffixEntered(suffix_text.text)
        }			
    }

}
