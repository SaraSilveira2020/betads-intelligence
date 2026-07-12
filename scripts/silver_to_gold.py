from pathlib import Path
from datetime import datetime
import pandas as pd


SILVER_DIR = Path("datalake/silver/dominio=marketing_digital")
GOLD_DIR = Path("datalake/gold/dominio=marketing_digital")


def carregar_silver() -> pd.DataFrame:
    arquivos = list(SILVER_DIR.glob("dt=*/videos_transcricoes.csv"))

    if not arquivos:
        raise FileNotFoundError("Nenhum arquivo Silver encontrado.")

    dfs = []

    for arquivo in arquivos:
        print(f"Lendo Silver: {arquivo}")
        df = pd.read_csv(arquivo)
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


def gerar_gold(df: pd.DataFrame):
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    ranking = df[
        [
            "video_id",
            "total_palavras",
            "mencoes_termos_bets",
            "mencoes_marcas_bets",
            "total_mencoes_bets",
            "indice_exposicao_bets",
            "data_processamento",
            "arquivo_origem",
        ]
    ].sort_values(
        by="indice_exposicao_bets",
        ascending=False
    )

    ranking_file = GOLD_DIR / "ranking_exposicao_bets_por_video.csv"
    ranking.to_csv(ranking_file, index=False, encoding="utf-8-sig")

    resumo = pd.DataFrame([
        {
            "data_atualizacao": datetime.now().isoformat(),
            "total_videos_processados": len(df),
            "total_palavras_analisadas": int(df["total_palavras"].sum()),
            "total_mencoes_bets": int(df["total_mencoes_bets"].sum()),
            "media_indice_exposicao_bets": round(df["indice_exposicao_bets"].mean(), 4),
            "maior_indice_exposicao_bets": round(df["indice_exposicao_bets"].max(), 4),
            "video_maior_exposicao": df.loc[
                df["indice_exposicao_bets"].idxmax(),
                "video_id"
            ],
        }
    ])

    resumo_file = GOLD_DIR / "resumo_exposicao_bets.csv"
    resumo.to_csv(resumo_file, index=False, encoding="utf-8-sig")

    print(f"Gold ranking gerado em: {ranking_file}")
    print(f"Gold resumo gerado em: {resumo_file}")
    print(resumo)


def main():
    df = carregar_silver()
    gerar_gold(df)


if __name__ == "__main__":
    main()
    