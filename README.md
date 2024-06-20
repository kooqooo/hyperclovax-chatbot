## 브랜치 전략
기존의 우리팀 브랜치 전략은 `Git flow`였는데, 릴리즈 개념이 필요하지 않아서 이 리파지토리에서는 `GitHub flow`를 적용할 계획입니다.
### GitHub flow 설명
<img src="https://miro.medium.com/v2/resize:fit:1100/format:webp/1*bFl2IXVT2xIRy8uOm7v4JA.png" width="50%" height="40%">

> [image source] medium.com/@yanminthwin

- `main` 브랜치가 Git flow의 `develop`를 대신합니다.
- 따라서 새로운 기능을 완성하고 나서 `main`브랜치에 병합합니다.
- hotfix가 필요한 경우 `main` 브랜치에 직접 commit, push 합니다.
- 자세한 설명은 [링크](https://docs.github.com/ko/get-started/using-github/github-flow)를 참고해주세요.
