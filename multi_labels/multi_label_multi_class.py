import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

import tensorflow as tf
import import_data as data
import pickle

# General architecture

IMG_SZ = 28
L_SZ = 2 # Labels size: Shape and Color
C_SZ = 3 # Classes size: (Circle, Square, Triangle) and (Red, Green, Blue)

INPUT_DIR = '../figures/'
VAL_DIR = '../val_figures/'
BATCH_SZ = 64
IMG_HEIGHT = IMG_SZ
IMG_WIDTH = IMG_SZ

N_CLASSES = 3 # total number of classes

# Parameters
learning_rate = 0.001
batch_size = 128
num_steps = 4000
display_step = 100

# Network Parameters
dropout = 0.75 # Dropout, probability to keep units

# multi label
X, Y = data.read_images(input_directory = INPUT_DIR, batch_size = BATCH_SZ, 
	img_height = IMG_HEIGHT, img_width = IMG_WIDTH, mode = 'multi_label')

X_val, Y_val = data.read_images(input_directory = VAL_DIR, batch_size = BATCH_SZ, 
    img_height = IMG_HEIGHT, img_width = IMG_WIDTH, mode = 'multi_label')

# Create model
def conv_net(x, n_classes, dropout, reuse, is_training):
    # Define a scope for reusing the variables
    with tf.variable_scope('ConvNet', reuse=reuse):

        # Convolution Layer with 32 filters and a kernel size of 5
        conv1 = tf.layers.conv2d(x, 32, 5, activation=tf.nn.relu)
        # Max Pooling (down-sampling) with strides of 2 and kernel size of 2
        conv1 = tf.layers.max_pooling2d(conv1, 2, 2)

        # Convolution Layer with 64 filters and a kernel size of 3
        conv2 = tf.layers.conv2d(conv1, 64, 3, activation=tf.nn.relu)
        # Max Pooling (down-sampling) with strides of 2 and kernel size of 2
        conv2 = tf.layers.max_pooling2d(conv2, 2, 2)

        # Flatten the data to a 1-D vector for the fully connected layer
        fc1 = tf.contrib.layers.flatten(conv2)

        # Fully connected layer (in contrib folder for now)
        fc1 = tf.layers.dense(fc1, 512)
        # Apply Dropout (if is_training is False, dropout is not applied)
        fc1 = tf.layers.dropout(fc1, rate=dropout, training=is_training)

        # Output layer, class prediction
        out_1 = tf.layers.dense(fc1, n_classes)
        out_2 = tf.layers.dense(fc1, n_classes)
        # Because 'softmax_cross_entropy_with_logits' already apply softmax,
        # we only apply softmax to testing network
        out_1 = tf.nn.softmax(out_1) if not is_training else out_1
        out_2 = tf.nn.softmax(out_2) if not is_training else out_2

    return out_1, out_2

# Because Dropout have different behavior at training and prediction time, we
# need to create 2 distinct computation graphs that share the same weights.

# Create a graph for training
logits_train_1, logits_train_2 = conv_net(X, N_CLASSES, dropout, reuse=False, is_training=True)
# Create another graph for testing that reuse the same weights
logits_test_1, logits_test_2 = conv_net(X, N_CLASSES, dropout, reuse=True, is_training=False)
logits_val_1, logits_val_2 = conv_net(X_val, N_CLASSES, dropout, reuse=True, is_training=False)

# Define loss and optimizer (with train logits, for dropout to take effect)
loss_op = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(
    logits=logits_train_1, labels=Y[:,0])) + tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(
    logits=logits_train_2, labels=Y[:,1]))

optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
train_op = optimizer.minimize(loss_op)

# Evaluate model (with val logits on val, for dropout to be disabled)
correct_pred_val = tf.logical_and(
    tf.equal(tf.argmax(logits_val_1, 1), tf.cast(Y_val[:,0], tf.int64)),
    tf.equal(tf.argmax(logits_val_2, 1), tf.cast(Y_val[:,1], tf.int64)))
accuracy_val = tf.reduce_mean(tf.cast(correct_pred_val, tf.float32))

# Evaluate model (with test logits on train, for dropout to be disabled)
correct_pred_train = tf.logical_and(
    tf.equal(tf.argmax(logits_test_1, 1), tf.cast(Y[:,0], tf.int64)),
    tf.equal(tf.argmax(logits_test_2, 1), tf.cast(Y[:,1], tf.int64)))
accuracy_train = tf.reduce_mean(tf.cast(correct_pred_train, tf.float32))

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()

# Saver object
saver = tf.train.Saver()

# Start training
with tf.Session() as sess:

    # Run the initializer
    sess.run(init)

    # Start the data queue
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess = sess, coord = coord)

    losses = []
    train_accs = []
    val_accs = []
    # Training cycle
    for step in range(1, num_steps+1):

        if step % display_step == 0:
            # Run optimization
            sess.run([train_op])

            # Calculate average batch loss and accuracy
            total_loss = 0.0
            training_accuracy = 0.0
            validation_accuracy = 0.0

            for i in range(100):
                loss, acc_train, acc_val = sess.run([loss_op, accuracy_train, accuracy_val])
                total_loss += loss
                training_accuracy += acc_train
                validation_accuracy += acc_val

            total_loss /= 100.0
            training_accuracy /= 100.0    
            validation_accuracy /= 100.0

            print("Step " + str(step) + ", Loss= " + \
                  "{:.4f}".format(total_loss) + ", Training Accuracy= " + \
                  "{:.3f}".format(training_accuracy) + ", Validation Accuracy= " + \
                  "{:.3f}".format(validation_accuracy))

            losses.append(total_loss)
            train_accs.append(training_accuracy)
            val_accs.append(validation_accuracy)
        else:
            # Only run the optimization op (backprop)
            sess.run(train_op)

    print("Optimization Finished!")

    pickle.dump(losses, open('ml_losses.p', 'wb'))
    pickle.dump(train_accs, open('ml_train_accs.p', 'wb'))
    pickle.dump(val_accs, open('ml_val_accs.p', 'wb'))

    # Save your model
    saver.save(sess, './checkpts/shape_multi_class')

    # Stop threads
    coord.request_stop()
    coord.join(threads)

