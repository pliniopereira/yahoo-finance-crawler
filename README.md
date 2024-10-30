## Yahoo Finance Web Scraper

Este script Python usa `Selenium` e `BeautifulSoup` para extrair dados financeiros do Yahoo Finance com base em um filtro regional, salvando os dados de nome, símbolo e preço em um arquivo CSV.

### Requisitos

- **Python 3.7+**
- **Google Chrome** instalado e atualizado
- **ChromeDriver** (gerenciado automaticamente pelo `webdriver-manager`)

### Instalação e Configuração

1. **Clone o Repositório**

   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <NOME_DO_REPOSITORIO>
   ```

2. **Crie e Ative um Ambiente Virtual**

   No diretório do projeto, execute:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Para Linux/MacOS
   .\venv\Scripts\activate   # Para Windows
   ```

3. **Instale as Dependências**

   Com o ambiente virtual ativado, instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

   Certifique-se de que o `requirements.txt` contém as seguintes dependências:

   ```text
   beautifulsoup4
   selenium
   webdriver-manager
   ```

### Uso

Para executar o script, utilize o comando abaixo. O caminho do ChromeDriver foi predefinido no código, portanto, não é necessário especificá-lo.

```bash
python main.py <região>
```

- `<região>`: Nome da região que deseja filtrar (exemplo: "Brazil").

**Exemplo**:

```bash
python main.py Brazil
```

Se necessário, você também pode adicionar caminhos alternativos para a execução, comentados diretamente no código:

```python
# driver_path = "/usr/local/bin/chromedriver"  # Caminho alternativo
# python main.py Argentina /caminho/para/chromedriver
```

### Observações

- Certifique-se de que o Google Chrome está atualizado para a versão mais recente compatível com `webdriver-manager`.
- Este script roda em modo headless para facilitar a execução em pipelines de CI/CD.

### Licença

Este projeto é distribuído sob a licença MIT.
