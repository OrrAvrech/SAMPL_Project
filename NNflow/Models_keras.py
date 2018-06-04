import tensorflow as tf
from tensorflow.python.keras import layers
from tensorflow.python.keras.optimizers import Adam

def cross_corr(logits, labels ):
    batch_size = 2
    data_params = ([64,16,4])
    maxSources = data_params[2]
    imgSize = data_params[0]
    for i in range(batch_size):  
        y_conv = logits[i, 0:imgSize, 0:imgSize, 0:maxSources]
        y_conv = tf.reshape(y_conv, [1, imgSize, imgSize, maxSources])
        label_resh = tf.reshape(labels, [imgSize, imgSize, maxSources, -1])
        y_ = label_resh[0:imgSize, 0:imgSize, 0:maxSources, i]
        y_ = tf.reshape(y_, [imgSize, imgSize, maxSources, 1])
        result = 0  
        corr2d = tf.nn.conv2d(y_conv, y_, strides=[1, 1, 1, 1], padding='SAME')
        result += tf.reduce_mean(corr2d)
    return result/batch_size

def DeconvN(data_params):
  """DeconvN builds the graph for a deconvolutional net for seperating emitters.
  Args:
    data_params: [imgSize, numFrames, maxSources]  
    x: an input tensor of shape 64 x 64 x numFrames
  Returns:
    y_conv: a tensor of shape 64 x 64 x maxSources 
  """
  
  # Data Dimensions
  # Reshape to use within a convolutional neural net.
  # Last dimension is for "features" - it would be 1 for grayscale
  # 3 for an RGB image, 4 for RGBA, numFrames for a movie.    
  maxSources = data_params[2]
  numFrames = data_params[1]
  imgSize = data_params[0]
  input_size_flat = imgSize * imgSize * numFrames
  input_shape_full = (imgSize, imgSize, numFrames)
  
  # Start construction of a Keras Sequential model.
  model = tf.keras.Sequential()
  
  model.add(layers.InputLayer(input_shape=(input_size_flat,)))
  
  model.add(layers.Reshape(input_shape_full))
  
  # First convolutional layer.
  # TODO: Categorial activations
  model.add(layers.Conv2D(kernel_size=3, strides=1, filters=32, padding='same',
                     activation='relu', name='layer_conv1_1')) 
  model.add(layers.Conv2D(kernel_size=3, strides=1, filters=32, padding='same',
                     activation='relu', name='layer_conv1_2'))
  model.add(layers.MaxPooling2D(pool_size=2, strides=2))
  # Maps to 32x32x32 feature map
  
  # Second convolutional layer.
  model.add(layers.Conv2D(kernel_size=3, strides=1, filters=64, padding='same',
                     activation='relu', name='layer_conv2_1')) 
  model.add(layers.Conv2D(kernel_size=3, strides=1, filters=64, padding='same',
                     activation='relu', name='layer_conv2_2'))
  model.add(layers.MaxPooling2D(pool_size=2, strides=2))
  # Maps to 16x16x64 feature map
  
  # Third convolutional layer.
  model.add(layers.Conv2D(kernel_size=3, strides=1, filters=128, padding='same',
                     activation='relu', name='layer_conv3_1')) 
  model.add(layers.Conv2D(kernel_size=3, strides=1, filters=128, padding='same',
                     activation='relu', name='layer_conv3_2'))
  model.add(layers.MaxPooling2D(pool_size=2, strides=2))
  # Maps to 8x8x128 feature map
  
  # First Deconvolutional Layer + Unpsampling
  model.add(layers.UpSampling2D((2, 2)))
  model.add(layers.Conv2DTranspose(kernel_size=3, strides=1, filters=128, padding='same',
                     activation='relu', name='layer_deconv1_1')) 
  model.add(layers.Conv2DTranspose(kernel_size=3, strides=1, filters=64, padding='same',
                     activation='relu', name='layer_deconv1_2')) 
  
  # Second Deconvolutional Layer + Unpsampling
  model.add(layers.UpSampling2D((2, 2)))
  model.add(layers.Conv2DTranspose(kernel_size=3, strides=1, filters=64, padding='same',
                     activation='relu', name='layer_deconv2_1')) 
  model.add(layers.Conv2DTranspose(kernel_size=3, strides=1, filters=32, padding='same',
                     activation='relu', name='layer_deconv2_2')) 
  
  # First Deconvolutional Layer + Unpsampling
  model.add(layers.UpSampling2D((2, 2)))
  model.add(layers.Conv2DTranspose(kernel_size=3, strides=1, filters=32, padding='same',
                     activation='relu', name='layer_deconv3_1')) 
  model.add(layers.Conv2DTranspose(kernel_size=3, strides=1, filters=32, padding='same',
                     activation='relu', name='layer_deconv3_2')) 
  model.add(layers.Conv2DTranspose(kernel_size=3, strides=1, filters=maxSources, padding='same',
                     activation='linear', name='layer_deconv3_3')) 
  
  # Use the Adam method for training the network.
  # We want to find the best learning-rate for the Adam method.
  # TODO: learning rate param
  optimizer = Adam(lr=1e-4)
    
  # In Keras we need to compile the model so it can be trained.
  model.compile(optimizer=optimizer,
                  loss='mean_absolute_error',
                  metrics=['accuracy', cross_corr])
    
  return model

#history = model.fit(x=data.train.images,
#                        y=data.train.labels,
#                        epochs=3,
#                        batch_size=128)
 
#  with tf.name_scope('reshape_x'):  
#    x_image = tf.reshape(x, [-1, imgSize, imgSize, numFrames])
#    # -1 is for the batch size, will be dynamically assigned 
#
#  # First Convolutional Layer + maxPooling with argmax
#  with tf.name_scope('conv1'):
#    conv1_1 = layers.conv(x_image, [3, 3, numFrames, 32])  
#    conv1_2 = layers.conv(conv1_1, [3, 3, 32, 32])  
#    h_pool1 = layers.max_pool(conv1_2, 2, 'pool1')
#    # Maps to 32x32x32 feature map
#
#  # Second Convolutional Layer + maxPooling with argmax
#  with tf.name_scope('conv2'):
#    conv2_1 = layers.conv(h_pool1, [3, 3, 32, 64])  
#    conv2_2 = layers.conv(conv2_1, [3, 3, 64, 64])  
#    h_pool2 = layers.max_pool(conv2_2, 2, 'pool2')
#    # Maps to 16x16x64 feature map
#    
#  # Third Convolutional Layer + maxPooling with argmax
#  with tf.name_scope('conv3'):
#    conv3_1 = layers.conv(h_pool2, [3, 3, 64, 128])  
#    conv3_2 = layers.conv(conv3_1, [3, 3, 128, 128])  
#    conv3_3 = layers.conv(conv3_2, [3, 3, 128, 128])  
#    h_pool3 = layers.max_pool(conv3_3, 2, 'pool3')
#    # Maps to 8x8x128 feature map
    
#  # Dropout - controls the complexity of the model, prevents co-adaptation of
#  # features.
#  with tf.name_scope('dropout'):  
#    keep_prob = tf.placeholder(tf.float32) # dummy placeholder
#    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

  # First Deconvolutional Layer + Unpooling with argmax
#  with tf.name_scope('deconv1'):  
#    h_unpool1 = layers.unpool(h_pool3, 2, 'unpool1') 
#    deconv1_1 = layers.deconv(h_unpool1, [3, 3, 128, 128])
#    deconv1_2 = layers.deconv(deconv1_1, [3, 3, 128, 128])
#    deconv1_3 = layers.deconv(deconv1_2, [3, 3, 64, 128])
#    # Maps to 16x16x64
#          
#  # Second Deconvolutional Layer + Unpooling with argmax
#  with tf.name_scope('deconv2'):
#    h_unpool2 = layers.unpool(deconv1_3, 2, 'unpool2')  
#    deconv2_1 = layers.deconv(h_unpool2, [3, 3, 64, 64])
#    deconv2_2 = layers.deconv(deconv2_1, [3, 3, 32, 64])
#    # Maps to 32x32x32
#    
#  # Third Deconvolutional Layer + Unpooling with argmax
#  with tf.name_scope('deconv3'):
#    h_unpool3 = layers.unpool(deconv2_2, 2, 'unpool3')  
#    deconv3_1 = layers.deconv(h_unpool3, [3, 3, 32, 32])
#    deconv3_2 = layers.deconv(deconv3_1, [3, 3, 32, 32])
#    deconv3_3 = layers.deconv(deconv3_2, [3, 3, maxSources, 32], activation='linear')
    
#  with tf.name_scope('reshape_y'):
#    y_conv = tf.reshape(deconv3_3, [-1, imgSize, imgSize, maxSources])
#    # -1 is for the batch size, will be dynamically assigned 
#    
#  return y_conv, keep_prob


def ConvFCN(x,data_params):
  """ConvFCN builds the graph for a convolutional fully connected net for seperating emitters.
  Args:
    data_params: [imgSize, numFrames, maxSources]  
    x: an input tensor of shape 64 x 64 x numFrames
  Returns:
    y_conv: a tensor of shape 64 x 64 x maxSources 
    keep_prob: dropout placeholder
  """
  
  # Reshape to use within a convolutional neural net.
  # Last dimension is for "features" - it would be 1 for grayscale
  # 3 for an RGB image, 4 for RGBA, numFrames for a movie.    
  maxSources = data_params[2]
  numFrames = data_params[1]
  imgSize = data_params[0]
  with tf.name_scope('reshape_x'):
    x_image = tf.reshape(x, [-1, imgSize, imgSize, numFrames])
    # -1 is for the batch size, will be dynamically assigned 

  # First convolutional layer
  with tf.name_scope('conv1'):
    h_conv1 = layers.conv(x_image, [5, 5, numFrames, 16])
  # First pooling layer - downsamples by 2X.
  with tf.name_scope('pool1'):
    h_pool1 = layers.max_pool(h_conv1, 2, 'pool1')
  # 32x32x16 feature map  

  # Second convolutional layer
  with tf.name_scope('conv2'):
    h_conv2 = layers.conv(h_pool1, [5, 5, 16, 32])
  # Second pooling layer.
  with tf.name_scope('pool2'):
    h_pool2 = layers.max_pool(h_conv2, 2, 'pool2')
  # 16x16x32 feature map   

  # Fully connected layer 1 -- feature map to hidden layer
  fc1_length = 8192 # user defined
  feature_map_size = 16 * 16 * 32
  with tf.name_scope('fc1'):
    h_fc1 = layers.fc(h_pool2, [feature_map_size, fc1_length])

  # Dropout - controls the complexity of the model, prevents co-adaptation of
  # features.
  with tf.name_scope('dropout'):
    keep_prob = tf.placeholder(tf.float32, name = 'keep_prob')
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

  # Fully connected layer 2 -- hidden layer to output layer
  with tf.name_scope('fc2'):
    h_fc2 = layers.fc(h_fc1_drop, [fc1_length, imgSize*imgSize*maxSources], activation='linear')
    
  with tf.name_scope('reshape_y'):
    y_conv = tf.reshape(h_fc2, [-1, imgSize, imgSize, maxSources], name="y_conv")
    # -1 is for the batch size, will be dynamically assigned 
    
  return y_conv, keep_prob

