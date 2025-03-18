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

# Filter berdasarkan rentang tanggal
min_date = data['order_purchase_timestamp'].min()
max_date = data['order_purchase_timestamp'].max()
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filter kategori produk
if 'product_category_name' in data.columns:
    categories = data['product_category_name'].dropna().unique()
    selected_category = st.sidebar.selectbox("Pilih Kategori Produk", ['Semua'] + list(categories))
else:
    selected_category = 'Semua'

# Filter metode pembayaran
if 'payment_type' in data.columns:
    payment_methods = data['payment_type'].dropna().unique()
    selected_payment = st.sidebar.multiselect("Pilih Metode Pembayaran", payment_methods, default=payment_methods)
else:
    selected_payment = []

# Filter status pengiriman
if 'order_status' in data.columns:
    delivery_status = data['order_status'].dropna().unique()
    selected_status = st.sidebar.multiselect("Pilih Status Pengiriman", delivery_status, default=delivery_status)
else:
    selected_status = []

# Terapkan filter ke data
filtered_data = data[(data['order_purchase_timestamp'] >= pd.to_datetime(date_range[0])) & (data['order_purchase_timestamp'] <= pd.to_datetime(date_range[1]))]
if selected_category != 'Semua':
    filtered_data = filtered_data[filtered_data['product_category_name'] == selected_category]
if selected_payment:
    filtered_data = filtered_data[filtered_data['payment_type'].isin(selected_payment)]
if selected_status:
    filtered_data = filtered_data[filtered_data['order_status'].isin(selected_status)]

# Visualisasi jumlah pesanan per bulan
st.subheader("📊 Jumlah Pesanan per Bulan")
fig, ax = plt.subplots(figsize=(12, 5))
filtered_data['order_purchase_timestamp'].dt.to_period("M").value_counts().sort_index().plot(kind='bar', ax=ax)
ax.set_title("Jumlah Pesanan per Bulan")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Pesanan")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# Interaktif: Pilihan analisis
st.subheader("🔍 Pilih Analisis yang Ditampilkan")
options = st.multiselect("Pilih Analisis", ["Waktu Pengiriman", "Tren Pesanan", "Data Tabel"], default=["Waktu Pengiriman", "Tren Pesanan"])

# Analisis waktu rata-rata pengiriman
if "Waktu Pengiriman" in options:
    st.subheader("❓ Waktu Rata-rata Pengiriman vs. Estimasi")
    filtered_data['delivery_time'] = (filtered_data['order_delivered_customer_date'] - filtered_data['order_purchase_timestamp']).dt.days
    avg_actual_delivery = filtered_data['delivery_time'].mean()
    avg_estimated_delivery = (filtered_data['order_estimated_delivery_date'] - filtered_data['order_purchase_timestamp']).dt.days.mean()
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=["Actual Delivery Time", "Estimated Delivery Time"], y=[avg_actual_delivery, avg_estimated_delivery], palette=["blue", "red"], ax=ax)
    ax.set_ylabel("Hari")
    st.pyplot(fig)

# Tren jumlah pesanan dari waktu ke waktu
if "Tren Pesanan" in options:
    st.subheader("❓ Tren Jumlah Pesanan dari Waktu ke Waktu")
    filtered_data['order_month'] = filtered_data['order_purchase_timestamp'].dt.to_period('M')
    monthly_orders = filtered_data.groupby('order_month').size()
    fig, ax = plt.subplots(figsize=(12, 5))
    monthly_orders.plot(ax=ax, marker='o', linestyle='-', color='blue')
    ax.set_title("Tren Jumlah Pesanan dari Waktu ke Waktu")
    ax.set_xlabel("Waktu (Bulan)")
    ax.set_ylabel("Jumlah Pesanan")
    ax.tick_params(axis='x', rotation=45)
    ax.grid()
    st.pyplot(fig)

# Tampilkan data yang telah difilter
if "Data Tabel" in options:
    st.subheader("📋 Data E-Commerce")
    st.dataframe(filtered_data)
