import os
import torch
import torch.nn as nn
import streamlit as st
from PIL import Image
from torchvision import transforms
# Importar os modelos e classes do script de treinamento existente
from cardioia_treinamento_cnn import CNNFromScratch, get_transfer_learning_model

# Configurações de estilo e visual da página do Streamlit
st.set_page_config(
    page_title="CardioIA - Protótipo de Apresentação",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para dar um ar premium e moderno
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        color: white;
    }
    .reportview-container {
        background: #f0f2f6
    }
    h1 {
        color: #1e293b;
        font-family: 'Inter', sans-serif;
    }
    .card-normal {
        padding: 1.5rem;
        background-color: #d1e7dd;
        border-left: 6px solid #0f5132;
        border-radius: 8px;
        color: #0f5132;
    }
    .card-abnormal {
        padding: 1.5rem;
        background-color: #f8d7da;
        border-left: 6px solid #842029;
        border-radius: 8px;
        color: #842029;
    }
    </style>
""", unsafe_allow_html=True)

# Definir o dispositivo padrão (CPU é mais estável e rápido para inferência de teste)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Caminhos das pastas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR_N = os.path.abspath(os.path.join(BASE_DIR, "..", "assets", "dataset_final", "test", "N"))
TEST_DIR_M = os.path.abspath(os.path.join(BASE_DIR, "..", "assets", "dataset_final", "test", "M"))
CONFIG_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "config"))

# Carregar imagens de teste disponíveis
@st.cache_data
def load_test_images():
    images = []
    
    # Adicionar imagens normais (N)
    if os.path.exists(TEST_DIR_N):
        for file in sorted(os.listdir(TEST_DIR_N)):
            if file.endswith((".png", ".jpg", ".jpeg")):
                images.append({
                    "name": file,
                    "class": "Normal",
                    "path": os.path.join(TEST_DIR_N, file)
                })
                
    # Adicionar imagens anormais (M)
    if os.path.exists(TEST_DIR_M):
        for file in sorted(os.listdir(TEST_DIR_M)):
            if file.endswith((".png", ".jpg", ".jpeg")):
                images.append({
                    "name": file,
                    "class": "Anomalia (Classe M)",
                    "path": os.path.join(TEST_DIR_M, file)
                })
                
    return images

# Carregar e armazenar modelos em cache para evitar recarregamento pesado
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
    else: # ResNet50
        model = get_transfer_learning_model()
        weights_path = os.path.join(CONFIG_DIR, "resnet_transfer_weights.pth")
        if os.path.exists(weights_path):
            model.load_state_dict(torch.load(weights_path, map_location=device))
        model.to(device)
        model.eval()
        return model

# Cabeçalho da página
st.markdown("<h1 style='text-align: center;'>🏥 CardioIA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:1.1rem; color:#64748b;'>Protótipo de Apresentação e Diagnóstico de ECG assistido por IA</p>", unsafe_allow_html=True)
st.divider()

# Barra lateral para configurações
st.sidebar.header("⚙️ Configurações")
selected_model_type = st.sidebar.radio(
    "Modelo de Rede Neural:",
    ("CNN do Zero", "ResNet50 (Transfer Learning)")
)

st.sidebar.markdown("""
---
### Sobre o Protótipo:
Este painel simula um ecossistema médico onde exames de ECG são submetidos a redes neurais convolucionais.
*   **CNN do Zero:** Modelo otimizado, leve e rápido (`~25MB`).
*   **ResNet50 TL:** Modelo baseado em Transfer Learning de alta precisão (`~94MB`).
""")

# Carregar imagens de teste
test_images = load_test_images()

if not test_images:
    st.warning("Nenhuma imagem de teste encontrada. Verifique se o diretório `assets/dataset_final/test/` existe e contém imagens.")
else:
    # Seletor de imagens
    image_options = [f"{img['name']} - [{img['class']}]" for img in test_images]
    selected_option = st.selectbox(
        "Selecione um exame de ECG da base de testes para analisar:",
        options=image_options
    )
    
    # Obter os dados da imagem selecionada
    selected_index = image_options.index(selected_option)
    selected_image_data = test_images[selected_index]
    
    # Exibir a imagem na tela
    st.write("---")
    st.subheader("🖼️ Exame Selecionado")
    
    image = Image.open(selected_image_data["path"])
    st.image(image, caption=f"Arquivo: {selected_image_data['name']} (Classe Real: {selected_image_data['class']})", use_container_width=True)
    
    # Transformação de imagem para o PyTorch
    image_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    st.write("---")
    # Botão de análise
    if st.button("🔍 Analisar Exame"):
        with st.spinner("Analisando o padrão eletrocardiográfico..."):
            try:
                # Carregar o modelo selecionado
                model = load_model(selected_model_type)
                
                # Preprocessar a imagem
                img_rgb = image.convert("RGB")
                img_tensor = image_transforms(img_rgb).unsqueeze(0).to(device)
                
                # Fazer a predição
                with torch.no_grad():
                    outputs = model(img_tensor)
                    probabilities = torch.softmax(outputs, dim=1)
                    confidence, prediction = torch.max(probabilities, 1)
                    
                    confidence_percent = confidence.item() * 100
                    prediction_class = prediction.item() # 0 = M (Anormal), 1 = N (Normal)
                
                # Apresentação do Resultado
                st.subheader("📋 Laudo de Análise")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if prediction_class == 1: # Normal
                        st.markdown("""
                            <div class='card-normal'>
                                <h3>Padrão Identificado: Normal</h3>
                                <p>O traçado eletrocardiográfico apresenta características dentro da faixa de normalidade.</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else: # Anomalia
                        st.markdown("""
                            <div class='card-abnormal'>
                                <h3>Padrão Identificado: Anomalia Detectada</h3>
                                <p><b>Atenção:</b> Traçado eletrocardiográfico anormal detectado. Indica possíveis batimentos irregulares ou arritmias.</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                with col2:
                    st.metric(
                        label="Certeza da IA",
                        value=f"{confidence_percent:.2f}%"
                    )
                    st.caption(f"Processado via: **{selected_model_type}**")
                    
            except Exception as e:
                st.error(f"Erro ao processar o exame: {str(e)}")
