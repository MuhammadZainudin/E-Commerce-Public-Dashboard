import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import zipfile
import io
import os
import calendar


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


data = load_data()

default_start_date = pd.to_datetime("2016-09-15").date()
default_end_date = pd.to_datetime("2018-08-29").date()

st.sidebar.header("\U0001F4C5 Pilih Rentang Waktu")
start_date = st.sidebar.date_input("Tanggal Mulai", default_start_date, min_value=default_start_date,
                                   max_value=default_end_date)
end_date = st.sidebar.date_input("Tanggal Akhir", default_end_date, min_value=default_start_date,
                                 max_value=default_end_date)

filtered_data = data[(data['order_purchase_timestamp'].dt.date >= start_date) &
                     (data['order_purchase_timestamp'].dt.date <= end_date)].copy()

filtered_data['estimated_delivery_time'] = (
            filtered_data['order_estimated_delivery_date'] - filtered_data['order_purchase_timestamp']).dt.days
filtered_data['delivery_time'] = (
            filtered_data['order_delivered_customer_date'] - filtered_data['order_purchase_timestamp']).dt.days
filtered_data = filtered_data[filtered_data['delivery_time'] >= 0]

conditions = [
    filtered_data['order_delivered_customer_date'].isna(),
    filtered_data['order_delivered_customer_date'] > filtered_data['order_estimated_delivery_date'],
    filtered_data['order_delivered_customer_date'] <= filtered_data['order_estimated_delivery_date']
]
status_labels = ['Pending', 'Late', 'On Time']
filtered_data['delivery_status'] = np.select(conditions, status_labels, default='Unknown')

st.title("Dashboard Analisis E-Commerce")
st.markdown("---")

st.header("Bagaimana waktu rata-rata pengiriman pesanan dibandingkan dengan estimasi waktu pengiriman?")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Rata-rata Waktu Pengiriman vs Estimasi")
    avg_actual_delivery = filtered_data['delivery_time'].mean()
    avg_estimated_delivery = filtered_data['estimated_delivery_time'].mean()
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=["Actual Delivery Time", "Estimated Delivery Time"], y=[avg_actual_delivery, avg_estimated_delivery],
                palette=["blue", "red"], ax=ax)
    st.pyplot(fig)

with col2:
    st.subheader("Distribusi Waktu Pengiriman vs Estimasi")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=filtered_data[['delivery_time', 'estimated_delivery_time']], palette=["blue", "red"], ax=ax)
    st.pyplot(fig)

st.subheader("Distribusi Status Pengiriman")
fig, ax = plt.subplots(figsize=(6, 4))
sns.countplot(x="delivery_status", data=filtered_data, palette="viridis", order=["On Time", "Late", "Pending"], ax=ax)
st.pyplot(fig)

st.subheader("Hubungan Waktu Pengiriman vs Estimasi")
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(x="estimated_delivery_time", y="delivery_time", hue="delivery_status", data=filtered_data, alpha=0.6,
                ax=ax)
plt.axline((0, 0), slope=1, linestyle="dashed", color="black", label="Ideal Line")
st.pyplot(fig)

show_analysis = st.button("Tampilkan Hasil Analisis Pertanyaan 1")
if show_analysis:
    st.session_state.analysis_shown = not st.session_state.get("analysis_shown", False)

if st.session_state.get("analysis_shown", False):
    st.markdown("""
    Berdasarkan hasil analisis, terdapat perbedaan signifikan antara waktu pengiriman aktual dan estimasi yang mencerminkan efisiensi atau kendala dalam sistem logistik. Jika waktu pengiriman aktual lebih lama dari estimasi, hal ini menunjukkan adanya keterlambatan yang dapat dipengaruhi oleh faktor operasional, infrastruktur logistik, kondisi cuaca, atau kendala dalam rantai pasokan. Keterlambatan ini berpotensi menurunkan tingkat kepuasan pelanggan dan meningkatkan risiko keluhan. Sebaliknya, jika pengiriman lebih cepat dari estimasi, ini menunjukkan efisiensi tinggi dalam sistem distribusi. Distribusi status pengiriman (On Time, Late, dan Pending) memberikan gambaran lebih jelas mengenai performa pengiriman. Jika jumlah pesanan dengan status Late cukup tinggi, ini menjadi indikasi bahwa sistem logistik perlu dioptimalkan untuk meningkatkan keandalan pengiriman. Langkah-langkah seperti penggunaan analitik prediktif untuk estimasi waktu yang lebih akurat, transparansi informasi kepada pelanggan, dan penguatan kerja sama dengan mitra logistik dapat diterapkan untuk meningkatkan kepuasan pelanggan serta memastikan layanan yang lebih andal dan efisien.
    """)

st.markdown("---")

st.header("Bagaimana tren jumlah pesanan dari waktu ke waktu? Apakah ada pola musiman?")

filtered_data['order_month'] = filtered_data['order_purchase_timestamp'].dt.to_period('M').astype(str)
monthly_orders = filtered_data.groupby('order_month').size().reset_index(name='order_count')

st.subheader("Tren Jumlah Pesanan")
fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(data=monthly_orders, x='order_month', y='order_count', marker='o', color='blue', ax=ax)
plt.xticks(rotation=45)
ax.grid(True, linestyle="--", alpha=0.7)
st.pyplot(fig)

filtered_data['month'] = filtered_data['order_purchase_timestamp'].dt.month
seasonal_trend = filtered_data.groupby('month').size().reset_index(name='order_count')

st.subheader("Pola Musiman dalam Jumlah Pesanan")
fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(data=seasonal_trend, x='month', y='order_count', palette="Blues_d", ax=ax)
plt.xticks(ticks=range(12), labels=[calendar.month_abbr[i] for i in range(1, 13)])
st.pyplot(fig)

grouped_data = filtered_data.groupby(['order_month', 'delivery_status']).size().reset_index(name='order_count')

st.subheader("Tren Pesanan dari Waktu ke Waktu Berdasarkan Status Pengiriman")
fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(data=grouped_data, x='order_month', y='order_count', hue='delivery_status', marker='o', ax=ax)
plt.xticks(rotation=45)
ax.grid(True, linestyle="--", alpha=0.7)
st.pyplot(fig)

if st.button("Tampilkan Hasil Analisis Pertanyaan 2"):
    st.session_state.analysis_trend_shown = not st.session_state.get("analysis_trend_shown", False)

if st.session_state.get("analysis_trend_shown", False):
    st.markdown("""
    Analisis tren jumlah pesanan menunjukkan adanya fluktuasi dari waktu ke waktu, dengan pola yang mencerminkan pertumbuhan bisnis serta faktor musiman. Jika tren pesanan meningkat secara konsisten, ini mengindikasikan pertumbuhan bisnis yang positif, sehingga strategi pemasaran dan operasional dapat diperkuat untuk mempertahankan momentum tersebut. Sebaliknya, jika terjadi penurunan pesanan, perlu dilakukan evaluasi terhadap faktor-faktor yang memengaruhi, seperti perubahan tren pasar, kondisi ekonomi, persaingan, atau perubahan kebiasaan pelanggan. Dari analisis pola musiman (seasonal trend), terlihat bahwa terdapat lonjakan pesanan pada bulan-bulan tertentu, terutama di akhir tahun (November–Desember), yang dapat dikaitkan dengan musim belanja seperti Black Friday, Harbolnas, dan Natal. Dengan memahami pola ini, bisnis dapat menyusun strategi yang lebih efektif, seperti meningkatkan stok barang menjelang periode lonjakan pesanan, memperkuat kampanye pemasaran berbasis musiman, serta mengoptimalkan kapasitas pengiriman untuk menghindari keterlambatan akibat lonjakan permintaan. Dengan strategi yang tepat, perusahaan dapat memastikan stabilitas operasional dan meningkatkan kepuasan pelanggan, sekaligus memanfaatkan peluang dari pola musiman untuk meningkatkan profitabilitas.
    """)

st.markdown("---")
st.caption('© 2025 Muhammad Zainudin Damar Jati.')
