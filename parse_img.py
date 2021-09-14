import cv2
import numpy as np


def split_codes(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    img_open = cv2.bitwise_not(img[1:-1, 1:-1])
    g = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    img_open = cv2.morphologyEx(img_open, cv2.MORPH_OPEN, g)
    img_gray = cv2.cvtColor(img_open, cv2.COLOR_BGR2GRAY)
    ret, img_thres = cv2.threshold(img_gray, 63, 255, cv2.THRESH_TOZERO)
    data = img_thres
    rows, cols = data.shape
    ranges = []

    c = 0
    while c < cols:
        if np.sum(data[0:rows, c]) == 0:
            c += 1
        else:
            beg_idx = c
            while True:
                if np.sum(data[0:rows, c]) == 0:
                    end_idx = c
                    ranges.append([beg_idx, end_idx])
                    break
                else:
                    c += 1
                    continue
            c += 1
    img_out = img_thres

    split_images = []
    for i in range(4):
        roi = img_out[0:rows, ranges[i][0]-1:ranges[i][1]+1]
        split_images.append(roi)
    return split_images


if __name__ == '__main__':
    for i0 in range(256, 512):
        path = 'images/codes/{0}.png'.format(i0)
        images = split_codes(i0)
        for i in range(4):
            cv2.imwrite('images/src_split/{0}.png'.format(i0 * 4 + i), images[i])


    # cv2.imshow('img: ', img_thres)
    #cv2.waitKey(0)
