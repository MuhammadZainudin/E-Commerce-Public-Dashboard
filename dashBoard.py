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
monthly_counts = data['order_purchase_timestamp'].dt.to_period("M").value_counts().sort_index()
if not monthly_counts.empty:
    monthly_counts.plot(kind='bar', ax=ax)
    ax.set_title("Jumlah Pesanan per Bulan")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Jumlah Pesanan")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
else:
    st.warning("Tidak ada data pesanan dalam rentang waktu yang dipilih.")

st.subheader("❓ Bagaimana waktu rata-rata pengiriman pesanan dibandingkan dengan estimasi waktu pengiriman?")
data['delivery_time'] = (data['order_delivered_customer_date'] - data['order_purchase_timestamp']).dt.days
if data['delivery_time'].notna().sum() > 0:
    avg_actual_delivery = data['delivery_time'].mean()
    avg_estimated_delivery = (data['order_estimated_delivery_date'] - data['order_purchase_timestamp']).dt.days.mean()
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=["Actual Delivery Time", "Estimated Delivery Time"], y=[avg_actual_delivery, avg_estimated_delivery],
                palette=["blue", "red"], ax=ax)
    ax.set_ylabel("Hari")
    ax.set_title("Rata-rata Waktu Pengiriman vs Estimasi")
    st.pyplot(fig)
else:
    st.warning("Tidak ada data pengiriman tersedia.")

st.subheader("❓ Bagaimana tren jumlah pesanan dari waktu ke waktu? Apakah ada pola musiman?")
data['order_month'] = data['order_purchase_timestamp'].dt.to_period('M')
data_filtered = data[data['order_month'] <= '2018-08']
monthly_orders = data_filtered.groupby('order_month').size()
if not monthly_orders.empty:
    fig, ax = plt.subplots(figsize=(12, 5))
    monthly_orders.plot(marker='o', linestyle='-', color='blue', ax=ax)
    ax.set_title("Tren Jumlah Pesanan dari Waktu ke Waktu (sampai Agustus 2018)")
    ax.set_xlabel("Waktu (Bulan)")
    ax.set_ylabel("Jumlah Pesanan")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
else:
    st.warning("Tidak ada data tren pesanan yang tersedia.")

seasonal_trend = data.groupby(data['order_purchase_timestamp'].dt.month).size()
if not seasonal_trend.empty:
    fig, ax = plt.subplots(figsize=(8, 4))
    seasonal_trend.plot(kind='bar', color='green', alpha=0.7, ax=ax)
    ax.set_title("Pola Musiman dalam Jumlah Pesanan")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Jumlah Pesanan")
    ax.set_xticks(range(12))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)
    st.pyplot(fig)
else:
    st.warning("Tidak ada data pola musiman yang tersedia.")

st.subheader("📋 Data E-Commerce")
st.dataframe(data)
