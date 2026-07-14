"""gemini_tts — Gemini Flash TTS (Preview) 를 아주 단순하게 쓰는 코어 모듈.

텍스트 한 줄을 넣으면 표현력 있는 음성(wav)을 돌려준다.
- 모델: `gemini-2.5-flash-preview-tts` (무료 티어 있음, 안정적)
- 스타일 제어: (a) 자연어 style/지시  (b) 대괄호 인라인 태그([laughs] 등)
  (c) Director's notes 구조화 프롬프트 — 셋 다 결국 `contents` 텍스트로 전달된다.
- 키: 환경변수 `GEMINI_API_KEY` (프로젝트 루트 `.env` 에서 자동 로드).

사용 예:
    from gemini_tts import synthesize, save_wav
    wav, sr = synthesize("반가워요! 오늘 기분이 참 좋네요.", voice="Kore",
                         style="밝고 따뜻하게")
    save_wav(wav, sr, "outputs/hello.wav")

패키지 구성(같은 폴더/상위에 있어야 동작):
    - .env            ← GEMINI_API_KEY=...  (.env.example 참고)
    - requirements.txt ← google-genai / numpy / soundfile / python-dotenv
"""
from __future__ import annotations

import base64
import os
import re
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

# ── 모델 ──────────────────────────────────────────────────────────────────
SIMPLE_MODEL = "gemini-2.5-flash-preview-tts"   # 권장 시작점(무료 티어 O)
PRO_MODEL = "gemini-2.5-pro-preview-tts"        # 더 고품질·고비용(무료 X)
DEFAULT_MODEL = SIMPLE_MODEL
DEFAULT_SR = 24000                              # 출력 PCM 24kHz·16bit·mono

# ── 프리셋 보이스 30종 (이름 → 스타일 descriptor) ─────────────────────────
# 스타일은 Google 공식 표기. 성별은 공식적으로 라벨되어 있지 않다(아래 GENDER_HINT 참고).
VOICES = {
    "Zephyr": "Bright",          "Puck": "Upbeat",           "Charon": "Informative",
    "Kore": "Firm",              "Fenrir": "Excitable",      "Leda": "Youthful",
    "Orus": "Firm",              "Aoede": "Breezy",          "Callirrhoe": "Easy-going",
    "Autonoe": "Bright",         "Enceladus": "Breathy",     "Iapetus": "Clear",
    "Umbriel": "Easy-going",     "Algieba": "Smooth",        "Despina": "Smooth",
    "Erinome": "Clear",          "Algenib": "Gravelly",      "Rasalgethi": "Informative",
    "Laomedeia": "Upbeat",       "Achernar": "Soft",         "Alnilam": "Firm",
    "Schedar": "Even",           "Gacrux": "Mature",         "Pulcherrima": "Forward",
    "Achird": "Friendly",        "Zubenelgenubi": "Casual",  "Vindemiatrix": "Gentle",
    "Sadachbia": "Lively",       "Sadaltager": "Knowledgeable", "Sulafat": "Warm",
}

# 성별은 Google 공식 라벨이 아니다 — 아래는 청감상 편의 분류(대략적, 참고용).
# voices_for() 헬퍼가 노트북에서 성별 매칭 데모에 쓴다. 정답이 아니라 힌트다.
FEMALE_VOICES = ["Kore", "Leda", "Aoede", "Callirrhoe", "Autonoe", "Despina",
                 "Erinome", "Achernar", "Vindemiatrix", "Sulafat"]
MALE_VOICES = ["Charon", "Puck", "Orus", "Enceladus", "Iapetus", "Algieba",
               "Fenrir", "Algenib", "Rasalgethi", "Alnilam"]


def voices_for(gender: str) -> list:
    """성별 힌트로 보이스 목록 반환(대략적 분류, 공식 아님)."""
    return FEMALE_VOICES if str(gender).lower().startswith("f") else MALE_VOICES


# ── 인라인 태그 레퍼런스(문장 중간에 대괄호로 삽입) ────────────────────────
# 감정/비언어 소리를 넣는 태그. 아래는 자주 쓰이는 예시이며, 커스텀 태그도 동작한다.
INLINE_TAGS = [
    "[laughs]", "[laughing]", "[giggles]", "[sighs]", "[gasp]", "[whispers]",
    "[excited]", "[amazed]", "[curious]", "[crying]", "[sarcastic]", "[serious]",
    "[shouting]", "[tired]", "[bored]", "[panicked]", "[mischievously]", "[trembling]",
]
# 커스텀 태그도 인식된다: 속도/톤을 자유 서술.
CUSTOM_TAG_EXAMPLES = ["[very fast]", "[very slow]", "[like a cartoon dog]",
                       "[in a spooky whisper]", "[warmly]"]

# 언어 코드 예시(BCP-47). Gemini 는 자동 언어 감지도 하므로 보통 생략 가능.
LANGUAGE_HINTS = {"Korean": "ko-KR", "English (US)": "en-US", "Japanese": "ja-JP",
                  "Chinese (Mandarin)": "cmn-CN", "Spanish": "es-US"}

# 마지막 호출 메타(usage 등) — 디버깅/과금 확인용.
LAST_META: dict = {}


# ── 키 로드 (.env → 환경변수) ─────────────────────────────────────────────
def _load_env() -> None:
    """프로젝트 .env 를 os.environ 에 로드(이미 있으면 덮어쓰지 않음)."""
    try:
        from dotenv import load_dotenv
    except Exception:  # python-dotenv 미설치여도 이미 export 돼 있으면 동작
        return
    # 이 파일 옆의 .env 를 우선 로드.
    load_dotenv(Path(__file__).resolve().parent / ".env")
    load_dotenv()  # 현재 작업 디렉터리 .env 도 보조로


def _api_key() -> str:
    _load_env()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY 가 없습니다.\n"
            "  1) https://aistudio.google.com → 'Get API key' 로 키 발급\n"
            "  2) 프로젝트 루트에 .env 파일을 만들고 아래 한 줄 추가(따옴표 없이):\n"
            "        GEMINI_API_KEY=AIza...당신의_키...\n"
            "  ( .env.example 을 복사해서 쓰면 됩니다. 키는 코드/깃에 직접 넣지 마세요. )"
        )
    return key


# ── genai 클라이언트(싱글턴) ──────────────────────────────────────────────
_CLIENT = None


def _client():
    # genai.Client 를 여러 번 만들면 공유 transport 가 닫혀 오류 → 1개만 유지.
    global _CLIENT
    if _CLIENT is None:
        from google import genai  # 지연 import(설치 안내를 늦게)
        _CLIENT = genai.Client(api_key=_api_key())
    return _CLIENT


# ── 응답 오디오 디코드(base64 PCM16 → float32) ────────────────────────────
def _decode(data, mime: str) -> Tuple[np.ndarray, int]:
    raw = base64.b64decode(data) if isinstance(data, str) else data
    m = re.search(r"rate=(\d+)", mime or "")
    sr = int(m.group(1)) if m else DEFAULT_SR
    wav = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    return wav, sr


def build_contents(text: str, style: Optional[str] = None) -> str:
    """실제로 모델에 보내는 `contents` 문자열을 만든다.

    - style 이 있으면 `"<style>: <text>"` 형태(자연어 지시 프리픽스).
    - Director's notes 처럼 이미 완성된 구조화 프롬프트는 style 없이 text 로 그대로 넘긴다.
    """
    return f"{style}: {text}" if style else text


# ── 핵심 합성 ─────────────────────────────────────────────────────────────
def synthesize(
    text: str,
    voice: str = "Kore",
    *,
    style: Optional[str] = None,
    model: Optional[str] = None,
    language_code: Optional[str] = None,
) -> Tuple[np.ndarray, int]:
    """텍스트를 Gemini Flash TTS 로 합성해 (wav float32, sr) 반환.

    Args:
        text: 읽을 문장. 인라인 태그([laughs] 등)나 Director's notes 블록을 그대로 넣어도 된다.
        voice: 프리셋 보이스 이름(VOICES 참고). 기본 "Kore".
        style: 자연어 톤 지시(예: "밝고 활기차게"). 없으면 text 그대로 합성.
        model: 기본 gemini-2.5-flash-preview-tts. 고품질은 PRO_MODEL.
        language_code: BCP-47(예: "ko-KR"). 보통 생략(자동 감지).
    """
    from google.genai import types

    contents = build_contents(text, style)
    speech_kwargs = dict(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
        )
    )
    if language_code:
        speech_kwargs["language_code"] = language_code

    resp = _client().models.generate_content(
        model=model or DEFAULT_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(**speech_kwargs),
        ),
    )
    inline = resp.candidates[0].content.parts[0].inline_data
    wav, sr = _decode(inline.data, getattr(inline, "mime_type", "") or "")

    LAST_META.clear()
    LAST_META.update({"model": model or DEFAULT_MODEL, "voice": voice,
                      "mime": getattr(inline, "mime_type", "")})
    um = getattr(resp, "usage_metadata", None)
    if um is not None:
        LAST_META["usage"] = {"total_tokens": getattr(um, "total_token_count", None)}
    return wav, sr


def preview_request(text: str, voice: str = "Kore", *, style: Optional[str] = None,
                    model: Optional[str] = None,
                    language_code: Optional[str] = None) -> dict:
    """API 호출 없이 '무엇을 보낼지'만 구성해서 반환(--dry-run/검증용)."""
    return {
        "model": model or DEFAULT_MODEL,
        "voice": voice,
        "language_code": language_code,
        "contents": build_contents(text, style),
    }


# ── 저장 ──────────────────────────────────────────────────────────────────
def save_wav(wav: np.ndarray, sr: int, path) -> str:
    """wav(ndarray) 를 path 에 저장하고 저장 경로(str) 반환. 상위 폴더 자동 생성."""
    import soundfile as sf  # 지연 import

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out), np.asarray(wav), sr)
    return str(out)


__all__ = [
    "synthesize", "preview_request", "save_wav", "build_contents", "voices_for",
    "VOICES", "FEMALE_VOICES", "MALE_VOICES", "INLINE_TAGS", "CUSTOM_TAG_EXAMPLES",
    "LANGUAGE_HINTS", "SIMPLE_MODEL", "PRO_MODEL", "DEFAULT_MODEL", "DEFAULT_SR",
    "LAST_META",
]
