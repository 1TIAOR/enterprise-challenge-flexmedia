# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width="40%" height="40%"></a>
</p>

<br>

# Totem Inteligente FlexMedia com IA

## Grupo 50 R

## 👨‍🎓 Integrantes:

- Gabriel Henrique de Oliveira Moraes
- Guilherme Filartiga Pereira da Silva
- Thiago Limongi Faria dos Reis
- Gabriel Luiz Fagundes

## 👩‍🏫 Professores:

### Tutoras

- Ana Cristana dos Santos

---

## 📜 Descrição

O **Totem Inteligente FlexMedia** é um projeto desenvolvido em parceria com a empresa **FlexMedia**, que atua na criação de soluções digitais interativas para espaços culturais e comerciais.

O objetivo é construir um **totem inteligente com Inteligência Artificial**, capaz de **coletar, processar e analisar interações humanas**, como presença, atenção, emoções e engajamento, gerando insights em tempo real e um **NPS (Net Promoter Score) estimado por IA**.

A proposta combina sensores físicos (ESP32, PIR, toque), **visão computacional** (análise de atenção e afeto via câmera SBC), **IA em nuvem** (para predição e aprendizado contínuo), e **dashboards interativos** (para gestores de ambiente).

Além de fornecer experiências mais personalizadas aos visitantes, o projeto se preocupa com **segurança e privacidade dos dados**, adotando um modelo **Privacy by Design**, onde nenhuma imagem é armazenada, apenas métricas anônimas são processadas.

---

## 📡 Arquitetura Técnica da Solução

### **Visão Geral**

<p align="center">
<img src="assets/fluxo1.png" width="80%" alt="Fluxo 1 - Visão Geral da Arquitetura">
</p>

O Totem é composto por três camadas principais:

- **Edge (Totem físico)** → coleta e processamento inicial (sensores e câmera).
- **Nuvem (Cloud)** → armazenamento, APIs, IA e dashboards.
- **Interface (UI)** → interação direta com o visitante (toque e exibição de conteúdo).

### **Pipeline de Dados e IA**

<p align="center">
<img src="assets/fluxo2.png" width="80%" alt="Fluxo 2 - Pipeline de Dados e IA">
</p>

1. **Sensores e Câmera** capturam presença, atenção e emoções básicas (valência/arousal).
2. **ESP32 e SBC (Raspberry/Jetson)** convertem os sinais físicos em dados digitais.
3. **API REST** recebe, valida e grava os eventos no **banco de dados (PostgreSQL)**.
4. **Serviço de IA** calcula o **NPS estimado** com base em dados de atenção e engajamento.
5. **Dashboards** exibem métricas e insights para a equipe da FlexMedia.

---

## ⚙️ Coleta de Dados e Sensores

### Dispositivos utilizados:

- **ESP32** — microcontrolador principal; coleta sinais de sensores e envia via Wi-Fi.
- **Sensor PIR** — detecta presença e tempo de permanência.
- **Sensor capacitivo** — registra interações físicas (toques).
- **LDR** — ajusta automaticamente o brilho da tela.
- **Câmera SBC (ou ESP32-CAM)** — analisa atenção, número de pessoas e emoções sem armazenar imagens.

### Fluxo físico:

1. Sensor detecta movimento → ESP32 cria uma nova sessão.
2. Câmera identifica presença e atenção → extrai features de valência/arousal.
3. Dados são enviados em JSON via HTTPS para o backend.
4. O backend processa, armazena e repassa para dashboards e IA.

---

## 🧩 Estrutura de Dados

**Banco:** PostgreSQL (com colunas JSONB para flexibilidade).

**Entidades principais:**

- `totems` → informações físicas do dispositivo.
- `sessions` → período ativo de interação.
- `events` → cliques e ações do usuário.
- `vision_ticks` → medições de atenção/emoção por janela de tempo.
- `affect_sessions` → agregados por sessão (valência, arousal, dwell time, gaze mean).

**Exemplo de evento registrado:**

```json
{
  "session_id": "uuid",
  "ts": "2025-11-01T13:22:00Z",
  "people_count": 1,
  "gaze_score": 0.78,
  "valence": 0.12,
  "arousal": 0.45
}
```

---

## 🤖 Inteligência Artificial Planejada

### **Etapa 1 — Edge AI**

- Processamento de vídeo no dispositivo (SBC / ESP32-CAM);
- Extração de features de atenção e emoção;
- Nenhuma imagem armazenada, apenas vetores numéricos.

### **Etapa 2 — Cloud AI**

- Modelo supervisionado de **Regressão Logística ou KNN**;
- Predição de **NPS estimado** a partir de métricas emocionais e comportamentais;
- Classificação:
  - 0–6 → Detratores
  - 7–8 → Neutros
  - 9–10 → Promotores

---

## ☁️ Infraestrutura de Nuvem

| Camada             | Tecnologia                          | Função                           |
| ------------------ | ----------------------------------- | -------------------------------- |
| **Edge**           | ESP32 / ESP32-CAM / SBC             | Coleta e pré-processamento local |
| **API**            | FastAPI (Python) / NestJS (Node.js) | Recepção e validação de eventos  |
| **Banco de Dados** | PostgreSQL / Supabase               | Armazenamento relacional         |
| **IA/ML**          | Scikit-learn / TensorFlow           | Modelagem e predição             |
| **Dashboard**      | Metabase / Power BI                 | Visualização de resultados       |
| **Cloud Provider** | Oracle / AWS / GCP                  | Hospedagem e segurança           |

---

## 🔒 Segurança e Privacidade

- **Privacy by Design:** nenhum dado pessoal ou imagem é armazenado;
- **Criptografia:** HTTPS + AES-256;
- **Anonimização:** apenas dados agregados são transmitidos;
- **Retenção controlada:** logs e eventos expiram em 90 dias;
- **Conformidade:** aderente à **LGPD** e boas práticas de segurança da informação.

---

## 📁 Estrutura de Pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- **.github/** → automações e configurações do repositório.
- **assets/** → imagens e diagramas (`logo-fiap.png`, `fluxo1.png`, `fluxo2.png`).
- **config/** → arquivos de configuração do ambiente.
- **document/** → documentação do projeto e relatórios FIAP.
- **scripts/** → scripts de setup, migração ou automação.
- **src/** → código-fonte principal (Edge, API e Dashboard).
- **README.md** → este arquivo principal de referência.

---

## 🔧 Como Executar o Código

> _Nesta Sprint não há código executável._  
> Nas próximas sprints, o repositório incluirá:

1. Firmware do **ESP32** (para sensores e câmera);
2. **API REST** para recebimento de eventos;
3. **Dashboard Metabase** conectado ao banco PostgreSQL.

**Pré-requisitos futuros:**

- Python 3.10+
- Node.js 20+
- PostgreSQL
- Conta Cloud (Oracle / AWS / GCP)

---

## 🗓 Plano de Desenvolvimento

| Sprint | Entregas                                                       |
| ------ | -------------------------------------------------------------- |
| **1**  | Documentação técnica (escopo, arquitetura, segurança e plano). |
| **2**  | PoC de coleta (ESP32 e simulação de API).                      |
| **3**  | Dashboards e análise exploratória.                             |
| **4**  | Modelo de IA funcional (predição de NPS).                      |

---

## 🧠 Divisão de Responsabilidades

| Função                     | Responsável         | Entregas                        |
| -------------------------- | ------------------- | ------------------------------- |
| Arquiteto                  | Gabriel Oliveira    | Estrutura geral e integração IA |
| Edge (Sensores e Câmera)   | Guilherme Filartiga | Coleta de dados e ESP32         |
| Backend/API e Documentação | Gabriel Luiz        | Modelagem e endpoints           |
| IA e Dashboards            | Thiago Limongi      | Modelos e relatórios            |

---

## 🗃 Histórico de Lançamentos

- 0.1.0 — 11/2025 — Entrega Sprint 1 (Documentação e Arquitetura).

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
