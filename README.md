# 🎫 Chamados API - FastAPI + Supabase

Sistema completo de gerenciamento de chamados (tickets) desenvolvido com FastAPI e Supabase. Uma solução moderna, segura e escalável para gestão de suporte técnico com autenticação JWT, controle de acesso baseado em roles e interface REST API completa.

## 📋 Descrição do Projeto

Este projeto implementa um sistema de chamados corporativo que permite aos usuários criar, acompanhar e gerenciar tickets de suporte. O sistema oferece diferentes níveis de acesso (USER/ADMIN) e funcionalidades completas de CRUD para chamados, categorias e usuários.

**Principais funcionalidades:**
- 🔐 **Autenticação JWT** com roles USER/ADMIN
- 🎫 **CRUD completo de Chamados** com status, prioridades e categorias  
- 🏷️ **Gestão de Categorias** para organização dos tickets
- 👥 **Gestão de Usuários** com controle de permissões
- 🛡️ **Segurança avançada** com CSRF protection e validações
- 📊 **API REST documentada** com Swagger/OpenAPI

## 🏗️ Arquitetura

<details>
<summary>Diagrama de Contexto</summary>

![context](/docs/system-design/context.jpg)
</details>

<details>
<summary>Diagrama de Container</summary>

![container](/docs/system-design/container.jpg)
</details>

<details>
<summary>Diagrama de Entidade-Relacionamento</summary>

![architecture](/docs/system-design/erd.jpg)
</details>

<details>
<summary>Diagrama Sequencial de Login</summary>

![architecture](/docs/system-design/sequence-login.png)
</details>

<details>
<summary>Diagrama Sequencial de Tickets</summary>

![architecture](/docs/system-design/sequence-tickets.png)
</details>

## Estrutura do Projeto

```
app/
├── __init__.py
├── main.py              # Aplicação principal
├── config.py            # Configurações
├── database.py          # Singleton Supabase
├── security.py          # Hash + JWT
├── models.py            # Modelos de dados
├── schemas.py           # Schemas Pydantic
├── deps.py              # Dependências
└── routers/
    ├── __init__.py
    ├── auth.py          # Autenticação
    ├── categories.py    # CRUD Categorias
    └── tickets.py       # CRUD Chamados
```

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8+
- Conta no [Supabase](https://supabase.com)
- Git

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd prajabackend
   ```

2. **Crie e ative um ambiente virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o Supabase**
   - Crie um projeto no [Supabase](https://supabase.com)
   - Acesse Settings > API para obter as chaves
   - Execute o SQL para criar as tabelas (ver seção "Banco de Dados")

5. **Configure as variáveis de ambiente**
   - Copie o arquivo `env.example` para `.env`
   - Preencha com suas credenciais do Supabase (veja seção "Variáveis de Ambiente")
   ```bash
   cp env.example .env
   ```

6. **Execute as migrations/seeds**
   - Execute o SQL fornecido no Supabase SQL Editor
   - Isso criará as tabelas, índices e dados iniciais

7. **Inicie o servidor**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

8. **Acesse a aplicação**
   - **API**: http://localhost:8000
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc

## ⚙️ Variáveis de Ambiente

O arquivo `env.example` contém todas as variáveis necessárias com documentação detalhada. As principais são:

### Obrigatórias
- **SUPABASE_URL**: URL do seu projeto Supabase
- **SUPABASE_KEY**: Chave anônima (pública) do Supabase  
- **SUPABASE_SERVICE_ROLE_KEY**: Chave de service role do Supabase
- **JWT_SECRET**: Chave secreta para JWT (mínimo 32 caracteres)

### Opcionais
- **JWT_ALG**: Algoritmo JWT (padrão: HS256)
- **JWT_EXPIRES_MIN**: Expiração do token em minutos (padrão: 60)
- **ENV**: Ambiente da aplicação (padrão: dev)


## 🗄️ Banco de Dados

### Configuração do Supabase

Execute este SQL no **SQL Editor** do Supabase para criar as tabelas, índices e dados iniciais:
<details>
<summary>Query</summary>

```sql
-- Criar enum para roles
CREATE TYPE user_role AS ENUM ('USER', 'ADMIN');

-- Criar enum para status dos tickets
CREATE TYPE ticket_status AS ENUM ('open', 'closed');

-- Tabela de usuários
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'USER' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de categorias
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de tickets
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status ticket_status DEFAULT 'open' NOT NULL,
    created_by INTEGER REFERENCES users(id) NOT NULL,
    category_id INTEGER REFERENCES categories(id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_tickets_created_by ON tickets(created_by);
CREATE INDEX idx_tickets_category_id ON tickets(category_id);
CREATE INDEX idx_tickets_status ON tickets(status);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tickets_updated_at BEFORE UPDATE ON tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Inserir algumas categorias padrão
INSERT INTO categories (name) VALUES 
    ('Suporte Técnico'),
    ('Financeiro'),
    ('Recursos Humanos'),
    ('Infraestrutura');

-- Inserir usuários de teste
INSERT INTO users (name, email, password_hash, role) VALUES 
    ('Administrador', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsUNjqq4.', 'ADMIN'),
    ('João Silva', 'joao@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsUNjqq4.', 'USER'),
    ('Maria Santos', 'maria@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsUNjqq4.', 'USER');
```
</details>
## 👥 Usuários de Teste

O sistema vem com usuários pré-configurados para demonstração:

| Tipo | Nome          | Email               | Senha       | Permissões |
|------|---------------|---------------------|-------------|------------|
| **Admin** | Administrador | `admin@example.com` | `Admin123!` | Todas as funcionalidades |
| **User** | User Teste    | `user@example.com`  | `User123!`  | Gerenciar próprios tickets |

## 🎯 Fluxos de Demonstração

### 1. Fluxo do Usuário (USER)
1. **Login** como `joao@example.com` / `admin123`
2. **Criar Ticket**: Título, descrição, categoria e prioridade
3. **Visualizar Tickets**: Ver apenas seus próprios tickets
4. **Editar Ticket**: Modificar título, descrição (se não fechado)
5. **Acompanhar Status**: Ver se admin respondeu/fechou

### 2. Fluxo do Administrador (ADMIN)
1. **Login** como `admin@example.com` / `admin123`
2. **Gerenciar Usuários**: Criar, visualizar, editar, deletar
3. **Gerenciar Categorias**: CRUD completo de categorias
4. **Gerenciar Tickets**: Ver todos, responder, fechar
5. **Relatórios**: Visualizar todos os tickets do sistema

### 3. Fluxo de API Testing
1. **Acesse** http://localhost:8000/docs (Swagger)
2. **Teste Login**: Use `/auth/login` com credenciais acima
3. **Autorização**: Clique "Authorize" e cole o token
4. **Teste Endpoints**: Experimente criar tickets, categorias, etc.
5. **Teste Permissões**: Compare funcionalidades USER vs ADMIN

## Executar Localmente

```bash
uvicorn app.main:app --reload --port 8000
```

A API estará disponível em: http://localhost:8000


## 📡 API Endpoints

> **📚 Documentação Completa**: Acesse http://localhost:8000/docs (Swagger) ou http://localhost:8000/redoc para documentação interativa completa.

## Segurança

- Senhas são hasheadas com bcrypt
- Autenticação via JWT Bearer token
- Controle de acesso baseado em roles (USER/ADMIN)
- Validação de dados com Pydantic

## Variáveis de Ambiente Obrigatórias

Configure no painel do Render > Environment:

```env
# Supabase (obrigatório)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon
SUPABASE_SERVICE_ROLE_KEY=sua_chave_service_role

# JWT (obrigatório)
JWT_SECRET=sua_chave_secreta_32_caracteres

# Ambiente (obrigatório)
ENV=prod

# Opcional - para CORS customizado
RENDER_SERVICE_NAME=nome-do-seu-servico
CUSTOM_ORIGINS=https://seuapp.com,https://app.seudominio.com
```


## 🛠️ Tecnologias

- **FastAPI**: Framework web moderno e rápido
- **Supabase**: Backend-as-a-Service com PostgreSQL
- **Pydantic**: Validação de dados
- **JWT**: Autenticação stateless
- **bcrypt**: Hash de senhas
- **uvicorn**: Servidor ASGI
