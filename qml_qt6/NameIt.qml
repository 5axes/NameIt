// Import the standard GUI elements from QTQuick
import QtQuick 6.0
import QtQuick.Controls 6.0

// Imports the Uranium GUI elements, which are themed for Cura.
import UM 1.6 as UM

// Imports the Cura GUI elements.
import Cura 1.7 as Cura


// UM.Dialog
// Dialog
Window
{
    id: base

    title: "Name It Parameters"

    color: "#fafafa" //Background color of cura: #fafafa

    // NonModal like that the dialog to block input in the main window
    modality: Qt.NonModal

    // WindowStaysOnTopHint to stay on top
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint

    // Setting the dimensions of the dialog window
    width: 250
    height: 170
    minimumWidth: 250
    minimumHeight: 170

    // Position of the window
    x: Screen.width*0.5 - width - 50
    y: 400 

    // Define a Window a border (Red for) and a background color
    Rectangle {
        id: bg_rect
        width: 250
        height: 170
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

		ToolTip.delay: 2000
		ToolTip.timeout: 1000
		ToolTip.visible: hovered
		ToolTip.text: qsTr("Close this dialog box")
				
		background: Rectangle {
			implicitWidth: 100
			implicitHeight: 25
			radius: 3
			color: "#D22"
		}

        onClicked:
        {
            base.close();
        }
    }

    // Label "Size: "
    Label
    {
        id: label_size
		width: 90
        text: "Size:"
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: close_button.top
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }

    //User input of height
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

		font.family: "Arial"
        font.pointSize: 12
		
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
    Label
    {
        id: label_height
		width: 90
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

		font.family: "Arial"
        font.pointSize: 12
		
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
	
	// Label "Distance: "
    Label
    {
        id: label_distance
		width: 90
        text: "Distance :"
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: height_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }

    //User input of height
    UM.TextFieldWithUnit
    {
        id: distance_input
        width: 90
        text: distanceInput
		// "ie. 20.0"

        anchors.top: label_distance.top
        anchors.topMargin: -2
        anchors.left: label_distance.right
        anchors.leftMargin: 10

		font.family: "Arial"
        font.pointSize: 12
		
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
	
	// Label "Kerning: "
    Label
    {
        id: label_kerning
		width: 90
        text: "Kerning :"
        font.family: "Arial"
        font.pointSize: 12
        color: "#131151"

        anchors.top: distance_input.bottom
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
    }

    //User input of height
    UM.TextFieldWithUnit
    {
        id: kerning_input
        width: 90
        text: kerningInput
		// "ie. 20.0"

        anchors.top: label_kerning.top
        anchors.topMargin: -2
        anchors.left: label_kerning.right
        anchors.leftMargin: 10

		font.family: "Arial"
        font.pointSize: 12
		
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
}
