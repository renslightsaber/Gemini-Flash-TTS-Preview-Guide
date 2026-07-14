# ⚙️ SETUP — 설치 & API 키 발급 (처음부터 끝까지)

이 문서만 따라 하면 **아무 것도 없는 상태**에서 Gemini Flash TTS로 첫 음성을 뽑을 때까지 마칠 수 있습니다.
순서대로 5단계입니다: **① 키 발급 → ② 키 저장(.env) → ③ 파이썬 환경 → ④ 라이브러리 설치 → ⑤ 검증**.

---

## ① Google AI Studio에서 API 키 발급 (무료)

1. 브라우저로 **<https://aistudio.google.com>** 접속 → Google 계정으로 로그인.
2. 좌측 메뉴(또는 우상단)의 **"Get API key"(API 키 가져오기)** 클릭.
3. **"Create API key"** 클릭.
   - 처음이면 **새 프로젝트 생성**을 요청받을 수 있습니다 → **"Create API key in new project"** 선택하면 프로젝트가 자동 생성됩니다. (이미 Google Cloud 프로젝트가 있으면 그걸 골라도 됩니다.)
4. 생성된 키 문자열을 **복사**해 둡니다.
   - 키 형태는 계정에 따라 다를 수 있습니다(예: `AIza...` 또는 `AQ.Ab...` 등). **발급된 값 그대로** 쓰면 됩니다.
5. **무료 한도**가 있어 바로 실습할 수 있습니다. 사용량이 많아지면 AI Studio → **Billing(결제)** 활성화가 필요할 수 있습니다.

> 🔐 **키는 비밀번호입니다.** 코드·노트북·깃(GitHub)에 **직접 적지 마세요.** 아래 ②처럼 `.env` 파일에만 두고, 그 파일은 `.gitignore`로 커밋이 차단돼 있습니다.

---

## ② 키를 `.env` 에 저장

프로젝트 루트에서 예시 파일을 복사한 뒤 키를 채웁니다.

```bash
cd /home/aithe209/Gemini_Falsh_TTS_Preview_Guide   # 프로젝트 폴더로 이동
cp .env.example .env
```

`.env` 를 열어 아래 한 줄을 **따옴표 없이** 채웁니다:

```dotenv
GEMINI_API_KEY=여기에_복사한_키_붙여넣기
```

- 저장 후 끝. 코드가 자동으로 이 `.env` 에서 키를 읽습니다(`python-dotenv`).
- `.env` 는 절대 커밋되지 않습니다(`.gitignore` 에 포함).

---

## ③ 파이썬 환경 준비

Python **3.10+** 권장. 깨끗한 가상환경을 새로 만드는 걸 추천합니다.

**venv (표준 라이브러리)**
```bash
cd /home/aithe209/Gemini_Falsh_TTS_Preview_Guide
python3 -m venv .venv
source .venv/bin/activate        # (Windows: .venv\Scripts\activate)
```

**또는 conda**
```bash
conda create -n gemini_tts python=3.11 -y
conda activate gemini_tts
```

---

## ④ 라이브러리 설치

```bash
pip install -r requirements.txt
```

설치되는 핵심 패키지:

| 패키지 | 용도 |
|---|---|
| **google-genai** | Gemini 네이티브 SDK (`from google import genai`) — ⚠️ `openai` SDK와 **다른** 패키지 |
| **numpy** | 오디오 배열 처리(PCM16 → float32) |
| **soundfile** | `.wav` 저장 |
| **python-dotenv** | `.env` 에서 키 로드 |
| **ipython** | 노트북에서 `Audio` 로 바로 청음 |

> 노트북을 로컬에서 열려면 추가로 `pip install jupyter` 후 `jupyter lab`(또는 `jupyter notebook`).

---

## ⑤ 검증 (설치가 잘 됐는지)

**(a) 키 없이도 되는 점검 — `--dry-run` / 보이스 목록**
```bash
python cli.py --list-voices                 # 프리셋 30종이 출력되면 OK
python cli.py "테스트" --style "밝게" --dry-run   # 보낼 요청이 출력되면 OK(과금 없음)
```

**(b) 실제 1회 합성 (키 필요, 무료 티어)**
```bash
python cli.py "안녕하세요, 설치가 잘 되었네요!" --voice Kore --style "밝고 친근하게"
# → ✅ 저장: outputs/tts_Kore_....wav  (24000Hz, mono)
```
`outputs/` 폴더에 `.wav` 가 생기고 재생되면 성공입니다. 🎉

다음 단계: **[USE_GUIDE.md](USE_GUIDE.md)** 로 인라인 태그·Instruction·Director's notes 사용법을 익히고, `notebooks/` 예제를 실행해 보세요.

---

## ⑥ (선택) 이 프로젝트를 내 GitHub로 버전관리하기

여러 명이 공유하는 서버 계정에서 **이 폴더만** 내 개인 GitHub로 push하려면, 전역 설정을 건드리지 않고 **repo-local** 로만 신원을 고정합니다.

```bash
cd /home/aithe209/Gemini_Falsh_TTS_Preview_Guide
git init
git config user.name  "renslightsaber"
git config user.email "heiscold@gmail.com"
# 이 repo의 push만 지정한 SSH 키로 나가게 고정(다른 사람/다른 repo와 격리)
git config core.sshCommand \
  "ssh -i /경로/secrets/id_ed25519_gh_renslightsaber -o IdentitiesOnly=yes"

git remote add origin git@github.com:renslightsaber/Gemini-Falsh-TTS-Preview-Guide.git
git add -A && git commit -m "first commit"
git push -u origin main
```

- `--global` 을 **쓰지 않는 것**이 핵심입니다(전역/타인 설정 미변경).
- 새 SSH 키를 만든다면: `ssh-keygen -t ed25519 -C "메일" -f secrets/id_ed25519_gh_renslightsaber` (**passphrase 반드시 설정**) → 공개키(`.pub`)를 GitHub → Settings → SSH keys 에 등록 → `ssh -i secrets/... -T git@github.com` 으로 `Hi renslightsaber!` 확인.
- 자세한 배경/보안 원칙은 [`secrets/README.md`](secrets/README.md) 참고. 키는 절대 커밋 금지(`.gitignore` 처리됨).
