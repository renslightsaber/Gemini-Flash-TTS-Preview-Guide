# 📚 INFO — Gemini Flash TTS (Preview) 레퍼런스

Gemini 네이티브 TTS의 **가격 · 보이스 · 언어 · 인라인 태그 · Instruction · Director's notes** 를 한 장에 모았습니다.

> ⚠️ 이 모델들은 **preview(미리보기)** 라 사양·가격·가용성이 바뀔 수 있습니다.
> 아래 수치는 **Google 공식 문서 기준(2026-07 확인)** 이며, 최신 값은 항상
> [공식 가격 페이지](https://ai.google.dev/gemini-api/docs/pricing) · [Speech generation 문서](https://ai.google.dev/gemini-api/docs/speech-generation) 에서 확인하세요.

---

## 💰 1. 가격 (per 1M tokens)

TTS는 **입력=텍스트 토큰**, **출력=오디오 토큰**으로 과금됩니다.

| 모델 | 무료 티어 | 입력(텍스트) | 출력(오디오) | 비고 |
|---|:---:|---|---|---|
| **`gemini-2.5-flash-preview-tts`** | ✅ 있음 | **$0.50** / 1M | **$10.00** / 1M | 권장 시작점 |
| `gemini-2.5-pro-preview-tts` | ❌ 없음 | $1.00 / 1M | $20.00 / 1M | 더 고품질·고비용 |

- **Batch(비실시간 일괄) 요금**은 절반: flash = 입력 $0.25 / 출력 $5.00, pro = 입력 $0.50 / 출력 $10.00.
- **무료로 시작**하려면 `gemini-2.5-flash-preview-tts` 를 쓰세요(무료 한도 내 실습 가능). 양이 많아지면 AI Studio에서 **billing(결제)** 활성화가 필요할 수 있습니다.
- 참고 감각: 짧은 광고 카피 한 줄(수 초 분량)은 보통 **수백 토큰** 수준입니다(위 스모크 테스트: 5초 합성 ≈ 157 tokens).

---

## 🗣️ 2. 보이스 — 프리셋 **30종**

커스텀 음색/클로닝은 지원하지 않고, 아래 **사전 정의 30종** 중에서 고릅니다. 괄호는 Google이 붙인 **스타일 descriptor**.

| # | 이름 | 스타일 | # | 이름 | 스타일 |
|:--:|---|---|:--:|---|---|
| 1 | Zephyr | Bright | 16 | Erinome | Clear |
| 2 | Puck | Upbeat | 17 | Algenib | Gravelly |
| 3 | Charon | Informative | 18 | Rasalgethi | Informative |
| 4 | Kore | Firm | 19 | Laomedeia | Upbeat |
| 5 | Fenrir | Excitable | 20 | Achernar | Soft |
| 6 | Leda | Youthful | 21 | Alnilam | Firm |
| 7 | Orus | Firm | 22 | Schedar | Even |
| 8 | Aoede | Breezy | 23 | Gacrux | Mature |
| 9 | Callirrhoe | Easy-going | 24 | Pulcherrima | Forward |
| 10 | Autonoe | Bright | 25 | Achird | Friendly |
| 11 | Enceladus | Breathy | 26 | Zubenelgenubi | Casual |
| 12 | Iapetus | Clear | 27 | Vindemiatrix | Gentle |
| 13 | Umbriel | Easy-going | 28 | Sadachbia | Lively |
| 14 | Algieba | Smooth | 29 | Sadaltager | Knowledgeable |
| 15 | Despina | Smooth | 30 | Sulafat | Warm |

> 💡 **성별**은 Google이 공식 라벨하지 않습니다. 이 프로젝트의 `gt.FEMALE_VOICES` / `gt.MALE_VOICES` 는 편의를 위한 **대략적 청감 분류**일 뿐이니 참고만 하세요. 목록은 `python cli.py --list-voices`.

---

## 🌐 3. 언어 · 출력 포맷 · 한도

| 항목 | 값 |
|---|---|
| 지원 언어 | **80개 이상** (한국어 포함, 자동 언어 감지) |
| 언어 지정 | 보통 생략(자동). 필요 시 BCP-47 코드(예: `ko-KR`, `en-US`) |
| 출력 오디오 | **24 kHz · 16-bit · mono PCM** (이 프로젝트는 `.wav` 로 저장) |
| 컨텍스트 한도 | 약 **32k tokens** |
| 화자 수 | 최대 **2명**(멀티 스피커) — 이 가이드는 단일 화자 중심 |
| 워터마크 | preview 출력에 **SynthID**(비가청) 포함 가능 |

---

## 🎭 4. 인라인 태그 (`[laughs]` 등)

문장 **중간에 대괄호**로 감정·비언어 소리를 삽입하면 모델이 그 연기를 반영합니다.

**자주 쓰는 태그** (이 프로젝트 `gt.INLINE_TAGS`):
`[laughs]` `[laughing]` `[giggles]` `[sighs]` `[gasp]` `[whispers]`
`[excited]` `[amazed]` `[curious]` `[crying]` `[sarcastic]` `[serious]`
`[shouting]` `[tired]` `[bored]` `[panicked]` `[mischievously]` `[trembling]`

**커스텀 태그도 동작** (속도·톤을 자유 서술) — `gt.CUSTOM_TAG_EXAMPLES`:
`[very fast]` `[very slow]` `[like a cartoon dog]` `[in a spooky whisper]` `[warmly]`

예:
```text
정말요? [laughs] 믿을 수가 없어요!
[sighs] 오늘 하루 정말 길었어요.
[very fast] 마감이 오늘까지예요, 서둘러요!
```

---

## 🎯 5. Instruction (자연어 스타일 지시)

읽을 문장 앞에 **어떻게 읽을지**를 자연어로 붙이면 됩니다. 이 프로젝트에서는 `style=` 인자(또는 CLI `--style`)가 이 역할을 합니다 — 내부적으로 `"<style>: <text>"` 형태로 전달됩니다.

```python
from gemini_tts import synthesize, save_wav
wav, sr = synthesize("지금 바로 만나보세요!", voice="Puck",
                     style="긴급 프로모션처럼 힘있고 빠르게")
save_wav(wav, sr, "outputs/promo.wav")
```

예시 스타일 문구: `밝고 따뜻하게` · `신뢰감 있고 차분한 내레이션` · `다정하게 속삭이듯` · `밝고 통통 튀는 MZ 톤`.

---

## 🎬 6. Director's notes (구조화 프롬프트)

더 정교한 연출은 **감독 노트** 형식의 구조화 프롬프트를 통째로 넣습니다. 앞부분은 **연기 지시**이고, **`#### TRANSCRIPT` 섹션만 실제로 발화**됩니다.

```text
# AUDIO PROFILE: 40대 남성, 미들로우 바리톤, 신뢰감 있는 기업 내레이터
## SCENE: 브랜드 PR 영상. 차분하고 묵직한 배경음악과 어우러진다.
### DIRECTOR'S NOTES
Style: 신뢰감 있고 단단하게, 과장 없이 진정성 있게
Pacing: 또렷한 보통 속도, 문장 끝은 단호하게 끊기
Emphasis: 핵심어(연결·신뢰·미래)에 절제된 강조
#### TRANSCRIPT
혼자가 아닌 함께 연결될 때, 기술은 더 멀리 나아갑니다.
```

```python
director = """<위 블록 전체>"""
wav, sr = synthesize(director, voice="Charon")   # style 없이 블록 자체가 지시
```

- **TRANSCRIPT 안에 인라인 태그**도 넣을 수 있습니다(예: `... 나아갑니다. [warmly]`).
- 같은 TRANSCRIPT를 두고 **DIRECTOR'S NOTES만 바꿔** 톤 A/B를 비교해 보세요.

> 자세한 실행 예제와 단계별 설명은 **[USE_GUIDE.md](USE_GUIDE.md)** 와 `notebooks/05_directors_notes.ipynb` 를 보세요.
