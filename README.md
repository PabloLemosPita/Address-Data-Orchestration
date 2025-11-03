Address Data Orchestration

Projeto simples para orquestração de ingestão de endereços usando Apache Airflow.

Visão geral

Este repositório contém uma DAG (address_orchestration) que consulta a API randomuser.me para obter endereços (nacionalidade BR), transforma os dados e os insere em uma tabela PostgreSQL chamada brazilian_address.

Principais componentes

dags/address_orchestration.py — definição da DAG e tasks (extract, decide, transform, load).

Dependência: requests para chamar a API externa.

Pré-requisitos

Docker e Docker Compose (se executar localmente via contêineres).

Apache Airflow (com conexão a um Postgres acessível).

Uma instância PostgreSQL (pode ser um container) e credenciais.

Estrutura da tabela (SQL)

CREATE TABLE IF NOT EXISTS brazilian_address (
    id SERIAL PRIMARY KEY,
    estado TEXT,
    cidade TEXT,
    rua TEXT,
    numero_endereco INTEGER,
    cep TEXT
);

Observação: a DAG insere valores para estado, cidade, rua, numero_endereco e cep — certifique-se de que os tipos de dados estejam de acordo com os retornos da API.

Como criar a conexão postgres na UI do Airflow (passo a passo)

Acesse a UI do Airflow (por exemplo, http://localhost:8080).

No menu superior clique em Admin (ou Settings dependendo da versão) → Connections.

Clique em Create (ou +) para adicionar uma nova conexão.

Preencha os campos principais:

Conn Id: postgres  ← esse ID deve bater com o PostgresHook(postgres_conn_id="postgres") do código.

Conn Type: Postgres

Host: endereço do servidor Postgres (ex.: postgres se usando Docker Compose em mesma rede, ou 127.0.0.1/IP)

Schema: nome do banco (ex.: postgres ou mydatabase)

Login: usuário do banco (ex.: postgres)

Password: senha do usuário

Port: 5432 (padrão)

Extra (opcional): JSON com parâmetros adicionais, ex.: { "sslmode": "disable" }

Clique em Save.

Dicas

Verifique conectividade: na UI do Airflow (Connections) há um botão para testar a conexão em versões recentes; caso não exista, você pode testar executando um pequeno PythonOperator que usa PostgresHook().get_conn() para confirmar.

Garanta que o Airflow e o Postgres estejam na mesma rede de contêineres (Docker Compose) ou que as regras de firewall/ports permitam a conexão.

Como criar a tabela dentro do container PostgreSQL (terminal interativo)

Abaixo estão instruções genéricas — ajuste postgres_container_name, DB_USER, DB_NAME e DB_PASSWORD conforme seu ambiente.

Passo A — Acessando o container via Docker

Encontre o nome/ID do container Postgres:

docker ps

Acesse o shell do container (exemplo):

docker exec -it <postgres_container_name> bash

Dentro do container, execute o cliente psql (exemplo):

psql -U <DB_USER> -d <DB_NAME>

Crie a tabela com o SQL acima:

CREATE TABLE IF NOT EXISTS brazilian_address (
    id SERIAL PRIMARY KEY,
    estado TEXT,
    cidade TEXT,
    rua TEXT,
    numero_endereco INTEGER,
    cep TEXT
);

Saia do psql com \q e do shell do container com exit.
