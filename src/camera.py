# coding=utf-8
from time import sleep

import cv2
import numpy as np
import mvsdk
import platform
from PySide6.QtCore import Signal, QObject


def getCamList():
    return mvsdk.CameraEnumerateDevice()


class Camera(QObject):
    """
    Camera class for handling frame capture and pre-processing.

    :ivar frameReadyEvent: Signal emitted when a new frame is ready. Emits an integer.
    :ivar pFrameBuffer: Frame buffer for storing image data.
    :ivar isRunning: Indicates if the camera is currently capturing frames.
    :ivar isWaiting: Indicates if the camera is waiting for the worker class to finish.
    :ivar DevInfo: Device information for the camera initialization.
    :ivar hCamera: Handle for the camera device.
    :ivar outputSize: Output resolution size for captured images.
    """

    frameReadyEvent = Signal(int, int)  # parameter1: camera handle number. parameter2: 0 for upside 1 for bottom

    def __init__(self, DevInfo):
        """
        Initializes the Camera instance with the provided device information.

        :param DevInfo: Device information for initializing the camera.
        :type DevInfo: DeviceInfo
        """
        super(Camera, self).__init__()
        self.image = None
        self.pFrameBuffer = 0
        self.isRunning = False
        self.isWaiting = False
        self.DevInfo = DevInfo
        self.hCamera = -1
        self.outputSize = [1224, 1024]

    def main(self):
        """
        Main routine for camera setting initialization.
        """
        try:
            self.hCamera = mvsdk.CameraInit(self.DevInfo, -1, -1)
        except mvsdk.CameraException as e:
            print("CameraInit Failed({}): {}".format(e.error_code, e.message))
            return

        # Set camera output format based on the camera color type
        cap = mvsdk.CameraGetCapability(self.hCamera)
        monoCamera = (cap.sIspCapacity.bMonoSensor != 0)
        if monoCamera:
            mvsdk.CameraSetIspOutFormat(self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)
        else:
            mvsdk.CameraSetIspOutFormat(self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_BGR8)

        # Set exposure time in millisecond
        # mvsdk.CameraSetAeState(self.hCamera, 0)
        # mvsdk.CameraSetExposureTime(self.hCamera, 300 * 1000)

        mvsdk.CameraPlay(self.hCamera)  # Start camera internal thread

        # Allocate RGB buffer based on the largest resolution the camera can capture.
        FrameBufferSize = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax * (1 if monoCamera else 3)

        # Allocate RGB buffer for ISP output image
        # 备注：从相机传输到PC端的是RAW数据，在PC端通过软件ISP转为RGB数据（如果是黑白相机就不需要转换格式，但是ISP还有其它处理，所以也需要分配这个buffer）
        self.pFrameBuffer = mvsdk.CameraAlignMalloc(FrameBufferSize, 16)

        mvsdk.CameraSetTriggerMode(self.hCamera, 0)  # Set capture mode. 0 for continuous 1 for software 2 for hardware
        mvsdk.CameraSetCallbackFunction(self.hCamera, self.GrabCallback,
                                        0)  # Configure camera callback function on trigger

        # Set camera running flag to true
        self.isRunning = True

    def preProcess(self, hCamera, pRawData, pFrameBuffer, FrameHead):
        mvsdk.CameraImageProcess(hCamera, pRawData, pFrameBuffer, FrameHead)

        # windows下取到的图像数据是上下颠倒的，以BMP格式存放。转换成opencv则需要上下翻转成正的
        # linux下直接输出正的，不需要上下翻转
        if platform.system() == "Windows":
            mvsdk.CameraFlipFrameBuffer(pFrameBuffer, FrameHead, 1)

        # 此时图片已经存储在pFrameBuffer中，对于彩色相机pFrameBuffer=RGB数据，黑白相机pFrameBuffer=8位灰度数据
        # 把pFrameBuffer转换成opencv的图像格式以进行后续算法处理
        frame_data = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(pFrameBuffer)
        frame = np.frombuffer(frame_data, dtype=np.uint8)
        frame = frame.reshape(
            (FrameHead.iHeight, FrameHead.iWidth, 1 if FrameHead.uiMediaType == mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3))

        self.image = cv2.resize(frame, (self.outputSize[0], self.outputSize[1]), interpolation=cv2.INTER_LINEAR)

    @mvsdk.method(mvsdk.CAMERA_SNAP_PROC)
    def GrabCallback(self, hCamera, pRawData, pFrameHead, pContext):
        """
        Camera callback function on trigger.
        Captures a frame on trigger, resizes the frame, saves it as a class member, and notifies the worker class.
        If the worker class has not finished its task, new triggers will be ignored.

        :param hCamera: Camera handle.
        :type hCamera: int
        :param pRawData: Frame captured in RAW data format.
        :type pRawData: bytes
        :param pFrameHead: Frame header information, such as metadata.
        :type pFrameHead: dict
        :param pContext: Additional context information (optional).
        :type pContext: Any, optional
        """
        if self.isWaiting:
            return
        FrameHead = pFrameHead[0]
        pFrameBuffer = self.pFrameBuffer
        self.preProcess(hCamera, pRawData, pFrameBuffer, FrameHead)
        self.isWaiting = True
        self.frameReadyEvent.emit(hCamera, 0)  # Notify worker class for frame ready signal
        mvsdk.CameraReleaseImageBuffer(hCamera, pRawData)
        if mvsdk.CameraGetTriggerMode(self.hCamera) != 2:
            self.isWaiting = False
            return
        sleep(3)
        mvsdk.CameraSoftTrigger(hCamera)
        pRawData, FrameHead = mvsdk.CameraGetImageBuffer(hCamera, 200)
        self.preProcess(hCamera, pRawData, pFrameBuffer, FrameHead)
        self.frameReadyEvent.emit(hCamera, 1)
        self.isWaiting = False

    def unInit(self):
        mvsdk.CameraUnInit(self.hCamera)
        mvsdk.CameraAlignFree(self.pFrameBuffer)
        self.isRunning = False
