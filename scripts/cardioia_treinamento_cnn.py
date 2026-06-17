import os
import random
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, ConfusionMatrixDisplay

# Configurar sementes para reprodutibilidade
def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

set_seed(42)

# Definir dispositivo (GPU se disponível, senão CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Dispositivo selecionado para treinamento: {device}")

# Caminhos do dataset final
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "dataset_final"))
TRAIN_DIR = os.path.join(BASE_DIR, "train")
VAL_DIR = os.path.join(BASE_DIR, "validation")
TEST_DIR = os.path.join(BASE_DIR, "test")

# Transformações de imagem (Redimensionar para 224x224, normalização ImageNet)
image_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print("Carregando datasets...")
train_dataset = datasets.ImageFolder(root=TRAIN_DIR, transform=image_transforms)
val_dataset = datasets.ImageFolder(root=VAL_DIR, transform=image_transforms)
test_dataset = datasets.ImageFolder(root=TEST_DIR, transform=image_transforms)

# DataLoaders
batch_size = 32
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

print(f"Classes encontradas: {train_dataset.classes}")
print(f"Total de imagens - Treino: {len(train_dataset)}, Validação: {len(val_dataset)}, Teste: {len(test_dataset)}")


# ----------------------------------------------------
# TAREFA 1: Arquitetura da CNN do Zero
# ----------------------------------------------------
class CNNFromScratch(nn.Module):
    def __init__(self):
        super(CNNFromScratch, self).__init__()
        # Entrada: 3 x 224 x 224
        self.features = nn.Sequential(
            # Bloco Convolucional 1
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2), # Output: 16 x 112 x 112
            
            # Bloco Convolucional 2
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2), # Output: 32 x 56 x 56
            
            # Bloco Convolucional 3
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)  # Output: 64 x 28 x 28
        )
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 28 * 28, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 2) # 2 classes: M (Abnormal) e N (Normal)
        )
        
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


# ----------------------------------------------------
# TAREFA 2: Transfer Learning com Modelo Pré-treinado
# ----------------------------------------------------
def get_transfer_learning_model():
    try:
        from torchvision.models import resnet50, ResNet50_Weights
        resnet = resnet50(weights=ResNet50_Weights.DEFAULT)
        print("ResNet50 importada usando a API moderna de pesos.")
    except ImportError:
        # Compatibilidade com versões mais antigas do torchvision
        from torchvision import models
        resnet = models.resnet50(pretrained=True)
        print("ResNet50 importada usando a API antiga de pesos (pretrained=True).")
        
    # Congelar as camadas iniciais do modelo
    for param in resnet.parameters():
        param.requires_grad = False
        
    # Substituir a camada final (fc) por uma nova que aprenda nosso contexto
    num_features = resnet.fc.in_features
    resnet.fc = nn.Linear(num_features, 2) # 2 classes de saída
    
    return resnet


# ----------------------------------------------------
# Função de Treinamento e Validação
# ----------------------------------------------------
def train_model(model, criterion, optimizer, num_epochs=10):
    best_acc = 0.0
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    
    for epoch in range(num_epochs):
        # Fase de Treino
        model.train()
        running_loss = 0.0
        running_corrects = 0
        total_train = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            _, preds = torch.max(outputs, 1)
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            total_train += inputs.size(0)
            
        epoch_train_loss = running_loss / total_train
        epoch_train_acc = running_corrects.double() / total_train
        
        # Fase de Validação
        model.eval()
        running_val_loss = 0.0
        running_val_corrects = 0
        total_val = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                _, preds = torch.max(outputs, 1)
                
                running_val_loss += loss.item() * inputs.size(0)
                running_val_corrects += torch.sum(preds == labels.data)
                total_val += inputs.size(0)
                
        epoch_val_loss = running_val_loss / total_val
        epoch_val_acc = running_val_corrects.double() / total_val
        
        history['train_loss'].append(epoch_train_loss)
        history['train_acc'].append(epoch_train_acc.item())
        history['val_loss'].append(epoch_val_loss)
        history['val_acc'].append(epoch_val_acc.item())
        
        print(f"Época {epoch+1:02d}/{num_epochs:02d} | "
              f"Treino Loss: {epoch_train_loss:.4f} Acc: {epoch_train_acc:.4f} | "
              f"Val Loss: {epoch_val_loss:.4f} Acc: {epoch_val_acc:.4f}")
              
    return model, history


# ----------------------------------------------------
# Função de Avaliação no Conjunto de Teste
# ----------------------------------------------------
def evaluate_model(model, model_name):
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())
            
    # Calcular métricas
    acc = accuracy_score(all_labels, all_preds)
    prec = precision_score(all_labels, all_preds, average='macro')
    rec = recall_score(all_labels, all_preds, average='macro')
    f1 = f1_score(all_labels, all_preds, average='macro')
    
    print(f"\n==========================================")
    print(f"Métricas de Avaliação do Teste: {model_name}")
    print(f"==========================================")
    print(f"Acurácia:     {acc:.4f}")
    print(f"Precisão:     {prec:.4f}")
    print(f"Recall (Sensibilidade): {rec:.4f}")
    print(f"F1-Score:     {f1:.4f}")
    
    # Gerar e Plotar Matriz de Confusão
    cm = confusion_matrix(all_labels, all_preds)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=test_dataset.classes)
    
    fig, ax = plt.subplots(figsize=(6, 6))
    disp.plot(cmap=plt.cm.Blues, ax=ax, values_format='d')
    plt.title(f"Matriz de Confusão - {model_name}")
    
    # Salvar matriz de confusão em assets
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
    filename = f"matriz_confusao_{model_name.lower().replace(' ', '_')}.png"
    filepath = os.path.join(assets_dir, filename)
    plt.savefig(filepath, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"Matriz de confusão salva em: {filepath}")
    
    return {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1_score': f1}


# ----------------------------------------------------
# EXECUÇÃO DO PROCESSO
# ----------------------------------------------------
if __name__ == "__main__":
    epochs = 10
    
    # 1. Treinamento da CNN do Zero
    print("\n----------------------------------------------------")
    print("Iniciando Treinamento: CNN do Zero")
    print("----------------------------------------------------")
    model_scratch = CNNFromScratch().to(device)
    criterion_scratch = nn.CrossEntropyLoss()
    optimizer_scratch = optim.Adam(model_scratch.parameters(), lr=0.001)
    
    model_scratch, history_scratch = train_model(
        model_scratch, criterion_scratch, optimizer_scratch, num_epochs=epochs
    )
    
    metrics_scratch = evaluate_model(model_scratch, "CNN do Zero")
    
    # Salvar pesos do modelo do zero
    torch.save(model_scratch.state_dict(), os.path.join(BASE_DIR, "..", "..", "config", "cnn_scratch_weights.pth"))
    print("Pesos do modelo CNN do Zero salvos.")
    
    # 2. Treinamento da ResNet50 (Transfer Learning)
    print("\n----------------------------------------------------")
    print("Iniciando Treinamento: ResNet50 (Transfer Learning)")
    print("----------------------------------------------------")
    model_resnet = get_transfer_learning_model().to(device)
    criterion_resnet = nn.CrossEntropyLoss()
    # Apenas otimizar os parâmetros que não estão congelados (a camada fc final)
    optimizer_resnet = optim.Adam(filter(lambda p: p.requires_grad, model_resnet.parameters()), lr=0.001)
    
    model_resnet, history_resnet = train_model(
        model_resnet, criterion_resnet, optimizer_resnet, num_epochs=epochs
    )
    
    metrics_resnet = evaluate_model(model_resnet, "ResNet50 Transfer Learning")
    
    # Salvar pesos do modelo pré-treinado
    torch.save(model_resnet.state_dict(), os.path.join(BASE_DIR, "..", "..", "config", "resnet_transfer_weights.pth"))
    print("Pesos do modelo ResNet50 Transfer Learning salvos.")
    
    # 3. Comparação Final
    print("\n==========================================")
    print("RESUMO E COMPARAÇÃO DOS MODELOS NO TESTE")
    print("==========================================")
    print(f"{'Métrica':<25} | {'CNN do Zero':<15} | {'ResNet50 TL':<15}")
    print("-" * 63)
    print(f"{'Acurácia':<25} | {metrics_scratch['accuracy']:<15.4f} | {metrics_resnet['accuracy']:<15.4f}")
    print(f"{'Precisão':<25} | {metrics_scratch['precision']:<15.4f} | {metrics_resnet['precision']:<15.4f}")
    print(f"{'Recall (Sensibilidade)':<25} | {metrics_scratch['recall']:<15.4f} | {metrics_resnet['recall']:<15.4f}")
    print(f"{'F1-Score':<25} | {metrics_scratch['f1_score']:<15.4f} | {metrics_resnet['f1_score']:<15.4f}")
    print("==========================================")
    
    # Plotar o histórico de treinamento
    plt.figure(figsize=(12, 5))
    
    # Perda
    plt.subplot(1, 2, 1)
    plt.plot(history_scratch['train_loss'], label='Scratch Treino')
    plt.plot(history_scratch['val_loss'], label='Scratch Val')
    plt.plot(history_resnet['train_loss'], label='ResNet Treino')
    plt.plot(history_resnet['val_loss'], label='ResNet Val')
    plt.title('Histórico de Perda (Loss)')
    plt.xlabel('Época')
    plt.ylabel('Loss')
    plt.legend()
    
    # Acurácia
    plt.subplot(1, 2, 2)
    plt.plot(history_scratch['train_acc'], label='Scratch Treino')
    plt.plot(history_scratch['val_acc'], label='Scratch Val')
    plt.plot(history_resnet['train_acc'], label='ResNet Treino')
    plt.plot(history_resnet['val_acc'], label='ResNet Val')
    plt.title('Histórico de Acurácia')
    plt.xlabel('Época')
    plt.ylabel('Acurácia')
    plt.legend()
    
    plt.tight_layout()
    history_filepath = os.path.abspath(os.path.join(BASE_DIR, "..", "historico_treinamento.png"))
    plt.savefig(history_filepath, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"Histórico de treinamento salvo em: {history_filepath}")
