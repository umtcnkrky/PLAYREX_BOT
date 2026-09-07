from faster_whisper import WhisperModel

print("Candidate Whisper analizi basliyor...")

model = WhisperModel("small", device="cpu", compute_type="int8")

segments, info = model.transcribe(
    r"candidates\candidate_01_audio.wav",
    language="en",
    vad_filter=True,
    beam_size=5
)

with open(r"candidates\candidate_01_transcript.txt", "w", encoding="utf-8") as f:
    for segment in segments:
        text = segment.text.strip()
        if text:
            f.write(f"[{segment.start:.2f} --> {segment.end:.2f}] {text}\n")

print("BITTI!")
print("candidates\\candidate_01_transcript.txt olusturuldu.")
