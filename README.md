# Kyeongin Hong — 홈페이지 편집 안내

공개 주소: <https://kyeonginh.com/>

로컬 저장소: `/Users/kian/Documents/phd/kyeonginh.github.io`

HTML은 구조, CSS는 디자인, JavaScript는 움직임을 담당합니다. Python은 문구와 HTML을 합쳐 배포용 파일을 만듭니다. Python 3.10 이상이면 macOS·Linux에서 추가 패키지 설치 없이 사용할 수 있습니다.

## 1. 무엇을 바꾸려면 어느 파일을 열까?

| 바꾸려는 것 | 파일 |
|---|---|
| 이름, 소개 문장, 이메일, 연구 관심사, 사진 설정 | [`site/content.json`](site/content.json) |
| 첫 화면의 문단 순서, 새 문단, 제목 배치 | [`site/templates/home.html`](site/templates/home.html) |
| 모든 페이지의 상단 메뉴·하단 정보 | [`site/templates/base.html`](site/templates/base.html) |
| 배경색, 글자 크기, 간격, 배경 움직임 | [`site/style.css`](site/style.css) |
| 스크롤할 때 문단이 나타나는 효과 | [`site/interactions.js`](site/interactions.js) |
| 문구와 템플릿을 조립하는 규칙 | [`scripts/build.py`](scripts/build.py) |
| push 후 자동 배포하는 설정 | [`.github/workflows/pages.yml`](.github/workflows/pages.yml) |

**평소에는 `content.json`과 `style.css`만 편집해도 대부분 바꿀 수 있습니다.**

## 2. 편집하면서 바로 확인하기

터미널에서 한 번 실행합니다.

```sh
cd /Users/kian/Documents/phd/kyeonginh.github.io
python3 scripts/serve.py
```

브라우저에서 <http://127.0.0.1:8765>를 엽니다. 파일을 저장하고 브라우저를 새로고침하면 바뀐 내용을 볼 수 있습니다. 서버를 끄려면 터미널에서 **Ctrl+C**를 누릅니다. 포트가 사용 중이면 `python3 scripts/serve.py --port 8766`으로 실행합니다.

이 단계에서는 인터넷에 공개되지 않습니다. 공개 사이트는 아래의 commit·push를 해야 갱신됩니다.

## 3. 문구 수정 — `content.json`

예를 들어 직무·학력을 소개하는 첫 문단은 다음 항목입니다.

```json
"about": "I am a research engineer at ENERZAi, working on machine-learning inference optimization. I received my B.S. in Industrial Engineering from Seoul National University."
```

큰따옴표 안의 문장만 바꾸면 됩니다.

| 항목 | 화면에서의 위치 |
|---|---|
| `name` | 상단 이름, 브라우저 탭, 하단 이름 |
| `name_lines` | 첫 화면의 큰 이름. 배열의 각 항목이 한 줄 |
| `location`, `email`, `github` | 위치와 연락처 |
| `about` | 현재 직무와 학력을 소개하는 첫 문단 |
| `research_interests` | 관심 분야를 소개하는 두 번째 문단 |
| `portrait` | 프로필 사진의 파일명과 대체 설명. `null`로 두면 숨김 |

예를 들어 이름을 한 줄로 표시하려면 다음과 같이 바꿉니다.

```json
"name_lines": ["Kyeongin Hong"]
```

연구 관심사는 `research_interests`에 일반 문장으로 적습니다. 별도 제목이나 세 항목으로 나누지 않습니다.

```json
"research_interests": "My interests are in combinatorial optimization, particularly the use of combinatorial structure and polyhedral methods in algorithm design."
```

JSON에서는 항목 사이에 쉼표를 넣되, **마지막 항목 뒤에는 쉼표를 넣지 않습니다.** 문장 안에 큰따옴표가 필요하면 `\"`로 씁니다. JSON에는 주석을 쓸 수 없습니다. 문구는 일반 텍스트로 처리하므로 HTML 태그를 넣어도 디자인으로 적용되지 않습니다. 다만 `about` 문단에서는 `[ENERZAi](https://enerzai.com)`처럼 쓰면 해당 이름에 링크가 연결됩니다. 링크 주소는 `https://` 또는 `http://`로 시작해야 합니다.

## 4. 배치 수정 — `home.html`

템플릿의 `${about}`과 `${research_interests}`는 `content.json`의 두 문단이 들어갈 자리입니다.

```html
<div class="intro-copy">
  <p>${about}</p>
  <p>${research_interests}</p>
</div>
```

- `<p>...</p>` 하나가 문단 하나입니다.
- `<h1>`, `<h2>`, `<h3>`는 제목입니다.
- `<section>`은 화면의 큰 구역입니다.
- `class="intro-copy"`는 CSS에서 `.intro-copy`라는 디자인 규칙을 적용한다는 뜻입니다.
- `id="about"`은 상단 About 메뉴가 이동할 위치입니다.

기존 두 문단의 순서를 바꾸려면 위의 `<p>` 줄 순서만 바꾸면 됩니다. 짧은 새 문단은 `<p>새 문장</p>`으로 직접 넣어도 됩니다. `${...}`의 이름을 새로 만들려면 `build.py`에도 연결해야 하므로, 처음에는 기존 항목을 편집하는 편이 간단합니다.

`base.html`은 페이지 공통 틀, `home.html`은 첫 화면 본문입니다. `note*.html`과 `archive*.html`은 나중에 발표 자료를 공개할 때 사용할 틀입니다. 세미나에 관한 소개는 `expositions.html`과 `archive.html`에 두고, 첫 화면에서는 별도로 서술하지 않습니다.

## 5. 디자인 수정 — `style.css`

파일 맨 위의 색상 변수부터 보면 됩니다.

```css
:root {
  --paper: #091426;   /* 전체 배경 */
  --ink: #edf2fa;     /* 주요 글자 */
  --muted: #aebdd2;   /* 보조 글자 */
  --accent: #a8c6f7;  /* 링크와 강조 */
  --line: #26354d;    /* 구분선 */
}
```

| CSS 이름 | 담당하는 부분 |
|---|---|
| `.intro` | 첫 화면의 두 열 배치와 위아래 여백 |
| `.identity h1` | 큰 이름의 글꼴 크기와 줄 간격 |
| `.intro-copy > p` | 두 소개 문단의 글자 크기와 줄 간격 |
| `.intro::before` | 흐릿하게 움직이는 푸른 배경 |
| `.intro::after` | 아주 작은 점 무늬 |
| `@keyframes navy-drift` | 배경이 움직이는 방식 |
| `@media (max-width: ...)` | 모바일·작은 화면에서 덮어쓰는 규칙 |

예를 들어 배경 움직임을 느리게 하려면 `animation: navy-drift 24s ...`의 `24s`를 `40s`로 바꿉니다. 끄려면 `.intro::before`의 `animation`을 `none`으로 바꿉니다.

모바일에서는 파일 아래쪽의 `@media` 규칙이 우선 적용될 수 있습니다. 데스크톱 글자 크기를 바꿨는데 휴대폰에서 그대로라면 해당 `@media`도 확인하세요. 기기의 ‘움직임 줄이기’ 설정을 존중하는 규칙은 유지하는 것을 권합니다.

### 프로필 사진

프로필 사진은 `assets/profile/profile.jpeg`에 있습니다. 같은 파일을 교체하면 사진을 바꿀 수 있습니다. `assets/profile/`은 공개 프로필 사진 전용이며, 미공개 발표 이미지용 `assets/images/`와 구분합니다.

화면에서의 크롭은 `.profile-photo`의 `--portrait-zoom`과 `--portrait-focus-x`·`--portrait-focus-y`로 조정합니다. 원본 파일의 픽셀은 수정하지 않습니다. 현재는 정사각형 프레임 안에서 1.45배 확대해 얼굴과 인형을 함께 보여줍니다. 사진 너비는 데스크톱 320px, 작은 데스크톱 280px, 모바일 최대 300px이며 좁은 화면에 맞춰 줄어듭니다.

## 6. 확인하고 공개하기

```sh
python3 scripts/build.py
python3 scripts/check.py dist

git diff
# 실제로 바꾼 파일만 선택합니다. 아래는 문구만 바꾼 경우의 예시입니다.
git add site/content.json
git commit -m "💬 Update homepage introduction"
git push origin main
```

GitHub Actions가 자동으로 빌드·배포합니다. CSS도 바꿨다면 `git add site/style.css`를 추가합니다. 배포 상태는 저장소의 Actions 탭에서 확인합니다.

**`dist/`는 자동 생성 결과물이므로 직접 편집하지 않습니다.** 다음 빌드 때 덮어써집니다. 원본인 `site/` 파일을 편집하세요.

## 7. CV와 발표 자료

현재 설정은 다음과 같으며, 파일과 링크가 공개되지 않습니다.

```json
"notes": [],
"cv": null
```

이 두 항목은 공개를 결정하기 전까지 그대로 두면 됩니다. `assets/documents/`·`assets/images/`는 Git 업로드에서도 제외되어 있습니다. 나중에 자료를 공개할 때만 파일 추가와 ignore 규칙을 의도적으로 변경합니다.
