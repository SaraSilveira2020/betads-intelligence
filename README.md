# BetAds Intelligence

**Análise automatizada da exposição de publicidade de bets em conteúdos esportivos no YouTube.**

## 1. Sobre o projeto

O **BetAds Intelligence** é um projeto de Engenharia de Dados voltado ao monitoramento de menções a bets em conteúdos esportivos publicados no YouTube, com foco inicial na CazéTV durante o período da Copa do Mundo.

O objetivo é transformar transcrições públicas de vídeos em indicadores analíticos que permitam acompanhar a frequência, intensidade e evolução da exposição de termos e marcas associadas a apostas esportivas.

## 2. Problema

A publicidade de bets em transmissões esportivas digitais alcança grandes audiências e pode impactar públicos jovens, torcedores e espectadores altamente engajados.

O acompanhamento manual por planilhas não escala, pois exige assistir ou revisar muitos vídeos, lives, cortes e transcrições. Este projeto automatiza a coleta, tratamento e análise desses dados.

## 3. Objetivo

Criar um pipeline de dados capaz de:

- Capturar transcrições públicas de vídeos do YouTube;
- Armazenar dados brutos na camada Bronze;
- Padronizar e calcular métricas na camada Silver;
- Gerar indicadores analíticos na camada Gold;
- Disponibilizar os resultados em um dashboard Streamlit.

## 4. Indicador principal

O principal indicador do projeto é o **IEB — Índice de Exposição a Bets**.

```text
IEB = (total de menções a bets / total de palavras transcritas) * 1000
