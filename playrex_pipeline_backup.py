import subprocess
from pathlib import Path
import re


# ============================================================
# PLAYREX AI SHORTS PIPELINE
# ============================================================

BASE = Path(__file__).resolve().parent

VIDEO = BASE / "BF6_LIVE_PS5.mp4"
TRANSCRIPT = BASE / "BF6_transcript.txt"
CANDIDATES = BASE / "clip_candidates.txt"

OUTPUT_DIR = BASE / "shorts"

OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# KOMUT ÇALIŞTIR
# ============================================================

def run_command(command):

    print()
    print("=" * 70)
    print("ÇALIŞTIRILIYOR:")
    print(" ".join(str(x) for x in command))
    print("=" * 70)

    result = subprocess.run(command)

    if result.returncode != 0:
        raise RuntimeError(
            f"Komut başarısız oldu. Kod: {result.returncode}"
        )


# ============================================================
# TRANSKRİPSİYON
# ============================================================

def transcribe():

    if TRANSCRIPT.exists():
        print()
        print("✓ BF6_transcript.txt zaten mevcut.")
        print("  Yeniden Whisper çalıştırılmayacak.")
        return

    print()
    print("Whisper transkripsiyonu başlatılıyor...")

    run_command([
        "py",
        str(BASE / "transcribe_full.py")
    ])


# ============================================================
# SHORTS ADAYLARINI BUL
# ============================================================

def find_candidates():

    print()
    print("Shorts aday analizi başlatılıyor...")

    run_command([
        "py",
        str(BASE / "find_clips.py")
    ])


# ============================================================
# ADAYLARI OKU
# ============================================================

def read_candidates():

    if not CANDIDATES.exists():
        raise FileNotFoundError(
            "clip_candidates.txt bulunamadı."
        )

    text = CANDIDATES.read_text(
        encoding="utf-8"
    )

    blocks = re.split(
        r"\n-{10,}\n",
        text
    )

    candidates = []

    for block in blocks:

        start_match = re.search(
            r"START\s*:\s*([0-9.]+)",
            block
        )

        end_match = re.search(
            r"END\s*:\s*([0-9.]+)",
            block
        )

        score_match = re.search(
            r"PUAN\s*:\s*(-?[0-9]+)",
            block
        )

        text_match = re.search(
            r"TEXT\s*:\s*(.*)",
            block
        )

        if not start_match or not end_match:
            continue

        start = float(start_match.group(1))
        end = float(end_match.group(1))

        score = 0

        if score_match:
            score = int(score_match.group(1))

        speech = ""

        if text_match:
            speech = text_match.group(1).strip()

        candidates.append({
            "start": start,
            "end": end,
            "score": score,
            "text": speech
        })

    return candidates


# ============================================================
# HAM SHORT OLUŞTUR
# ============================================================

def create_raw_clip(index, candidate):

    start = candidate["start"]
    end = candidate["end"]

    duration = end - start

    output = OUTPUT_DIR / f"short_{index:02d}_raw.mp4"

    print()
    print(
        f"Short {index:02d}: "
        f"{start:.2f} → {end:.2f} "
        f"({duration:.2f}s)"
    )

    run_command([
        "ffmpeg",
        "-y",
        "-ss",
        str(start),
        "-i",
        str(VIDEO),
        "-t",
        str(duration),

        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "18",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        str(output)
    ])

    return output


# ============================================================
# ANA PROGRAM
# ============================================================

def main():

    print()
    print("=" * 70)
    print("          PLAYREX AI SHORTS PIPELINE")
    print("=" * 70)

    if not VIDEO.exists():

        raise FileNotFoundError(
            f"Video bulunamadı:\n{VIDEO}"
        )

    # 1
    transcribe()

    # 2
    find_candidates()

    # 3
    candidates = read_candidates()

    if not candidates:

        print()
        print("Hiç Shorts adayı bulunamadı.")
        return

    print()
    print("=" * 70)
    print(f"{len(candidates)} ADET ADAY BULUNDU")
    print("=" * 70)

    # İlk 4 adayı işle
    selected = candidates[:4]

    for index, candidate in enumerate(
        selected,
        start=1
    ):

        print()
        print(
            f"[{index}] "
            f"PUAN={candidate['score']} "
            f"{candidate['start']:.2f} → "
            f"{candidate['end']:.2f}"
        )

        create_raw_clip(
            index,
            candidate
        )

    print()
    print("=" * 70)
    print("PIPELINE TAMAMLANDI")
    print("=" * 70)

    print()
    print("Oluşturulan dosyalar:")
    print()

    for file in sorted(
        OUTPUT_DIR.glob("short_*_raw.mp4")
    ):

        print(file.name)


if __name__ == "__main__":
    main()
    