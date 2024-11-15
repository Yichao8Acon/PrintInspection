import os
import sys
import unittest
from time import sleep

import cv2 as cv

sys.path.insert(0, os.path.abspath('../src'))
from src import cameraworker
from src import mvsdk
from src import crosshairInspection


class MyTestCase(unittest.TestCase):

    src = cv.imread('../assets/images/sample1.BMP')

    def test_show(self):
        cv.imshow('output', self.src)
        cv.waitKey(0)
        cv.destroyAllWindows()

    def test_image_capture(self):
        hCamera = 1
        camera_worker = cameraworker.CameraWorker()
        camera_worker.init()
        mvsdk.CameraPause(hCamera)
        mvsdk.CameraSetTriggerMode(hCamera, 1)  # Set camera as software trigger
        mvsdk.CameraPlay(hCamera)
        mvsdk.CameraSoftTrigger(hCamera)
        sleep(0.1)
        cv.imwrite("../assets/images/sample1.BMP", camera_worker.camList[0].image)
        camera_worker.unInit(hCamera)

    def test_edge_detection(self):
        cv.namedWindow('output',cv.WINDOW_NORMAL)
        src = cv.imread('../assets/images/sample1.BMP')
        inspection_obj = crosshairInspection.CrossHairInspection()
        img = inspection_obj.preprocess(src)
        cv.imshow('output', img)
        cv.waitKey(0)
        cv.destroyAllWindows()


    def test_find_transition(self):
        cv.namedWindow('output', cv.WINDOW_NORMAL)
        cv.resizeWindow('output', 800, 600)
        img  = self.src.copy()
        inspector = crosshairInspection.CrossHairInspection()
        processed = inspector.preprocess(img)
        height, width = processed.shape[:2]
        inspector.search_area1[3] = height
        inspector.search_area2[2] = width
        print(processed.shape[:2])
        print(inspector.search_area1)
        cv.rectangle(processed, inspector.search_area1, (0, 0, 255), 4)
        cv.imshow('output', processed)
        cv.waitKey(0)
        cv.destroyAllWindows()
        transition = inspector.find_transitions(processed, inspector.search_area2, search_dir='vertical')
        print(transition)


if __name__ == '__main__':
    unittest.main()
