#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.config/opencode"
mkdir -p "$CONFIG_DIR"

V='\033[32m'
C='\033[36m'
A='\033[33m'
R='\033[31m'
B='\033[1m'
S='\033[0m'
G='\033[90m'

echo ""
echo -e "  ${C}${B}+--------------------------------------------------+${S}"
echo -e "  ${C}${B}| OpenCode Core - Onboarding                        |${S}"
echo -e "  ${C}${B}+--------------------------------------------------+${S}"
echo ""
echo -e "  ${B}Ola! Vou te fazer 3 perguntas rapidas pra${S}"
echo -e "  ${B}entender como voce gosta de receber ajuda.${S}"
echo ""
echo -e "  ${A}Nao tem resposta errada.${S}"
echo -e "  ${A}Da pra mudar depois com /config.${S}"
echo ""
read -p "  Pressione ENTER pra comecar > " dummy
echo ""

echo -e "  ${G}--------------------------------------------------${S}"
echo ""
echo -e "  ${C}PERGUNTA 1 DE 3${S}"
echo ""
echo -e "  ${B}ESTILO DE RESPOSTA${S}"
echo -e "  ${G}Isso define como EU vou falar com voce.${S}"
echo ""
echo -e "  ${A}Voce perguntou:${S}  ${G}\"Como criar uma rota GET /users?\"${S}"
echo ""
echo -e "  ${V}${B}[1]${S} ${B}DIRETO${S}"
echo -e "    ${G}\"Cria routes/users.js com handler GET.\"${S}"
echo -e "    ${G}Vai direto ao ponto, sem rodeios${S}"
echo ""
echo -e "  ${C}${B}[2]${S} ${B}EQUILIBRADO${S}  ${G}<<< recomendado${S}"
echo -e "    ${G}\"Cria routes/users.js. Recomendo express.Router().\"${S}"
echo -e "    ${G}Explica o necessario, nem mais nem menos${S}"
echo ""
echo -e "  ${A}${B}[3]${S} ${B}DIDATICO${S}"
echo -e "    ${G}\"Passo 1: crie routes/users.js. Passo 2: adicione router.get...\"${S}"
echo -e "    ${G}Passo a passo detalhado${S}"
echo ""
echo -e "  ${R}${B}[4]${S} ${B}RELAXADO${S}"
echo -e "    ${G}\"Bora! Cria o arquivo e bota a rota la!\"${S}"
echo -e "    ${G}Informal, bem tranquilo${S}"
echo ""
echo -e "  ${B}Qual estilo prefere? [1-4, Enter=2]${S}"
read -p "  > " STYLE_CHOICE
STYLE_CHOICE="${STYLE_CHOICE:-2}"

case "$STYLE_CHOICE" in
  1) TONE="direct"; TONE_R="DIRETO"; TONE_EX="Vou ser direto e objetivo." ;;
  3) TONE="didatic"; TONE_R="DIDATICO"; TONE_EX="Vou explicar passo a passo." ;;
  4) TONE="casual"; TONE_R="RELAXADO"; TONE_EX="Vou ser informal e relaxado." ;;
  *) TONE="balanced"; TONE_R="EQUILIBRADO"; TONE_EX="Vou explicar o necessario." ;;
esac

echo ""
echo -e "  ${V}+--------------------------------------------------+${S}"
echo -e "  ${V}|  ${TONE_R} ativado!${S}"
echo -e "  ${V}|${S}"
echo -e "  ${V}|  ${TONE_EX}${S}"
echo -e "  ${V}|${S}"
echo -e "  ${V}|  Se quiser mudar depois: /config${S}"
echo -e "  ${V}+--------------------------------------------------+${S}"
echo ""

echo -e "  ${G}--------------------------------------------------${S}"
echo ""
echo -e "  ${C}PERGUNTA 2 DE 3${S}"
echo ""
echo -e "  ${B}FOCO PRINCIPAL${S}"
echo -e "  ${G}Isso ajuda a dar exemplos na SUA area.${S}"
echo ""
echo -e "  ${V}${B}[1]${S} ${B}WEB${S}"
echo -e "    ${G}React, HTML, CSS, frontend${S}"
echo ""
echo -e "  ${C}${B}[2]${S} ${B}BACKEND / API${S}  ${G}<<< recomendado${S}"
echo -e "    ${G}Servidores, banco de dados, rotas${S}"
echo ""
echo -e "  ${A}${B}[3]${S} ${B}AUTOMACAO / CLI${S}"
echo -e "    ${G}Scripts, shell, ferramentas de terminal${S}"
echo ""
echo -e "  ${R}${B}[4]${S} ${B}DADOS / ML${S}"
echo -e "    ${G}Analise, pipelines, machine learning${S}"
echo ""
echo -e "  ${G}${B}[5]${S} ${B}GERAL${S}"
echo -e "    ${G}Um pouco de tudo${S}"
echo ""
echo -e "  ${B}Qual seu foco principal? [1-5, Enter=2]${S}"
read -p "  > " FOCUS_CHOICE
FOCUS_CHOICE="${FOCUS_CHOICE:-2}"

case "$FOCUS_CHOICE" in
  1) FOCUS="web"; FOCUS_R="WEB"; FOCUS_EX="Vou dar exemplos com React e frontend." ;;
  3) FOCUS="cli"; FOCUS_R="AUTOMACAO / CLI"; FOCUS_EX="Vou dar exemplos com scripts e shell." ;;
  4) FOCUS="data"; FOCUS_R="DADOS / ML"; FOCUS_EX="Vou dar exemplos com analise e ML." ;;
  5) FOCUS="general"; FOCUS_R="GERAL"; FOCUS_EX="Vou adaptar os exemplos ao contexto." ;;
  *) FOCUS="backend"; FOCUS_R="BACKEND / API"; FOCUS_EX="Vou dar exemplos com APIs e servidores." ;;
esac

echo ""
echo -e "  ${V}+--------------------------------------------------+${S}"
echo -e "  ${V}|  ${FOCUS_R} ativado!${S}"
echo -e "  ${V}|${S}"
echo -e "  ${V}|  ${FOCUS_EX}${S}"
echo -e "  ${V}|${S}"
echo -e "  ${V}|  Se quiser mudar depois: /config${S}"
echo -e "  ${V}+--------------------------------------------------+${S}"
echo ""

echo -e "  ${G}--------------------------------------------------${S}"
echo ""
echo -e "  ${C}PERGUNTA 3 DE 3${S}"
echo ""
echo -e "  ${B}NIVEL DE EXPERIENCIA${S}"
echo -e "  ${G}Isso define o nivel de detalhe das respostas.${S}"
echo ""
echo -e "  ${V}${B}[1]${S} ${B}INICIANTE${S}"
echo -e "    ${G}Explica cada linha como se fosse a primeira vez${S}"
echo ""
echo -e "  ${A}${B}[2]${S} ${B}INTERMEDIARIO${S}"
echo -e "    ${G}Explica o necessario, sem exageros${S}"
echo ""
echo -e "  ${C}${B}[3]${S} ${B}AVANCADO${S}  ${G}<<< recomendado${S}"
echo -e "    ${G}Vai direto, nao precisa explicar obviedades${S}"
echo ""
echo -e "  ${R}${B}[4]${S} ${B}EXPERT${S}"
echo -e "    ${G}So o codigo. Explicacao minima.${S}"
echo ""
echo -e "  ${B}Qual seu nivel? [1-4, Enter=3]${S}"
read -p "  > " LEVEL_CHOICE
LEVEL_CHOICE="${LEVEL_CHOICE:-3}"

case "$LEVEL_CHOICE" in
  1) VERBOSITY="high"; NIVEL_R="INICIANTE"; NIVEL_EX="Vou explicar cada detalhe." ;;
  2) VERBOSITY="medium"; NIVEL_R="INTERMEDIARIO"; NIVEL_EX="Vou explicar o necessario." ;;
  4) VERBOSITY="low"; NIVEL_R="EXPERT"; NIVEL_EX="Vou ser minimalista." ;;
  *) VERBOSITY="low"; NIVEL_R="AVANCADO"; NIVEL_EX="Vou ser conciso, mostrando o codigo direto." ;;
esac

echo ""
echo -e "  ${V}+--------------------------------------------------+${S}"
echo -e "  ${V}|  ${NIVEL_R} ativado!${S}"
echo -e "  ${V}|${S}"
echo -e "  ${V}|  ${NIVEL_EX}${S}"
echo -e "  ${V}|${S}"
echo -e "  ${V}|  Se quiser mudar depois: /config${S}"
echo -e "  ${V}+--------------------------------------------------+${S}"
echo ""

cat > "$CONFIG_DIR/AGENTS.md" << AGENTS
# ONBOARDING
TONE=$TONE FOCUS=$FOCUS VERBOSITY=$VERBOSITY
AGENTS

echo ""
echo -e "  ${V}${B}+--------------------------------------------------+${S}"
echo -e "  ${V}${B}| Onboarding concluido!                             |${S}"
echo -e "  ${V}${B}+--------------------------------------------------+${S}"
echo -e "  ${V}|  ESTILO       [ $(echo $TONE_R | xargs) ]${S}"
echo -e "  ${V}|  FOCO         $(echo $FOCUS_R | xargs)${S}"
echo -e "  ${V}|  DETALHE      $(echo $VERBOSITY | xargs)${S}"
echo -e "  ${V}+--------------------------------------------------+${S}"
echo ""
echo -e "  ${G}Config salva em: $CONFIG_DIR/AGENTS.md${S}"
echo -e "  ${G}(2 linhas, ~20 tokens)${S}"
echo ""
echo -e "  ${G}--------------------------------------------------${S}"
echo ""
echo -e "  ${B}PROXIMO PASSO:${S}"
echo -e "  ${A}  bash setup.sh${S}"
echo ""
echo -e "  ${G}Quer mudar depois?${S}"
echo -e "  ${C}  No chat, digite:  /config${S}"
echo ""
