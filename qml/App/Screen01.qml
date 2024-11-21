import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Column {
    id: column

    ToolBar {
        id: toolBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: 0
        anchors.rightMargin: 0
    }

    Row {
        id: row
        width: column.width
        height: column.height * 0.6

        Image {
            id: dynamicImage
            width: row.width / 2
            // Layout.preferredWidth: parent.width / 2
            source: "../../assets/images/sample1.BMP"
            fillMode: Image.PreserveAspectFit
            Connections {
                target: imageProvider
                function onImageUpdated() {
                    dynamicImage.source = "image://dynamicImage?" + Date.now()
                }
            }
        }

        Image {
            id: image2
            width: row.width / 2
            // Layout.preferredWidth: parent.width / 2
            source: "../../assets/images/sample1.BMP"
            fillMode: Image.PreserveAspectFit
        }

    }
}
