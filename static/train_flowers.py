# train_flowers.py
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os, sys

base_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(base_dir, "flowers")

datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

train_gen = datagen.flow_from_directory(
    dataset_path,
    target_size=(224, 224),
    batch_size=32,
    class_mode="categorical",
    subset="training",
    shuffle=True
)

val_gen = datagen.flow_from_directory(
    dataset_path,
    target_size=(224, 224),
    batch_size=32,
    class_mode="categorical",
    subset="validation",
    shuffle=False
)

# Save label order that corresponds to model outputs
labels = [None] * len(train_gen.class_indices)
for label, idx in train_gen.class_indices.items():
    labels[idx] = label
with open("labels.txt", "w", encoding="utf-8") as f:
    for lab in labels:
        f.write(lab + "\n")
print("Saved labels.txt:", labels)

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224,224,3),
    include_top=False,
    weights="imagenet"
)
base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation="relu")(x)
x = Dropout(0.5)(x)
predictions = Dense(train_gen.num_classes, activation="softmax")(x)
model = Model(inputs=base_model.input, outputs=predictions)

model.compile(optimizer=Adam(learning_rate=0.0005), loss="categorical_crossentropy", metrics=["accuracy"])

early_stop = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)
checkpoint = ModelCheckpoint("best_flowers_model.keras", save_best_only=True)

history = model.fit(train_gen, validation_data=val_gen, epochs=15, verbose=1, callbacks=[early_stop, checkpoint])

# fine-tune
base_model.trainable = True
for layer in base_model.layers[:100]:
    layer.trainable = False

model.compile(optimizer=Adam(learning_rate=1e-5), loss="categorical_crossentropy", metrics=["accuracy"])
history_fine = model.fit(train_gen, validation_data=val_gen, epochs=10, verbose=1, callbacks=[early_stop, checkpoint])

model.save("flowers_model.keras")
sys.stdout.reconfigure(encoding='utf-8')
print("✅ Training selesai. Model dan labels.txt disimpan.")
