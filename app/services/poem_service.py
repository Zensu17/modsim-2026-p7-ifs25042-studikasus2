from app.extensions import SessionLocal
from app.models.poem import Poem
from app.models.request_log import PoemRequest
from app.services.llm_service import generate_from_llm
from app.utils.parser import parse_poem_response


def _serialize_poem(poem: Poem):
    return {
        "id": poem.id,
        "title": poem.title,
        "content": poem.content,
        "request_id": poem.request_id,
        "created_at": poem.created_at.isoformat(),
    }


def _build_prompt(theme: str, mood: str, stanza_count: int) -> str:
    return f"""
Kamu adalah penyair Indonesia yang menulis puisi singkat, puitis, hangat, dan natural.

Buat satu puisi dalam format JSON valid, tanpa penjelasan tambahan dan tanpa markdown fence.

Aturan:
- Tema puisi: "{theme}"
- Suasana hati: "{mood}"
- Jumlah bait: {stanza_count}
- Setiap bait harus terdiri dari 4 baris.
- Gunakan bahasa Indonesia yang indah, imajinatif, dan tidak klise berlebihan.
- Hindari pengulangan baris yang sama antar bait.
- Puisi harus terasa utuh dari awal sampai akhir.
- Isi content harus dipisahkan dengan satu baris kosong antar bait.

Format output wajib:
{{
  "poem": {{
    "title": "Judul puisi yang singkat dan kuat",
    "content": "bait pertama\nbaris kedua\nbaris ketiga\nbaris keempat\n\nbait kedua..."
  }}
}}
""".strip()


def _count_stanzas(content: str) -> int:
    return len([part for part in content.split("\n\n") if part.strip()])


def _normalize_poem_content(content: str, stanza_count: int) -> str:
    stanzas = [part.strip() for part in content.split("\n\n") if part.strip()]
    normalized_stanzas = []

    for index, stanza in enumerate(stanzas[:stanza_count], start=1):
        lines = [line.strip() for line in stanza.splitlines() if line.strip()]
        lines = lines[:4]
        if len(lines) < 4:
            lines.extend(["" for _ in range(4 - len(lines))])
        normalized_stanzas.append("\n".join(lines))

    while len(normalized_stanzas) < stanza_count:
        normalized_stanzas.append(
            "\n".join([
                "Langit belum selesai bercerita,",
                "angin menyimpan sisa cahaya,",
                "dan hati belajar bertahan,",
                "meski perlahan, ia pulang juga."
            ])
        )

    return "\n\n".join(normalized_stanzas)


def _generate_local_poem(theme: str, mood: str, stanza_count: int):
    mood_phrases = {
        "bahagia": [
            "mentari menabur warna di ambang jendela,",
            "langit terasa dekat seperti doa yang pulang,",
            "langkah menari kecil di atas pagi yang lunak,",
            "dan dada pun lapang oleh syukur yang sederhana.",
        ],
        "sedih": [
            "hujan mengetuk pelan pada tepi kenangan,",
            "malam memanjang seperti nama yang tak dipanggil,",
            "air mata belajar jujur tanpa banyak suara,",
            "dan sunyi duduk dekat, menjaga yang retak.",
        ],
        "galau": [
            "jalan bercabang di bawah kepala yang lelah,",
            "hati bertanya pelan pada arah yang berdebu,",
            "angin membawa ragu seperti kertas tua,",
            "dan langkah pun ragu, namun tetap mencoba.",
        ],
        "semangat": [
            "api kecil menyala di tengah dada yang ingin bangun,",
            "langkah menolak lelah dengan rahasia pagi,",
            "hari baru memanggil nama kita pelan-pelan,",
            "dan harap tumbuh terus, seperti akar yang teguh.",
        ],
    }
    lines = mood_phrases.get(mood, mood_phrases["semangat"])
    stanzas = []
    for i in range(1, stanza_count + 1):
        start_line = f"Pada bait {i}, {theme} kembali berbicara,"
        middle_line = lines[(i - 1) % len(lines)]
        closing_line = {
            "bahagia": "kita belajar merayakan yang kecil dengan dada terbuka.",
            "sedih": "meski berat, luka tetap punya cara untuk reda.",
            "galau": "jawaban belum datang, tetapi langkah tak perlu berhenti.",
            "semangat": "dan hari depan menunggu dengan pintu yang terbuka.",
        }.get(mood, "dan hari depan menunggu dengan pintu yang terbuka.")

        stanzas.append("\n".join([
            start_line,
            middle_line,
            f"{theme.title()} menjaga ritme di sela napas,",
            closing_line,
        ]))

    return {
        "title": f"{theme.title()} dalam Nada {mood.title()}",
        "content": _normalize_poem_content("\n\n".join(stanzas), stanza_count),
    }


def create_poem(theme: str, mood: str, stanza_count: int):
    session = SessionLocal()
    try:
        prompt = _build_prompt(theme=theme, mood=mood, stanza_count=stanza_count)

        try:
            result = generate_from_llm(prompt)
            poem_data = parse_poem_response(result)
        except Exception:
            poem_data = _generate_local_poem(theme=theme, mood=mood, stanza_count=stanza_count)

        poem_data["content"] = _normalize_poem_content(poem_data["content"], stanza_count)

        if _count_stanzas(poem_data["content"]) != stanza_count:
            poem_data = _generate_local_poem(theme=theme, mood=mood, stanza_count=stanza_count)

        req = PoemRequest(theme=theme, mood=mood, stanza_count=stanza_count)
        session.add(req)
        session.commit()

        poem = Poem(
            title=poem_data["title"],
            content=poem_data["content"],
            request_id=req.id,
        )
        session.add(poem)

        session.commit()
        session.refresh(poem)
        return _serialize_poem(poem)

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_poems():
    session = SessionLocal()
    try:
        data = session.query(Poem).order_by(Poem.id.desc()).all()
        return [_serialize_poem(poem) for poem in data]
    finally:
        session.close()


def get_poem_by_id(poem_id: int):
    session = SessionLocal()
    try:
        poem = session.query(Poem).filter(Poem.id == poem_id).first()
        if not poem:
            return None
        return _serialize_poem(poem)
    finally:
        session.close()