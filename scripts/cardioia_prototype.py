import os
import sys

# Garantir que o diretório scripts está no path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import torch
import torch.nn as nn
import streamlit as st
from PIL import Image
from torchvision import transforms
from cardioia_treinamento_cnn import CNNFromScratch, get_transfer_learning_model

st.set_page_config(
    page_title="CardioIA - Protótipo de Apresentação",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="expanded"
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR_N = os.path.abspath(os.path.join(BASE_DIR, "..", "assets", "dataset_final", "test", "N"))
TEST_DIR_M = os.path.abspath(os.path.join(BASE_DIR, "..", "assets", "dataset_final", "test", "M"))
CONFIG_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "config"))

@st.cache_data
def load_test_images():
    images = []
    if os.path.exists(TEST_DIR_N):
        for file in sorted(os.listdir(TEST_DIR_N)):
            if file.endswith((".png", ".jpg", ".jpeg")):
                images.append({
                    "name": file,
                    "class": "Normal",
                    "path": os.path.join(TEST_DIR_N, file)
                })
    if os.path.exists(TEST_DIR_M):
        for file in sorted(os.listdir(TEST_DIR_M)):
            if file.endswith((".png", ".jpg", ".jpeg")):
                images.append({
                    "name": file,
                    "class": "Anomalia (Classe M)",
                    "path": os.path.join(TEST_DIR_M, file)
                })
    return images

@st.cache_resource
def load_model(model_type):
    if model_type == "CNN do Zero":
        model = CNNFromScratch()
        weights_path = os.path.join(CONFIG_DIR, "cnn_scratch_weights.pth")
        if os.path.exists(weights_path):
            model.load_state_dict(torch.load(weights_path, map_location=device))
        model.to(device)
        model.eval()
        return model
    else:
        model = get_transfer_learning_model()
        weights_path = os.path.join(CONFIG_DIR, "resnet_transfer_weights.pth")
        if os.path.exists(weights_path):
            model.load_state_dict(torch.load(weights_path, map_location=device))
        model.to(device)
        model.eval()
        return model

st.markdown("<h1 style='text-align: center;'>🏥 CardioIA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:1.1rem;'>Protótipo de Apresentação e Diagnóstico de ECG assistido por IA</p>", unsafe_allow_html=True)
st.divider()

st.sidebar.header("⚙️ Configurações")
selected_model_type = st.sidebar.radio(
    "Modelo de Rede Neural:",
    ("CNN do Zero", "ResNet50 (Transfer Learning)")
)

st.sidebar.markdown("""
---
### Sobre o Protótipo:
Este painel simula um ecossistema médico onde exames de ECG são submetidos a redes neurais convolucionais.
* **CNN do Zero:** Modelo otimizado, leve e rápido (`~25MB`).
* **ResNet50 TL:** Modelo baseado em Transfer Learning de alta precisão (`~94MB`).
""")

test_images = load_test_images()

if not test_images:
    st.warning("Nenhuma imagem de teste encontrada. Verifique se o diretório `assets/dataset_final/test/` existe e contém imagens.")
else:
    image_options = [f"{img['name']} - [{img['class']}]" for img in test_images]
    selected_option = st.selectbox(
        "Selecione um exame de ECG da base de testes para analisar:",
        options=image_options
    )
    
    selected_index = image_options.index(selected_option)
    selected_image_data = test_images[selected_index]
    
    st.write("---")
    st.subheader("🖼️ Exame Selecionado")
    
    image = Image.open(selected_image_data["path"])
    try:
        st.image(image, caption=f"Arquivo: {selected_image_data['name']} (Classe Real: {selected_image_data['class']})", use_column_width=True)
    except TypeError:
        st.image(image, caption=f"Arquivo: {selected_image_data['name']} (Classe Real: {selected_image_data['class']})")
    
    image_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    st.write("---")
    if st.button("🔍 Analisar Exame", type="primary"):
        with st.spinner("Analisando o padrão eletrocardiográfico..."):
            try:
                model = load_model(selected_model_type)
                
                img_rgb = image.convert("RGB")
                img_tensor = image_transforms(img_rgb).unsqueeze(0).to(device)
                
                with torch.no_grad():
                    outputs = model(img_tensor)
                    probabilities = torch.softmax(outputs, dim=1)
                    confidence, prediction = torch.max(probabilities, 1)
                    
                    confidence_percent = confidence.item() * 100
                    prediction_class = prediction.item()
                
                st.subheader("📋 Laudo de Análise")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if prediction_class == 1:
                        st.success("### Padrão Identificado: Normal\n\nO traçado eletrocardiográfico apresenta características dentro da faixa de normalidade.")
                    else:
                        st.error("### Padrão Identificado: Anomalia Detectada\n\n**Atenção:** Traçado eletrocardiográfico anormal detectado. Indica possíveis batimentos irregulares ou arritmias.")
                        
                with col2:
                    st.metric(
                        label="Certeza da IA",
                        value=f"{confidence_percent:.2f}%"
                    )
                    st.caption(f"Processado via: **{selected_model_type}**")
                    
            except Exception as e:
                st.error(f"Erro ao processar o exame: {str(e)}")
