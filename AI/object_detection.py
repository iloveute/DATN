import cv2
import numpy as np



class ObjectDetection:
    def __init__(self, weights_path="dnn_model/MobileNetSSD_deploy.caffemodel", cfg_path="dnn_model/MobileNetSSD_deploy.prototxt"):
        print("Dang tai Object Detection")
        print("Dang chay opencv dnn voi MobileNetSSD")
        self.nmsThreshold = 0.4
        self.confThreshold = 0.5
        self.image_size = 608

        # Load Network
        net = cv2.dnn.readNet(weights_path, cfg_path)

        # Enable GPU CUDA
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        self.model = cv2.dnn_DetectionModel(net)

        self.model.setInputParams(size=(self.image_size, self.image_size), scale= 1/255)

    def detect(self, frame):
        return self.model.detect(frame, nmsThreshold=self.nmsThreshold, confThreshold=self.confThreshold)

