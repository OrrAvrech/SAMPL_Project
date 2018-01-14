# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 01:05:30 2018

@author: orrav
"""

#%%
import tensorflow as tf
import numpy as np
import h5py
import os

def datasetFromMat(path, start_idx, end_idx, test_perc):

    data_dir = os.path.dirname(path)
    
    dataset_x = []
    dataset_y = []
    
    for i in range(start_idx, end_idx):
        data_file = os.path.join(data_dir, str(i)+ '.mat')
        with h5py.File(data_file, 'r') as f:
            sample_x = np.array(f.get('features'))
            sample_y = np.array(f.get('labels'))
            sample_y = np.reshape(sample_y, (1,sample_y.shape[0],sample_y.shape[1],sample_y.shape[2]))
            sample_x = np.reshape(sample_x, (1,sample_x.shape[0],sample_x.shape[1],sample_x.shape[2]))
            if i == start_idx:
                dataset_x = sample_x
                dataset_y = sample_y
            else:
                dataset_x = np.append(dataset_x,sample_x, axis=0)
                dataset_y = np.append(dataset_y,sample_y, axis=0)
    features = dataset_x
    labels = dataset_y
    
    dataset_size = features.shape[0]
    test_size = np.rint(test_perc * dataset_size).astype(int) # round to int
    train_size = dataset_size - test_size  
    
    train_features, test_features = tf.split(features, [train_size, test_size]) 
    train_labels, test_labels = tf.split(labels, [train_size, test_size])                                           
                                               
    datasetMat = type('', (), {})()
    datasetMat.train_features = train_features
    datasetMat.train_labels   = train_labels
    datasetMat.test_features  = test_features
    datasetMat.test_labels    = test_labels
#    dataset = tf.data.Dataset.from_tensor_slices((features, labels))
    return datasetMat

class DataSet(object):

  def __init__(self,
               features,
               labels):
    """Construct a DataSet"""
    self._features = features
    self._labels = labels
    self._epochs_completed = 0
    self._index_in_epoch = 0

  @property
  def features(self):
    return self._features

  @property
  def labels(self):
    return self._labels

  @property
  def num_examples(self):
    return self._num_examples

  @property
  def epochs_completed(self):
    return self._epochs_completed

  def next_batch(self, batch_size, shuffle=True):
    """Return the next `batch_size` examples from this data set."""
    start = self._index_in_epoch
    # Shuffle for the first epoch
    if self._epochs_completed == 0 and start == 0 and shuffle:
      perm0 = np.arange(self._num_examples)
      np.random.shuffle(perm0)
      self._features = self.features[perm0]
      self._labels = self.labels[perm0]
    # Go to the next epoch
    if start + batch_size > self._num_examples:
      # Finished epoch
      self._epochs_completed += 1
      # Get the rest examples in this epoch
      rest_num_examples = self._num_examples - start
      features_rest_part = self._features[start:self._num_examples]
      labels_rest_part = self._labels[start:self._num_examples]
      # Shuffle the data
      if shuffle:
        perm = np.arange(self._num_examples)
        np.random.shuffle(perm)
        self._features = self.features[perm]
        self._labels = self.labels[perm]
      # Start next epoch
      start = 0
      self._index_in_epoch = batch_size - rest_num_examples
      end = self._index_in_epoch
      features_new_part = self._features[start:end]
      labels_new_part = self._labels[start:end]
      return np.concatenate((features_rest_part, features_new_part), axis=0) , np.concatenate((labels_rest_part, labels_new_part), axis=0)
    else:
      self._index_in_epoch += batch_size
      end = self._index_in_epoch
      return self._features[start:end], self._labels[start:end]


def read_data_sets(path, start_idx, end_idx):

  test_perc = 0.2
  validation_perc = 0.2 # out of train size
  datasetMat = datasetFromMat(path, start_idx, end_idx, test_perc)  
    
  train_features = datasetMat.train_features
  train_labels   = datasetMat.train_labels  
  test_features  = datasetMat.test_features
  test_labels    = datasetMat.test_labels
    
  validation_size = np.rint(validation_perc * np.float_(train_features.shape[0].value)).astype(int)
  
  validation_images = train_features[:validation_size]
  validation_labels = train_labels[:validation_size]
  train_images = train_features[validation_size:]
  train_labels = train_labels[validation_size:]

  train = DataSet(train_images, train_labels)
  validation = DataSet(validation_images, validation_labels)
  test = DataSet(test_features, test_labels)

  dataObj = type('', (), {})()
  dataObj.train = train
  dataObj.validation = validation
  dataObj.test = test
  return dataObj

def load_dataset(path, start_idx=1, end_idx=100):
  return read_data_sets(path, start_idx, end_idx)
