
import whisper
from pathlib import Path
import sys

# --------------------------------------------------
# AYARLAR
# --------------------------------------------------

AUDIO_DIR = Path("subtitle_audio")
SUBTITLE_DIR = Path("subtitles")

# Ryzen 3 3200U için hafif model
MODEL_NAME = "base"

SUBTITLE_DIR.mkdir(exist_ok=True)

# Sadece yeni 8 Shorts
audio_files = [
    AUDIO_DIR / f"short_{i:02d}.wav"
    for i in range(1, 9)
]

existing = [f for f in audio_files if f.exists()]

if not existing:
    print("❌ Ses dosyaları bulunamadı.")
    raise SystemExit(1)

# --------------------------------------------------
# WHISPER
# --------------------------------------------------

print()
print("=" * 65)
print("🎤 PLAYREX - WHISPER ALTYAZI SİSTEMİ")
print("=" * 65)
print(f"Model        : {MODEL_NAME}")
print(f"İşlenecek ses: {len(existing)}")
print()

print("🧠 Whisper modeli yükleniyor...")
print("⏳ İlk çalıştırmada model indirilebilir.")
print()

try:
    model = whisper.load_model(MODEL_NAME)
except Exception as e:
    print("❌ Whisper modeli yüklenemedi:")
    print(e)
    raise SystemExit(1)

print("✅ Whisper modeli hazır!")
print()

# --------------------------------------------------
# SRT ZAMAN FORMATI
# --------------------------------------------------

def format_timestamp(seconds):
    """
    Whisper saniyesini SRT formatına çevirir.
    Örnek:
    12.345 -> 00:00:12,345
    """

    milliseconds = int(round(seconds * 1000))

    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000

    minutes = milliseconds // 60_000
    milliseconds %= 60_000

    seconds = milliseconds // 1000
    milliseconds %= 1000

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


# --------------------------------------------------
# SRT OLUŞTUR
# --------------------------------------------------

success = 0

for index, audio_file in enumerate(existing, start=1):

    subtitle_file = SUBTITLE_DIR / f"short_{index:02d}.srt"

    print("-" * 65)
    print(f"🎬 {index}/{len(existing)}")
    print(f"Ses      : {audio_file}")
    print(f"Altyazı  : {subtitle_file}")
    print()

    try:

        print("   🧠 Konuşma analiz ediliyor...")

        result = model.transcribe(
            str(audio_file),

            # Türkçe
            language="tr",

            # CPU
            fp16=False,

            # Daha doğal segmentler
            condition_on_previous_text=True,

            # Sessiz bölümlerde gereksiz metni azalt
            no_speech_threshold=0.6
        )

        segments = result.get("segments", [])

        if not segments:
            print("   ⚠️ Konuşma bulunamadı.")
            continue

        # --------------------------------------------------
        # SRT YAZ
        # --------------------------------------------------

        with open(
            subtitle_file,
            "w",
            encoding="utf-8"
        ) as f:

            subtitle_index = 1

            for segment in segments:

                start = segment["start"]
                end = segment["end"]
                text = segment["text"].strip()

                if not text:
                    continue

                f.write(f"{subtitle_index}\n")
                f.write(
                    f"{format_timestamp(start)} --> "
                    f"{format_timestamp(end)}\n"
                )
                f.write(f"{text}\n")
                f.write("\n")

                subtitle_index += 1

        size_kb = subtitle_file.stat().st_size / 1024

        print(f"   ✅ ALTYAZI OLUŞTU")
        print(f"   📝 Segment : {len(segments)}")
        print(f"   📦 Boyut   : {size_kb:.1f} KB")

        success += 1

    except KeyboardInterrupt:

        print()
        print("🛑 İşlem kullanıcı tarafından durduruldu.")
        sys.exit(0)

    except Exception as e:

        print("   ❌ HATA:")
        print(e)


# --------------------------------------------------
# SONUÇ
# --------------------------------------------------

print()
print("=" * 65)
print("🏁 WHISPER ALTYAZI İŞLEMİ TAMAMLANDI")
print("=" * 65)

print(f"Toplam ses : {len(existing)}")
print(f"Başarılı   : {success}")
print(f"Başarısız  : {len(existing) - success}")
print(f"Çıkış      : {SUBTITLE_DIR.resolve()}")

if success == len(existing):

    print()
    print("🔥🔥🔥 TÜM 8 SHORTS İÇİN ALTYAZI HAZIR!")

else:

    print()
    print("⚠️ Bazı videolarda altyazı oluşturulamadı.")

print()

