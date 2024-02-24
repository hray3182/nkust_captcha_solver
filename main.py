from flask import Flask, request, jsonify
import numpy as np
import cv2
import tensorflow as tf

app = Flask(__name__)

# 加載 TensorFlow Lite 模型
interpreter = tf.lite.Interpreter(model_path="./assets/webap_captcha.tflite")
interpreter.allocate_tensors()

# 獲取輸入和輸出張量的詳細信息
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# 讀取標籤文件
with open('./assets/labels.txt', 'r') as file:
    labels = [line.strip() for line in file.readlines()]

def preprocess_image(image):
    # 轉換為灰度圖
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 分割驗證碼為單獨字符
    digits = []
    digits_count = 4
    w = image.shape[1] // digits_count
    for i in range(digits_count):
        digit = image[:, i * w:(i + 1) * w]
        digit = cv2.resize(digit, (input_details[0]['shape'][2], input_details[0]['shape'][1]))
        digit = np.expand_dims(digit, axis=-1)
        digit = np.expand_dims(digit, axis=0)
        digit = np.float32(digit) / 255.0
        digits.append(digit)
    return digits

def recognize_text(digits):
    result_text = ''
    for digit in digits:
        # 設置輸入張量
        interpreter.set_tensor(input_details[0]['index'], digit)
        # 運行模型
        interpreter.invoke()
        # 獲取輸出數據
        output_data = interpreter.get_tensor(output_details[0]['index'])
        predicted_label = np.argmax(output_data[0])
        result_text += labels[predicted_label]
    return result_text

@app.route('/recognize-text', methods=['POST'])
def recognize_text_api():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    # 讀取圖片
    file = request.files['image']
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)

    # 預處理圖片
    digits = preprocess_image(image)

    # 識別文字
    result = recognize_text(digits)
    return jsonify({'text': result})

if __name__ == '__main__':
    app.run(debug=True)
