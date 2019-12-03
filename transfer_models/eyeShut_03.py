'''This script goes along the blog post
"Building powerful image classification models using very little data"
from blog.keras.io.
It uses data that can be downloaded at:
https://www.kaggle.com/c/dogs-vs-cats/data
In our setup, we:
- created a data/ folder
- created train/ and validation/ subfolders inside data/
- created cats/ and dogs/ subfolders inside train/ and validation/
- put the cat pictures index 0-999 in data/train/cats
- put the cat pictures index 1000-1400 in data/validation/cats
- put the dogs pictures index 12500-13499 in data/train/dogs
- put the dog pictures index 13500-13900 in data/validation/dogs
So that we have 1000 training examples for each class, and 400 validation examples for each class.
In summary, this is our directory structure:
```
data/
    train/
        dogs/
            dog001.jpg
            dog002.jpg
            ...
        cats/
            cat001.jpg
            cat002.jpg
            ...
    validation/
        dogs/
            dog001.jpg
            dog002.jpg
            ...
        cats/
            cat001.jpg
            cat002.jpg
            ...
```
'''
import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dropout, Flatten, Dense
from keras import applications

# dimensions of our images.
img_width, img_height = 32, 32

top_model_weights_path = 'bottleneck_fc_model.h5'
top_model_easy_path = 'whole_model.h5'
train_data_dir = 'data/train'
validation_data_dir = 'data/validation'
test_data_dir = 'data/test'
nb_train_samples = 2000
nb_validation_samples = 800
nb_test_samples = 800
epochs = 10
# epochs = 50
batch_size = 16


def save_bottlebeck_features():
    datagen = ImageDataGenerator(rescale=1. / 255)

    # build the VGG16 network
    model = applications.VGG16(include_top=False, weights='imagenet', input_shape=(32,32,3)) # specify input shape (need to change channels to 3?)

    # Added color_mode    
    generator = datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_width, img_height),
        color_mode='rgb',
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
    bottleneck_features_train = model.predict_generator(
        generator, nb_train_samples // batch_size)

# Changed commented line below to conform with Python 3
# https://stackoverflow.com/questions/50542683/typeerror-write-argument-must-be-str-not-bytes-while-saving-npy-file
    with open('bottleneck_features_train.npy', 'wb') as features_train_file:
        np.save(features_train_file, bottleneck_features_train)

    # Added color_mode
        
    generator = datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_width, img_height),
        color_mode='rgb',
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
    bottleneck_features_validation = model.predict_generator(
        generator, nb_validation_samples // batch_size)

    with open('bottleneck_features_validation.npy', 'wb') as features_validation_file:
        np.save(features_validation_file, bottleneck_features_validation)


def train_top_model():

    with open('bottleneck_features_train.npy', 'rb') as features_train_file:
        train_data = np.load(features_train_file)

    train_labels = np.array(
        [0] * int(nb_train_samples / 2) + [1] * int(nb_train_samples / 2))

    with open('bottleneck_features_validation.npy', 'rb') as features_validation_file:
        validation_data = np.load(features_validation_file)

    validation_labels = np.array(
        [0] * int(nb_validation_samples / 2) + [1] * int(nb_validation_samples / 2))

    model = Sequential()
    model.add(Flatten(input_shape=train_data.shape[1:]))
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy', metrics=['accuracy'])

    model.fit(train_data, train_labels,
              epochs=epochs,
              batch_size=batch_size,
              validation_data=(validation_data, validation_labels))
    model.save_weights(top_model_weights_path)

    model.save(top_model_easy_path)

#### Test model...should probably be separate function ####
    
    from sklearn.metrics import classification_report
    from keras.models import load_model
    from keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img

    datagen = ImageDataGenerator(rescale=1. / 255)

    generator = datagen.flow_from_directory(
        test_data_dir,
        target_size=(img_width, img_height),
        color_mode='rgb',
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)


    model = applications.VGG16(include_top=False, weights='imagenet', input_shape=(32,32,3))

    predTest = model.predict_generator(
        generator, nb_test_samples // batch_size)

    print(predTest.shape)

    #for i in predTest[:2]:
    #    print(i)

    model = Sequential()
    model.add(Flatten(input_shape=(1,1,512)))
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    #model = Sequential()
    #model.add(Flatten(input_shape=train_data.shape[1:]))
    #model.add(Dense(256, activation='relu'))
    #model.add(Dropout(0.5))
    #model.add(Dense(1, activation='sigmoid'))

    model.load_weights(top_model_weights_path)

    predicted = model.predict_classes(predTest)

    #for i in predTest:
    #    print(predTest[:2])

    #print(predicted.shape)
    #print(predicted)
    #predicted = np.argmax(predicted, axis=1)
    #print(predicted.shape)
    #print(type(predTest))
    predClasses = np.array(
        [0] * int(nb_test_samples/2) + [1] * int(nb_test_samples/2))

    print(classification_report(predClasses, predicted))    


save_bottlebeck_features()
train_top_model()
#test_model()
