# -*- coding: utf-8 -*-
"""
Created on Sun Apr  8 22:26:35 2018

@author: sorrav
"""

import tensorflow as tf

def conv(x, kernel_shape, stride=[1,1,1,1]):
  """conv returns a 2d convolution layer with ReLu activation.
      x: layer input
      kernel_shape: A 4-D Tensor with shape [height, width, in_channels, out_channels]    
  """  
  bias_shape = [kernel_shape[-1]]

  W = weight_variable(kernel_shape) 
  b = bias_variable(bias_shape)

  conv = tf.nn.conv2d(x, W, strides=stride, padding='SAME')

  return tf.nn.relu(conv + b)

def deconv(x, kernel_shape, stride=[1,1,1,1], activation='ReLu'):
  """deconv returns a 2d deconvolution layer with ReLu activation.
      x: layer input
      kernel_shape: A 4-D Tensor with shape [height, width, out_channels, in_channels]  
      activation: linear for no activation
  """   
  stride_val = stride[1]

  bias_shape = [kernel_shape[-2]]
  channel_out = kernel_shape[-2]

  W = weight_variable(kernel_shape) 
  b = bias_variable(bias_shape)
  
  dyn_input_shape = tf.shape(x)
  batch_size = dyn_input_shape[0]
  height = dyn_input_shape[1]
  width = dyn_input_shape[2]
  
  output_shape = tf.stack([batch_size, height*stride_val, width*stride_val, channel_out])
  conv_transpose = tf.nn.conv2d_transpose(x, W, output_shape=output_shape, strides=stride, padding='SAME')

  if activation == 'linear':
      return tf.add(conv_transpose, b)
  
  return tf.nn.relu(conv_transpose + b)

def fc(x, kernel_shape, activation='ReLu'):
   """fc returns a fully connected layer with ReLu activation.
      x: layer input
      kernel_shape: A 2-D Tensor with shape [feature_map_size, layer_size]
      activation: linear for no activation
  """ 
   bias_shape = [kernel_shape[-1]]
   feature_map_size = kernel_shape[0]
  
   W = weight_variable(kernel_shape) 
   b = bias_variable(bias_shape) 
  
   h_flat = tf.reshape(x, [-1, feature_map_size])
   
   if activation == 'linear':
      h_fc = tf.matmul(h_flat, W) + b
      return h_fc
  
   h_fc = tf.nn.relu(tf.matmul(h_flat, W) + b)   
   return h_fc
  
def max_pool(x, size, name, stride=[1, 2, 2, 1], padding='SAME'):
  """max_pool downsamples a feature map by taking the max value in a sizeXsize environment."""  
  return tf.nn.max_pool(x, ksize=[1, size, size, 1], strides=stride, padding=padding, name=name)

def max_pool_argmax(x, size, name, stride=[1, 2, 2, 1], padding='SAME'):
  """max_pool and additionally outputs max values indices."""
  return tf.nn.max_pool_with_argmax(x, ksize=[1, size, size, 1], strides=stride, padding=padding, name=name)

def unpool(x, size, scope):
  """unpool upsamples a feature map.""" 
  with tf.variable_scope(scope):
      out = tf.concat([x, tf.zeros_like(x)], 3)
      out = tf.concat([out, tf.zeros_like(out)], 2)
    
      sh = x.get_shape().as_list()
      if None not in sh[1:]:
        out_size = [-1, sh[1] * size, sh[2] * size, sh[3]]
        return tf.reshape(out, out_size)
    
      shv = tf.shape(x)
      ret = tf.reshape(out, tf.stack([-1, shv[1] * size, shv[2] * size, sh[3]]))
      ret.set_shape([None, None, None, sh[3]])
      return ret

def unpool_argmax(pool, 
              ind, 
              scope,
              stride=[1, 2, 2, 1]
              ):
  """Adds a 2D unpooling op.
  https://arxiv.org/abs/1505.04366
  Unpooling layer after max_pool_with_argmax.
       Args:
           pool:        max pooled output tensor
           ind:         argmax indices
           stride:      stride is the same as for the pool
       Return:
           unpool:    unpooling tensor
  """    
  with tf.variable_scope(scope):
    input_shape = tf.shape(pool)
    output_shape = [input_shape[0], input_shape[1] * stride[1], input_shape[2] * stride[2], input_shape[3]]

    flat_input_size = tf.reduce_prod(input_shape)
    flat_output_shape = [output_shape[0], output_shape[1] * output_shape[2] * output_shape[3]]

    pool_ = tf.reshape(pool, [flat_input_size])
    batch_range = tf.reshape(tf.range(tf.cast(output_shape[0], tf.int64), dtype=ind.dtype), 
                                      shape=[input_shape[0], 1, 1, 1])
    b = tf.ones_like(ind) * batch_range
    b1 = tf.reshape(b, [flat_input_size, 1])
    ind_ = tf.reshape(ind, [flat_input_size, 1])
    ind_ = tf.concat([b1, ind_], 1)

    ret = tf.scatter_nd(ind_, pool_, shape=tf.cast(flat_output_shape, tf.int64))
    ret = tf.reshape(ret, output_shape)

    set_input_shape = pool.get_shape()
    set_output_shape = [set_input_shape[0], set_input_shape[1] * stride[1], set_input_shape[2] * stride[2], set_input_shape[3]]
    ret.set_shape(set_output_shape)
    return ret

def weight_variable(shape):
  """weight_variable generates a weight variable of a given shape."""
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  """bias_variable generates a bias variable of a given shape."""
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)
