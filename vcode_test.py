from neuralnet import NeuralNet
import numpy as np
from vcode_train import read_all


if __name__ == '__main__':
    data_x, data_y = read_all('images/train_set/data_1.dat')

    nn = NeuralNet([600, 300, 10])
    nn.read_parameters('nn1')
    count = 0
    for i in range(1024):
        test_x = data_x[:, i:i+1]
        test_y = data_y[:, i:i+1]
        nn.forward_prop(test_x)
        nn.softmax()
        predict_row = np.argmax(nn.A[2], axis=0)[0]
        if test_y[predict_row, 0] == 1:
            count += 1
    print('accuracy: {0} / {1}'.format(count, 1024))
