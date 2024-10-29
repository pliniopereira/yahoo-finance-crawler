# Yahoo Finance Crawler

## Descrição
Crawler desenvolvido em Python para extrair nomes, símbolos e preços de ações do Yahoo Finance com base na região especificada.

## Como usar
### Instalação
```bash
poetry install
```

### Executar o Crawler
```bash
poetry run python main.py --region "Argentina"
```

### Usar o Makefile
Instalar dependências:
```bash
make install
```

Executar o crawler:
```bash
make run region=Argentina
```

### Executar via Docker
```bash
docker build -t yahoo-finance-crawler .
docker run -it yahoo-finance-crawler
```

### Testes
```bash
make test
```

## Estrutura do Projeto
- `crawler.py`: Implementação principal do crawler.
- `main.py`: Script para executar o crawler.
- `data_model.py`: Modelo de dados para armazenar as informações coletadas.
- `utils.py`: Funções utilitárias.
- `tests/`: Testes unitários.
