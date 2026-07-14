# secrets/ — 로컬 전용(커밋 금지)

이 폴더에는 GitHub push 에 쓰는 **SSH 개인키** 같은 비밀 파일을 둡니다.
`.gitignore` 가 `secrets/*` 를 차단하므로(이 `README.md` 만 예외) 키는 절대 커밋되지 않습니다.

## 이 프로젝트의 키 정책 (공유 계정에서 "이 repo만 내 GitHub"로)

이 서버 계정은 여러 명이 공유합니다. 그래서 전역(`--global`) 설정을 건드리지 않고,
**이 repo 안에서만** 내 GitHub 계정(`renslightsaber`)으로 push 되도록 고정했습니다.

- **push 신원 고정**: `git config core.sshCommand "... -i <키경로> -o IdentitiesOnly=yes"`
  → 계정을 공유해도 **이 repo 의 push 만** 지정한 키/계정으로 나갑니다.
- **커밋 작성자 고정**: repo-local `user.name=renslightsaber`, `user.email=heiscold@gmail.com`.
- **보안의 핵심은 키 위치가 아니라 passphrase** 입니다(같은 계정 사용자끼리는 파일 권한으로 못 막음).
  키에는 반드시 passphrase 를 걸고, 유출 의심 시 GitHub 에서 즉시 삭제(폐기)하세요.

이 프로젝트는 **기존에 등록된 키를 재사용**하도록 설정되어 있어(`core.sshCommand` 가 그 절대경로를
가리킴), 여기 `secrets/` 안에 새 키를 두지 않아도 push 가 됩니다. 새 키를 만들고 싶다면
`SETUP.md` 의 안내를 따르세요.
