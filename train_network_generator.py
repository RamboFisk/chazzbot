import keras
import numpy as np
import math
import json
import os
from random import shuffle

from dnn_model import model_creator
from data_extractor import reshape_moves

from sklearn.model_selection import train_test_split
from keras.models import Sequential, load_model
from keras.wrappers.scikit_learn import KerasRegressor
from keras.callbacks import EarlyStopping, ModelCheckpoint

#-----------------------------------------
# get trining data
#-----------------------------------------
#get all data from files
#need to use GENERATOR
def get_training_data(batch_size, data_size):
  print("loading files...")
  count = 0
  data = []

  #find all files
  file_names = os.listdir("./ext")
  shuffle(file_names)

  pop_new = True
  while len(file_names):
    if pop_new:
      while len(data) < data_size:
        if len(file_names) < 1:
          break
        file_name = file_names.pop()
        file_extension = os.path.splitext(file_name)[1]
        if file_extension != '.json':
          continue
        print('   ' + file_name, end='\r')

        with open("ext/" + file_name, "r") as file:
          try:
            data = data + json.load(file)
          except:
            continue
        pop_new = False
      shuffle(data)
      count = 0

    x, y = return_training_data(batch_size, count, data)    
    if len(x) < batch_size:
      pop_new = True
      data = []
      continue
    
    yield x, y

    count += batch_size

    if len(file_names) == 0:
      print('Whole dataset has been looped through... \n\n')
      file_names = os.listdir("./ext")
      shuffle(file_names)
  print('woh')

def return_training_data(batch_size, point, data):
  X = []
  Y = []
  for x in data[point:point+batch_size]:
    X.append(x[:-1]) # first are move data
    Y.append([x[-1]]) #last spot is score

  return np.array(X), np.array(Y)

# should add training function and so on
def train_network(model_name):
  epochs = 6
  batch_size = 256
  data_size = 262144 # number of datapoins loaded into momory at once
  samples_per_epoch = 36*data_size/batch_size#number of datapoins traversed per epoch
  validation_steps = 200
  evaluate_samples_per_epoch = 100

  model_filepath = "model/" + model_name + ".h5"

  callbacks = []
  callbacks.append(keras.callbacks.TensorBoard(log_dir='./Graph/' + model_name, histogram_freq=0, write_graph=True, write_images=True))
  callbacks.append(ModelCheckpoint(model_filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max'))
  #callbacks.append(EarlyStopping(monitor='val_acc', patience=4, min_delta=0.0001))

  try:
    model = load_model(model_filepath)
    print('Loaded prevoisly saved model')
  except:
    model = model_creator()
    print('Created new model')


  model.fit_generator(get_training_data(batch_size, data_size), epochs=epochs, steps_per_epoch=samples_per_epoch, callbacks=callbacks, validation_data=get_training_data(batch_size, data_size), validation_steps=validation_steps)
  loss_and_metrics = model.evaluate_generator(get_training_data(batch_size, data_size), steps=evaluate_samples_per_epoch, verbose=0)
  print(loss_and_metrics)
  print(model.metrics_names[1] + ": " + str(loss_and_metrics[1] * 100))

  model.save(model_filepath)

def evaluate_model(model):
  evaluate_samples_per_epoch = 100
  batch_size = 256
  loss_and_metrics = model.evaluate_generator(get_training_data(batch_size, 250000), steps=evaluate_samples_per_epoch, verbose=0)
  print(loss_and_metrics)
  print(model.metrics_names[1] + ": " + str(loss_and_metrics[1] * 100))