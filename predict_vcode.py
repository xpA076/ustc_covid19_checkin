from parse_img import split_codes
from neuralnet import NeuralNet
from mark_images import padding_image
import numpy as np


def predict(image_path, nn_path, nn_name):
    images = split_codes(image_path)
    nn = NeuralNet([600, 300, 10])
    nn.data_path = nn_path
    nn.read_parameters(nn_name)
    ans = []
    for i in range(4):
        data_img = padding_image(images[i])
        data_bytes = data_img.tobytes()
        x = np.zeros((600, 1))
        for bi in range(600):
            x[bi, 0] = float(data_bytes[bi])
        nn.forward_prop(x)
        nn.softmax()
        predict_row = np.argmax(nn.A[2], axis=0)[0]
        ans.append(predict_row)
    return ans


if __name__ == '__main__':
    ans = predict('images/codes/22.png', 'nn_data', 'nn1')
    print(ans)