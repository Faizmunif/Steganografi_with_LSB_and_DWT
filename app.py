import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pywt
from skimage.metrics import peak_signal_noise_ratio, mean_squared_error
import io

# ===== Helper Functions =====
def perform_eda(img):
    st.subheader("Exploratory Data Analysis")
    st.write("Format:", img.format)
    st.write("Ukuran:", img.size)
    st.write("Mode:", img.mode)

    img_np = np.array(img)
    st.write("Dimensi array:", img_np.shape)
    st.write("Rata-rata pixel:", np.mean(img_np))
    st.write("Maksimum pixel:", np.max(img_np))
    st.write("Minimum pixel:", np.min(img_np))

    st.image(img, caption="Original Image", use_container_width=True)

    if img.mode != 'RGB':
        img = img.convert('RGB')
    r, g, b = img.split()
    r_np, g_np, b_np = np.array(r), np.array(g), np.array(b)

    st.subheader("Histograms per Channel")
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))
    colors = ('red', 'green', 'blue')
    for i, channel in enumerate([r_np, g_np, b_np]):
        axs[i].hist(channel.flatten(), bins=256, color=colors[i], alpha=0.7)
        axs[i].set_title(f'{colors[i].capitalize()} Histogram')
    st.pyplot(fig)

    st.subheader("Channel Heatmaps")
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    cmap_names = ['Reds', 'Greens', 'Blues']
    for i, (channel, name) in enumerate(zip([r_np, g_np, b_np], ['Red', 'Green', 'Blue'])):
        sns.heatmap(channel, cmap=cmap_names[i], cbar=False, ax=axs[i])
        axs[i].set_title(f"{name} Channel Heatmap")
        axs[i].axis("off")
    st.pyplot(fig)

    st.subheader("DWT Level-1 (Channel Merah)")
    coeffs2 = pywt.dwt2(img_np[:, :, 0], 'haar')
    LL, (LH, HL, HH) = coeffs2
    fig, axs = plt.subplots(2, 2, figsize=(10, 6))
    titles = ['LL', 'LH', 'HL', 'HH']
    for i, data in enumerate([LL, LH, HL, HH]):
        ax = axs[i//2, i%2]
        ax.imshow(data, cmap='gray')
        ax.set_title(titles[i])
        ax.axis("off")
    st.pyplot(fig)

def encode_LSB(image, message):
    encoded = image.copy()
    width, height = encoded.size
    message += chr(0)
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    data_index = 0
    for y in range(height):
        for x in range(width):
            if data_index >= len(binary_message):
                break
            pixel = encoded.getpixel((x, y))
            if isinstance(pixel, int):  # grayscale
                new_pixel = pixel & ~1 | int(binary_message[data_index])
                encoded.putpixel((x, y), new_pixel)
                data_index += 1
            else:  # RGB
                pixel = list(pixel)
                for n in range(3):
                    if data_index < len(binary_message):
                        pixel[n] = pixel[n] & ~1 | int(binary_message[data_index])
                        data_index += 1
                encoded.putpixel((x, y), tuple(pixel))
    return encoded

def decode_LSB(image):
    binary_data = ""
    for y in range(image.height):
        for x in range(image.width):
            pixel = image.getpixel((x, y))
            if isinstance(pixel, int):
                binary_data += str(pixel & 1)
            else:
                for n in range(3):
                    binary_data += str(pixel[n] & 1)
    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    message = ""
    for c in chars:
        if int(c, 2) == 0:
            break
        message += chr(int(c, 2))
    return message

def encode_DWT(image, message):
    image = image.convert('L')
    img_array = np.array(image).astype(np.float32)
    coeffs = pywt.dwt2(img_array, 'haar')
    LL, (LH, HL, HH) = coeffs
    binary_message = ''.join(format(ord(char), '08b') for char in message + chr(0))
    flat_HH = HH.flatten()
    for i in range(len(binary_message)):
        if binary_message[i] == '1':
            flat_HH[i] += 1
        else:
            flat_HH[i] -= 1
    HH_modified = flat_HH.reshape(HH.shape)
    watermarked = pywt.idwt2((LL, (LH, HL, HH_modified)), 'haar')
    watermarked = np.clip(watermarked, 0, 255).astype(np.uint8)
    return Image.fromarray(watermarked)

def decode_DWT(image):
    image = image.convert('L')
    img_array = np.array(image).astype(np.float32)
    LL, (LH, HL, HH) = pywt.dwt2(img_array, 'haar')
    flat_HH = HH.flatten()
    binary_data = ""
    for value in flat_HH:
        binary_data += '1' if value % 2 != 0 else '0'
    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    message = ""
    for c in chars:
        if int(c, 2) == 0:
            break
        message += chr(int(c, 2))
    return message

def evaluate_image_quality(original, encoded):
    original = np.array(original.resize(encoded.size).convert('RGB'))
    encoded = np.array(encoded.convert('RGB'))
    mse = mean_squared_error(original, encoded)
    rmse = np.sqrt(mse)
    psnr = peak_signal_noise_ratio(original, encoded, data_range=255)
    return mse, rmse, psnr

# ===== Streamlit App Layout =====
st.title("🕵️‍♂️ Steganografi Gambar (LSB & DWT)")
tab1, tab2 = st.tabs(["Encode (Sisipkan Pesan)", "Decode (Ambil Pesan)"])

with tab1:
    st.header("Sisipkan Pesan")
    uploaded_img = st.file_uploader("Upload gambar", type=['png', 'jpg', 'jpeg'])

    method = st.selectbox("Pilih metode encoding:", ["LSB", "DWT"])
    secret_msg = st.text_area("Masukkan pesan rahasia:")

    if uploaded_img and secret_msg:
        image = Image.open(uploaded_img)
        perform_eda(image)

        if method == "LSB":
            encoded_img = encode_LSB(image.convert("RGB"), secret_msg)
        else:
            encoded_img = encode_DWT(image, secret_msg)

        st.image(encoded_img, caption="Gambar dengan pesan tersembunyi", use_container_width=True)
        mse, rmse, psnr = evaluate_image_quality(image, encoded_img)
        st.success(f"MSE: {mse:.4f}, RMSE: {rmse:.4f}, PSNR: {psnr:.2f} dB")

        buf = io.BytesIO()
        encoded_img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button("💾 Download Gambar", byte_im, file_name="encoded_image.png")

with tab2:
    st.header("Ambil Pesan")
    uploaded_encoded = st.file_uploader("Upload gambar hasil steganografi", type=['png', 'jpg', 'jpeg'], key="decode")

    decode_method = st.selectbox("Metode decoding:", ["LSB", "DWT"])

    if uploaded_encoded:
        encoded_image = Image.open(uploaded_encoded)
        if decode_method == "LSB":
            result = decode_LSB(encoded_image)
        else:
            result = decode_DWT(encoded_image)
        st.success("Pesan Tersembunyi:")
        st.code(result)
