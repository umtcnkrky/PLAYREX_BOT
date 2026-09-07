
import json
import re
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# ============================================================
# PLAYREX SHORTS - AI METADATA GENERATOR
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
SRT_DIR = BASE_DIR / "subtitles"
OUT_DIR = BASE_DIR / "metadata"

OUT_DIR.mkdir(exist_ok=True)

# .env yükle
load_dotenv(BASE_DIR / ".env")

# OpenAI istemcisi
client = OpenAI()

MODEL = "gpt-5.6-luna"


def read_srt(path):
    """SRT dosyasını okuyup sadece konuşma metnini çıkarır."""

    text = path.read_text(encoding="utf-8")

    # SRT numaralarını ve zaman kodlarını temizle
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(
        r"\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}",
        "",
        text,
    )

    # Fazla boşlukları temizle
    lines = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        lines.append(line)

    return " ".join(lines)


def generate_metadata(transcript, filename):
    """AI ile Shorts metadata üretir."""

    prompt = f"""
Sen PlayRex adlı bir YouTube Gaming Shorts kanalının içerik üreticisisin.

Aşağıdaki metin Battlefield 6 PS5 gameplay Shorts videosunun konuşma
altyazısıdır.

SADECE verilen metne dayan.
Metinde olmayan olayları, skorları, kill sayılarını veya detayları UYDURMA.

Amaç:
YouTube Shorts için yüksek tıklanma potansiyeline sahip ama doğal
ve spam olmayan metadata üretmek.

Şunları oluştur:

1. title
- Türkçe
- Maksimum 90 karakter
- Merak uyandırıcı
- Clickbait olabilir ama videoda gerçekten olmayan bir şeyi iddia etme
- Gereksiz şekilde "OMG", "VIRAL" gibi kelimeler kullanma

2. description
- 2-3 kısa cümle
- Videonun gerçek içeriğini anlat
- Sonuna doğal şekilde birkaç hashtag eklenebilir

3. hashtags
- 5 ila 8 hashtag
- Örneğin #Battlefield6 #BF6 #PS5 #Gaming #Shorts
- Videoya uygun olmayan hashtag kullanma

4. hook
- Videonun ilk saniyelerinde kullanılabilecek çok kısa Türkçe cümle
- Maksimum 10 kelime
- Merak uyandırsın

5. category
- "gameplay"
- "action"
- "funny"
- "reaction"
- "combat"
seçeneklerinden en uygun olanı seç.

SADECE aşağıdaki JSON formatında cevap ver:

{{
  "title": "...",
  "description": "...",
  "hashtags": ["...", "..."],
  "hook": "...",
  "category": "..."
}}

ALTYAZI METNİ:
{transcript}
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    result = response.output_text.strip()

    # Markdown JSON bloğu geldiyse temizle
    result = re.sub(r"^```json\s*", "", result)
    result = re.sub(r"\s*```$", "", result)

    return json.loads(result)


def main():

    print("=" * 60)
    print("PLAYREX AI SHORTS - METADATA GENERATOR")
    print("=" * 60)

    srt_files = sorted(
        SRT_DIR.glob("short_*.srt"),
        key=lambda p: int(re.search(r"(\d+)", p.stem).group(1))
    )

    # SADECE 01-08
    srt_files = [
        p for p in srt_files
        if 1 <= int(re.search(r"(\d+)", p.stem).group(1)) <= 8
    ]

    if not srt_files:
        print("HATA: subtitles klasöründe SRT bulunamadı.")
        return

    all_metadata = {}

    for index, srt_path in enumerate(srt_files, start=1):

        print()
        print(f"[{index}/{len(srt_files)}] {srt_path.name}")

        try:

            transcript = read_srt(srt_path)

            if not transcript:
                print("  HATA: Altyazı metni boş.")
                continue

            print("  AI metadata oluşturuyor...")

            metadata = generate_metadata(
                transcript,
                srt_path.name
            )

            output_path = OUT_DIR / f"{srt_path.stem}.json"

            output_path.write_text(
                json.dumps(
                    metadata,
                    ensure_ascii=False,
                    indent=2
                ),
                encoding="utf-8"
            )

            all_metadata[srt_path.stem] = metadata

            print(f"  ✓ {output_path.name}")
            print(f"  Başlık: {metadata.get('title', '')}")
            print(f"  Kategori: {metadata.get('category', '')}")

        except Exception as e:

            print(f"  ✗ HATA: {e}")

    # Hepsini tek dosyada da sakla
    all_path = OUT_DIR / "all_metadata.json"

    all_path.write_text(
        json.dumps(
            all_metadata,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print("=" * 60)
    print("METADATA ÜRETİMİ TAMAMLANDI")
    print("=" * 60)
    print(f"Toplam başarılı: {len(all_metadata)}/{len(srt_files)}")
    print(f"Klasör: {OUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()

