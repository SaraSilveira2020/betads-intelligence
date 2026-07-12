from pathlib import Path
from datetime import datetime
import sqlite3

import pandas as pd
import streamlit as st


# =========================
# Caminhos do projeto
# =========================

DOMINIO = "marketing_digital"

BRONZE_DIR = Path("datalake/bronze/dominio=marketing_digital")
SILVER_DIR = Path("datalake/silver/dominio=marketing_digital")
GOLD_DIR = Path("datalake/gold/dominio=marketing_digital")

CONTROL_DB = Path("datalake/control/ingestion.db")

RESUMO_FILE = GOLD_DIR / "resumo_exposicao_bets.csv"
RANKING_FILE = GOLD_DIR / "ranking_exposicao_bets_por_video.csv"


# =========================
# Configuração da página
# =========================

st.set_page_config(
    page_title="Monitor BetAds - Análise de Exposição de Bets",
    page_icon="⚠️",
    layout="wide"
)


# =========================
# Estilo visual
# =========================

st.markdown(
    """
    <style>
        .main-title {
            font-size: 42px;
            font-weight: 800;
            color: #F8FAFC;
            margin-bottom: 0px;
        }

        .subtitle {
            font-size: 18px;
            color: #CBD5E1;
            margin-top: 0px;
            margin-bottom: 24px;
        }

        .hero-box {
            background: linear-gradient(135deg, #111827 0%, #7F1D1D 100%);
            padding: 28px;
            border-radius: 18px;
            border: 1px solid #991B1B;
            margin-bottom: 24px;
        }

        .risk-box {
            background-color: #FEF2F2;
            border-left: 7px solid #DC2626;
            padding: 18px;
            border-radius: 10px;
            color: #111827;
            margin-bottom: 20px;
        }

        .info-box {
            background-color: #EFF6FF;
            border-left: 7px solid #2563EB;
            padding: 18px;
            border-radius: 10px;
            color: #111827;
            margin-bottom: 20px;
        }

        .metric-card {
            background-color: #0F172A;
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 20px;
            color: white;
            text-align: center;
        }

        .metric-label {
            color: #94A3B8;
            font-size: 14px;
        }

        .metric-value {
            color: #F8FAFC;
            font-size: 32px;
            font-weight: 800;
        }

        .section-title {
            font-size: 26px;
            font-weight: 700;
            margin-top: 20px;
            margin-bottom: 10px;
        }

        .ok {
            color: #16A34A;
            font-weight: 700;
        }

        .warn {
            color: #DC2626;
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# Funções auxiliares
# =========================

def carregar_dados_gold():
    if not RESUMO_FILE.exists() or not RANKING_FILE.exists():
        return None, None

    resumo = pd.read_csv(RESUMO_FILE)
    ranking = pd.read_csv(RANKING_FILE)

    return resumo, ranking


def contar_arquivos(pasta: Path, extensao: str) -> int:
    if not pasta.exists():
        return 0

    return len(list(pasta.rglob(f"*{extensao}")))


def ultima_modificacao(caminho: Path):
    if not caminho.exists():
        return None

    timestamp = caminho.stat().st_mtime
    return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")


def carregar_controle_sqlite():
    if not CONTROL_DB.exists():
        return None

    try:
        conn = sqlite3.connect(CONTROL_DB)
        df = pd.read_sql_query("SELECT * FROM videos_processados", conn)
        conn.close()
        return df
    except Exception:
        return None


def formatar_numero(valor):
    try:
        return f"{int(valor):,}".replace(",", ".")
    except Exception:
        return valor


def render_metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================
# Carregamento dos dados
# =========================

resumo, ranking = carregar_dados_gold()


# =========================
# Cabeçalho
# =========================

st.markdown(
    """
    <div class="hero-box">
        <div class="main-title">Monitor BetAds - Análise de Exposição de Bet</div>
        <div class="subtitle">
            Monitoramento automatizado da exposição publicitária de bets em conteúdos esportivos no YouTube
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="risk-box">
        <strong>Por que este tema importa?</strong><br>
        A publicidade de bets em transmissões esportivas digitais alcança grandes audiências,
        incluindo públicos jovens e altamente engajados. Monitorar a frequência, o contexto e a evolução
        dessas menções ajuda a transformar uma percepção subjetiva em evidência mensurável.
    </div>
    """,
    unsafe_allow_html=True
)


if resumo is None or ranking is None:
    st.warning("Arquivos Gold ainda não encontrados. Rode primeiro o pipeline Silver → Gold.")
    st.stop()


linha_resumo = resumo.iloc[0]


# =========================
# Abas
# =========================

aba_visao, aba_ranking, aba_observabilidade, aba_metodologia = st.tabs(
    [
        "📊 Visão Geral",
        "🏆 Ranking de Exposição",
        "🛠️ Observabilidade",
        "📘 Metodologia"
    ]
)


# =========================
# Aba 1 - Visão Geral
# =========================

with aba_visao:
    st.markdown('<div class="section-title">Indicadores principais</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card(
            "Vídeos processados",
            formatar_numero(linha_resumo["total_videos_processados"])
        )

    with col2:
        render_metric_card(
            "Palavras analisadas",
            formatar_numero(linha_resumo["total_palavras_analisadas"])
        )

    with col3:
        render_metric_card(
            "Menções a bets",
            formatar_numero(linha_resumo["total_mencoes_bets"])
        )

    with col4:
        render_metric_card(
            "IEB médio",
            round(float(linha_resumo["media_indice_exposicao_bets"]), 4)
        )

    st.markdown("---")

    st.markdown("### Índice de Exposição a Bets por vídeo")

    ranking_chart = ranking.copy()
    ranking_chart["video_id"] = ranking_chart["video_id"].astype(str)

    grafico = ranking_chart[["video_id", "indice_exposicao_bets"]].set_index("video_id")
    st.bar_chart(grafico)

    maior_ieb = float(linha_resumo["maior_indice_exposicao_bets"])

    if maior_ieb > 0:
        st.error(
            f"O maior índice de exposição identificado foi {maior_ieb:.4f} menções a bets a cada 1.000 palavras."
        )
    else:
        st.info("Nenhuma exposição a termos de bets foi identificada nos vídeos processados até o momento.")

    st.markdown(
        """
        <div class="info-box">
            <strong>Leitura executiva:</strong><br>
            O indicador não afirma irregularidade. Ele mede exposição textual a termos e marcas associadas a bets.
            A interpretação deve considerar o contexto editorial, publicitário e regulatório de cada vídeo.
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================
# Aba 2 - Ranking
# =========================

with aba_ranking:
    st.markdown('<div class="section-title">Ranking de vídeos por exposição a bets</div>', unsafe_allow_html=True)

    ranking_view = ranking.copy()
    ranking_view["url_youtube"] = "https://www.youtube.com/watch?v=" + ranking_view["video_id"].astype(str)

    ranking_view = ranking_view[
        [
            "video_id",
            "url_youtube",
            "total_palavras",
            "mencoes_termos_bets",
            "mencoes_marcas_bets",
            "total_mencoes_bets",
            "indice_exposicao_bets",
            "data_processamento",
        ]
    ]

    st.dataframe(
        ranking_view,
        use_container_width=True
    )

    st.download_button(
        label="Baixar ranking em CSV",
        data=ranking_view.to_csv(index=False, encoding="utf-8-sig"),
        file_name="ranking_exposicao_bets_por_video.csv",
        mime="text/csv"
    )


# =========================
# Aba 3 - Observabilidade
# =========================

with aba_observabilidade:
    st.markdown('<div class="section-title">Observabilidade do pipeline</div>', unsafe_allow_html=True)

    bronze_count = contar_arquivos(BRONZE_DIR, ".json")
    silver_count = contar_arquivos(SILVER_DIR, ".csv")
    gold_count = contar_arquivos(GOLD_DIR, ".csv")

    col1, col2, col3 = st.columns(3)

    with col1:
        render_metric_card("Arquivos Bronze", bronze_count)

    with col2:
        render_metric_card("Arquivos Silver", silver_count)

    with col3:
        render_metric_card("Arquivos Gold", gold_count)

    st.markdown("---")

    st.markdown("### Status das camadas")

    status_camadas = pd.DataFrame(
        [
            {
                "camada": "Bronze",
                "caminho": str(BRONZE_DIR),
                "arquivos": bronze_count,
                "ultima_modificacao": ultima_modificacao(BRONZE_DIR) or "Não encontrada",
                "status": "OK" if bronze_count > 0 else "Pendente",
            },
            {
                "camada": "Silver",
                "caminho": str(SILVER_DIR),
                "arquivos": silver_count,
                "ultima_modificacao": ultima_modificacao(SILVER_DIR) or "Não encontrada",
                "status": "OK" if silver_count > 0 else "Pendente",
            },
            {
                "camada": "Gold",
                "caminho": str(GOLD_DIR),
                "arquivos": gold_count,
                "ultima_modificacao": ultima_modificacao(GOLD_DIR) or "Não encontrada",
                "status": "OK" if gold_count > 0 else "Pendente",
            },
        ]
    )

    st.dataframe(status_camadas, use_container_width=True)

    st.markdown("### Controle de ingestão")

    controle_df = carregar_controle_sqlite()

    if controle_df is None:
        st.warning(
            "Banco de controle SQLite ainda não encontrado. "
            "Ele será criado quando o pipeline automático com idempotência estiver ativo."
        )

        st.code("datalake/control/ingestion.db")
    else:
        total_processados = len(controle_df)
        total_sucesso = len(controle_df[controle_df["status"] == "processado"])
        total_erro = len(controle_df[controle_df["status"] == "erro"])

        col1, col2, col3 = st.columns(3)

        with col1:
            render_metric_card("Vídeos registrados", total_processados)

        with col2:
            render_metric_card("Processados com sucesso", total_sucesso)

        with col3:
            render_metric_card("Erros registrados", total_erro)

        st.dataframe(controle_df, use_container_width=True)

    st.markdown("### Checklist técnico")

    checklist = pd.DataFrame(
        [
            {
                "item": "Bronze com dados brutos",
                "status": "OK" if bronze_count > 0 else "Pendente",
            },
            {
                "item": "Silver com dados tratados",
                "status": "OK" if silver_count > 0 else "Pendente",
            },
            {
                "item": "Gold com indicadores analíticos",
                "status": "OK" if gold_count > 0 else "Pendente",
            },
            {
                "item": "Dashboard consumindo Gold",
                "status": "OK",
            },
            {
                "item": "SQLite de controle/idempotência",
                "status": "OK" if CONTROL_DB.exists() else "Pendente",
            },
        ]
    )

    st.dataframe(checklist, use_container_width=True)


# =========================
# Aba 4 - Metodologia
# =========================

with aba_metodologia:
    st.markdown('<div class="section-title">Metodologia analítica</div>', unsafe_allow_html=True)

    st.markdown(
        """
        ### Objetivo

        Medir a exposição textual a termos e marcas relacionadas a bets em vídeos do YouTube,
        usando transcrições públicas como fonte de dados.

        ### Indicador principal

        **IEB — Índice de Exposição a Bets**

        O IEB calcula quantas menções a termos ou marcas de bets aparecem a cada 1.000 palavras transcritas.

        ```text
        IEB = (total de menções a bets / total de palavras transcritas) * 1000
        ```

        ### Camadas do pipeline

        - **Bronze:** armazena a transcrição bruta em JSON.
        - **Silver:** padroniza texto, calcula palavras e menções.
        - **Gold:** consolida indicadores para consumo analítico.
        - **Dashboard:** apresenta KPI, ranking e status do pipeline.

        ### Limitações

        - O projeto não afirma irregularidade legal.
        - O indicador depende da disponibilidade de transcrição pública.
        - Menções podem aparecer em contexto editorial, crítico, publicitário ou narrativo.
        - A leitura final exige análise de contexto.
        """
    )

    st.markdown(
        """
        <div class="risk-box">
            <strong>Gravidade do tema:</strong><br>
            A análise de publicidade de bets exige cuidado porque envolve consumo,
            comportamento de risco, influência midiática, responsabilidade social
            e potenciais impactos sobre públicos vulneráveis.
        </div>
        """,
        unsafe_allow_html=True
    )