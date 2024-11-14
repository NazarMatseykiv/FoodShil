import streamlit as st
import tensorflow as tf
import numpy as np
import time
import os
from pymongo import MongoClient
from bson import Binary

# Підключення до MongoDB
client = MongoClient("mongodb+srv://administrator:STZbC7Nvcvpq61RS@shil.xeunmt2.mongodb.net/shil")
db = client["shil"]
collection = db["prediction"]

def load_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Model
def model_prediction(img):
    model = tf.keras.models.load_model("model/model_food.h5")
    image = tf.keras.preprocessing.image.load_img(img, target_size = (100,100))
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])
    predictions = model.predict(input_arr)
    return np.argmax(predictions)

def save_prediction_to_db(image, prediction):
    unique_filename = f"{int(time.time() * 1000)}{image.name}"
    
    with open(os.path.join("uploaded_images", unique_filename), "wb") as f:
        f.write(image.read())
    
    prediction_data = {
        "image": unique_filename,
        "prediction": prediction
    }
    collection.insert_one(prediction_data)

load_css("style/style.css")

# Ліва частина
st.sidebar.markdown('<h1 class="sidebar-title">Головна</h1>', unsafe_allow_html=True)
app_mode = st.sidebar.selectbox("Сторінки", ["Home", "Classification"])

# Головна
if(app_mode =="Home"):
    st.markdown('<div class="center-content">', unsafe_allow_html=True)
    st.header("Shill")
    image_path = "shillogo.png"
    st.image(image_path)
    st.subheader("Ласкаво просимо до Shill!")
    st.write(
        """
        Це ваш помічник для класифікації зображень їжі.
        Завантажте зображення та отримайте результат від моделі. 
        Проста у використанні платформа для кухарів, ресторанів та всіх, хто цікавиться їжею!
        """
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Адміністрація
elif(app_mode == "Classification"):
    st.header("Класифікація зображення")
    img = st.file_uploader("Завантажити зображення")
    if(st.button("Показати зображення")):
        st.image(img, width = 6, use_container_width = True)
# Прогнозування
    if(st.button("Розпізнати")):
        result = model_prediction(img)
        with open("asset/assets.txt") as food:
            content = food.readlines()
        asset = []
        for i in content[:11]:
            asset.append(i[:-1])
        st.success("Модель прогнозування: {}".format(asset[result]))
        save_prediction_to_db(img, asset[result])