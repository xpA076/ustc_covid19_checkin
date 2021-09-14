import numpy as np
import struct


def relu(x):
    return np.maximum(x, 0)


def drelu(x):
    return np.where(x > 0, 1, 0)


def sigmoid(x):
    return 1.0 / (1 + np.exp(0 - x))


def dsigmoid(x):
    return sigmoid(x) * (1 - sigmoid(x))


# 自定义全连接神经网络
# 除最后一层激活函数为sigmoid外，激活函数为ReLU
class NeuralNet:
    layer = 0  # 神经元层数
    m = 1
    n = []  # 每层神经元数量
    A = []  # 每层激活函数后响应
    Z = []  # 每层激活函数前响应
    W = []  # 权重矩阵
    b = []  # bias矩阵
    dA = []
    dZ = []
    dW = []
    db = []

    data_path = 'nn_data'

    def __init__(self, n):
        self.layer = len(n) - 1
        self.n = n
        self.A = []
        self.Z = []
        self.W = []
        self.b = []
        self.dA = []
        self.dZ = []
        self.dW = []
        self.db = []
        for lyr in range(self.layer + 1):
            self.A.append(np.zeros((0, 0)))
            self.Z.append(np.zeros((0, 0)))
            self.W.append(np.zeros((0, 0)))
            self.b.append(np.zeros((0, 0)))
            self.dA.append(np.zeros((0, 0)))
            self.dZ.append(np.zeros((0, 0)))
            self.dW.append(np.zeros((0, 0)))
            self.db.append(np.zeros((0, 0)))

    def rand_init(self):
        for layer_idx in range(1, self.layer + 1):
            self.W[layer_idx] = np.random.randn(self.n[layer_idx], self.n[layer_idx - 1]) * 0.01
            self.b[layer_idx] = np.zeros((self.n[layer_idx], 1))

    def read_parameters(self, name):
        with open(self.data_path + '/{0}_w.dat'.format(name), 'rb') as rd:
            count = struct.unpack('i', rd.read(4))[0]
            n = []
            for l in range(count):
                n.append(struct.unpack('i', rd.read(4))[0])
            w = [np.array([[]])]
            for l in range(1, count):
                w0 = np.zeros((n[l], n[l - 1]), dtype=float)
                for row in range(n[l]):
                    for col in range(n[l - 1]):
                        data = struct.unpack('f', rd.read(4))
                        w0[row, col] = data[0]
                w.append(w0)
        self.W = w
        self.n = n
        with open(self.data_path + '/{0}_b.dat'.format(name), 'rb') as rd:
            count = struct.unpack('i', rd.read(4))[0]
            n = []
            for l in range(count):
                n.append(struct.unpack('i', rd.read(4))[0])
            b = [np.array([[]])]
            for l in range(1, count):
                b0 = np.zeros((n[l], 1), dtype=float)
                for row in range(n[l]):
                    data = struct.unpack('f', rd.read(4))
                    b0[row, 0] = data[0]
                b.append(b0)
        self.b = b

    def write_parameters(self, name):
        count = len(self.n)
        with open(self.data_path + '/{0}_w.dat'.format(name), 'wb') as wt:
            wt.write(struct.pack('i', count))
            for lyr in range(count):
                wt.write(struct.pack('i', self.n[lyr]))
            for lyr in range(1, count):
                for row in range(self.n[lyr]):
                    for col in range(self.n[lyr - 1]):
                        wt.write(struct.pack('f', self.W[lyr][row, col]))

        with open(self.data_path + '/{0}_b.dat'.format(name), 'wb') as wt:
            wt.write(struct.pack('i', count))
            for lyr in range(count):
                wt.write(struct.pack('i', self.n[lyr]))
            for lyr in range(1, count):
                for row in range(self.n[lyr]):
                    wt.write(struct.pack('f', self.b[lyr][row, 0]))

    def forward_prop(self, x):
        self.A[0] = x
        for l in range(1, self.layer + 1):
            self.Z[l] = np.dot(self.W[l], self.A[l - 1]) + self.b[l]
            if l == self.layer:
                self.A[l] = sigmoid(self.Z[l])
            else:
                self.A[l] = relu(self.Z[l])

    def softmax(self):
        t = np.exp(self.Z[self.layer])
        self.A[self.layer] = t / np.sum(t, axis=0, keepdims=True)

    def back_prop(self, y):
        useless, self.m = y.shape
        for i in range(self.layer):
            l = self.layer - i
            if l == self.layer:
                self.dZ[l] = self.A[l] - y
            else:
                self.dZ[l] = self.dA[l] * drelu(self.Z[l])
            self.dW[l] = 1.0 / self.m * np.dot(self.dZ[l], self.A[l - 1].T)
            self.db[l] = 1.0 / self.m * np.sum(self.dZ[l], axis=1, keepdims=True)
            self.dA[l - 1] = np.dot(self.W[l].T, self.dZ[l])

    def grad_descent(self, alpha, lambd=0):
        for l in range(1, self.layer + 1):
            self.W[l] = (1 - alpha * lambd / self.m) * self.W[l] - alpha * self.dW[l]
            self.b[l] = self.b[l] - alpha * self.db[l]

    def train_lr(self, x, y, alpha, out_layer='norm', lambd=0):
        self.forward_prop(x)
        if out_layer == 'softmax':
            self.softmax()
        self.back_prop(y)
        self.grad_descent(alpha, lambd)
        loss_mat = -y * np.log(self.A[self.layer])
        return np.sum(loss_mat)

