# 문제 해결 가이드

## "Operation not permitted" 에러 해결 방법

### 문제
Next.js 컴파일 중 `Operation not permitted (os error 1)` 에러 발생

### 해결 방법

#### 1. Next.js 캐시 삭제
```bash
rm -rf .next
npm run dev
```

#### 2. node_modules 재설치
```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

#### 3. 파일 권한 확인 및 수정
```bash
# 확장 속성 제거 (macOS)
xattr -cr node_modules
npm run dev
```

#### 4. 프로젝트 디렉토리 권한 확인
```bash
# 현재 디렉토리 권한 확인
ls -la
# 필요시 권한 수정
chmod -R u+w .
```

#### 5. 관리자 권한으로 실행 (최후의 수단)
```bash
sudo npm run dev
```
⚠️ 주의: 관리자 권한 사용은 권장하지 않습니다.

### 대안: 다른 포트 사용
```bash
PORT=3001 npm run dev
```
그 후 http://localhost:3001 접속

### 문제가 계속되면
1. 프로젝트를 공백이 없는 디렉토리 이름으로 이동
2. Node.js 및 npm 최신 버전 확인
3. macOS 보안 설정 확인 (시스템 설정 > 개인정보 보호 및 보안)
