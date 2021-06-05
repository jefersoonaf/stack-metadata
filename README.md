# Preparações para o uso da aplicação

## Versão do Python
Foi utilizado o Python3.9, logo aconselha-se a utilização da mesma versão.

## Criando as configurações
Dentro da pasta app, crie um arquivo **.env**, de modo que se tenha a seguinte estrutura:
```
|--app/
    |--.env
```
E dentro desse arquivo **.env**, deve-se colocar uma **SECRET_KEY** que será usada pelo flask app da seguinte forma:
```
SECRET_KEY = 'sua chave secreta aqui'
#pode ser qualquer string, mas é desejável uma com alto fator de criptografia
```

Também deve conter a Key fornecida pela API do StackExchange da seguinte forma:
```
API_KEY = 'sua chave da API aqui'
```

Você pode conseguir uma key da api do StackExchange se registrando aqui: https://stackapps.com/apps/oauth/register
## Instalando e executando o ambiente virtual
```
python3.9 -m pip install virtualenv
```
```
python3.9 -m venv venv
```
```
source venv/bin/activate
```

## Instalação das bibliotecas
Com ambiente virtual ativo, execute:
```
python3.9 -m pip install -r requirements.txt
```

# Start da aplicação
Com ambiente virtual ativo, execute:
```
python3.9 run.py
```

- Se obter um erro na importação do app, execute:
```
FLASK_APP=run.py
```

Após ter iniciado a aplicação, vá até http://localhost:5000/ no seu navegador.