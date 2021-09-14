from neuralnet import NeuralNet
import numpy as np
import random


def read_all(path):
    x = np.zeros((600, 1024))
    y = np.zeros((10, 1024))
    with open(path, 'rb') as r:
        for ii in range(1024):
            bs = r.read(601)
            for bi in range(600):
                x[bi, ii] = float(bs[bi]) + (random.random() - 0.5) * 0
            y[int(bs[600]-0x30), ii] = 1
    return x, y


if __name__ == '__main__':
    alpha = 0.001
    lambd = 0

    data_x, data_y = read_all('images/train_set/data_0.dat')

    nn = NeuralNet([600, 300, 10])
    nn.rand_init()
    print('training ...')
    for epoch in range(5000):
        loss = 0
        for batch_idx in range(0, 1024, 64):
            batch_x = data_x[:, batch_idx:batch_idx + 64]
            batch_y = data_y[:, batch_idx:batch_idx + 64]
            loss += nn.train_lr(batch_x, batch_y, alpha, 'softmax', lambd)
        if epoch % 10 == 0:
            print('epoch times : {0}, loss : {1}'.format(epoch, loss))
        if epoch % 50 == 0:
            nn.write_parameters('nn1')



