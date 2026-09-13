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

## Arquitetura e decisões de projeto

A API foi estruturada para permitir a integração de diferentes empresas de transporte sem concentrar as regras de todas elas em um único fluxo de decisão.

Cada empresa possui seu próprio normalizador, responsável por reconhecer o formato recebido e converter os dados para o contrato padrão da aplicação.

### Estrutura principal

```text
app/
├── api/
│   └── viagens.py
├── domain/
│   ├── exceptions.py
│   ├── models.py
│   └── validacoes.py
└── normalizacao/
    ├── interface.py
    ├── pipeline.py
    ├── registry.py
    └── empresas/
        ├── progresso.py
        ├── rota.py
        ├── gontijo.py
        └── sertao_bus.py
```

### Programação Orientada a Objetos

Foi criada a abstração `NormalizadorViagem`, que define o comportamento esperado para todos os normalizadores:

- reconhecer se um payload pertence à empresa;
- normalizar o payload para o contrato padrão.

Cada empresa implementa essa mesma interface com suas próprias regras.

Dessa forma, objetos diferentes podem ser utilizados pelo sistema através do mesmo contrato.

### Strategy

Cada normalizador representa uma estratégia diferente de normalização.

Embora todas as empresas precisem produzir o mesmo resultado final, cada uma possui formatos próprios de datas, preços, duração, categorias, origem, destino e demais campos.

As estratégias ficam separadas em classes específicas, evitando que toda a lógica fique concentrada no endpoint.

### Registry

O `NormalizadorRegistry` mantém os normalizadores disponíveis na aplicação.

Quando um payload é recebido, o Registry percorre os normalizadores registrados e pergunta a cada um se ele reconhece aquela estrutura.

O primeiro normalizador compatível é retornado para o fluxo de processamento.

Essa abordagem evita uma sequência de condicionais específicas como:

```python
if empresa == "Progresso":
    ...
elif empresa == "Rota":
    ...
elif empresa == "Gontijo":
    ...
```

A identificação é feita através do comportamento dos próprios normalizadores.

### Pipeline

O `PipelineNormalizacao` representa o fluxo principal de normalização.

Sua responsabilidade é:

1. receber o payload;
2. solicitar ao Registry o normalizador adequado;
3. delegar a normalização para a estratégia encontrada;
4. retornar a viagem normalizada.

O Pipeline não precisa conhecer as regras específicas de nenhuma empresa.

### Open/Closed Principle — OCP

A arquitetura foi projetada com foco no princípio Aberto/Fechado do SOLID.

O sistema deve estar:

- aberto para extensão;
- fechado para modificação.

Isso significa que novas empresas podem ser adicionadas através de novos normalizadores, sem alterar as regras das empresas já existentes e sem adicionar novos blocos condicionais ao fluxo principal.

A inclusão da empresa fictícia Sertão Bus foi utilizada para demonstrar essa extensibilidade.

Foi criada uma nova estratégia de normalização para a empresa, mantendo o contrato de saída, o Registry e o Pipeline compatíveis com o novo formato.

### Separação de responsabilidades

As responsabilidades foram distribuídas entre componentes diferentes:

- `api/viagens.py`: recebe a requisição HTTP e devolve a resposta;
- `models.py`: define o contrato normalizado;
- `validacoes.py`: concentra regras de validação reutilizáveis;
- `exceptions.py`: representa erros do processo de normalização;
- `interface.py`: define o contrato dos normalizadores;
- `registry.py`: encontra a estratégia adequada;
- `pipeline.py`: coordena o processamento;
- `empresas/`: contém as regras específicas de cada integração.

Essa separação reduz o acoplamento e facilita manutenção, testes e inclusão de novas empresas.
