import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, Slot

from cameraworker import CameraWorker


class ImageViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.camera_worker = CameraWorker()
        self.camera_worker.init()
        self.camera_worker.image_ready_event.connect(self.updateImage)

        self.setWindowTitle("QImage Viewer")
        self.setGeometry(100, 100, 800, 600)

        # QLabel for displaying the QImage
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("No Image Loaded")

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.say_hello)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.stop_button)

        # Set up the central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    @Slot()
    def say_hello(self):
        print("Stop Button clicked, Hello!")
        self.camera_worker.unInit(1)

    @Slot(QImage, int)
    def updateImage(self, image, hCamera):
        self.display_image(image)
        pass

    def load_image(self):
        # Example: Load a dummy QImage (you can replace this with actual loading logic)
        dummy_image = QImage(640, 480, QImage.Format.Format_RGB32)
        dummy_image.fill(Qt.GlobalColor.red)  # Fill with red for demonstration
        self.display_image(dummy_image)

    def display_image(self, image):
        """Display a QImage on the QLabel."""
        pixmap = QPixmap.fromImage(image)
        # Resize the pixmap to 640x480 while keeping the aspect ratio
        pixmap = pixmap.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_label.setText("")


def main():
    app = QApplication(sys.argv)
    viewer = ImageViewerApp()
    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
