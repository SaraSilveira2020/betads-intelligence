from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime
from pathlib import Path
import json

VIDEO_ID = "u9Z0OGvYp_o"

def buscar_transcricao(video_id: str):
    ytt_api = YouTubeTranscriptApi()

    transcript = ytt_api.fetch(
        video_id,
        languages=["pt", "pt-BR", "en"]
    )

    return transcript.to_raw_data()

def salvar_bronze(video_id: str, transcript):
    data_hoje = datetime.now().strftime("%Y-%m-%d")

    output_dir = Path(f"datalake/bronze/dominio=marketing_digital/dt={data_hoje}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{video_id}.json"

    payload = {
        "video_id": video_id,
        "dominio": "marketing_digital",
        "fonte": "youtube",
        "coletado_em": datetime.now().isoformat(),
        "transcript": transcript
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Arquivo salvo em: {output_file}")

if __name__ == "__main__":
    transcricao = buscar_transcricao(VIDEO_ID)
    salvar_bronze(VIDEO_ID, transcricao)