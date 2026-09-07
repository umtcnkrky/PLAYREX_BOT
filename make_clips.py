
import re
import subprocess
import shutil
from pathlib import Path

VIDEO = Path("BF6_LIVE_PS5.mp4")
CANDIDATES = Path("clip_candidates.txt")
OUT_DIR = Path("shorts")

# --------------------------------------------------
# KONTROLLER
# --------------------------------------------------

if not VIDEO.exists():
    print("❌ VIDEO BULUNAMADI:")
    print(VIDEO.resolve())
    raise SystemExit(1)

if not CANDIDATES.exists():
    print("❌ clip_candidates.txt BULUNAMADI")
    raise SystemExit(1)

if shutil.which("ffmpeg") is None:
    print("❌ FFmpeg PATH üzerinde bulunamadı.")
    raise SystemExit(1)

OUT_DIR.mkdir(exist_ok=True)

# --------------------------------------------------
# CLIP SATIRLARINI OKU
# Örnek:
# CLIP : 2806.43 -> 2838.68
# --------------------------------------------------

text = CANDIDATES.read_text(encoding="utf-8")

pattern = re.compile(
    r"CLIP\s*:\s*"
    r"(\d+(?:\.\d+)?)"
    r"\s*->\s*"
    r"(\d+(?:\.\d+)?)"
)

matches = pattern.findall(text)

if not matches:
    print("❌ clip_candidates.txt içinde CLIP bulunamadı.")
    raise SystemExit(1)

print()
print("=" * 60)
print("🎬 PLAYREX SHORTS - KLİP OLUŞTURMA")
print("=" * 60)
print(f"Kaynak video : {VIDEO.name}")
print(f"Aday sayısı  : {len(matches)}")
print()

# --------------------------------------------------
# KLİPLERİ OLUŞTUR
# --------------------------------------------------

created = 0

for index, (start, end) in enumerate(matches, start=1):

    start_float = float(start)
    end_float = float(end)
    duration = end_float - start_float

    output = OUT_DIR / f"candidate_{index:02d}.mp4"

    print("-" * 60)
    print(f"🎯 ADAY {index}")
    print(f"   Başlangıç : {start_float:.2f}s")
    print(f"   Bitiş     : {end_float:.2f}s")
    print(f"   Süre      : {duration:.2f}s")
    print(f"   Çıkış     : {output}")

    command = [
        "ffmpeg",
        "-y",

        # Hızlı seek
        "-ss",
        str(start_float),

        "-i",
        str(VIDEO),

        # Süre
        "-t",
        str(duration),

        # Video + ses
        "-map",
        "0:v:0",
        "-map",
        "0:a?",

        # Yeniden encode ETME
        "-c",
        "copy",

        # MP4 zaman damgası düzeltmesi
        "-avoid_negative_ts",
        "make_zero",

        str(output)
    ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        if result.returncode == 0 and output.exists():

            size_mb = output.stat().st_size / (1024 * 1024)

            print(f"   ✅ OLUŞTU")
            print(f"   📦 Boyut: {size_mb:.2f} MB")

            created += 1

        else:

            print("   ❌ FFmpeg HATASI")
            print(result.stderr[-1500:])

    except Exception as e:

        print("   ❌ Python hatası:")
        print(e)


# --------------------------------------------------
# SONUÇ
# --------------------------------------------------

print()
print("=" * 60)
print("🏁 KLİP OLUŞTURMA TAMAMLANDI")
print("=" * 60)

print(f"Toplam aday : {len(matches)}")
print(f"Oluşan klip : {created}")
print(f"Klasör      : {OUT_DIR.resolve()}")

if created == len(matches):
    print()
    print("🔥 TÜM ADAYLAR BAŞARIYLA OLUŞTURULDU!")
else:
    print()
    print("⚠️ Bazı adaylarda hata oluştu. Yukarıdaki FFmpeg çıktısını kontrol et.")

print()

