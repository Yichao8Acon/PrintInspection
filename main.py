import os
import sys

from PySide6.QtCore import QUrl, QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication, QImage
from PySide6.QtQuick import QQuickView, QQuickImageProvider

sys.path.insert(0, os.path.abspath('src'))
from src import cameraworker


class ImageProvider(QQuickImageProvider, QObject):
    imageUpdated = Signal()  # Signal to notify QML that the image has changed

    def __init__(self):
        super().__init__(QQuickImageProvider.Image)
        self._image = QImage()

    def requestImage(self, id, size, requestedSize):
        if not self._image.isNull():
            return self._image
        else:
            return QImage()

    @Slot(QImage, int)
    def setImage(self, image):
        self._image = image
        self.imageUpdated.emit()


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    view = QQuickView()
    engine = view.engine()
    engine.addImportPath(sys.path[0])

    # Set the context property
    image_provider = ImageProvider()
    engine.addImageProvider("dynamicImage", image_provider)
    engine.rootContext().setContextProperty("imageProvider", image_provider)
    image_provider.setImage(QImage("assets/images/sample1.BMP"))  # Set an initial image

    # Load the QML file directly
    qml_file_path = QUrl.fromLocalFile("qml/App/Main.qml")  # Replace with your actual QML file path
    view.setSource(qml_file_path)

    # Show the view
    view.show()

    image_provider.setImage(QImage("assets/images/1.jpg"))

    cameraworker = cameraworker.CameraWorker()
    cameraworker.image_ready_event.connect(image_provider.setImage)
    cameraworker.init()


    def onExit():
        cameraworker.unInit()
        print("Exiting...")


    app.aboutToQuit.connect(onExit)

    ex = app.exec()
    del view
    sys.exit(ex)
