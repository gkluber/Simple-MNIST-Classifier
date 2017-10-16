import argparse
import sys

from tensorflow.examples.tutorials.mnist import input_data

import tensorflow as tf

FLAGS = None


def main(_):
  # Import data
  mnist = input_data.read_data_sets(FLAGS.data_dir, one_hot=True)

  # Create the model
  x = tf.placeholder(tf.float32, [None, 784])
  W = tf.Variable(tf.zeros([784, 10]))
  b = tf.Variable(tf.zeros([10]))
  y = tf.matmul(x, W) + b
  
  #For saving model
  saver = tf.train.Saver()

  # Define loss and optimizer
  y_ = tf.placeholder(tf.float32, [None, 10])

  # The raw formulation of cross-entropy,
  #
  #   tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(tf.nn.softmax(y)),
  #                                 reduction_indices=[1]))
  #
  # can be numerically unstable.
  #
  # So here we use tf.nn.softmax_cross_entropy_with_logits on the raw
  # outputs of 'y', and then average across the batch.
  cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y))
  train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)

  sess = tf.InteractiveSession()
  tf.global_variables_initializer().run()
  
  #Error statistics
  correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
  
  accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  
  #summary statistics for use with Tensorboard UI
  tf.summary.scalar("accuracy",accuracy)
  summary = tf.summary.merge_all()
  train_writer = tf.summary.FileWriter('summary/train',
                                      sess.graph)
  test_writer = tf.summary.FileWriter('summary/test')
  tf.global_variables_initializer().run()
  
  # Train
  for epoch in range(10000):
    batch_xs, batch_ys = mnist.train.next_batch(100)
    sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})
    if(epoch%20==0):
      acc, sum = sess.run([accuracy,summary], feed_dict={x: batch_xs, y_: batch_ys})
      train_writer.add_summary(sum,epoch)
      print("Epoch {}. Accuracy {}".format(epoch,acc))
      saver.save(sess, "models/model.ckpt")

  #Test trained model
  print(sess.run(accuracy, feed_dict={x: mnist.test.images,y_: mnist.test.labels}))

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--data_dir', type=str, default='/tmp/tensorflow/mnist/input_data',
                      help='Directory for storing input data')
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)