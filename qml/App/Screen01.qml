import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: mainScreen
    anchors.fill: parent
    ToolBar {
        id: toolBar
        Layout.fillWidth: true
    }

    RowLayout {
        id: rowLayout
        Layout.fillWidth: true

        Image {
                id: dynamicImage2
                // source: "../../assets/images/sample1.BMP"
                width: rowLayout.width / 2

            }
    }

    Rectangle {
        Layout.fillWidth: true
        height: 50
    }

    Component.onCompleted: {
        console.log(mainScreen.width)
        console.log("Main Screen load complete")
    }
}

