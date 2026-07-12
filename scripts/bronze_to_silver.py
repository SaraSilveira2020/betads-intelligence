from pathlib import Path
from datetime import datetime
import json
import re
import unicodedata
import pandas as pd


BRONZE_DIR = Path("datalake/bronze/dominio=marketing_digital")
SILVER_DIR = Path("datalake/silver/dominio=marketing_digital")


TERMOS_BETS = [
    "bet",
    "bets",
    "aposta",
    "apostas",
    "apostar",
    "odds",
    "bonus",
    "bônus",
    "cassino",
    "jogo responsavel",
    "jogo responsável",
    "publicidade",
    "patrocinio",
    "patrocínio",
    "patrocinador",
    "promocao",
    "promoção",
    "cupom",
    "codigo promocional",
    "código promocional",
    "regulacao",
    "regulação",
    "regulamentacao",
    "regulamentação",
    "tabata",
    "casimiro",
    "cazetv",
    "cazé tv",
]


MARCAS_BETS = [
    "betano",
    "superbet",
    "bet365",
    "kto",
    "estrelabet",
    "betnacional",
    "novibet",
]


def normalizar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def contar_mencoes(texto_normalizado: str, termos: list[str]) -> int:
    total = 0

    for termo in termos:
        termo_normalizado = normalizar_texto(termo)
        padrao = rf"\b{re.escape(termo_normalizado)}\b"
        total += len(re.findall(padrao, texto_normalizado))

    return total


def processar_arquivo_bronze(caminho_json: Path) -> dict:
    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    transcript = dados.get("transcript", [])

    texto_transcricao = " ".join(
        item.get("text", "") for item in transcript if item.get("text")
    )

    texto_normalizado = normalizar_texto(texto_transcricao)

    total_palavras = len(texto_normalizado.split()) if texto_normalizado else 0
    mencoes_termos_bets = contar_mencoes(texto_normalizado, TERMOS_BETS)
    mencoes_marcas_bets = contar_mencoes(texto_normalizado, MARCAS_BETS)

    total_mencoes_bets = mencoes_termos_bets + mencoes_marcas_bets

    indice_exposicao_bets = (
        total_mencoes_bets / total_palavras * 1000
        if total_palavras > 0
        else 0
    )

    return {
        "video_id": dados.get("video_id"),
        "dominio": dados.get("dominio"),
        "fonte": dados.get("fonte"),
        "arquivo_origem": str(caminho_json),
        "data_processamento": datetime.now().isoformat(),
        "total_palavras": total_palavras,
        "mencoes_termos_bets": mencoes_termos_bets,
        "mencoes_marcas_bets": mencoes_marcas_bets,
        "total_mencoes_bets": total_mencoes_bets,
        "indice_exposicao_bets": round(indice_exposicao_bets, 4),
        "texto_transcricao": texto_transcricao,
    }


def main():
    arquivos_json = list(BRONZE_DIR.glob("dt=*/*.json"))

    if not arquivos_json:
        print("Nenhum arquivo encontrado na camada Bronze.")
        return

    registros = []

    for arquivo in arquivos_json:
        print(f"Processando: {arquivo}")
        registro = processar_arquivo_bronze(arquivo)
        registros.append(registro)

    df = pd.DataFrame(registros)

    data_hoje = datetime.now().strftime("%Y-%m-%d")
    output_dir = SILVER_DIR / f"dt={data_hoje}"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "videos_transcricoes.csv"

    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"Silver gerado com sucesso em: {output_file}")
    print(df[[
        "video_id",
        "total_palavras",
        "total_mencoes_bets",
        "indice_exposicao_bets"
    ]])


if __name__ == "__main__":
    main()