# API-TRANSPORTE-RODOVIARIO

## Instalação e execução

### Pré-requisitos

Para executar o projeto, é necessário ter instalado:

- Python 3.11 ou superior
- Git

### 1. Clonar o repositório

```bash
git clone https://github.com/sabrynardev/API-TRANSPORTE-RODOVIARIO.git
```

Entre na pasta do projeto:

```bash
cd API-TRANSPORTE-RODOVIARIO
```

### 2. Criar o ambiente virtual

No Windows:

```bash
python -m venv .venv
```

### 3. Ativar o ambiente virtual

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a execução do script, utilize:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

e tente ativar novamente:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 5. Executar a API

```bash
python -m uvicorn app.main:app --reload
```

A aplicação ficará disponível localmente em:

`http://127.0.0.1:8000`

A documentação interativa do Swagger estará disponível em:

`http://127.0.0.1:8000/docs`

### 6. Executar os testes automatizados

Com o ambiente virtual ativado:

```bash
python -m pytest -v
```

O projeto possui testes automatizados para as integrações, regras de normalização, tratamento de erros e processamento de múltiplas empresas.
