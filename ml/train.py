import argparse,json
from pathlib import Path
import tensorflow as tf
p=argparse.ArgumentParser();p.add_argument("--data_dir",required=True);p.add_argument("--epochs",type=int,default=8);a=p.parse_args()
t=(224,224);tr=tf.keras.utils.image_dataset_from_directory(a.data_dir,validation_split=.2,subset="training",seed=42,image_size=t,batch_size=16);va=tf.keras.utils.image_dataset_from_directory(a.data_dir,validation_split=.2,subset="validation",seed=42,image_size=t,batch_size=16);classes=tr.class_names
base=tf.keras.applications.MobileNetV2(input_shape=(224,224,3),include_top=False,weights="imagenet");base.trainable=False
i=tf.keras.Input((224,224,3));x=tf.keras.layers.RandomFlip("horizontal")(i);x=tf.keras.layers.RandomRotation(.08)(x);x=tf.keras.applications.mobilenet_v2.preprocess_input(x);x=base(x,training=False);x=tf.keras.layers.GlobalAveragePooling2D()(x);x=tf.keras.layers.Dropout(.25)(x);o=tf.keras.layers.Dense(len(classes),activation="softmax")(x);m=tf.keras.Model(i,o);m.compile(optimizer="adam",loss="sparse_categorical_crossentropy",metrics=["accuracy"]);m.fit(tr,validation_data=va,epochs=a.epochs);out=Path("backend/ml_models");out.mkdir(parents=True,exist_ok=True);m.save(out/"banana_model.keras");(out/"class_names.json").write_text(json.dumps(classes));print("Validation accuracy:",m.evaluate(va,verbose=0)[1])
