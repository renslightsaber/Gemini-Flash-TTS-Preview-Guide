# 🧭 USE GUIDE — 친절한 사용법 (처음 보는 분도 OK)

Gemini Flash TTS로 **텍스트를 감정 있는 음성으로** 만드는 법을, 예제와 함께 하나씩 설명합니다.
아직 설치를 안 했다면 먼저 **[SETUP.md](SETUP.md)** 를 끝내고 오세요.

- 두 가지 방법으로 쓸 수 있습니다: **① 커맨드라인(CLI)** — 가장 빠름 · **② 파이썬/노트북** — 프로그램에 넣거나 여러 개 실험.
- 스타일을 주는 레버는 3가지: **자연어 Instruction** · **인라인 태그** · **Director's notes**. 아래에서 차례로 봅니다.

---

## 1. 가장 빠른 시작 — CLI 한 줄

```bash
python cli.py "안녕하세요, 반갑습니다."
```
→ `outputs/` 폴더에 `.wav` 가 생깁니다. 기본 보이스는 **Kore**.

### 플래그(옵션) 한눈에

| 플래그 | 의미 | 예시 |
|---|---|---|
| `(첫 인자)` | 읽을 문장 | `"지금 바로 만나보세요!"` |
| `--voice` | 프리셋 보이스 이름 | `--voice Puck` |
| `--style` | 자연어 톤 지시(Instruction) | `--style "밝고 활기차게"` |
| `--out` | 저장 위치(폴더 또는 `.wav`) | `--out my_audio/` · `--out a.wav` |
| `--lang` | 언어 코드(보통 생략) | `--lang ko-KR` |
| `--model` | 모델 | `--model gemini-2.5-pro-preview-tts` |
| `--prompt-file` | Director's notes 파일 | `--prompt-file director.md` |
| `--dry-run` | 호출 없이 요청만 확인(과금 X) | |
| `--list-voices` | 보이스 30종 출력 | |

> **저장 위치 규칙**: `--out` 이 폴더면 `tts_<보이스>_<문장앞부분>.wav` 로 자동 명명하고, `.wav` 로 끝나면 정확히 그 경로에 저장합니다. 기본값은 `outputs/`.

### 파이썬으로는

```python
from gemini_tts import synthesize, save_wav

wav, sr = synthesize("안녕하세요, 반갑습니다.", voice="Kore", style="밝고 따뜻하게")
save_wav(wav, sr, "outputs/hello.wav")
```
`synthesize(...)` 는 `(wav, sr)` 를 돌려줍니다(`sr` = 24000). 노트북이라면 저장 없이 바로 들을 수 있어요:
```python
from IPython.display import Audio
Audio(wav, rate=sr)
```

---

## 2. 보이스 고르기

프리셋 **30종** 중에서 고릅니다(커스텀 음색은 지원 안 함).

```bash
python cli.py --list-voices
```
각 보이스에는 스타일 힌트가 붙어 있습니다 — 예: `Kore=Firm(단단한)`, `Puck=Upbeat(경쾌한)`, `Aoede=Breezy(산뜻한)`, `Sulafat=Warm(따뜻한)`, `Charon=Informative(정보전달형)`.

- 광고 내레이션처럼 **신뢰감** → `Charon`, `Kore`, `Alnilam`
- **밝고 경쾌** → `Puck`, `Laomedeia`, `Autonoe`
- **부드럽고 따뜻** → `Sulafat`, `Achernar`, `Vindemiatrix`

> 전체 목록·설명은 **[INFO.md](INFO.md) §2** 참고. 성별 표기는 공식이 아니라 대략적 힌트예요.

---

## 3. Instruction — 자연어로 "어떻게 읽을지" 지시하기

읽을 문장 앞에 톤을 자연어로 붙이면 됩니다. CLI는 `--style`, 파이썬은 `style=`.

```bash
python cli.py "이 순간을 놓치지 마세요." --voice Charon --style "신뢰감 있고 차분한 내레이션으로"
python cli.py "완전 대박이에요!"        --voice Puck   --style "밝고 통통 튀는 MZ 톤으로"
python cli.py "천천히, 깊게 숨을 쉬어요." --voice Sulafat --style "다정하게 속삭이듯 부드럽게"
```

**같은 문장, 다른 style** 로 여러 톤을 비교해 보는 게 감을 잡는 가장 빠른 길입니다
(노트북 `04_style_instructions.ipynb` 가 이 실험을 그대로 담고 있어요).

💡 팁
- 원하는 **감정 + 속도 + 상황**을 함께 적으면 좋습니다: `"긴급 세일처럼 힘있고 빠르게"`.
- 너무 과한 연기가 나오면 `"과장 없이", "차분하게"` 를 넣어 눌러 주세요.

---

## 4. 인라인 태그 — 문장 속에 감정/소리 넣기

문장 **중간에 대괄호** `[ ]` 로 웃음·한숨·속삭임 같은 걸 끼워 넣습니다.

```bash
python cli.py "정말요? [laughs] 믿을 수가 없어요!" --voice Aoede
python cli.py "[sighs] 오늘 하루 정말 길었어요."      --voice Enceladus
python cli.py "[whispers] 조용히 해, 다들 자고 있어."  --voice Despina
python cli.py "[excited] 우리가 드디어 해냈어요!"      --voice Fenrir
```

자주 쓰는 태그: `[laughs]` `[giggles]` `[sighs]` `[gasp]` `[whispers]` `[excited]` `[amazed]` `[curious]` `[crying]` `[sarcastic]` `[serious]` `[shouting]` `[tired]` `[bored]` `[panicked]` `[trembling]` `[mischievously]`

**커스텀 태그**(속도·톤 자유 서술)도 됩니다:
```bash
python cli.py "[very fast] 마감이 오늘까지예요, 서둘러요!" --voice Puck
python cli.py "[very slow] 자… 하나씩… 천천히 볼게요."      --voice Kore
```

💡 태그는 **효과를 원하는 위치**에 두세요. 문장 맨 앞에 두면 그 문장 전체의 톤에, 중간에 두면 그 지점의 반응(웃음 등)에 반영됩니다.

---

## 5. Director's notes — 감독처럼 연출하기

가장 정교한 방법입니다. **감독 노트** 형식의 블록을 통째로 넣으면, 앞부분은 **연기 지시**로 쓰이고 **`#### TRANSCRIPT` 부분만 실제로 소리 납니다.**

### 5-1. 구조

```text
# AUDIO PROFILE: (화자 설정) 40대 남성, 미들로우 바리톤, 신뢰감 있는 내레이터
## SCENE: (장면/분위기) 브랜드 PR 영상, 차분한 배경음악
### DIRECTOR'S NOTES
Style: 신뢰감 있고 단단하게, 과장 없이 진정성 있게
Pacing: 또렷한 보통 속도, 문장 끝은 단호하게 끊기
Emphasis: 핵심어(연결·신뢰·미래)에 절제된 강조
#### TRANSCRIPT
혼자가 아닌 함께 연결될 때, 기술은 더 멀리 나아갑니다.
```

### 5-2. 실행 — 파일로 (CLI)

위 블록을 `director.md` 로 저장한 뒤:
```bash
python cli.py --prompt-file director.md --voice Charon
```
(`--prompt-file` 을 쓰면 파일 내용 전체가 프롬프트가 되고, `--style` 은 붙지 않습니다.)

### 5-3. 실행 — 파이썬으로

```python
from gemini_tts import synthesize, save_wav

director = """# AUDIO PROFILE: 40대 남성, 미들로우 바리톤, 신뢰감 있는 내레이터
## SCENE: 브랜드 PR 영상, 차분한 배경음악
### DIRECTOR'S NOTES
Style: 신뢰감 있고 단단하게, 과장 없이 진정성 있게
Pacing: 또렷한 보통 속도, 문장 끝은 단호하게 끊기
Emphasis: 핵심어(연결·신뢰·미래)에 절제된 강조
#### TRANSCRIPT
혼자가 아닌 함께 연결될 때, 기술은 더 멀리 나아갑니다."""

wav, sr = synthesize(director, voice="Charon")   # style 없이 블록 자체가 연출
save_wav(wav, sr, "outputs/director.wav")
```

### 5-3. 팁
- **TRANSCRIPT만** 발화됩니다 — 앞의 PROFILE/SCENE/NOTES는 "어떻게 연기할지"를 알려줄 뿐.
- **TRANSCRIPT 안에 인라인 태그**도 넣을 수 있어요: `... 나아갑니다. [warmly]`
- 같은 TRANSCRIPT로 **DIRECTOR'S NOTES만 바꿔** A/B를 비교하면 연출 효과가 확 보입니다(노트북 `05_directors_notes.ipynb`).

---

## 6. 노트북으로 실험하기

`notebooks/` 에 단계별 예제가 있습니다(생성물은 저장 없이 셀에서 바로 청음):

| 노트북 | 내용 |
|---|---|
| `01_quickstart.ipynb` | 첫 합성 1콜 + 재생 |
| `02_voices_gallery.ipynb` | 여러 보이스를 한 문장으로 비교 |
| `03_inline_tags.ipynb` | `[laughs]` 등 태그 시연 |
| `04_style_instructions.ipynb` | 같은 문장을 여러 톤으로 |
| `05_directors_notes.ipynb` | 감독 노트 연출 A/B |

실행: `.env` 준비 → `jupyter lab` → 위에서 아래로 셀 실행.

---

## 7. 자주 겪는 문제

| 증상 | 해결 |
|---|---|
| `GEMINI_API_KEY 가 없습니다` | `.env` 에 키를 넣었는지 확인([SETUP.md](SETUP.md) ①②). 실행 위치가 프로젝트 루트인지도 확인. |
| `API key not valid` | 키를 **따옴표 없이** 정확히 붙였는지, 앞뒤 공백이 없는지 확인. AI Studio에서 키 재발급도 가능. |
| `ModuleNotFoundError: google` | `pip install -r requirements.txt` 를 (활성화된 가상환경에서) 실행했는지 확인. |
| 소리가 밋밋함 | `--style` 을 더 구체적으로, 또는 인라인 태그/Director's notes 사용. |
| 너무 과장됨 | style에 `"과장 없이, 차분하게"` 추가. |
| 파일이 어디 저장됐는지 모름 | CLI 출력의 `✅ 저장: ...` 경로 확인. 기본은 `outputs/`. |

더 많은 사양·가격·태그 목록은 **[INFO.md](INFO.md)** 를 보세요.
