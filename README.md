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

## Como adicionar uma nova empresa

A arquitetura foi criada para permitir a inclusão de novas empresas sem alterar o endpoint ou o fluxo principal de normalização.

Para adicionar uma nova integração, siga os passos abaixo.

### 1. Criar um novo normalizador

Crie um arquivo dentro de:

```text
app/normalizacao/empresas/
```

Exemplo:

```text
nova_empresa.py
```

A nova classe deve implementar `NormalizadorViagem`.

Exemplo:

```python
from app.normalizacao.interface import NormalizadorViagem
from app.domain.models import ViagemNormalizada


class NormalizadorNovaEmpresa(NormalizadorViagem):

    def reconhece(self, payload: dict) -> bool:
        return "campo_identificador" in payload

    def normalizar(
        self,
        payload: dict,
    ) -> ViagemNormalizada:
        # aplicar as regras específicas
        # da nova empresa

        ...
```

O método `reconhece()` deve identificar o formato da empresa através da estrutura do payload.

Não deve ser adicionado um novo `if/elif` no endpoint ou no Pipeline para escolher a empresa.

### 2. Implementar as regras específicas

Dentro do método `normalizar()`, devem ser tratados os formatos particulares da nova empresa, como:

- datas e fusos horários;
- duração;
- preço e moeda;
- categoria;
- assentos disponíveis;
- origem e destino;
- campos obrigatórios.

O resultado deve sempre seguir o mesmo contrato representado por `ViagemNormalizada`.

### 3. Registrar o normalizador

Abra:

```text
app/normalizacao/configuracao.py
```

Importe a nova implementação:

```python
from app.normalizacao.empresas.nova_empresa import (
    NormalizadorNovaEmpresa,
)
```

Depois registre a estratégia:

```python
registry.registrar(
    NormalizadorNovaEmpresa()
)
```

Essa é a única alteração necessária no mecanismo de configuração das empresas.

O endpoint, o Pipeline, o Registry e os normalizadores existentes não precisam ser modificados.

### 4. Criar testes automatizados

Crie testes específicos para a nova empresa dentro da pasta:

```text
tests/
```

Os testes devem verificar pelo menos:

- reconhecimento do payload;
- normalização para o contrato padrão;
- tratamento dos principais erros;
- compatibilidade com o processamento de múltiplas empresas.

### Exemplo aplicado: Sertão Bus

A empresa fictícia Sertão Bus foi adicionada seguindo esse processo.

Foi criada uma nova implementação:

```text
app/normalizacao/empresas/sertao_bus.py
```

Ela implementa a mesma abstração utilizada pelas demais empresas e foi registrada em `configuracao.py`.

Para sua inclusão, não foi necessário alterar:

```text
app/api/viagens.py
app/normalizacao/pipeline.py
app/normalizacao/registry.py
```

Esse comportamento demonstra a aplicação do Open/Closed Principle: o sistema pode ser estendido com novas estratégias sem modificar o fluxo principal já existente.


## Contrato da API

### Endpoint

```http
POST /api/v1/viagens/normalizar
```

O corpo da requisição deve ser um array JSON contendo uma ou mais viagens.

A API identifica automaticamente qual empresa originou cada objeto através da estrutura do payload.

Não é necessário informar campos como:

```text
empresa
companhia
tipo
integracao
```

A ordem dos objetos enviada na requisição é preservada na resposta.

---

## Exemplo de requisição

```json
[
  {
    "codigoViagem": "PRG-2026-001",
    "cidadeOrigem": "Paulo Afonso",
    "ufOrigem": "BA",
    "cidadeDestino": "Recife",
    "ufDestino": "PE",
    "dataHoraSaida": "15/10/2026 06:30",
    "dataHoraChegada": "15/10/2026 12:50",
    "fusoHorario": "America/Bahia",
    "tempoEstimado": "06:20",
    "valorPassagem": "129,90",
    "tipoServico": "EXECUTIVO",
    "assentosDisponiveis": "18"
  },
  {
    "trip_id": "ROT-2026-872",
    "origem": {
      "municipio": "Paulo Afonso",
      "estado": "BA"
    },
    "destino": {
      "municipio": "Aracaju",
      "estado": "SE"
    },
    "partida_em": "2026-10-15T07:00:00-03:00",
    "chegada_em": "2026-10-15T12:10:00-03:00",
    "duracao_minutos": 310,
    "tarifa_centavos": 8990,
    "moeda": "BRL",
    "classe": "convencional",
    "vagas": 22
  }
]
```

---

## Exemplo de resposta

```json
{
  "total": 2,
  "viagens": [
    {
      "id_viagem": "PRG-2026-001",
      "empresa": "Auto Viação Progresso",
      "origem": {
        "cidade": "Paulo Afonso",
        "uf": "BA"
      },
      "destino": {
        "cidade": "Recife",
        "uf": "PE"
      },
      "partida": "2026-10-15T06:30:00-03:00",
      "chegada": "2026-10-15T12:50:00-03:00",
      "duracao_minutos": 380,
      "preco": {
        "valor": 129.9,
        "moeda": "BRL"
      },
      "categoria": "executivo",
      "assentos_disponiveis": 18
    },
    {
      "id_viagem": "ROT-2026-872",
      "empresa": "Rota Transportes",
      "origem": {
        "cidade": "Paulo Afonso",
        "uf": "BA"
      },
      "destino": {
        "cidade": "Aracaju",
        "uf": "SE"
      },
      "partida": "2026-10-15T07:00:00-03:00",
      "chegada": "2026-10-15T12:10:00-03:00",
      "duracao_minutos": 310,
      "preco": {
        "valor": 89.9,
        "moeda": "BRL"
      },
      "categoria": "convencional",
      "assentos_disponiveis": 22
    }
  ]
}
```

## Contrato normalizado de saída

Todas as empresas são convertidas para a mesma estrutura:

```text
id_viagem
empresa
origem
    cidade
    uf
destino
    cidade
    uf
partida
chegada
duracao_minutos
preco
    valor
    moeda
categoria
assentos_disponiveis
```

As categorias possíveis após a normalização são:

```text
convencional
executivo
semileito
leito
```

As datas são retornadas no formato ISO 8601.

Quando o payload não possui informação de fuso horário, a aplicação utiliza:

```text
America/Bahia
```

---

## Tratamento de erros

Quando qualquer objeto da requisição é inválido, toda a requisição é rejeitada com status:

```http
422 Unprocessable Entity
```

A API não retorna resultados parciais.

Exemplo:

```json
{
  "detail": {
    "indice": 1,
    "empresa_identificada": "Rota Transportes",
    "campo": "chegada_em",
    "mensagem": "A data de chegada deve ser posterior à data de saída."
  }
}
```

O campo `indice` informa qual objeto do array apresentou o problema.

Caso o formato não corresponda a nenhuma empresa suportada:

```json
{
  "detail": {
    "indice": 0,
    "empresa_identificada": null,
    "campo": null,
    "mensagem": "O formato do payload não corresponde a nenhuma companhia suportada."
  }
}
```

Entre as validações realizadas estão:

- campos obrigatórios;
- formato das datas;
- chegada posterior à partida;
- duração maior que zero;
- compatibilidade entre duração e horários;
- preço maior que zero;
- quantidade de assentos não negativa;
- UF com exatamente dois caracteres;
- categoria reconhecida pelo sistema.
