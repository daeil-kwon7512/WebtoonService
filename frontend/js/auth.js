// 현재 로그인 상태 확인
async function checkAuth() {
    try {
        const user = await api.getMe();
        return user;
    } catch (e) {
        return null;
    }
}

// 네비게이션 업데이트
async function updateNavbar() {
    const authArea = document.getElementById('navbar-auth');
    if (!authArea) return;

    const user = await checkAuth();

    if (user) {
        authArea.innerHTML = `
            <span>${user.username}님</span>
            <a href="mypage.html">마이페이지</a>
            <a href="#" id="logout-btn">로그아웃</a>
        `;
        document.getElementById('logout-btn').addEventListener('click', async (e) => {
            e.preventDefault();
            await api.logout();
            location.href = 'index.html';
        });
    } else {
        authArea.innerHTML = `
            <a href="login.html">로그인</a>
            <a href="signup.html">회원가입</a>
        `;
    }
}

// 페이지 로드 시 네비바 업데이트
document.addEventListener('DOMContentLoaded', updateNavbar);
