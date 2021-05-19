# Preparações para o uso da aplicação

## Versão do Python
Foi utilizado o Python3.9, logo aconselha-se a utilização da mesma.

## Instalando e executando o ambiente virtual
'''python3.9 -m pip install virtualenv'''
'''python3.9 -m venv tp2'''
'''source tp2/bin/activate'''

## Instalação das bibliotecas
Com ambiente virtual ativo, execute:
'''python3.9 -m pip install -r requirements.txt'''

# Start da aplicação
Com ambiente virtual ativo, execute:
'''python3.9 run.py'''

- Se obter um erro na importação do app, execute:
'''FLASK_APP=run.py'''

Após ter iniciado a aplicação, vá até http://localhost:5000/ no seu navegador.