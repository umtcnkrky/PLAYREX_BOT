from faster_whisper import WhisperModel

print("Whisper modeli yukleniyor...")

model = WhisperModel("small", device="cpu", compute_type="int8")

print("Transkripsiyon basliyor...")

segments, info = model.transcribe(
    "test_audio_loud.wav",
    language="en",
    vad_filter=True
)

with open("test_transcript.txt", "w", encoding="utf-8") as f:
    for segment in segments:
        f.write(f"[{segment.start:.2f} --> {segment.end:.2f}] {segment.text.strip()}\n")

print("BITTI! test_transcript.txt olusturuldu.")

