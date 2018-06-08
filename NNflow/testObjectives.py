import numpy as np
from tensorflow.python.keras import backend as K

#%% Accuracy Metric: Normalized Cross Correlation (NCC)
def tensor_NCC(y_pred, y_label):
    Npred  = (y_pred - K.mean(y_pred, [1,2], keepdims=True)) / K.std(y_pred, [1, 2], keepdims=True)
    Nlabel = (y_label - K.mean(y_label, [1,2], keepdims=True)) / K.std(y_label, [1, 2], keepdims=True)
    res = K.abs(K.mean(Npred * Nlabel, [1, 2], keepdims=True))
    return K.mean(res)

def np_NCC(y_pred, y_label):
    res = 0
    batch_size = np.shape(y_label)[0]
    maxSources = np.shape(y_label)[-1]
    for ii in range(batch_size):  
        resSources = 0
        for jj in range(maxSources):
            pred   = y_pred[ii,:,:,jj].flatten()
            label  = y_label[ii,:,:,jj].flatten()
            Npred  = (pred - np.mean(pred)) / np.std(pred)
            Nlabel = (label - np.mean(label)) / np.std(label)
            resSources += np.absolute(np.mean(Npred * Nlabel))
        res += resSources/maxSources
    return res/batch_size

#%% Tensor to numpy objective testing environment
def check_loss(shape, tensor_objective, np_objective):
    y_a = np.random.random(shape)
    y_b = np.random.random(shape)

    out1 = K.eval(tensor_objective(K.variable(y_a), K.variable(y_b)))
    out2 = np_objective(y_a, y_b)
    print('l2 norm of tensor_objective output:', np.linalg.norm(out1))
    print('l2 norm of numpy_objective output:', np.linalg.norm(out2))
    print('Euclidean distance between the two outputs:', np.linalg.norm(out1-out2))

if __name__ == '__main__':
    # Set tested tensor shape 
    shape = (8, 64, 64, 2)
    # Set tensor objective function
    tensor_objective = tensor_NCC
    # Set numpy objective function
    np_objective     = np_NCC
    # Obtain the ditance between the two outputs
    check_loss(shape, tensor_objective, np_objective)

