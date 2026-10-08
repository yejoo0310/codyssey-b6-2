# AI Git Commit / PR Generator

Git 변경 사항을 AI API로 분석해 커밋 제목과 Pull Request(PR) 초안을 생성하는 Python CLI 도구입니다. 변경 이유를 별도로 입력하지 않고, 변경 파일 목록과 diff를 기반으로 한국어 문구를 작성합니다.

결과는 검증과 후처리를 거쳐 터미널에 출력됩니다. 사용자가 내용을 검토하고 복사해 적용하며, 도구가 직접 커밋하거나 push하거나 GitHub PR을 생성하지는 않습니다.

## 주요 기능

- `git status --short`로 변경 파일 목록 수집
- `git diff --cached`와 `git diff`로 staged·unstaged 변경 내용 수집
- Conventional Commits 형식의 커밋 제목 한 줄 생성
- PR 제목과 `Why`, `What`, `How to Test` 섹션 생성
- 모델, temperature, 최대 출력 토큰 수를 CLI 옵션으로 설정
- 제목 길이와 본문 형식 검증 및 후처리
- 안전 모드에서 diff의 민감정보 패턴 마스킹
- 변경 없음, API Key 누락, API 오류 등의 안내 메시지 출력

## 실행 환경 및 설치

- Python 3.10 이상
- Git
- Python 패키지 `requests`
- 사용 가능한 AI API Key와 네트워크 연결

프로젝트를 내려받은 뒤 프로젝트 루트에서 가상환경을 생성합니다. 아래 명령은 macOS/Linux 셸 기준입니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install requests
python main.py --help
```

현재 `requirements.txt`는 없으므로 `requests`를 직접 설치합니다.

## API Key 설정

API Key는 코드에 넣지 않고 환경변수로 설정합니다.

```bash
export AI_API_KEY="YOUR_API_KEY"
```

현재 터미널 세션에서 적용되는 설정입니다. 새 터미널을 열면 다시 설정해야 합니다. `.env` 파일을 자동으로 읽는 기능은 없습니다.

현재 구현은 다음 API 설정을 사용합니다.

| 항목 | 값 |
| --- | --- |
| 요청 URL | `https://copa.codyssey.kr/v1/messages` |
| 호환 방식 | Anthropic Messages |
| 인증 | `x-api-key` 헤더에 `AI_API_KEY` 환경변수 값 전달 |
| API 버전 | `2023-06-01` |
| 기본 모델 | `claude-haiku-4` |
| 요청 타임아웃 | 30초 |

요청에는 `model`, `temperature`, `max_tokens`, `system`, `messages`를 포함하며, 응답의 `content` 배열에서 텍스트 블록을 추출합니다.

## 사용 방법

분석할 Git 프로젝트의 루트에서 실행합니다.

### 커밋 제목 생성

```bash
python main.py commit --safe-mode
```

커밋 본문 없이 `type: 한글 제목` 형식의 한 줄을 생성합니다. 지원하는 type은 `feat`, `fix`, `docs`, `refactor`, `test`, `chore`입니다.

### PR 초안 생성

```bash
python main.py pr --safe-mode
```

PR 제목과 `Why`, `What`, `How to Test` 본문을 생성합니다. 생성된 테스트 방법은 사용자가 실제로 수행하고 확인해야 합니다.

### 생성 옵션 변경

```bash
python main.py commit --model claude-sonnet-4 --temperature 0.2 --max-tokens 800 --safe-mode
python main.py pr --max-tokens 1200 --safe-mode
```

모델 ID는 API 서비스에서 사용할 수 있는 값으로 지정해야 합니다.

| 옵션 | 기본값 | 설명 |
| --- | --- | --- |
| `--model` | `claude-haiku-4` | 사용할 모델 ID |
| `--temperature` | `0.2` | 생성 파라미터. 0 이상 1 이하 |
| `--max-tokens` | `800` | 최대 출력 토큰 수. 1 이상의 정수 |
| `--safe-mode` | OFF | diff의 민감정보 패턴을 마스킹한 뒤 전송 |
| `-h`, `--help` | — | 사용법 출력 |

## Git 변경 사항의 수집 범위

staged·unstaged diff를 각각 수집하고, `=== Staged Changes ===`와 `=== Unstaged Changes ===`로 구분해 프롬프트에 전달합니다.

- 아직 `git add`하지 않은 새 파일은 status에 나타나지만 내용은 diff에 포함되지 않습니다. 내용 분석이 필요하면 해당 파일을 먼저 stage하세요.
- stage한 변경과 stage하지 않은 변경을 모두 분석합니다. 특정 커밋에 포함할 변경만 남겨 두고 실행하는 것이 좋습니다.
- 현재 구현은 Git 저장소 내부인지 확인하지만, 루트에서 실행하는지까지 강제하지는 않습니다. 수집 범위를 명확히 하기 위해 프로젝트 루트에서 실행하세요.
- status가 비어 있으면 `변경 사항이 없습니다.`를 출력하고 API 호출 없이 종료합니다.
- 새 파일만 있어 status는 있지만 diff가 비어 있는 경우에도 현재 구현은 API를 호출합니다. 충분한 근거로 생성하려면 실행 전에 `git add`가 필요합니다.

```bash
# 예: 새 파일 내용을 분석에 포함
# 파일명은 실제 변경 파일로 바꿔주세요.
git add main.py
python main.py commit --safe-mode
```

## 출력 예시

아래는 출력 형식을 보여주는 예시입니다. 로그의 파일 수·줄 수와 생성 문구는 변경 내용 및 모델 응답에 따라 달라집니다.

### 커밋 제목

```text
[INFO] Git status 수집 완료: 2개 파일 변경 감지
[INFO] Git diff 수집 완료: 42줄
[INFO] model: claude-haiku-4
[INFO] temperature: 0.2
[INFO] max_tokens: 800
[INFO] safe-mode: ON
[INFO] Safe mode 적용
[INFO] 민감정보 마스킹: 0건
[INFO] AI API 요청 중...
[INFO] API 호출 횟수: 1
[DONE] 커밋 메시지 생성 완료

--- Commit Message ---
feat: Git 변경 사항 기반 커밋 제목 생성 기능 추가
----------------------
```

### PR 제목과 본문

API 요청 등의 로그 뒤에 다음 형식으로 출력됩니다.

```text
[DONE] PR 초안 생성 완료

--- PR Title ---
feat: 커밋 제목과 PR 초안 자동 생성 기능 추가

--- PR Body ---
## Why
- Git 변경 사항을 바탕으로 커밋과 PR 설명을 일관된 형식으로 작성하기 위해 생성 기능을 추가합니다.

## What
- staged·unstaged diff를 수집해 AI 입력으로 전달합니다.
- 커밋 제목과 PR 초안을 생성하고 형식을 검증합니다.

## How to Test
- 변경 파일을 준비하고 python main.py commit --safe-mode를 실행해 제목을 확인합니다.
- python main.py pr --safe-mode를 실행해 필수 섹션과 불릿을 확인합니다.
----------------------
```

## 결과 검증과 후처리

| 대상 | 검증 및 처리 |
| --- | --- |
| 커밋 제목 | 한 줄, 최대 72자, 허용 type과 비어 있지 않은 제목 확인 |
| PR 제목 | 한 줄, 최대 80자, 비어 있지 않은 제목 확인 |
| PR 본문 | `## Why`, `## What`, `## How to Test` 존재 및 각 섹션의 `- ` 불릿 확인 |

커밋 제목 50자 이내와 한국어 작성은 프롬프트로 요청합니다. 별도 검증으로 강제하는 항목은 아닙니다.

검증 실패 시 API를 다시 호출하지 않고 후처리합니다. 긴 제목은 최대 길이로 자르고, 커밋 type이 없거나 허용되지 않으면 `chore`로 보정합니다. PR 본문에서 빠진 섹션이나 불릿에는 `- 내용 확인 필요`를 추가합니다.

후처리 후에도 문제가 남으면 경고와 함께 결과를 출력할 수 있습니다. `[PR_TITLE]` 또는 `[PR_BODY]`가 없는 등 PR 응답 파싱에 실패하면 오류를 출력하고 결과 표시를 중단합니다. 제목이 잘렸거나 `내용 확인 필요`가 포함된 경우에는 사용자가 수정해야 합니다.

## 안전 모드와 비용 안내

`--safe-mode`를 지정하면 diff에서 다음 패턴을 치환합니다. 원본 파일은 수정하지 않습니다.

| 패턴 | 치환 결과 |
| --- | --- |
| 이메일 주소 | `[REDACTED_EMAIL]` |
| `api_key`, `api-key`, `apikey`, `secret`, `token`, `password` 뒤의 `:` 또는 `=`로 지정된 값 중 정규표현식에 맞는 8자 이상 값 | `[REDACTED_SECRET]` |
| `Bearer` 뒤의 토큰 | `Bearer [REDACTED_TOKEN]` |

안전 모드는 기본적으로 꺼져 있습니다. 현재 마스킹은 **diff에만 적용**하며 status의 파일명에는 적용하지 않습니다. 패턴에 맞지 않는 비밀값이나 개인정보는 남을 수 있으며, 파일·줄 수 전송 제한도 없습니다. 전송할 변경 내용을 확인하고 민감한 파일은 분석 대상에서 제거한 뒤 사용하세요.

`commit`과 `pr`은 각각 HTTP 요청을 1회 수행하며 자동 재시도·재생성은 없습니다. 성공하면 로그에 `API 호출 횟수: 1`을 표시합니다. 비용은 서비스와 모델, 입력·출력량에 따라 달라질 수 있으므로 필요한 변경만 준비하고 `--max-tokens`를 조정해 사용하세요. 이 옵션은 출력량을 제한하며 입력 diff 크기를 제한하지는 않습니다.

## 오류 안내

| 상황 | 안내 및 대응 |
| --- | --- |
| API Key 미설정 | `AI_API_KEY 환경변수가 설정되지 않았습니다.` → 환경변수 설정 |
| Git 저장소가 아닌 위치 | `Git 저장소가 아닙니다.` → Git 프로젝트에서 실행 |
| 잘못된 생성 옵션 값 | temperature 범위 또는 max-tokens 조건 안내 → 값 수정 |
| HTTP 401 / 403 | 인증 실패 / 접근 권한 안내 → Key와 권한 확인 |
| HTTP 429 | 요청 한도 초과 안내 → 서비스 한도 확인 |
| 요청 시간 초과 / 연결 실패 | 타임아웃 / 연결 오류 안내 → 네트워크 및 서비스 상태 확인 |
| HTTP 5xx | 서버 오류와 상태 코드 안내 |
| 응답 형식 오류 | JSON·텍스트 추출 또는 PR 파싱 오류 안내 |

생성 문구는 초안입니다. 실제 변경 내용, 변경 목적, 테스트 결과와 일치하는지 검토한 뒤 적용하세요.

## 프로젝트 구조

```text
.
├── main.py         # CLI 옵션, 전체 실행 흐름 및 결과 출력
├── git_utils.py    # Git 저장소 확인, status·diff 수집
├── ai_client.py    # API Key 로딩, REST 요청, 응답 및 오류 처리
├── prompts.py      # 커밋·PR 생성 프롬프트
├── parsers.py      # PR 제목·본문 분리
├── validators.py   # 생성 결과 검증 및 후처리
├── safety.py       # 정규표현식 기반 민감정보 마스킹
├── logger.py       # 터미널 로그 출력
├── test_git.py     # Git status 수집 확인 스크립트
├── test_api.py     # 실제 API 연결 확인 스크립트
├── README.md
└── .gitignore
```

## 동작 확인

```bash
python main.py --help
python test_git.py
```

`test_git.py`는 현재 저장소의 status를 출력하는 확인용 스크립트입니다. 자동화된 테스트 스위트는 아닙니다.

API 연결만 확인하려면 Key를 설정한 뒤 다음 명령을 실행합니다.

```bash
python test_api.py
```

이 스크립트는 실제 API를 1회 호출하므로 요청 한도와 비용에 반영될 수 있습니다. 실제 변경 기반 생성 흐름은 `python main.py commit --safe-mode`와 `python main.py pr --safe-mode`로 확인합니다.
