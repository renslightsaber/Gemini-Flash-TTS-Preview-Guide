# 🎙️ Gemini Flash TTS (Preview) — 사용 가이드

**Google Gemini 네이티브 TTS**(`gemini-2.5-flash-preview-tts`)로 텍스트를 **감정·톤이 살아있는 음성**으로 만드는 법을 담은, 바로 쓰는 가이드입니다. 커맨드라인 한 줄부터 노트북 실험까지 예제로 익힐 수 있습니다.

```bash
python cli.py "안녕하세요, 반갑습니다!" --voice Puck --style "밝고 활기차게"
# → ✅ 저장: outputs/tts_Puck_....wav   (24kHz · mono)
```

---

## ✨ 특징

- **감정/톤 제어 3종 레버** — 자연어 Instruction · 인라인 태그(`[laughs]` 등) · Director's notes 구조화 프롬프트
- **프리셋 보이스 30종** · **80+ 언어**(한국어 지원, 자동 감지) · 출력 **24kHz·16bit·mono**
- **CLI + 파이썬 모듈 + 예제 노트북 5종** — 저장 위치 지정 가능(기본 `outputs/`)
- **의존성 최소** — `google-genai` / `numpy` / `soundfile` / `python-dotenv`
- **무료로 시작** — flash 모델은 무료 티어 제공

---

## 🚀 빠른 시작 (3단계)

```bash
# 1) 라이브러리 설치
pip install -r requirements.txt

# 2) API 키 준비 (https://aistudio.google.com 에서 발급)
cp .env.example .env      # 그리고 .env 안에 GEMINI_API_KEY=... 채우기

# 3) 합성!
python cli.py "지금 바로 만나보세요." --voice Charon --style "신뢰감 있게"
```

키 발급부터 설치·검증까지 자세한 안내는 **[SETUP.md](SETUP.md)**.

---

## 📖 문서

| 문서 | 내용 |
|---|---|
| **[SETUP.md](SETUP.md)** | API 키 발급 → `.env` → 라이브러리 설치 → 검증 (처음부터 끝까지) |
| **[USE_GUIDE.md](USE_GUIDE.md)** | 친절한 사용법 — 플래그·인라인 태그·Instruction·Director's notes 예제 |
| **[INFO.md](INFO.md)** | 레퍼런스 — 가격 · 보이스 30종 · 언어 · 태그 목록 · 출력 포맷 |

---

## 🧑‍💻 사용 방법 두 가지

**① 커맨드라인(CLI)**
```bash
python cli.py "읽을 문장" --voice Kore --style "밝고 따뜻하게" --out outputs/
python cli.py --list-voices                       # 보이스 30종 보기
python cli.py "테스트" --style "차분하게" --dry-run   # 호출 없이 요청만 확인
python cli.py --prompt-file director.md --voice Charon   # Director's notes 파일
```

**② 파이썬 / 노트북**
```python
from gemini_tts import synthesize, save_wav
wav, sr = synthesize("반가워요! [laughs] 오늘 기분이 좋네요.",
                     voice="Aoede", style="밝고 명랑하게")
save_wav(wav, sr, "outputs/hello.wav")
```

---

## 🗂️ 프로젝트 구조

```
Gemini_Falsh_TTS_Preview_Guide/
├── gemini_tts.py        # 코어 모듈: synthesize(), save_wav(), VOICES, INLINE_TAGS ...
├── cli.py               # 커맨드라인 합성기
├── requirements.txt     # 필요한 패키지
├── .env.example         # 여기서 복사 → .env 에 GEMINI_API_KEY 저장
├── README.md · SETUP.md · USE_GUIDE.md · INFO.md
├── outputs/             # 합성 결과 .wav 기본 저장 위치(gitignore)
└── notebooks/
    ├── 01_quickstart.ipynb          # 첫 합성 1콜 + 재생
    ├── 02_voices_gallery.ipynb      # 여러 보이스 비교
    ├── 03_inline_tags.ipynb         # [laughs] 등 태그
    ├── 04_style_instructions.ipynb  # 같은 문장, 여러 톤
    └── 05_directors_notes.ipynb     # 감독 노트 연출
```

---

## 🎯 감정/톤 제어 미리보기

```bash
# 자연어 Instruction
python cli.py "이 순간을 놓치지 마세요." --voice Charon --style "긴급 프로모션처럼 힘있고 빠르게"

# 인라인 태그
python cli.py "정말요? [laughs] 믿을 수가 없어요!" --voice Aoede

# Director's notes (파일)  →  #### TRANSCRIPT 부분만 발화
python cli.py --prompt-file director.md --voice Charon
```

각 방법의 자세한 예제는 **[USE_GUIDE.md](USE_GUIDE.md)** 에 있습니다.

---

## ⚠️ 참고

- 이 모델들은 **preview(미리보기)** 라 사양·가격·가용성이 변경될 수 있습니다. 최신 정보는 [Google 공식 문서](https://ai.google.dev/gemini-api/docs/speech-generation)를 확인하세요.
- **API 키는 비밀**입니다 — `.env` 에만 두고 절대 커밋하지 마세요(이 프로젝트는 `.gitignore` 로 차단).
- 커스텀 음색/클로닝은 지원되지 않습니다(프리셋 30종 사용).
