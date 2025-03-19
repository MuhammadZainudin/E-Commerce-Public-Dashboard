import streamlit as st
import pandas as pd
import numpy as np
import requests
import zipfile
import io
import os
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style='dark')

@st.cache_data
def load_data():
    url = "https://github.com/MuhammadZainudin/E-Commerce-Public-Dataset/archive/refs/heads/main.zip"
    response = requests.get(url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    extract_path = "ecommerce_dataset"
    zip_file.extractall(extract_path)

    folder_path = os.path.join(extract_path, "E-Commerce-Public-Dataset-main")

    def load_dataset(file_name):
        path = os.path.join(folder_path, file_name)
        return pd.read_csv(path)

    orders = load_dataset('orders_dataset.csv')
    order_items = load_dataset('order_items_dataset.csv')
    order_payments = load_dataset('order_payments_dataset.csv')

    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
    orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
    orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])

    merged_data = orders.merge(order_items, on='order_id', how='left')
    merged_data = merged_data.merge(order_payments, on='order_id', how='left')

    return merged_data

st.title("📊 Dashboard Analisis E-Commerce")
st.sidebar.header("⚙️ Pengaturan")

data = load_data()

# Interaktif: Filter data berdasarkan rentang tanggal
st.sidebar.subheader("Filter Data")
start_date = st.sidebar.date_input("Tanggal Awal", data['order_purchase_timestamp'].min())
end_date = st.sidebar.date_input("Tanggal Akhir", data['order_purchase_timestamp'].max())
data = data[(data['order_purchase_timestamp'] >= pd.to_datetime(start_date)) & (data['order_purchase_timestamp'] <= pd.to_datetime(end_date))]

st.subheader("📊 Jumlah Pesanan per Bulan")
fig, ax = plt.subplots(figsize=(12, 5))
data['order_purchase_timestamp'].dt.to_period("M").value_counts().sort_index().plot(kind='bar', ax=ax)
ax.set_title("Jumlah Pesanan per Bulan")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Pesanan")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

st.subheader("❓ Bagaimana waktu rata-rata pengiriman pesanan dibandingkan dengan estimasi waktu pengiriman?")
data['delivery_time'] = (data['order_delivered_customer_date'] - data['order_purchase_timestamp']).dt.days
avg_actual_delivery = data['delivery_time'].mean()
avg_estimated_delivery = (data['order_estimated_delivery_date'] - data['order_purchase_timestamp']).dt.days.mean()
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(x=["Actual Delivery Time", "Estimated Delivery Time"], y=[avg_actual_delivery, avg_estimated_delivery],
            palette=["blue", "red"], ax=ax)
ax.set_ylabel("Hari")
ax.set_title("Rata-rata Waktu Pengiriman vs Estimasi")
st.pyplot(fig)

data['delivery_status'] = np.where(data['order_delivered_customer_date'] > data['order_estimated_delivery_date'], 'Late', 'On Time')
delivery_counts = data['delivery_status'].value_counts()
fig, ax = plt.subplots(figsize=(6, 4))
delivery_counts.plot(kind='bar', color=["gray", "red"], ax=ax)
ax.set_title("Distribusi Status Pengiriman")
ax.set_xlabel("Status Pengiriman")
ax.set_ylabel("Jumlah Pesanan")
ax.set_xticklabels(["On Time", "Late"], rotation=0)
st.pyplot(fig)

if 'show_answers' not in st.session_state:
    st.session_state.show_answers = {}

def toggle_answer(key):
    st.session_state.show_answers[key] = not st.session_state.show_answers.get(key, False)

if st.button("Jawaban Analisis", key="delivery_answer"):
    toggle_answer("delivery_answer")
if st.session_state.show_answers.get("delivery_answer", False):
    st.write("Berdasarkan hasil analisis, terdapat perbedaan antara waktu pengiriman aktual dan estimasi yang dapat mencerminkan efisiensi atau kendala dalam proses logistik. Jika waktu pengiriman aktual lebih lama dari estimasi, ini menunjukkan adanya keterlambatan yang dapat disebabkan oleh faktor operasional, kondisi cuaca, atau infrastruktur logistik yang kurang optimal. Sebaliknya, jika pengiriman berlangsung lebih cepat dari estimasi, maka sistem distribusi berjalan dengan efisien. Distribusi status pengiriman (On Time, Late, dan Pending) memberikan gambaran lebih jelas mengenai kinerja pengiriman. Jika proporsi pesanan yang mengalami keterlambatan (Late) cukup tinggi, maka optimalisasi dalam sistem logistik dan manajemen pengiriman diperlukan untuk meningkatkan kepuasan pelanggan dan memastikan layanan yang lebih andal.")

st.subheader("❓ Bagaimana tren jumlah pesanan dari waktu ke waktu? Apakah ada pola musiman?")
data['order_month'] = data['order_purchase_timestamp'].dt.to_period('M')
data_filtered = data[data['order_month'] <= '2018-08']
monthly_orders = data_filtered.groupby('order_month').size()
plt.figure(figsize=(12, 5))
monthly_orders.plot(marker='o', linestyle='-', color='blue')
plt.title("Tren Jumlah Pesanan dari Waktu ke Waktu (sampai Agustus 2018)")
plt.xlabel("Waktu (Bulan)")
plt.ylabel("Jumlah Pesanan")
plt.xticks(rotation=45)
plt.grid()
st.pyplot(plt)

data['month'] = data['order_purchase_timestamp'].dt.month
seasonal_trend = data.groupby('month').size()
fig, ax = plt.subplots(figsize=(8, 4))
seasonal_trend.plot(kind='bar', color='green', alpha=0.7, ax=ax)
ax.set_title("Pola Musiman dalam Jumlah Pesanan")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Pesanan")
ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)
st.pyplot(fig)

if st.button("Jawaban Analisis", key="trend_answer"):
    toggle_answer("trend_answer")
if st.session_state.show_answers.get("trend_answer", False):
    st.write("Analisis tren pesanan menunjukkan adanya fluktuasi jumlah pesanan dari waktu ke waktu. Jika tren menunjukkan peningkatan pesanan secara konsisten, ini menandakan pertumbuhan bisnis yang positif, sehingga strategi pemasaran dan operasional dapat diperkuat untuk mempertahankan momentum tersebut. Sebaliknya, jika terjadi tren penurunan, maka perlu dilakukan evaluasi terhadap faktor-faktor yang berpengaruh, seperti perubahan tren pasar, kondisi ekonomi, atau faktor musiman. Dari analisis pola musiman (seasonal trend), terlihat adanya lonjakan pesanan di bulan-bulan tertentu, misalnya pada akhir tahun, yang sering dikaitkan dengan musim belanja dan promosi. Dengan memahami pola ini, bisnis dapat mengoptimalkan strategi stok, pemasaran, dan operasional agar lebih responsif terhadap lonjakan permintaan di periode strategis, serta meningkatkan efisiensi dalam rantai pasokan dan distribusi.")

st.subheader("📋 Data E-Commerce")
st.dataframe(data)
