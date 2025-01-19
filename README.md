# Projeto Bolão Virtual Oficial

Este é o repositório do **Bolão Virtual Oficial**, um sistema completo para organização e gestão de bolões esportivos. O projeto é baseado no framework Django e utiliza diversas tecnologias e integrações modernas para oferecer uma experiência robusta.

---

## Estrutura de Diretórios

Abaixo está a estrutura principal do projeto:

```
hiagospencer-bolao_virtual_oficial/
├── Dockerfile                 # Configuração para criar a imagem Docker
├── Procfile                  # Arquivo para definição de processos (Heroku/Railway)
├── docker-compose.yml        # Orquestração de containers Docker
├── manage.py                 # Gerenciador de comandos Django
├── requirements.txt          # Dependências do projeto Python
├── app/                      # Aplicativo principal Django
│   ├── __init__.py
│   ├── asgi.py               # Configurações de ASGI
│   ├── celery.py             # Integração com Celery para tarefas assíncronas
│   ├── jazzmin.py            # Personalização do admin do Django
│   ├── settings.py           # Configurações principais
│   ├── urls.py               # Mapeamento de URLs do projeto
│   └── wsgi.py               # Configurações de WSGI
├── bolao/                    # App do bolão
│   ├── __init__.py
│   ├── admin.py              # Configurações do admin
│   ├── api_brasileirao.py    # Integração com dados do Campeonato Brasileiro
│   ├── api_mercadopago.py    # Integração com o Mercado Pago
│   ├── apps.py
│   ├── htmx_views.py         # Funções com HTMX
│   ├── models.py             # Modelos do banco de dados
│   ├── tasks.py              # Tarefas Celery
│   ├── urls.py               # URLs do app bolão
│   ├── utils.py              # Funções auxiliares
│   ├── views.py              # Views principais
│   ├── migrations/           # Migrações do banco de dados
│   ├── templates/            # Arquivos HTML
│   └── templatetags/         # Tags e filtros personalizados para templates
├── media/                    # Arquivos de mídia (ex: emblemas de times)
├── nginx/                    # Configurações do servidor Nginx
├── static/                   # Arquivos estáticos (CSS, JS, imagens)
├── staticfiles/              # Arquivos coletados para serviço
```

---

## Principais Funcionalidades

1. **Bolão Esportivo**: Permite a criação e gestão de palpites para jogos do Campeonato Brasileiro.
2. **Integração com Mercado Pago**: Processamento de pagamentos por PIX e cartão de crédito.
3. **Sistema de Ranking**: Classificação automática com pontuações atualizadas por rodada.
4. **Gráficos Interativos**: Exibição de dados visuais como variação no ranking e histórico de palpites.
5. **Interface Responsiva**: Layout intuitivo otimizado para desktop e dispositivos móveis.
6. **Tarefas Assíncronas**: Processos em segundo plano com Celery e RabbitMQ.
7. **Configurações Escaláveis**: Implantado em containers Docker com suporte a armazenamento na nuvem AWS.

---

## Configuração Inicial

### Requisitos

- Python 3.10+
- Docker e Docker Compose
- Redis (para fila de tarefas Celery)
- PostgreSQL (banco de dados)
- Nginx (para arquivos estáticos e media)

### Instalando o Projeto

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/bolao_virtual_oficial.git
   cd bolao_virtual_oficial
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente no arquivo `.env`.

4. Rode as migrações do banco:

   ```bash
   python manage.py migrate
   ```

5. Inicie o servidor local:

   ```bash
   python manage.py runserver
   ```

### Executando com Docker Compose

Para iniciar com Docker Compose:

```bash
docker-compose up --build
```

---

## Contribuições

Contribuições são bem-vindas! Por favor, abra um pull request ou uma issue para compartilhar ideias ou corrigir bugs.

---

## Licença

Este projeto está licenciado sob os termos da [MIT License](LICENSE).

---

## Contato

Em caso de dúvidas, entre em contato pelo e-mail: [hiagosouzadev10@gmail.com](mailto\:hiagosouzadev10@gmail.com).

