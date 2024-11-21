import json
import os

import numpy as np
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage
from crosshairInspection import CrossHairInspection
import camera

config_file_path='src/searchArea.json'

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


def findCamIndex(hCamera, camList):
    index = next((i for i, camera in enumerate(camList) if camera.hCamera == hCamera), None)
    if index is None:
        print(f"No camera of handle {hCamera} was found!")
        return
    return index


class CameraWorker(QObject):
    image_ready_event = Signal(QImage, int)  # Signal to GUI when an image is ready

    def __init__(self):
        super().__init__()
        self.camList = []  # list of scanned camera(can be disconnected and needs to remedy)
        self.camRef = {}  # dictionary used for querying what inspection job to perform. Based on friendly name of the camera, key: camera handle value:0 for left 1 for right.
        self.topLeftInspector = CrossHairInspection()
        self.topRightInspector = CrossHairInspection()
        self.botLeftInspector = CrossHairInspection()
        self.botRightInspector = CrossHairInspection()
        self.setSearchArea()

    def setSearchArea(self, config_file=config_file_path):
        def helper(inspector, name, configs):
            config = configs.get(name, {})
            inspector.roi_range = config.get("roi_range")
            inspector.search_area1 = config.get("search_area1")
            inspector.search_area2 = config.get("search_area2")
            inspector.search_area3 = config.get("search_area3")
            inspector.search_area4 = config.get("search_area4")

        if os.path.exists(config_file):
            with open(config_file, "r") as file:
                searchArea_config = json.load(file)
                helper(self.topLeftInspector, 'topLeft', searchArea_config)
                helper(self.topRightInspector, 'topRight', searchArea_config)
                helper(self.botLeftInspector, 'bottomLeft', searchArea_config)
                helper(self.botRightInspector, 'bottomRight', searchArea_config)

        else:
            print("Search Area JSON Configuration file not found.")

    @Slot(int)
    def onFrameReady(self, hCamera, inspectDirection):
        index = findCamIndex(hCamera, self.camList)

        if self.camList[index].image is not None:
            image = self.camList[index].image
            if inspectDirection == 0:
                image = self.topLeftInspector.main(image)
            else:
                image = self.topRightInspector.main(image)

            qt_image = cv_to_qt_image(image)
            self.image_ready_event.emit(qt_image, 0)

    def init(self):
        DevList = camera.getCamList()
        nDev = len(DevList)
        if nDev < 1:
            print("No camera was found!")
            return

        for i, DevInfo in enumerate(DevList):
            print(f"{i}: {DevInfo.GetFriendlyName()} {DevInfo.GetPortType()}")
            newCamera = camera.Camera(DevInfo)
            newCamera.frameReadyEvent.connect(self.onFrameReady)  # Connect camera's signal to the slot
            newCamera.main()  # Assuming start method initializes and starts the camera capture
            self.camList.append(newCamera)
            self.camRef[DevInfo.GetFriendlyName()] = newCamera.hCamera

    def unInit(self, hCamera=None):
        if hCamera is None:
            for cam in self.camList:
                if not cam.isRunning:
                    continue
                cam.frameReadyEvent.disconnect()
                cam.unInit()
        else:
            index = findCamIndex(hCamera, self.camList)
            if index is None:
                return
            self.camList[index].frameReadyEvent.disconnect()
            self.camList[index].unInit()
