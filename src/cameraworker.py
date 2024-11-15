import numpy as np
import mvsdk
from PySide6.QtCore import QObject, Signal, Slot, QMutex
from PySide6.QtGui import QImage
from crosshairInspection import CrossHairInspection
from camera import Camera


def cv_to_qt_image(cv_img):
    """
    Convert an OpenCV image to a QImage.
    :param cv_img: source image
    """
    cv_img = np.ascontiguousarray(cv_img)
    height, width, channel = cv_img.shape
    bytes_per_line = 3 * width
    # Convert BGR (OpenCV format) to RGB (Qt format)
    qt_img = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
    return qt_img


class CameraWorker(QObject):
    image_ready_event = Signal(QImage, int)  # Signal to GUI when an image is ready

    def __init__(self):
        super().__init__()
        self.camList = []  # list of scanned camera(can be disconnected and needs to remedy)
        self.camRef = {}
        self.topLeftInspector = CrossHairInspection()
        self.topRightInspector = CrossHairInspection()
        self.botLeftInspector = CrossHairInspection()
        self.botRightInspector = CrossHairInspection()

    @Slot(int)
    def onFrameReady(self, hCamera):
        # print(f"Camera {hCamera} Triggered")
        # Search for camera instance based on the camera handle and then acquire the stored frame in that camera
        index = next((i for i, camera in enumerate(self.camList) if camera.hCamera == hCamera), None)
        if self.camList[index].image is not None:
            image = self.camList[index].image
            # TODO: Start OpenCV image processing here
            image = self.topLeftInspector.main(image)
            qt_image = cv_to_qt_image(image)
            self.image_ready_event.emit(qt_image, hCamera)
            self.camList[index].isWaiting = False

    def init(self):
        DevList = mvsdk.CameraEnumerateDevice()
        nDev = len(DevList)
        if nDev < 1:
            print("No camera was found!")
            return

        for i, DevInfo in enumerate(DevList):
            print(f"{i}: {DevInfo.GetFriendlyName()} {DevInfo.GetPortType()}")
            newCamera = Camera(DevInfo)
            newCamera.frameReadyEvent.connect(self.onFrameReady)  # Connect camera's signal to the slot
            newCamera.main()  # Assuming start method initializes and starts the camera capture
            self.camList.append(newCamera)
            self.camRef[DevInfo.GetFriendlyName()] = newCamera.hCamera

    def unInit(self, hCamera):
        index = next((i for i, camera in enumerate(self.camList) if camera.hCamera == hCamera), None)
        if index is None:
            print(f"No camera of handle {hCamera} was found!")
            return
        if not self.camList[index].isRunning:
            print(f"Camera of handle {hCamera} is not running!")
            return
        self.camList[index].frameReadyEvent.disconnect()
        # 关闭相机
        mvsdk.CameraUnInit(hCamera)
        # 释放帧缓存
        mvsdk.CameraAlignFree(self.camList[index].pFrameBuffer)
        self.camList[index].isRunning = False
