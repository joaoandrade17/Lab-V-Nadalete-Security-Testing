# Mural da Turma — exemplo prático de Security Testing

Exemplo prático do seminário **Non-Functional Testing: Security Testing**.

É uma pequena aplicação web em **Python + Flask** (um mural de recados com login)
escrita com **duas vulnerabilidades de propósito**. O repositório mostra cada
vulnerabilidade sendo **explorada** e depois **corrigida**, bastando trocar de branch.

## As duas vulnerabilidades

| # | Vulnerabilidade | OWASP Top 10:2021 | Onde está |
|---|---|---|---|
| 1 | **SQL Injection** no login | A03 — Injection | `app/app.py` (rota `/login`) |
| 2 | **Stored XSS** no mural | A03 — Injection | `app/templates/mural.html` |

## As duas branches

| Branch | Estado |
|---|---|
| `vulneravel` | Os dois ataques **funcionam** |
| `corrigido` | Os dois ataques são **bloqueados** |

A branch padrão (`main`) já vem com a versão **corrigida**. A diferença entre as
versões é exatamente o conserto:

```bash
git diff vulneravel corrigido -- app/
```

## Como executar

Requer Python 3.9+.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r app/requirements.txt
python app/app.py
```

Abra **http://127.0.0.1:5080**. O banco SQLite é recriado com dados de exemplo
a cada vez que o app sobe.

> A porta é 5080 para evitar conflito com o AirPlay do macOS (que usa a 5000).

Usuários carregados:

| Usuário | Senha |
|---|---|
| `maria` | `maria2024` |
| `admin` | `supersecreta123` |

## Demonstração

### 1. SQL Injection (burlar o login)

Na branch `vulneravel`, na tela de login:

```
usuário:  admin' --
senha:    qualquer coisa
```

Você entra como **admin sem saber a senha**. O `--` transforma a checagem de
senha em comentário SQL. Na branch `corrigido` o mesmo payload é rejeitado.

### 2. Stored XSS (recado malicioso)

Logado, publique este recado:

```html
<script>alert('XSS de ' + document.domain)</script>
```

Na branch `vulneravel` o script é salvo e **executa no navegador** de todos que
abrirem o mural. Na branch `corrigido` ele aparece como texto inofensivo.

### 3. (Opcional) SAST com Bandit

```bash
pip install bandit
bandit app/app.py
```

Na `vulneravel` o Bandit aponta `B608` (SQL por concatenação) na linha do login;
na `corrigido` esse achado some. Os avisos restantes (`secret_key` fixa e
`debug=True`) são esperados num app didático de `localhost`.

## Como a correção funciona

| Vulnerabilidade | Versão vulnerável | Correção |
|---|---|---|
| SQL Injection | `"... WHERE username='%s'" % u` (concatenação) | consulta parametrizada `execute(sql, (u, p))` |
| Stored XSS | `{{ c.content \| safe }}` (escape desligado) | `{{ c.content }}` (escape automático do Jinja2) |

A raiz das duas é a mesma: **misturar dado do usuário com código** (SQL e HTML).
A correção é **separar dado de código**: parametrizar consultas e escapar a saída.

## Estrutura

```
nadalete/
├── app/                     aplicação Flask
│   ├── app.py               rotas + banco (ponto da correção do SQLi)
│   ├── requirements.txt
│   ├── templates/           base, login e mural (ponto da correção do XSS)
│   └── static/style.css
├── slides/index.html        apresentação (abrir no navegador)
├── docs/roteiro-demo.md     passo a passo da demonstração ao vivo
└── README.md
```

## Apresentação

Abra `slides/index.html` em qualquer navegador. Navegue com as setas
(← →), espaço, e `F` para tela cheia.

## Aviso

As vulnerabilidades aqui são **intencionais e didáticas**. Rode apenas em
`localhost`. Não use este código em produção.
