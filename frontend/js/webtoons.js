let currentProvider = 'NAVER';
let currentQuery = '';

// 카드 생성
function createWebtoonCard(toon, isLoggedIn) {
    const card = document.createElement('div');
    card.className = 'webtoon-card';

    if (isLoggedIn) {
        const favBtn = document.createElement('button');
        favBtn.className = 'favorite-btn';
        favBtn.dataset.id = toon.id;
        favBtn.textContent = toon.is_favorited ? '⭐' : '☆';
        favBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const result = await api.toggleFavorite(toon.id);
            favBtn.textContent = result.is_favorited ? '⭐' : '☆';
        });
        card.appendChild(favBtn);
    }

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
    img.onerror = () => {
        skeleton.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#999;">로드 실패</div>';
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
    author.textContent = toon.writers;
    card.appendChild(author);

    const days = document.createElement('div');
    days.className = 'webtoon-days';
    days.textContent = toon.update_days;
    card.appendChild(days);

    return card;
}

// 웹툰 목록 로드
async function loadWebtoons() {
    const grid = document.getElementById('webtoon-grid');
    grid.innerHTML = '<div class="message">불러오는 중...</div>';

    try {
        const user = await checkAuth();
        const params = { provider: currentProvider };
        if (currentQuery) params.q = currentQuery;

        const webtoons = await api.getWebtoons(params);

        grid.innerHTML = '';
        if (webtoons.length === 0) {
            grid.innerHTML = '<div class="message"><div class="message-icon">📚</div><p>웹툰이 없습니다.</p></div>';
            return;
        }

        webtoons.forEach(toon => {
            const card = createWebtoonCard(toon, !!user);
            grid.appendChild(card);
        });
    } catch (e) {
        grid.innerHTML = '<div class="message" style="color:#c33;">로딩 중 오류가 발생했습니다.</div>';
    }
}

// 이벤트 바인딩
document.addEventListener('DOMContentLoaded', () => {
    // 필터 버튼
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentProvider = btn.dataset.provider;
            loadWebtoons();
        });
    });

    // 검색 폼
    document.getElementById('search-form')?.addEventListener('submit', (e) => {
        e.preventDefault();
        currentQuery = document.getElementById('query-input').value.trim();
        loadWebtoons();
    });

    loadWebtoons();
});
