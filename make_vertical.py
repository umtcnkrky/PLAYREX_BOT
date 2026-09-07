
import subprocess
import shutil
from pathlib import Path

# --------------------------------------------------
# AYARLAR
# --------------------------------------------------

INPUT_DIR = Path("shorts")
OUTPUT_DIR = Path("shorts_vertical")

WIDTH = 1080
HEIGHT = 1920

OUTPUT_DIR.mkdir(exist_ok=True)

# --------------------------------------------------
# KONTROL
# --------------------------------------------------

if shutil.which("ffmpeg") is None:
    print("❌ FFmpeg bulunamadı.")
    raise SystemExit(1)

clips = sorted(INPUT_DIR.glob("candidate_*.mp4"))

if not clips:
    print("❌ shorts klasöründe candidate_*.mp4 bulunamadı.")
    raise SystemExit(1)

print()
print("=" * 65)
print("📱 PLAYREX - 9:16 SHORTS DÖNÜŞTÜRÜCÜ")
print("=" * 65)
print(f"Girdi sayısı : {len(clips)}")
print(f"Çözünürlük   : {WIDTH}x{HEIGHT}")
print(f"Çıkış klasörü: {OUTPUT_DIR}")
print()

# --------------------------------------------------
# KLİPLERİ DÖNÜŞTÜR
# --------------------------------------------------

success = 0

for index, input_file in enumerate(clips, start=1):

    output_file = OUTPUT_DIR / f"short_{index:02d}.mp4"

    print("-" * 65)
    print(f"🎬 {index}/{len(clips)}")
    print(f"   Girdi : {input_file}")
    print(f"   Çıktı : {output_file}")

    # --------------------------------------------------
    # FILTER
    #
    # Arka plan:
    #   Videoyu 1080x1920'ye büyüt
    #   Crop
    #   Hafif blur
    #
    # Ön plan:
    #   Videoyu 1080 genişliğe ölçekle
    #   Oran korunur
    #   Dikey videonun ortasına yerleştir
    #
    # Böylece 16:9 gameplay KESİLMEZ.
    # --------------------------------------------------

    filter_complex = (
        "[0:v]"
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "boxblur=20:10,"
        "setsar=1"
        "[bg];"

        "[0:v]"
        "scale=1080:-2,"
        "setsar=1"
        "[fg];"

        "[bg][fg]"
        "overlay=(W-w)/2:(H-h)/2"
        "[v]"
    )

    command = [
        "ffmpeg",
        "-y",

        "-i",
        str(input_file),

        "-filter_complex",
        filter_complex,

        "-map",
        "[v]",
        "-map",
        "0:a?",

        # CPU dostu H.264
        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        # Kalite
        "-crf",
        "20",

        # Ses
        "-c:a",
        "aac",
        "-b:a",
        "128k",

        # YouTube uyumluluğu
        "-pix_fmt",
        "yuv420p",

        "-movflags",
        "+faststart",

        str(output_file)
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

        if result.returncode == 0 and output_file.exists():

            size_mb = output_file.stat().st_size / (1024 * 1024)

            print(f"   ✅ BAŞARILI")
            print(f"   📦 Boyut: {size_mb:.2f} MB")

            success += 1

        else:

            print("   ❌ FFmpeg HATASI")
            print()
            print(result.stderr[-2000:])

    except Exception as e:

        print("   ❌ Python hatası:")
        print(e)


# --------------------------------------------------
# SONUÇ
# --------------------------------------------------

print()
print("=" * 65)
print("🏁 9:16 DÖNÜŞÜM TAMAMLANDI")
print("=" * 65)

print(f"Toplam klip : {len(clips)}")
print(f"Başarılı    : {success}")
print(f"Başarısız   : {len(clips) - success}")
print(f"Çıkış       : {OUTPUT_DIR.resolve()}")

if success == len(clips):
    print()
    print("🔥🔥🔥 TÜM VİDEOLAR 9:16 SHORTS FORMATINA HAZIR!")
else:
    print()
    print("⚠️ Bazı videolar oluşturulamadı.")

print()

