'''We modified a script posted on a Keras blog about how to employ bottleneck
features from the VGG16 neural net to distinguish cats from dogs. 

In our setup, we:
- created a data/ folder
- created train/ and validation/ subfolders inside data/
- created closedEyes/ and openEyes/ subfolders inside train/ and validation/

Thus, we have 1000 training examples for each class, and 400 validation examples 
for each class. (We randomly selected closed eye and open eye images as 
training, validation, and test examples. In summary, this is our directory 
structure:
```
data/
    train/
        closedEyes/
            ...
        openEyes/
            ...
    validation/
        closedEyes/
            ...
        openEyes/
            ...
    test/
        closedEyes/
            ...
        openEyes/
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
batch_size = 16


def save_bottlebeck_features():
    """
    Runs training and validation images through the VGG16 network (minus its top
    layer) that has been trained on ImageNet. Saves the resulting feature 
    outputs so that we can use them as inputs to train our own custom output
    layers
    """
    datagen = ImageDataGenerator(rescale=1. / 255)

    # build the VGG16 network
    model = applications.VGG16(include_top=False, weights='imagenet', input_shape=(32,32,3)) 

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
    """
    Employs the bottleneck feature outputs we saved above as training and
    validation data to fit an output network that classifies open and closed
    eyes
    """

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

    # Rescale pixel values to be between 0 and 1
    datagen = ImageDataGenerator(rescale=1. / 255)

    # Generate test data from a directory
    generator = datagen.flow_from_directory(
        test_data_dir,
        target_size=(img_width, img_height),
        color_mode='rgb',
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)

    # Instantiate the VGG16 model without its top layer. Run the test images 
    # through this model and collect its outputs
    model = applications.VGG16(include_top=False, weights='imagenet', input_shape=(32,32,3))

    predTest = model.predict_generator(
        generator, nb_test_samples // batch_size)

    print(predTest.shape)

    # Instantiate the output layers we added on top of the VGG16 bottlenecks
    model = Sequential()
    model.add(Flatten(input_shape=(1,1,512)))
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    # Load the model weights we calculated for our network above
    model.load_weights(top_model_weights_path)

    # Predict classes for our test images
    predicted = model.predict_classes(predTest)

    # Sets class labels
    predClasses = np.array(
        [0] * int(nb_test_samples/2) + [1] * int(nb_test_samples/2))

    print(classification_report(predClasses, predicted))    


save_bottlebeck_features()
train_top_model()
