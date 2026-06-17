echo "Inicializando o Aplicativo"

cd /d "%~dp0"

pip install -r requirements.txt

streamlit run scripts/cardioia_prototype.py

pause