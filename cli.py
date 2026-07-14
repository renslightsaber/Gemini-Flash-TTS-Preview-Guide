#!/usr/bin/env python3
"""Gemini Flash TTS — 커맨드라인 합성기.

예시:
    # 가장 단순 (기본 보이스 Kore, 결과는 outputs/ 에 자동 파일명으로 저장)
    python cli.py "안녕하세요, 반갑습니다."

    # 보이스 + 자연어 스타일 지시
    python cli.py "지금 바로 만나보세요!" --voice Puck --style "밝고 활기차게"

    # 인라인 태그 (문장 안에 대괄호로)
    python cli.py "정말요? [laughs] 믿을 수가 없네요!" --voice Aoede

    # 저장 위치 지정 (디렉터리 또는 정확한 .wav 경로)
    python cli.py "저장 테스트" --out my_audio/            # 디렉터리 → 자동 파일명
    python cli.py "저장 테스트" --out my_audio/hello.wav   # 정확한 파일

    # Director's notes 구조화 프롬프트를 파일로
    python cli.py --prompt-file director.md --voice Charon

    # 키/과금 없이 요청만 확인
    python cli.py "테스트" --style "차분하게" --dry-run

    # 보이스 목록
    python cli.py --list-voices
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import gemini_tts as gt


def _slug(text: str, n: int = 24) -> str:
    """텍스트 앞부분으로 파일명 슬러그 생성(한글/영숫자 유지)."""
    s = re.sub(r"\s+", "_", text.strip())
    s = re.sub(r"[^0-9A-Za-z가-힣_]+", "", s)
    return (s[:n] or "tts").rstrip("_")


def _resolve_out(out: str, voice: str, text: str) -> Path:
    """--out 이 디렉터리면 자동 파일명, .wav 면 그 경로 그대로."""
    p = Path(out)
    if p.suffix.lower() == ".wav":
        return p
    # 디렉터리로 취급 → tts_<voice>_<슬러그>.wav
    return p / f"tts_{voice}_{_slug(text)}.wav"


def _print_voices() -> None:
    print(f"프리셋 보이스 {len(gt.VOICES)}종 (이름 · 스타일):\n")
    for i, (name, style) in enumerate(gt.VOICES.items(), 1):
        mark = "F" if name in gt.FEMALE_VOICES else ("M" if name in gt.MALE_VOICES else " ")
        print(f"  {i:>2}. {name:<14} {style:<14} [{mark}]")
    print("\n  ([F]/[M] 은 공식 라벨이 아닌 대략적 청감 분류입니다.)")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cli.py",
        description="Gemini Flash TTS (Preview) 커맨드라인 합성기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("text", nargs="?", default=None,
                   help="합성할 문장(인라인 태그 포함 가능). --prompt-file 사용 시 생략.")
    p.add_argument("--voice", default="Kore",
                   help="프리셋 보이스 이름(기본: Kore). 목록은 --list-voices.")
    p.add_argument("--style", default=None,
                   help='자연어 톤 지시(예: "밝고 활기차게"). 생략 시 텍스트 그대로.')
    p.add_argument("--out", default="outputs",
                   help="저장 위치. 디렉터리면 자동 파일명, .wav면 그 경로(기본: outputs/).")
    p.add_argument("--lang", default=None,
                   help='언어 코드 BCP-47(예: ko-KR). 보통 생략(자동 감지).')
    p.add_argument("--model", default=gt.DEFAULT_MODEL,
                   help=f"모델(기본: {gt.DEFAULT_MODEL}).")
    p.add_argument("--prompt-file", default=None,
                   help="Director's notes 등 구조화 프롬프트 텍스트 파일 경로(있으면 text 대신 사용).")
    p.add_argument("--dry-run", action="store_true",
                   help="API 호출 없이 보낼 요청만 출력.")
    p.add_argument("--list-voices", action="store_true",
                   help="프리셋 보이스 30종을 출력하고 종료.")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_voices:
        _print_voices()
        return 0

    # 텍스트 소스 결정: --prompt-file 우선, 없으면 위치 인자 text.
    if args.prompt_file:
        text = Path(args.prompt_file).read_text(encoding="utf-8").strip()
        # 구조화 프롬프트는 style 프리픽스를 붙이지 않는다(블록 자체가 지시).
        style = None
    else:
        text = args.text
        style = args.style

    if not text:
        print("오류: 합성할 텍스트가 없습니다. 문장을 인자로 주거나 --prompt-file 을 쓰세요.\n",
              file=sys.stderr)
        build_parser().print_help(sys.stderr)
        return 2

    if args.voice not in gt.VOICES:
        print(f"경고: '{args.voice}' 는 알려진 프리셋 보이스가 아닙니다. "
              f"그대로 시도합니다. (목록: --list-voices)", file=sys.stderr)

    if args.dry_run:
        req = gt.preview_request(text, args.voice, style=style,
                                 model=args.model, language_code=args.lang)
        print("[dry-run] 보낼 요청 (API 호출 안 함):")
        print(f"  model        : {req['model']}")
        print(f"  voice        : {req['voice']}")
        print(f"  language_code: {req['language_code']}")
        print(f"  contents     : {req['contents']!r}")
        out_path = _resolve_out(args.out, args.voice, text)
        print(f"  (저장 예정 경로: {out_path})")
        return 0

    try:
        wav, sr = gt.synthesize(text, args.voice, style=style,
                                model=args.model, language_code=args.lang)
    except RuntimeError as e:  # 키 없음 등 사용자 조치 가능한 오류는 깔끔히
        print(f"오류: {e}", file=sys.stderr)
        return 1

    out_path = _resolve_out(args.out, args.voice, text)
    saved = gt.save_wav(wav, sr, out_path)
    dur = len(wav) / sr if sr else 0.0
    usage = gt.LAST_META.get("usage", {})
    print(f"✅ 저장: {saved}")
    print(f"   voice={args.voice}  model={args.model}  {sr}Hz  {dur:.2f}s"
          + (f"  tokens={usage.get('total_tokens')}" if usage else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
