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
    print(">>>", " ".join(str(x) for x in command))
    print()

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
# TRANSCRIPT SATIRLARINI OKU
# ============================================================

def read_transcript():

    if not TRANSCRIPT.exists():
        return []

    lines = TRANSCRIPT.read_text(
        encoding="utf-8"
    ).splitlines()

    items = []

    for line in lines:

        match = re.match(
            r"\[(\d+(?:\.\d+)?)\s*-->\s*(\d+(?:\.\d+)?)\]\s*(.*)",
            line
        )

        if not match:
            continue

        start = float(match.group(1))
        end = float(match.group(2))
        text = match.group(3).strip()

        if not text:
            continue

        items.append({
            "start": start,
            "end": end,
            "text": text
        })

    return items


# ============================================================
# SANIYE → ASS ZAMAN FORMATINA ÇEVİR
# ============================================================

def ass_time(seconds):

    seconds = max(0, float(seconds))

    hours = int(seconds // 3600)

    minutes = int(
        (seconds % 3600) // 60
    )

    secs = int(
        seconds % 60
    )

    centiseconds = int(
        round((seconds - int(seconds)) * 100)
    )

    if centiseconds >= 100:
        centiseconds = 0
        secs += 1

    if secs >= 60:
        secs = 0
        minutes += 1

    if minutes >= 60:
        minutes = 0
        hours += 1

    return (
        f"{hours}:"
        f"{minutes:02d}:"
        f"{secs:02d}."
        f"{centiseconds:02d}"
    )


# ============================================================
# ASS ALTYAZI OLUŞTUR
# ============================================================

def create_ass(index, candidate, transcript_items):

    clip_start = candidate["start"]
    clip_end = candidate["end"]

    ass_path = OUTPUT_DIR / f"short_{index:02d}.ass"

    events = []

    for item in transcript_items:

        # Kliple kesişiyor mu?
        if item["end"] <= clip_start:
            continue

        if item["start"] >= clip_end:
            continue

        local_start = max(
            0,
            item["start"] - clip_start
        )

        local_end = min(
            clip_end - clip_start,
            item["end"] - clip_start
        )

        if local_end <= local_start:
            continue

        text = item["text"]

        # ASS özel karakterlerini temizle
        text = (
            text
            .replace("\\", "")
            .replace("{", "(")
            .replace("}", ")")
        )

        events.append(
            f"Dialogue: 0,"
            f"{ass_time(local_start)},"
            f"{ass_time(local_end)},"
            f"Shorts,,0,0,0,,"
            f"{text}"
        )

    ass_content = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Shorts,Arial,72,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5,2,2,80,80,220,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    if events:

        ass_content += "\n".join(events)
        ass_content += "\n"

    ass_path.write_text(
        ass_content,
        encoding="utf-8-sig"
    )

    print(
        f"✓ Altyazı oluşturuldu: "
        f"{ass_path.name} "
        f"({len(events)} satır)"
    )

    return ass_path


# ============================================================
# RAW SHORT OLUŞTUR
# ============================================================

def create_raw_clip(index, candidate):

    start = candidate["start"]
    end = candidate["end"]

    duration = end - start

    output = OUTPUT_DIR / (
        f"short_{index:02d}_raw.mp4"
    )

    print()
    print(
        f"RAW SHORT {index:02d}"
    )

    print(
        f"START : {start:.2f}"
    )

    print(
        f"END   : {end:.2f}"
    )

    print(
        f"SÜRE  : {duration:.2f}s"
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
# FINAL SHORT OLUŞTUR
# ============================================================

def create_final_clip(
    index,
    raw_file,
    ass_file
):

    output = OUTPUT_DIR / (
        f"short_{index:02d}_final.mp4"
    )

    print()
    print(
        f"FINAL ENCODE {index:02d}"
    )

    ass_path = ass_file.resolve()

    # Windows yolu FFmpeg için güvenli hale getir
    ass_filter_path = (
        str(ass_path)
        .replace("\\", "/")
        .replace(":", "\\:")
    )

    run_command([
        "ffmpeg",
        "-y",

        "-i",
        str(raw_file),

        "-vf",
        f"ass='{ass_filter_path}'",

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
# TEKNİK KONTROL
# ============================================================

def check_video(file):

    print()
    print(
        f"Kontrol ediliyor: {file.name}"
    )

    run_command([
        "ffprobe",
        "-v",
        "error",

        "-show_entries",
        "format=duration,size",

        "-show_entries",
        "stream=codec_name,width,height,r_frame_rate",

        "-of",
        "default=noprint_wrappers=1",

        str(file)
    ])


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

    # 1 — Transcript
    transcribe()

    # 2 — Adayları bul
    find_candidates()

    # 3 — Adayları oku
    candidates = read_candidates()

    if not candidates:

        print()
        print("Hiç Shorts adayı bulunamadı.")
        return

    print()
    print("=" * 70)
    print(
        f"{len(candidates)} ADET ADAY BULUNDU"
    )
    print("=" * 70)

    # En iyi 4 aday
    selected = candidates[:4]

    # Transcript
    transcript_items = read_transcript()

    print()
    print(
        f"Transcript satırı: "
        f"{len(transcript_items)}"
    )

    # ========================================================
    # SHORTS ÜRET
    # ========================================================

    for index, candidate in enumerate(
        selected,
        start=1
    ):

        print()
        print("=" * 70)

        print(
            f"SHORT {index:02d}"
        )

        print(
            f"PUAN={candidate['score']} | "
            f"{candidate['start']:.2f} → "
            f"{candidate['end']:.2f}"
        )

        print("=" * 70)

        # RAW
        raw_file = create_raw_clip(
            index,
            candidate
        )

        # ASS
        ass_file = create_ass(
            index,
            candidate,
            transcript_items
        )

        # FINAL
        final_file = create_final_clip(
            index,
            raw_file,
            ass_file
        )

        # Kontrol
        check_video(final_file)

    # ========================================================
    # SONUÇ
    # ========================================================

    print()
    print("=" * 70)
    print("PIPELINE TAMAMLANDI")
    print("=" * 70)

    print()
    print("FINAL SHORTS:")
    print()

    for file in sorted(
        OUTPUT_DIR.glob(
            "short_*_final.mp4"
        )
    ):

        print(
            f"✓ {file.name}"
        )

    print()
    print(
        "Tüm final Shorts dosyaları "
        "shorts klasöründe."
    )


if __name__ == "__main__":
    main()