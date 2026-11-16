# Roteiro da demonstração ao vivo

Tempo alvo: ~35 min no total (slides + demo). A demonstração ao vivo ocupa os
últimos ~10 min. Deixe o ambiente pronto **antes** da aula (passo 0).

---

## Passo 0 — Preparação (antes da aula)

```bash
cd nadalete
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
pip install bandit          # opcional, para a parte de SAST
```

- Deixe **dois terminais** abertos na pasta do repositório, com a venv ativada.
- Deixe o navegador aberto em `slides/index.html` para a apresentação.
- Teste uma vez os dois ataques para não ter surpresa ao vivo.

---

## Passo 1 — Abrir a versão vulnerável

```bash
git checkout vulneravel
python app/app.py
```

Abra **http://127.0.0.1:5080** no navegador.

Mostre que a aplicação **funciona normalmente**: faça login com `maria / maria2024`
e publique um recado comum. Frase-chave: *"funciona — e mesmo assim é insegura"*.
Depois faça logout.

---

## Passo 2 — Ataque 1: SQL Injection (burlar o login)

Na tela de login, digite:

```
usuário:  admin' --
senha:    123
```

Resultado: entra como **admin**, sem saber a senha real (`supersecreta123`).

Explique no slide "Como funciona o SQL Injection": o texto digitado foi
concatenado na consulta e o `--` comentou a checagem de senha. Mostre a linha
vulnerável:

```bash
grep -n "SELECT \* FROM users" app/app.py
```

Variações que também funcionam, se quiser mostrar: `' OR '1'='1' --`.

---

## Passo 3 — Ataque 2: Stored XSS (recado malicioso)

Ainda logado, publique o recado:

```html
<script>alert('XSS de ' + document.domain)</script>
```

O alerta dispara **assim que a página do mural carrega**. Recarregue para mostrar
que fica salvo (é *stored*): dispara de novo, e dispararia para qualquer usuário.

Mostre a linha vulnerável no template:

```bash
grep -n "safe" app/templates/mural.html
```

---

## Passo 4 — (Opcional) SAST encontra o SQLi sozinho

```bash
bandit app/app.py
```

O Bandit aponta `B608` (hardcoded SQL / string-based query) na linha da
concatenação — ninguém escreveu um teste, a ferramenta achou lendo o código.
Comente que ela acha o SQLi, mas **não** acharia o XSS de template nem falhas de
regra de negócio.

---

## Passo 5 — Abrir a versão corrigida

Pare o servidor (Ctrl+C) e troque de branch:

```bash
git checkout corrigido
python app/app.py
```

Repita **os mesmos dois ataques**:

- Login `admin' --` → agora devolve "usuário ou senha inválidos". ✓
- Recado `<script>...</script>` → agora aparece como **texto na tela**, não executa. ✓

Se tiver rodado o Bandit, rode de novo: sem achados.

---

## Passo 6 — Mostrar o conserto (o diff)

```bash
git diff vulneravel corrigido -- app/app.py app/templates/mural.html
```

Aponte as duas mudanças:

1. `"... WHERE username = '%s'" % u` → `execute("... WHERE username = ?", (u, p))`
2. `{{ c.content | safe }}` → `{{ c.content }}`

Frase de fechamento: *"as duas falhas vêm de misturar dado com código; a correção
é separar dado de código."*

---

## Plano B (se algo falhar ao vivo)

Os slides 16–22 têm o código e a explicação de cada ataque e de cada correção.
Se o ambiente não subir, apresente por eles — o conteúdo é o mesmo.
