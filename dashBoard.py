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

# Fungsi untuk memuat data
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

# Judul dashboard
st.title("📊 Dashboard Analisis E-Commerce")

# Load data
data = load_data()

# Sidebar untuk filter interaktif
st.sidebar.header("⚙️ Pengaturan")

# Filter berdasarkan metode pembayaran
payment_methods = data['payment_type'].dropna().unique()
selected_payment = st.sidebar.multiselect("Pilih Metode Pembayaran", payment_methods, default=payment_methods)

# Filter berdasarkan status pengiriman
delivery_status = data['order_status'].dropna().unique()
selected_status = st.sidebar.multiselect("Pilih Status Pengiriman", delivery_status, default=delivery_status)

# Terapkan filter ke data
filtered_data = data[data['payment_type'].isin(selected_payment)]
filtered_data = filtered_data[filtered_data['order_status'].isin(selected_status)]

# Visualisasi jumlah pesanan per metode pembayaran
st.subheader("📊 Jumlah Pesanan per Metode Pembayaran")
fig, ax = plt.subplots(figsize=(10, 5))
payment_counts = filtered_data['payment_type'].value_counts()
payment_counts.plot(kind='bar', color='skyblue', ax=ax)
ax.set_title("Jumlah Pesanan per Metode Pembayaran")
ax.set_xlabel("Metode Pembayaran")
ax.set_ylabel("Jumlah Pesanan")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# Visualisasi jumlah pesanan per status pengiriman
st.subheader("📊 Distribusi Status Pengiriman")
fig, ax = plt.subplots(figsize=(10, 5))
status_counts = filtered_data['order_status'].value_counts()
status_counts.plot(kind='bar', color='salmon', ax=ax)
ax.set_title("Distribusi Status Pengiriman")
ax.set_xlabel("Status Pengiriman")
ax.set_ylabel("Jumlah Pesanan")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# Tampilkan data yang telah difilter
st.subheader("📋 Data E-Commerce")
st.dataframe(filtered_data.head())
