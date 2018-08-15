import numpy as np
import os

from tensorflow.python.keras import backend as K
from tensorflow.python.keras import callbacks
# Import Models
import Models_keras as models
from testObjectives import np_NCC


#%% Create and Fit Model
# best_accuracy = 0.0
best_accuracy = 10**100000000
call_num = 1
def fit_model(cfg, learning_rate, num_conv_Bulks, kernel_size, activation):
   
#      # Import data
      epochs = cfg.exp.epochs
      dataObj = cfg.data.obj
      batch_size = cfg.exp.batch
#      epochs = 10
#      dataObj = cfg.data.obj
#      batch_size = 2
      
      
      # Print the hyper-parameters.
      global call_num
      print()
      print('call_number:', call_num)
      call_num += 1
      print() #model dependent
      print('num_conv_Bulks:', num_conv_Bulks)
      print('kernel_size:', kernel_size)
      print('activation:', activation)
      print()
      print('learning rate: {0:.1e}'.format(learning_rate))
      print('epochs:',epochs)
      print('batch_size:', batch_size)
      print()
      
      # Create Model
      arch_func = models.DeconvN # TODO: Generalize to multiple models
      model = arch_func(cfg, learning_rate, num_conv_Bulks, kernel_size, activation)
      
      callback_list = [callbacks.TensorBoard(log_dir=cfg.paths.summaries_current)]
      
      # Use Keras to train the model.      
      validation_data = (dataObj.validation.features, dataObj.validation.labels)
      fitness = model.fit(x=dataObj.train.features,
                          y=dataObj.train.labels,
                          epochs=epochs,
                          batch_size=batch_size,
                          validation_data=validation_data,
                          callbacks=callback_list)
                      

      # Get the accuracy on the validation-set
      # after the last training-epoch.
#      fun = K.function([model.layers[0].input],[model.layers[-1].output])
#      x_input = dataObj.train.features[0:1,:,:,:]
#      layer_output = fun([x_input])[0]
#      label = dataObj.train.labels[0:1,:,:,:]
#      
#      print(layer_output)
#      print(np_NCC(layer_output,label))
#      print()
      
      
      accuracy = fitness.history['val_mean_absolute_error'][-1]
      if np.isnan(accuracy):
          accuracy=0

      global best_accuracy
      if accuracy < best_accuracy:
          # Save the new model to harddisk.
          if not os.path.exists(cfg.paths.best_models):
              os.makedirs(cfg.paths.best_models)
          model.save(cfg.paths.model)
          
          # Update the classification accuracy.
          best_accuracy = accuracy
      
      # Delete the Keras model with these hyper-parameters from memory.
      del model
    
      # Clear the Keras session, otherwise it will keep adding new
      # models to the same TensorFlow graph each time we create a model
      K.clear_session()
      return accuracy