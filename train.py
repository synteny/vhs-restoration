from config import *

from keras.layers import Convolution2D, MaxPooling2D, UpSampling2D

from keras.models import Sequential


class Net:
    def __init__(self, sess):
        self.sess = sess

    def construct(self):
        def encoder():
            model = Sequential()
            model.add(Convolution2D(128, 3, 3, activation='relu', border_mode='same', input_shape=(3, IMAGE_WIDTH, IMAGE_HEIGHT)))
            model.add(MaxPooling2D(pool_size=(2, 2), border_mode='same'))
            model.add(Convolution2D(64, 3, 3, activation='relu', border_mode='same'))
            model.add(MaxPooling2D(pool_size=(2, 2), border_mode='same'))
            model.add(Convolution2D(64, 3, 3, activation='relu', border_mode='same'))
            model.add(MaxPooling2D(pool_size=(2, 2), border_mode='same'))
            return model

        def decoder():
            model = Sequential()
            model.add(Convolution2D(64, 3, 3, activation='relu', border_mode='same'))
            model.add(UpSampling2D((2, 2)))
            model.add(Convolution2D(64, 3, 3, activation='relu', border_mode='same'))
            model.add(UpSampling2D((2, 2)))
            model.add(Convolution2D(128, 3, 3, activation='relu', border_mode='same'))
            model.add(UpSampling2D((2, 2)))
            return model