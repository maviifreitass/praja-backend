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

O sistema segue uma arquitetura em camadas (layered architecture) com separação clara de responsabilidades:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Routes    │────│    Services     │────│    Database     │
│   (FastAPI)     │    │   (Business)    │    │   (Supabase)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
    ┌────▼────┐             ┌────▼────┐             ┌────▼────┐
    │ Auth    │             │ Auth    │             │ Users   │
    │ Tickets │             │ Ticket  │             │ Tickets │
    │Categories│             │Category │             │Categories│
    └─────────┘             └─────────┘             └─────────┘
```

**Camadas:**
- **API Layer**: Endpoints REST com validação de entrada e autenticação
- **Service Layer**: Lógica de negócio e regras de domínio
- **Data Layer**: Acesso aos dados via Supabase PostgreSQL

**Tecnologias:**
- **Backend**: FastAPI + Supabase + JWT
- **Autenticação**: JWT Bearer tokens com bcrypt
- **Banco de Dados**: PostgreSQL (via Supabase)
- **Deploy**: Render (ou qualquer plataforma compatível)

### 🎯 Principais Decisões Arquiteturais

- **Arquitetura em Camadas**: Separação clara entre API, Service e Data layers
- **Service Layer Pattern**: Lógica de negócio isolada em serviços especializados
- **Dependency Injection**: Uso do sistema de dependências do FastAPI
- **JWT Stateless**: Autenticação sem estado para escalabilidade
- **Supabase BaaS**: Backend-as-a-Service para reduzir complexidade de infraestrutura

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

> 💡 **Dica**: Use `python -c "import secrets; print(secrets.token_urlsafe(32))"` para gerar uma JWT_SECRET segura.

## 🗄️ Banco de Dados

### Configuração do Supabase

Execute este SQL no **SQL Editor** do Supabase para criar as tabelas, índices e dados iniciais:

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

## 👥 Usuários de Teste

O sistema vem com usuários pré-configurados para demonstração:

| Tipo | Nome | Email | Senha | Permissões |
|------|------|-------|-------|------------|
| **Admin** | Administrador | `admin@example.com` | `admin123` | Todas as funcionalidades |
| **User** | João Silva | `joao@example.com` | `admin123` | Gerenciar próprios tickets |
| **User** | Maria Santos | `maria@example.com` | `admin123` | Gerenciar próprios tickets |

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

## 📚 Documentação da API (Swagger)

O **Swagger/OpenAPI** está totalmente configurado e integrado! 

Com o servidor rodando, acesse:
- **Swagger UI**: http://localhost:8000/docs (Interface interativa)
- **ReDoc**: http://localhost:8000/redoc (Documentação limpa)

### 🔐 Como usar o Swagger:
1. Acesse http://localhost:8000/docs
2. Faça login em `/auth/login` com admin@example.com / admin123
3. Copie o token retornado
4. Clique no botão **"Authorize" 🔒** no topo
5. Cole o token (formato: `Bearer seu_token`)
6. Agora pode testar todos os endpoints protegidos!

### ✨ Funcionalidades do Swagger:
- **Documentação rica** com exemplos
- **Teste interativo** de endpoints
- **Autenticação JWT** integrada
- **Validação automática** de dados
- **Schemas detalhados** de request/response

## 📡 API Endpoints

> **📚 Documentação Completa**: Acesse http://localhost:8000/docs (Swagger) ou http://localhost:8000/redoc para documentação interativa completa.

### 🔐 Autenticação (`/auth`)

| Método | Endpoint | Descrição | Permissão | Exemplo Response |
|--------|----------|-----------|-----------|------------------|
| `GET` | `/auth/csrf-token` | Obter token CSRF | Público | `{"csrf_token": "abc123"}` |
| `POST` | `/auth/register` | Registrar usuário | Público | `{"id": 1, "name": "João", "email": "joao@test.com", "role": "USER"}` |
| `POST` | `/auth/login` | Fazer login | Público | `{"access_token": "jwt_token", "token_type": "bearer", "role": "USER"}` |
| `GET` | `/auth/me` | Perfil do usuário | Autenticado | `{"id": 1, "name": "João", "email": "joao@test.com", "role": "USER"}` |
| `GET` | `/auth/users` | Listar usuários | Admin | `[{"id": 1, "name": "João", "email": "joao@test.com", "role": "USER"}]` |
| `GET` | `/auth/users/{id}` | Obter usuário | Admin | `{"id": 1, "name": "João", "email": "joao@test.com", "role": "USER"}` |
| `PUT` | `/auth/users/{id}` | Atualizar usuário | Admin/Own | `{"id": 1, "name": "João Silva", "email": "joao@test.com", "role": "USER"}` |
| `DELETE` | `/auth/users/{id}` | Deletar usuário | Admin | `{"message": "Usuário deletado"}` |

### 🏷️ Categorias (`/categories`)

| Método | Endpoint | Descrição | Permissão | Exemplo Response |
|--------|----------|-----------|-----------|------------------|
| `GET` | `/categories/` | Listar categorias | Autenticado | `[{"id": 1, "name": "Suporte Técnico", "color": "#ff5733"}]` |
| `POST` | `/categories/` | Criar categoria | Admin | `{"id": 1, "name": "Nova Categoria", "color": "#ff5733"}` |
| `GET` | `/categories/{id}` | Obter categoria | Admin | `{"id": 1, "name": "Suporte Técnico", "color": "#ff5733"}` |
| `PUT` | `/categories/{id}` | Atualizar categoria | Admin | `{"id": 1, "name": "Suporte Atualizado", "color": "#ff5733"}` |
| `DELETE` | `/categories/{id}` | Deletar categoria | Admin | `{"message": "Categoria deletada"}` |

### 🎫 Tickets (`/tickets`)

| Método | Endpoint | Descrição | Permissão | Exemplo Response |
|--------|----------|-----------|-----------|------------------|
| `GET` | `/tickets/` | Listar tickets | Autenticado | `[{"id": 1, "title": "Problema X", "status": "open", "priority": "HIGH"}]` |
| `POST` | `/tickets/` | Criar ticket | Autenticado | `{"id": 1, "title": "Novo Ticket", "status": "open", "created_by": 1}` |
| `GET` | `/tickets/{id}` | Obter ticket | Autenticado | `{"id": 1, "title": "Problema X", "description": "Detalhes...", "status": "open"}` |
| `PUT` | `/tickets/{id}` | Atualizar ticket | Owner/Admin | `{"id": 1, "title": "Título Atualizado", "status": "open"}` |
| `PATCH` | `/tickets/{id}/close` | Fechar ticket | Admin | `{"id": 1, "title": "Problema X", "status": "closed"}` |
| `DELETE` | `/tickets/{id}` | Deletar ticket | Owner/Admin | `{"message": "Ticket deletado"}` |

### 📊 Root

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| `GET` | `/` | Informações da API | Público |

## Segurança

- Senhas são hasheadas com bcrypt
- Autenticação via JWT Bearer token
- Controle de acesso baseado em roles (USER/ADMIN)
- Validação de dados com Pydantic

## 🚀 Deploy no Render

### Configuração do Serviço

1. **Conecte o repositório** ao Render
2. **Tipo de serviço**: Web Service
3. **Runtime**: Python 3
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Variáveis de Ambiente Obrigatórias

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

### Troubleshooting

**❌ ERR_CONNECTION_REFUSED**
1. Verifique se o serviço está rodando: `https://seu-servico.onrender.com/health`
2. Confirme as variáveis de ambiente no painel do Render
3. Verifique os logs do deploy para erros

**❌ CORS Errors**
1. Adicione sua origem frontend em `CUSTOM_ORIGINS`
2. Ou configure `RENDER_SERVICE_NAME` para CORS automático

**❌ 500 Internal Server Error**
1. Verifique as credenciais do Supabase
2. Confirme que `ENV=prod` está configurado
3. Verifique se `JWT_SECRET` tem pelo menos 32 caracteres

### URLs de Teste

Após o deploy, teste:
- **API Health**: `https://seu-servico.onrender.com/health`
- **API Root**: `https://seu-servico.onrender.com/`
- **Swagger**: `https://seu-servico.onrender.com/docs`
- **ReDoc**: `https://seu-servico.onrender.com/redoc`

## 🛠️ Tecnologias

- **FastAPI**: Framework web moderno e rápido
- **Supabase**: Backend-as-a-Service com PostgreSQL
- **Pydantic**: Validação de dados
- **JWT**: Autenticação stateless
- **bcrypt**: Hash de senhas
- **uvicorn**: Servidor ASGI
