#!/usr/bin/env bash
# Hook PreToolUse (Bash|PowerShell) do projeto e_seller.
#
# Regra 1: o Claude nunca executa git add, git commit nem git push neste
# repositório; ele propõe os comandos em blocos copiáveis e o dono executa.
# Cobre o que o "deny" por prefixo não pega: opções antes do subcomando
# (git -C <dir> commit, git -c k=v push), git.exe e comandos encadeados.
#
# Regra 2: o Claude nunca lê .env nem arquivo de credencial local (*.env) por
# shell (cat, type, Get-Content...). O .env.example continua legível.
#
# Saída 2 bloqueia a chamada e devolve a mensagem de stderr ao Claude.

entrada="$(cat)"

padrao_git='(^|[^[:alnum:]_-])git(\.exe)?([[:space:]]+-[^[:space:]]+([[:space:]]+[^-[:space:]][^[:space:]]*)?)*[[:space:]]+(add|commit|push)([^[:alnum:]_-]|$)'
padrao_segredo='(^|[^[:alnum:]_-])(cat|type|more|less|head|tail|bat|nl|gc|Get-Content|Select-String|sls)([[:space:]]+[^|;&]*)?[^[:space:]]*\.env([[:space:]"'"'"'\\]|$)'

if printf '%s' "$entrada" | grep -Eq "$padrao_git"; then
    echo "Bloqueado pela regra do projeto (.claude/settings.json): o Claude não executa git add, git commit nem git push. Proponha os comandos em blocos copiáveis e aguarde o dono executar." >&2
    exit 2
fi

if printf '%s' "$entrada" | grep -Eq "$padrao_segredo"; then
    echo "Bloqueado pela regra do projeto (.claude/settings.json): o Claude não lê .env nem credencial local. Para mudar o .env, instrua o dono; edite apenas .env.example." >&2
    exit 2
fi

exit 0
