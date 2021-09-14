import cv2
import random
import numpy as np


def padding_image(img):
    rows, cols = img.shape
    aim_cols = 20
    pad_img = np.uint8(np.zeros((30, aim_cols)))
    beg = round((aim_cols - cols) / 2 + (random.random() - 0.5))
    pad_img[0:rows, beg:beg + cols] = img
    return pad_img


def read_and_mark(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    data_img = padding_image(img)
    cv2.imshow('img: ', cv2.resize(data_img, (400, 600)))
    key = cv2.waitKey(0)
    print('{0} ans : '.format(path), str(key - 0x30))
    # data_vec = np.reshape(data_img, [20*30, 1])
    bs = data_img.tobytes()
    return bs, key - 0x30


if __name__ == '__main__':
    for data_idx in range(1, 2):
        with open('images/train_set/data_{0}.dat'.format(data_idx), 'wb') as f:
            for idx in range(1024, 2048):
                data, ans = read_and_mark('images/src_split/{0}.png'.format(idx))
                f.write(data)
                f.write((ans + 0x30).to_bytes(1, 'little'))

