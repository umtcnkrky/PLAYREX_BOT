from faster_whisper import WhisperModel

print("Whisper modeli yukleniyor...")

model = WhisperModel("small", device="cpu", compute_type="int8")

print("TUM VIDEO TRANSKRIPSIYONU BASLIYOR...")
print("Bu islem biraz surebilir. PowerShell'i kapatma.")

segments, info = model.transcribe(
    "BF6_audio_norm.wav",
    language="en",
    vad_filter=True,
    beam_size=5
)

with open("BF6_transcript.txt", "w", encoding="utf-8") as f:
    for segment in segments:
        text = segment.text.strip()
        if text:
            f.write(f"[{segment.start:.2f} --> {segment.end:.2f}] {text}\n")

print("")
print("========================================")
print("TRANSKRIPSIYON TAMAMLANDI!")
print("BF6_transcript.txt olusturuldu.")
print("========================================")
