import tensorflow as tf
import tensorflow.contrib.slim as slim
from helper_func import define_scope
from tensorflow.examples.tutorials.mnist import input_data

'''

This network outputs the gaze location for a given webcam image.

The input:
* Webcam image (128x128x3)
* Target gaze location (quadrant?)

The output:
* A trained refiner network

'''

class GazeModel(object):

    def __init__(self, image, target, config):
        self.image = image
        self.target = target
        self.config = config
        self.predict
        self.optimize
        self.error

    @define_scope(initializer=slim.xavier_initializer(),
                  regularizer=slim.l2_regularizer())
    def predict(self):
        # Simple test model
        x = self.image
        x = slim.conv2d(x, 32, [3, 3], scope='conv1')
        x = slim.conv2d(x, 32, [3, 3], scope='conv2')
        x = slim.conv2d(x, 64, [3, 3], scope='conv3')
        x = slim.max_pool2d(x, [2, 2], scope='pool1')
        x = slim.fully_connected(x, 256)
        x = slim.fully_connected(x, 128)
        x = slim.fully_connected(x, 4, tf.nn.softmax)
        return x

    @define_scope
    def optimize(self):
        loss = slim.losses.softmax_cross_entropy(self.predict, self.target)
        optimizer = tf.train.RMSPropOptimizer(0.03)
        return optimizer.minimize(loss)

    @define_scope
    def error(self):
        mistakes = tf.not_equal(
            tf.argmax(self.target, 1), tf.argmax(self.predict, 1))
        return tf.reduce_mean(tf.cast(mistakes, tf.float32))

    @define_scope
    def loss(self):
        pass


def main():
    mnist = input_data.read_data_sets('./mnist/', one_hot=True)

    config = {'input_height': 28,
              'input_width': 28,
              'input_channels': 3,
              'output_class': 4}

    # Input image dimensions from config
    h = config['input_height']
    w = config['input_width']
    c = config['input_channels']
    image = tf.placeholder(tf.float32, [None, h, w, c])
    label = tf.placeholder(tf.float32, [None, config['output_class']])

    model = GazeModel(image, label)
    sess = tf.Session()
    sess.run(tf.initialize_all_variables())

    for _ in range(10):
        images, labels = mnist.test.images, mnist.test.labels
        error = sess.run(model.error, {image: images, label: labels})
        print('Test error {:6.2f}%'.format(100 * error))
        for _ in range(60):
            images, labels = mnist.train.next_batch(100)
            sess.run(model.optimize, {image: images, label: labels})

if __name__ == '__main__':
    main()
