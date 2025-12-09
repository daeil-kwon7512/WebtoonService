let currentProvider = 'ALL';
let currentQuery = '';

// 카드 생성 (즐겨찾기 해제 시 삭제)
function createFavoriteCard(toon) {
    const card = document.createElement('div');
    card.className = 'webtoon-card';

    const favBtn = document.createElement('button');
    favBtn.className = 'favorite-btn';
    favBtn.textContent = '⭐';
    favBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        const result = await api.toggleFavorite(toon.id);
        if (!result.is_favorited) {
            card.style.opacity = '0';
            card.style.transform = 'scale(0.9)';
            setTimeout(() => {
                card.remove();
                checkEmpty();
            }, 300);
        }
    });
    card.appendChild(favBtn);

    const link = document.createElement('a');
    link.href = toon.url;
    link.target = '_blank';

    const thumbWrap = document.createElement('div');
    thumbWrap.className = 'thumbnail-wrapper';

    const skeleton = document.createElement('div');
    skeleton.className = 'thumbnail-skeleton';
    thumbWrap.appendChild(skeleton);

    const img = document.createElement('img');
    img.src = toon.thumbnail;
    img.alt = toon.title;
    img.className = 'webtoon-thumbnail';
    img.loading = 'lazy';
    img.onload = () => {
        img.classList.add('loaded');
        skeleton.style.display = 'none';
    };
    thumbWrap.appendChild(img);
    link.appendChild(thumbWrap);
    card.appendChild(link);

    const title = document.createElement('div');
    title.className = 'webtoon-title';
    title.textContent = toon.title;
    card.appendChild(title);

    const author = document.createElement('div');
    author.className = 'webtoon-author';
    author.textContent = toon.authors;
    card.appendChild(author);

    const days = document.createElement('div');
    days.className = 'webtoon-days';
    days.textContent = toon.update_days;
    card.appendChild(days);

    return card;
}

// 빈 상태 체크
function checkEmpty() {
    const grid = document.getElementById('webtoon-grid');
    if (grid.querySelectorAll('.webtoon-card').length === 0) {
        grid.innerHTML = `
            <div class="message">
                <div class="message-icon">📚</div>
                <h3>관심웹툰이 없습니다</h3>
                <p>웹툰 목록에서 별 버튼을 눌러 추가해보세요!</p>
                <a href="index.html" style="display:inline-block;margin-top:20px;padding:12px 24px;background:#667eea;color:white;text-decoration:none;border-radius:8px;">웹툰 둘러보기</a>
            </div>
        `;
    }
}

// 관심웹툰 로드
async function loadFavorites() {
    const grid = document.getElementById('webtoon-grid');
    grid.innerHTML = '<div class="message">불러오는 중...</div>';

    try {
        const params = {};
        if (currentProvider !== 'ALL') params.provider = currentProvider;
        if (currentQuery) params.q = currentQuery;

        const webtoons = await api.getMyFavorites(params);

        grid.innerHTML = '';
        if (webtoons.length === 0) {
            checkEmpty();
            return;
        }

        webtoons.forEach(toon => {
            const card = createFavoriteCard(toon);
            grid.appendChild(card);
        });
    } catch (e) {
        grid.innerHTML = '<div class="message" style="color:#c33;">로딩 중 오류가 발생했습니다.</div>';
    }
}

// 이벤트 바인딩
document.addEventListener('DOMContentLoaded', async () => {
    // 로그인 체크
    const user = await checkAuth();
    if (!user) {
        location.href = 'login.html';
        return;
    }

    // 필터 버튼
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentProvider = btn.dataset.provider;
            loadFavorites();
        });
    });

    // 검색 폼
    document.getElementById('search-form')?.addEventListener('submit', (e) => {
        e.preventDefault();
        currentQuery = document.getElementById('query-input').value.trim();
        loadFavorites();
    });

    loadFavorites();
});
