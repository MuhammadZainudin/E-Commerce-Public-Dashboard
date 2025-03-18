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

# Periksa apakah dataset memiliki kolom yang diharapkan
st.write("Kolom yang tersedia dalam dataset:", data.columns.tolist())

# Sidebar untuk filter interaktif
st.sidebar.header("⚙️ Pengaturan")

# Filter berdasarkan rentang tanggal
min_date = data['order_purchase_timestamp'].min()
max_date = data['order_purchase_timestamp'].max()
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal", [min_date, max_date], 
    min_value=min_date, max_value=max_date
)

# Filter berdasarkan kategori produk (hanya jika kolom tersedia)
if 'product_category_name' in data.columns:
    categories = data['product_category_name'].dropna().unique()
    selected_category = st.sidebar.selectbox(
        "Pilih Kategori Produk", ['Semua'] + list(categories)
    )
else:
    selected_category = 'Semua'
    st.sidebar.warning("Kolom 'product_category_name' tidak ditemukan dalam dataset.")

# Terapkan filter ke data
filtered_data = data[
    (data['order_purchase_timestamp'] >= pd.to_datetime(date_range[0])) & 
    (data['order_purchase_timestamp'] <= pd.to_datetime(date_range[1]))
]
if selected_category != 'Semua' and 'product_category_name' in data.columns:
    filtered_data = filtered_data[filtered_data['product_category_name'] == selected_category]

# Visualisasi jumlah pesanan per bulan
st.subheader("📊 Jumlah Pesanan per Bulan")
fig, ax = plt.subplots(figsize=(12, 5))
filtered_data['order_purchase_timestamp'].dt.to_period("M
