import streamlit as st
import pandas as pd
import numpy as np
import requests
import zipfile
import io
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi tampilan seaborn
sns.set(style='dark')

# Fungsi untuk memuat dataset dari GitHub
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

    # Konversi kolom tanggal
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
    orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
    orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])

    # Gabungkan dataset
    merged_data = orders.merge(order_items, on='order_id', how='left')
    merged_data = merged_data.merge(order_payments, on='order_id', how='left')

    return merged_data

# Inisialisasi dashboard
st.title("📊 Dashboard Analisis E-Commerce")
st.sidebar.header("⚙️ Pengaturan")

data = load_data()

data['order_month'] = data['order_purchase_timestamp'].dt.to_period('M')
monthly_orders = data.groupby('order_month').size()

# 1. Visualisasi jumlah pesanan per bulan
st.subheader("📊 Jumlah Pesanan per Bulan")
fig, ax = plt.subplots(figsize=(12, 5))
data['order_purchase_timestamp'].dt.to_period("M").value_counts().sort_index().plot(kind='bar', ax=ax)
ax.set_title("Jumlah Pesanan per Bulan")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Pesanan")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# 2. Visualisasi perbandingan waktu pengiriman aktual vs estimasi
st.subheader("⏳ Rata-rata Waktu Pengiriman vs Estimasi")
data['delivery_time'] = (data['order_delivered_customer_date'] - data['order_purchase_timestamp']).dt.days
avg_actual_delivery = data['delivery_time'].mean()
avg_estimated_delivery = (data['order_estimated_delivery_date'] - data['order_purchase_timestamp']).dt.days.mean()
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(x=["Actual", "Estimated"], y=[avg_actual_delivery, avg_estimated_delivery], palette=["blue", "red"], ax=ax)
ax.set_ylabel("Hari")
st.pyplot(fig)

# 3. Visualisasi distribusi status pengiriman
st.subheader("🚚 Distribusi Status Pengiriman")
data['delivery_status'] = np.where(data['order_delivered_customer_date'] > data['order_estimated_delivery_date'], 'Late', 'On Time')
delivery_counts = data['delivery_status'].value_counts()
fig, ax = plt.subplots(figsize=(6, 4))
delivery_counts.plot(kind='bar', color=["gray", "red"], ax=ax)
ax.set_title("Distribusi Status Pengiriman")
ax.set_xlabel("Status Pengiriman")
ax.set_ylabel("Jumlah Pesanan")
ax.set_xticklabels(["On Time", "Late"], rotation=0)
st.pyplot(fig)

# 4. Visualisasi tren jumlah pesanan per bulan
st.subheader("📆 Tren Jumlah Pesanan per Bulan")
fig, ax = plt.subplots(figsize=(12, 5))
monthly_orders.plot(ax=ax, marker='o', linestyle='-', color='blue')
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Pesanan")
ax.tick_params(axis='x', rotation=45)
ax.grid()
st.pyplot(fig)

# 5. Visualisasi pola musiman dalam jumlah pesanan
st.subheader("📆 Pola Musiman dalam Jumlah Pesanan")
data['order_month_numeric'] = data['order_purchase_timestamp'].dt.month
seasonal_trend = data['order_month_numeric'].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(8, 4))
seasonal_trend.plot(kind='bar', color='green', alpha=0.7, ax=ax)
ax.set_title("Pola Musiman dalam Jumlah Pesanan")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Pesanan")
ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)
st.pyplot(fig)

# Tampilkan 5 data pertama
st.subheader("📋 Data E-Commerce")
st.dataframe(data.head())
