import os
import cv2
import numpy as np
import tensorflow as tf

class TFLiteHandDetector:
    """基于TensorFlow Lite的轻量级手势检测器"""
    
    def __init__(self, model_path=None):
        self.model_path = model_path
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.input_shape = None
        self.is_loaded = False
        
        # 尝试加载模型
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            # 如果没有提供模型路径，尝试下载或使用默认模型
            self.download_default_model()
    
    def download_default_model(self):
        """下载默认的手势检测模型"""
        try:
            import requests
            

            model_url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            model_path = "hand_landmarker.task"
            
            print(f"正在下载TFLite模型: {model_path}")
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"模型下载完成: {model_path}")
            self.load_model(model_path)
        except Exception as e:
            print(f"模型下载失败: {e}")
            self.is_loaded = False
    
    def load_model(self, model_path):
        """加载TFLite模型"""
        try:
            # 加载TFLite解释器
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            
            # 获取输入输出信息
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.input_shape = self.input_details[0]['shape']
            
            self.is_loaded = True
            print(f"TFLite模型加载成功: {model_path}")
            print(f"模型输入形状: {self.input_shape}")
            print(f"模型输出数量: {len(self.output_details)}")
        except Exception as e:
            print(f"模型加载失败: {e}")
            self.is_loaded = False
    
    def preprocess_image(self, img):
        """预处理图像，使其符合模型输入要求"""
        if self.input_shape is None:
            return None
        

        input_width = self.input_shape[2]
        input_height = self.input_shape[1]
        resized_img = cv2.resize(img, (input_width, input_height))
        

        rgb_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
        

        normalized_img = rgb_img / 255.0
        

        input_data = np.expand_dims(normalized_img, axis=0)
        

        input_data = input_data.astype(self.input_details[0]['dtype'])
        
        return input_data
    
    def detect_landmarks(self, img):
        """检测手部关键点"""
        if not self.is_loaded:
            return [], img
        
        # 预处理图像
        input_data = self.preprocess_image(img)
        if input_data is None:
            return [], img
        
        # 设置模型输入
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        
        # 运行模型
        self.interpreter.invoke()
        
        # 获取模型输出
        landmarks = self.interpreter.get_tensor(self.output_details[0]['index'])
        handedness = self.interpreter.get_tensor(self.output_details[1]['index'])
        hand_flags = self.interpreter.get_tensor(self.output_details[2]['index'])
        
        # 处理检测结果
        detected_hands = []
        
        # 假设输出是[batch, num_hands, num_landmarks, 3]
        if landmarks.shape[1] > 0:
            for i in range(landmarks.shape[1]):
                hand_landmarks = landmarks[0, i, :, :]
                if np.all(hand_landmarks == 0):
                    continue
                
                # 将归一化坐标转换为图像像素坐标
                img_height, img_width, _ = img.shape
                lmList = []
                for landmark in hand_landmarks:
                    x = int(landmark[0] * img_width)
                    y = int(landmark[1] * img_height)
                    z = landmark[2]  # 深度信息
                    lmList.append((x, y, z))
                
                # 构建手部数据结构
                hand_info = {
                    'lmList': lmList,
                    'type': 'Right' if handedness[0, i, 0, 0] > 0.5 else 'Left',
                    'bbox': self.calculate_bbox(lmList, img_width, img_height)
                }
                detected_hands.append(hand_info)
        
        # 绘制检测结果
        self.draw_landmarks(img, detected_hands)
        
        return detected_hands, img
    
    def calculate_bbox(self, lmList, img_width, img_height):
        """计算手部边界框"""
        if not lmList:
            return (0, 0, 0, 0)
        

        xs = [lm[0] for lm in lmList]
        ys = [lm[1] for lm in lmList]
        

        x_min = max(0, min(xs))
        y_min = max(0, min(ys))
        x_max = min(img_width, max(xs))
        y_max = min(img_height, max(ys))
        
        width = x_max - x_min
        height = y_max - y_min
        
        return (x_min, y_min, width, height)
    
    def draw_landmarks(self, img, hands):
        """绘制手部关键点和连接线"""
        # 手部关键点连接关系（根据MediaPipe Hands定义）
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # 拇指
            (0, 5), (5, 6), (6, 7), (7, 8),  # 食指
            (0, 9), (9, 10), (10, 11), (11, 12),  # 中指
            (0, 13), (13, 14), (14, 15), (15, 16),  # 无名指
            (0, 17), (17, 18), (18, 19), (19, 20)   # 小指
        ]
        
        for hand in hands:
            lmList = hand['lmList']
            
            # 绘制连接线
            for connection in connections:
                start_idx, end_idx = connection
                if start_idx < len(lmList) and end_idx < len(lmList):
                    start_point = lmList[start_idx]
                    end_point = lmList[end_idx]
                    cv2.line(img, (start_point[0], start_point[1]), (end_point[0], end_point[1]), (0, 255, 0), 2)
            
            # 绘制关键点
            for i, lm in enumerate(lmList):
                color = (0, 0, 255) if i == 8 else (0, 255, 0)  # 食指指尖为红色
                cv2.circle(img, (lm[0], lm[1]), 5, color, cv2.FILLED)
    
    def findHands(self, img, draw=True, flipType=False):
        """兼容cvzone.HandDetector的接口"""

        if flipType:
            img = cv2.flip(img, 1)
        

        hands, img = self.detect_landmarks(img)
        

        cvzone_hands = []
        for hand in hands:
            cvzone_hand = {
                'lmList': hand['lmList'],
                'bbox': hand['bbox'],
                'type': hand['type']
            }
            cvzone_hands.append(cvzone_hand)
        
        return cvzone_hands, img
    
    def load_model(self, model_path):
        """加载TensorFlow Lite模型"""
        try:
            # 加载TFLite解释器
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            
            # 获取输入输出信息
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.input_shape = self.input_details[0]['shape']
            
            self.is_loaded = True
            print(f"TFLite模型加载成功: {model_path}")
            print(f"模型输入形状: {self.input_shape}")
            print(f"模型输出数量: {len(self.output_details)}")
        except Exception as e:
            print(f"模型加载失败: {e}")
            self.is_loaded = False