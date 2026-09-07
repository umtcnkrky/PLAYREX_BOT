
import re
from pathlib import Path

# ============================================================
# PLAYREX PS5 SHORTS - FIND CLIPS V14.4
# ============================================================

TRANSCRIPT = Path("BF6_transcript.txt")
OUTPUT = Path("clip_candidates.txt")

# ============================================================
# AYARLAR
# ============================================================

MAX_START_GAP = 18.0
MAX_SEGMENT_DURATION = 20.0

MIN_EVENT_DURATION = 8.0

MIN_CLIP_DURATION = 15.0
MAX_CLIP_DURATION = 45.0

WINDOWS = [
    15.0,
    20.0,
    25.0,
    30.0,
    35.0,
    40.0,
    45.0,
]

MIN_SCORE = 35

# Aynı olayın tekrar seçilmesini engeller
MAX_OVERLAP_RATIO = 0.50

# Başlangıçları birbirine çok yakın adayları da engeller
MIN_CANDIDATE_DISTANCE = 15.0

# Aynı event içinden maksimum aday
MAX_CANDIDATES_PER_EVENT = 1

# Toplam maksimum aday
MAX_FINAL_CANDIDATES = 8


# ============================================================
# ACTION
# ============================================================

ACTION_WORDS = [
    "hit",
    "hitting",
    "shoot",
    "shooting",
    "shot",
    "attack",
    "attacking",
    "attacked",
    "kill",
    "kills",
    "killed",
    "fell",
    "fall",
    "falling",
    "destroy",
    "destroyed",
    "blow",
    "rocket",
    "gun",
    "enemy",
    "target",
    "pilot",
    "plane",
    "air",
    "battle",
    "fight",
    "chase",
    "follow",
    "fire",
    "turn",
    "run away",
]


# ============================================================
# GAME
# ============================================================

GAME_WORDS = [
    "game",
    "play",
    "playing",
    "plane",
    "pilot",
    "rocket",
    "gun",
    "enemy",
    "target",
    "air",
    "battle",
    "fight",
]


# ============================================================
# REACTION
# ============================================================

REACTION_PHRASES = [
    "wow",
    "awesome",
    "amazing",
    "crazy",
    "no way",
    "opa",
    "finally",
    "professional",
    "love this game",
    "what did you do",
    "what a turn",
    "how did you",
    "are you a pilot",
    "are you a real pilot",
]


# ============================================================
# KILL
# ============================================================

KILL_PHRASES = [
    "kill",
    "kills",
    "killed",
    "one down",
    "we fell one",
    "four kills",
    "we have four kills",
    "two of them are attacking me",
]


# ============================================================
# DÜŞÜK DEĞER
# ============================================================

LOW_VALUE_PHRASES = [
    "securing bravo",
    "securing alpha",
    "reloading",
    "cover me reloading",
    "come along reloading",
    "no one came to broadcast",
    "wife",
    "youtube",
    "camera",
    "settings",
    "subscribe",
    "channel",
    "good night",
    "continue",
    "microphone",
    "can you hear me",
    "turn off microphone",
]


# ============================================================
# OCR
# ============================================================

OCR_PHRASES = [
    "hand pink waving",
    "eyes pink heart shape",
    "face red heart shape",
    "trophy yellow smiling",
    "text yellow goal",
    "stop watch blue hand timer",
    "baseball white capout",
    "person blue speaking microphone",
    "face red smell",
]


# ============================================================
# DOSYA
# ============================================================

if not TRANSCRIPT.exists():

    print(
        "HATA: BF6_transcript.txt bulunamadı."
    )

    raise SystemExit


# ============================================================
# TRANSCRIPT
# ============================================================

text = TRANSCRIPT.read_text(
    encoding="utf-8",
    errors="ignore"
)


pattern = re.compile(
    r"\[\s*(\d+(?:\.\d+)?)\s*-->\s*(\d+(?:\.\d+)?)\s*\]\s*(.+)"
)


lines = []


for raw_line in text.splitlines():

    match = pattern.match(
        raw_line.strip()
    )

    if not match:
        continue

    start = float(match.group(1))
    end = float(match.group(2))

    content = match.group(3).strip()

    if not content:
        continue

    lower = content.lower()

    # OCR temizliği
    if any(
        phrase in lower
        for phrase in OCR_PHRASES
    ):
        continue

    # Bozuk uzun segmentleri sınırlıyoruz
    effective_end = min(
        end,
        start + MAX_SEGMENT_DURATION
    )

    lines.append({
        "start": start,
        "end": end,
        "effective_end": effective_end,
        "text": content,
    })


print(
    f"Toplam transcript satırı : {len(text.splitlines())}"
)

print(
    f"Temiz transcript satırı  : {len(lines)}"
)


# ============================================================
# YARDIMCI
# ============================================================

def count_word(text, word):

    regex = (
        r"\b"
        + re.escape(word)
        + r"\b"
    )

    return len(
        re.findall(
            regex,
            text,
            flags=re.IGNORECASE
        )
    )


def event_text(event):

    return " ".join(
        item["text"]
        for item in event
    )


def event_start(event):

    return event[0]["start"]


def event_end(event):

    return max(
        item["effective_end"]
        for item in event
    )


# ============================================================
# EVENT OLUŞTUR
# ============================================================

events = []

current = []

previous_start = None


for line in lines:

    start = line["start"]

    if previous_start is None:

        current = [line]
        previous_start = start

        continue

    start_gap = start - previous_start

    if start_gap > MAX_START_GAP:

        if current:
            events.append(current)

        current = [line]

    else:

        current.append(line)

    previous_start = start


if current:
    events.append(current)


# ============================================================
# EVENT FİLTRELE
# ============================================================

valid_events = []


for event in events:

    start = event_start(event)
    end = event_end(event)

    duration = end - start

    if duration < MIN_EVENT_DURATION:
        continue

    lower = event_text(event).lower()

    action = sum(
        count_word(lower, word)
        for word in ACTION_WORDS
    )

    game = sum(
        count_word(lower, word)
        for word in GAME_WORDS
    )

    low_value = sum(
        1
        for phrase in LOW_VALUE_PHRASES
        if phrase in lower
    )

    # Hiç gameplay belirtisi yok
    if action == 0 and game == 0:
        continue

    # Çok fazla yayın konuşması
    if low_value >= 3 and action <= 1:
        continue

    valid_events.append(event)


# ============================================================
# PENCERE SKORU
# ============================================================

def score_window(window):

    if not window:
        return None

    text_lower = event_text(window).lower()

    action = sum(
        count_word(text_lower, word)
        for word in ACTION_WORDS
    )

    game = sum(
        count_word(text_lower, word)
        for word in GAME_WORDS
    )

    reaction = sum(
        1
        for phrase in REACTION_PHRASES
        if phrase in text_lower
    )

    kills = sum(
        1
        for phrase in KILL_PHRASES
        if phrase in text_lower
    )

    low_value = sum(
        1
        for phrase in LOW_VALUE_PHRASES
        if phrase in text_lower
    )

    # --------------------------------------------------------
    # TEMEL SKOR
    # --------------------------------------------------------

    score = (
        action * 7
        + game * 3
        + reaction * 18
        + kills * 20
    )

    # Yayın konuşması cezası
    score -= low_value * 15

    # --------------------------------------------------------
    # AKSİYON YOĞUNLUĞU
    # --------------------------------------------------------

    start = min(
        x["start"]
        for x in window
    )

    end = max(
        x["effective_end"]
        for x in window
    )

    duration = max(
        1.0,
        end - start
    )

    activity = (
        action
        + game
        + reaction * 2
        + kills * 2
    )

    density = activity / duration

    if density >= 0.30:
        score += 30

    elif density >= 0.20:
        score += 20

    elif density >= 0.12:
        score += 10

    # --------------------------------------------------------
    # KILL BONUS
    # --------------------------------------------------------

    if kills >= 2:
        score += 20

    if kills >= 3:
        score += 35

    if kills >= 5:
        score += 40

    # --------------------------------------------------------
    # ACTION + REACTION
    # --------------------------------------------------------

    if action >= 3 and reaction >= 1:
        score += 20

    # --------------------------------------------------------
    # TAMAMEN DÜŞÜK DEĞER
    # --------------------------------------------------------

    if action == 0 and game == 0:
        score -= 50

    return {
        "score": score,
        "action": action,
        "game": game,
        "reaction": reaction,
        "kills": kills,
        "low_value": low_value,
    }


# ============================================================
# EVENT İÇİNDE PENCERE TARAMA
# ============================================================

all_candidates = []


for event_index, event in enumerate(
    valid_events,
    1
):

    start = event_start(event)
    end = event_end(event)

    event_candidates = []

    for window_size in WINDOWS:

        if end - start < window_size:
            continue

        # Transcript satırlarını merkez olarak kullan
        for center_line in event:

            center = center_line["start"]

            window_start = (
                center
                -
                window_size * 0.35
            )

            window_end = (
                window_start
                +
                window_size
            )

            # Event sınırları
            window_start = max(
                window_start,
                start
            )

            window_end = min(
                window_end,
                end
            )

            # ------------------------------------------------
            # PENCEREDEKİ SATIRLAR
            # ------------------------------------------------

            selected_lines = []

            for line in event:

                line_start = line["start"]
                line_end = line["effective_end"]

                if (
                    line_start < window_end
                    and
                    line_end > window_start
                ):

                    selected_lines.append(line)

            if not selected_lines:
                continue

            info = score_window(
                selected_lines
            )

            if info is None:
                continue

            if info["score"] < MIN_SCORE:
                continue

            # ------------------------------------------------
            # GERÇEK PENCERE
            # ------------------------------------------------

            clip_start = max(
                0,
                window_start
            )

            clip_end = window_end

            # ------------------------------------------------
            # 15 SANİYE GARANTİSİ
            # ------------------------------------------------

            duration = (
                clip_end
                -
                clip_start
            )

            if duration < MIN_CLIP_DURATION:

                clip_end = (
                    clip_start
                    +
                    MIN_CLIP_DURATION
                )

            # ------------------------------------------------
            # 45 SANİYE LİMİTİ
            # ------------------------------------------------

            if (
                clip_end
                -
                clip_start
            ) > MAX_CLIP_DURATION:

                clip_end = (
                    clip_start
                    +
                    MAX_CLIP_DURATION
                )

            event_candidates.append({
                "event_index": event_index,
                "start": clip_start,
                "end": clip_end,
                "duration": clip_end - clip_start,
                "event_start": start,
                "event_end": end,
                "lines": selected_lines,
                **info,
            })

    # ========================================================
    # BU EVENTİN EN İYİ ADAYINI SEÇ
    # ========================================================

    event_candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    if event_candidates:

        best = event_candidates[0]

        all_candidates.append(best)


# ============================================================
# GLOBAL SIRALAMA
# ============================================================

all_candidates.sort(
    key=lambda x: x["score"],
    reverse=True
)


# ============================================================
# ÇAKIŞMA TEMİZLİĞİ
# ============================================================

selected = []


for candidate in all_candidates:

    overlap_found = False

    for existing in selected:

        a1 = candidate["start"]
        a2 = candidate["end"]

        b1 = existing["start"]
        b2 = existing["end"]

        overlap_start = max(
            a1,
            b1
        )

        overlap_end = min(
            a2,
            b2
        )

        overlap = max(
            0,
            overlap_end
            -
            overlap_start
        )

        shortest = min(
            candidate["duration"],
            existing["duration"]
        )

        if shortest <= 0:
            continue

        overlap_ratio = (
            overlap
            /
            shortest
        )

        # Aynı klibin büyük kısmı ortak
        if overlap_ratio >= MAX_OVERLAP_RATIO:

            overlap_found = True
            break

        # Başlangıçlar çok yakın
        if abs(
            candidate["start"]
            -
            existing["start"]
        ) < MIN_CANDIDATE_DISTANCE:

            overlap_found = True
            break

    if overlap_found:
        continue

    selected.append(candidate)

    if len(selected) >= MAX_FINAL_CANDIDATES:
        break


# ============================================================
# SONUÇLARI SKORA GÖRE SIRALA
# ============================================================

selected.sort(
    key=lambda x: x["score"],
    reverse=True
)


# ============================================================
# DOSYA
# ============================================================

output = []

output.append(
    "PLAYREX SHORTS ADAY ANALİZİ V14.4"
)

output.append(
    "=" * 70
)

output.append(
    f"Toplam transcript satırı : "
    f"{len(text.splitlines())}"
)

output.append(
    f"Temiz transcript satırı  : "
    f"{len(lines)}"
)

output.append(
    f"Toplam event              : "
    f"{len(events)}"
)

output.append(
    f"Geçerli gameplay event   : "
    f"{len(valid_events)}"
)

output.append(
    f"Event bazlı aday          : "
    f"{len(all_candidates)}"
)

output.append(
    f"Final Shorts adayı        : "
    f"{len(selected)}"
)

output.append("")


# ============================================================
# ADAYLARI YAZ
# ============================================================

for index, candidate in enumerate(
    selected,
    1
):

    output.append(
        f"#{index}"
    )

    output.append(
        f"CLIP : "
        f"{candidate['start']:.2f} -> "
        f"{candidate['end']:.2f}"
    )

    output.append(
        f"DURATION : "
        f"{candidate['duration']:.1f}s"
    )

    output.append(
        f"SCORE : "
        f"{candidate['score']}"
    )

    output.append(
        f"ACTION : "
        f"{candidate['action']}"
    )

    output.append(
        f"GAME : "
        f"{candidate['game']}"
    )

    output.append(
        f"REACTION : "
        f"{candidate['reaction']}"
    )

    output.append(
        f"KILLS : "
        f"{candidate['kills']}"
    )

    output.append(
        f"LOW VALUE : "
        f"{candidate['low_value']}"
    )

    output.append(
        f"EVENT : "
        f"{candidate['event_start']:.2f} -> "
        f"{candidate['event_end']:.2f}"
    )

    output.append(
        "TEXT:"
    )

    for line in candidate["lines"]:

        output.append(
            f"[{line['start']:.2f} -> "
            f"{line['end']:.2f}] "
            f"{line['text']}"
        )

    output.append(
        "-" * 70
    )


OUTPUT.write_text(
    "\n".join(output),
    encoding="utf-8"
)


# ============================================================
# EKRAN
# ============================================================

print()
print(
    "======================================================"
)

print(
    " PLAYREX SHORTS ADAY ANALİZİ V14.4"
)

print(
    "======================================================"
)

print(
    f"Toplam transcript satırı : "
    f"{len(text.splitlines())}"
)

print(
    f"Temiz transcript satırı  : "
    f"{len(lines)}"
)

print(
    f"Toplam event              : "
    f"{len(events)}"
)

print(
    f"Geçerli gameplay event   : "
    f"{len(valid_events)}"
)

print(
    f"Event bazlı aday          : "
    f"{len(all_candidates)}"
)

print(
    f"Final Shorts adayı        : "
    f"{len(selected)}"
)

print()


for index, candidate in enumerate(
    selected,
    1
):

    print(
        f"#{index} "
        f"{candidate['start']:.2f} -> "
        f"{candidate['end']:.2f} "
        f"| {candidate['duration']:.1f}s "
        f"| SCORE {candidate['score']} "
        f"| action {candidate['action']} "
        f"| game {candidate['game']} "
        f"| reaction {candidate['reaction']} "
        f"| kills {candidate['kills']}"
    )


print()
print(
    "Sonuçlar clip_candidates.txt dosyasına yazıldı."
)
print()

