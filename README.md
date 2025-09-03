# AluMusic

Sistema que recebe, classifica, analise comentários utilizando LLM e gera um dashboard com insights sobre eles construído principalmente com Python, Flask e conteinerizado via Docker

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## Primeiros passos

### Pre-requisitos

* Python ≥ 3.10 & Docker

### Instalação

1. Clone esse repositório:
    ```sh
    git clone https://github.com/gguidiniz/alumusic.git
    ```

2. Crie um arquivo .env a partir do .env.example, adicionando uma SECRET_KEY para o JWT e a sua chave da Gemini que pode ser obtida aqui `https://aistudio.google.com/apikey`.

3. Construa e execute os containers em modo detached:
    ```sh
    docker compose up --build -d
    ```

4. Crie as tabelas no banco de dados:
    ```sh
    docker compose exec app flask db upgrade
    ```
5. Crie um usuário para acessar o dashboard privado:
    ```sh
    docker compose exec app flask create-user seu-email@exemplo.com sua-senha-forte
    ```

6. A aplicação estará disponível em:
    * Relatório semanal: `http://localhost/relatorio/semanal`
    * Dashboard privado: `http://localhost/dashboard`

### Testes e evals
Antes de executar os testes e evals, entre crie um venv:
```sh
python -m venv venv
```
Ative o ambiente virtual:
```sh
.\venv\Scripts\activate
```
E instale as dependências do projeto:
```sh
pip install -r requirements.txt
```
#### Testes unitários e de integração
Eles são escritos com **pytest**, para executá-los, basta rodar com o seu venv ativo:
```sh
pytest
```

#### Eval
Para avaliar a acurácia do modelo de classificação de comentários, o script utiliza um golden dataset de exemplo, com o venv ativo, rode:
```sh
python -m scripts.run_evals
```


### Testando a API via Postman

1. Importe o arquivo `postman_collection` presente na raiz do projeto no seu Postman.
2. Para a rota de **login**, edite o `email` e `senha` com as suas credenciais e faça a requisição.
3. Copie o valor do `access_token` retornado no body do login.
4. Para enviar um **comentário**, faça o POST para a rota de comentários:
   - Substitua o token em `Authorization`.
   - Edite o body com um `uuid` e o `text` do comentário que deseja enviar.

## Decisões de design

### 1. Modelo de LLM

- Utilizei a **1.5 flash do Gemini** para classificação de comentários.
- **Justificativa**:
  - Tokens gratuitos disponíveis, facilitando testes sem custos iniciais.
  - Modelo adequado para tarefas de classificação de texto curto, como comentários musicais.
  - Familiaridade prévia com a API, permitindo integração rápida.

### 2. Configurações Centralizadas e Variáveis de Ambiente

- Todas as configurações da aplicação estão centralizadas na classe **`Settings`** em `config.py`.
  - Parâmetros críticos, como conexão com banco de dados (`DATABASE_URL`), chaves de JWT (`JWT_SECRET_KEY`), API keys (`GEMINI_API_KEY`) e URLs do Celery (`CELERY_BROKER_URL` e `CELERY_RESULT_BACKEND`), são carregados do arquivo **`.env`**.
  - Configurações de cache (`CACHE_TYPE`, `CACHE_DIR`, `CACHE_DEFAULT_TIMEOUT`) e flags de desenvolvimento (`MOCK_AI_SERVICE`) também estão centralizadas.
- O Flask carrega essa configuração ao criar a aplicação via `app.config.from_object(Settings)`.

- **Justificativa**:
  - Centralizar configurações facilita a manutenção e evita espalhar valores sensíveis pelo código.
  - O uso de `.env` permite separar **segredos** e **parâmetros de ambiente** do código-fonte, aumentando a segurança e a portabilidade.
  - Facilita testes e deploys em diferentes ambientes (dev, staging, produção) sem alterar o código.

### 3. Persistência

- Banco de dados: **PostgreSQL**.
- ORM: **SQLAlchemy**.
- **Justificativa**:
  - PostgreSQL oferece robustez, suporte a tipos avançados e performance adequada para análises agregadas.
  - SQLAlchemy simplifica a manipulação de modelos e abstrai queries complexas, mantendo o código limpo.
- Estrutura:
  - Tabelas principais: `Comment`, `Classification`, `Tag`, `User`, `WeeklySummary`.
  - Relacionamentos muitos-para-muitos entre classificações e tags via tabela associativa `classification_tags`.
  - Indexação em `created_at` para consultas rápidas em relatórios temporais.

### 4. Validação de Dados

- Utilizei **Pydantic** para validação e serialização de dados recebidos nos endpoints da API:
  - `CommentSchema` garante que cada comentário tenha um `uuid` válido e texto não vazio.
  - `ClassificationResultSchema` valida os resultados de classificação, incluindo categoria, confiança e tags associadas.
  - `AuthLoginSchema` valida login de usuários, garantindo formato de e-mail correto e presença de senha.
  - Erros de validação são tratados e retornam respostas `422 Unprocessable Entity` com detalhes claros para o cliente.
- **Justificativa**:
  - Garante integridade dos dados antes de enviá-los para processamento assíncrono ou persistência no banco.
  - Evita falhas silenciosas na aplicação causadas por dados malformados.
  - Facilita manutenção e evolução da API, com tipos fortemente tipados e mensagens de erro padronizadas.

### 5. Processamento de Lotes

- Utilizei **Celery e Redis** para processamento assíncrono e tarefas agendadas:
  - Para lidar com classificação de comentários em lote e geração de resumos semanais, é utilizado **Celery** como fila de tarefas assíncronas.
  - **Redis** é usado como broker e backend de resultados do Celery.
  - A arquitetura permite que o processamento de comentários não bloqueie a aplicação web.
  - A tarefa `process_and_save_comment` consome comentários e salva suas classificações na base de dados, garantindo consistência com commit/rollback.
  - A tarefa `generate_weekly_summary` roda semanalmente via `Celery Beat`, agregando comentários da última semana e gerando resumos com a LLM do Gemini.
  - O worker e o beat são executados em containers separados, garantindo isolamento e escalabilidade horizontal.
- **Justificativa**:
  - Permite processar grandes volumes de comentários sem bloquear a aplicação.
  - Redis atua como broker e backend, garantindo filas e persistência de tarefas assíncronas.

- Requisições para o endpoint `POST /api/comments` são validadas e imediatamente enfileiradas como tarefas em background, retornando ao cliente um status `202 Accepted`.  
  Isso garante:
  - Resposta rápida ao cliente.
  - Capacidade de lidar com altos volumes de comentários.
  - Isolamento do processamento para não bloquear a aplicação web.
- Trade-off:
    O padrão adotado é **"Fire and Forget"**, onde o cliente não recebe uma notificação ativa sobre a conclusão da tarefa.  
  Em produção, seria interessante:
  - Implementar endpoint de status para polling usando o ID da tarefa do Celery.
  - Ou usar **WebSockets** para notificações em tempo real.  
  A abordagem atual atende ao requisito principal de processamento robusto de lotes e é adequada para o escopo da avaliação.

### 6. Cache de Relatórios

- Utilizei **Flask-Caching** com `FileSystemCache` para armazenar resultados do relatório semanal.
  - O endpoint `/relatorio/semanal` é cacheado por 30 segundos via `@cache.cached(timeout=30)`.
  - Reduz chamadas repetidas ao banco de dados e processamento de dados para geração de gráficos.
  - Mantém a atualização quase em tempo real sem sobrecarregar a aplicação.
- **Justificativa**:
  - Melhora a performance de endpoints que envolvem agregações e múltiplas queries.
  - Evita sobrecarga desnecessária no banco de dados ao acessar relatórios frequentemente.
  - Mantém uma boa experiência de usuário com dados quase instantâneos, sem impactar a consistência, já que o cache expira em poucos segundos.

### 7. Autenticação e Autorização

  - Implementada via **JWT** com Flask-JWT-Extended.
  - Endpoints da API (`/api/comments`) protegidos com `@jwt_required()`.
  - Login via `/api/auth/login` retorna token JWT armazenado em cookie, permitindo acesso ao dashboard privado.
  - Usuários e senhas são gerenciados na tabela `User`, com hashing seguro via Werkzeug (`generate_password_hash`).
  - Para rotas web não-API, requisições sem token redirecionam para a página de login.
- **Justificativa**:
  - O uso de JWT simplifica a autenticação em APIs RESTful e permite escalabilidade sem sessões no servidor.
  - Cookies com o token garantem persistência do login no navegador e integração com a interface web.

### 8. Comando CLI para gerenciamento de usuários

- Foi implementado um comando CLI para criar usuários do sistema (`flask create-user <email> <senha>`).
- **Justificativa**:
  - O dashboard é uma ferramenta interna e privada; criar usuários via CLI garante que apenas administradores autorizados possam adicionar contas.
  - Evita expor endpoints sensíveis na API para criação de usuários.
  - Permite integração com scripts de administração ou automação sem depender da interface web.

### 9. Relatórios e Dashboard

- Relatórios gerados em **HTML** com **Chart.js**.
- Gráficos:
  1. Categorias de comentários
  2. Top 10 tags mais mencionadas
  3. Evolução de comentários nos últimos 7 dias
  4. Confiança média por categoria
  5. Top tags por categoria
- **Justificativa**:
  - HTML + Chart.js permite visualização rápida e interativa.
  - Atualização em tempo real a cada 60 segundos para insights imediatos.
  - Gráficos empilhados e linhas para facilitar a leitura de tendências.

### 10. Evals e Métricas

- Métricas coletadas:
  - **Precision, Recall, F1-score** por categoria
  - **Accuracy geral**
- Relatório gerado automaticamente via script `scripts/run_evals`.
- **Justificativa**:
  - Métricas padrão de classificação permitem avaliar desempenho do modelo.
  - Útil para monitorar acurácia em diferentes categorias e identificar falhas específicas (ex.: SUGESTÃO sem previsão correta).

### 11. Arquitetura Modular e Blueprints

- Utilizei **Blueprints do Flask** para organizar a aplicação em módulos distintos:
  - `main_bp`: rotas web, dashboard e relatórios.
  - `api_bp`: endpoints da API, como criação de comentários.
  - `auth_bp`: endpoints de autenticação e login.
- Cada módulo encapsula suas próprias rotas, validações, templates e lógica específica, mantendo o código coeso e legível.
- O `create_app` inicializa a aplicação, registra os blueprints e configura extensões (DB, JWT, Cache, Celery).
- **Justificativa**:
  - Facilita manutenção e escalabilidade, permitindo adicionar novos módulos sem alterar o núcleo da aplicação.
  - Separação clara entre API e interface web, além de autenticação, melhora a organização e segurança.
  - Reuso de componentes e facilitação de testes unitários, pois cada módulo pode ser testado isoladamente.