pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: rootArea
    anchors.fill: parent
    border.color: "red"; border.width: 2

    ColumnLayout {
        anchors.fill: parent

        ToolBar {
            Layout.fillWidth: true;
            Layout.preferredHeight: parent.height / 15
        }

        Item {
            Layout.fillWidth: true; Layout.fillHeight: true

            RowLayout {
                anchors.fill: parent

                Item {
                    Layout.fillWidth: true; Layout.fillHeight: true

                    ColumnLayout {
                        anchors.fill: parent

                        Image {
                            id: dynamicImage
                            Layout.fillWidth: true;
                            Layout.preferredHeight: parent.height * 0.6
                            source: "../../assets/images/sample1.BMP"
                            fillMode: Image.PreserveAspectFit
                            Connections {
                                target: imageProvider
                                function onImageUpdated() {
                                    dynamicImage.source = "image://dynamicImage?" + Date.now()
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true; Layout.fillHeight: true
                            color: "grey"
                            border.color: "teal"
                        }
                    }
                }

                Item {
                    Layout.fillWidth: true; Layout.fillHeight: true

                    ColumnLayout {
                        anchors.fill: parent

                        Image {
                            id: dynamicImage2
                            Layout.fillWidth: true;
                            Layout.preferredHeight: parent.height * 0.6
                            source: "../../assets/images/sample1.BMP"
                            fillMode: Image.PreserveAspectFit
                        }

                        Rectangle {
                            Layout.fillWidth: true; Layout.fillHeight: true
                            color: "grey"
                            border.color: "teal"
                        }
                    }
                }
            }
        }
    }
}
