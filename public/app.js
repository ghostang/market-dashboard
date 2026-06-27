const DATA_URL = './data/dashboard.json';

const fmt = new Intl.NumberFormat('ko-KR', { maximumFractionDigits: 2 });
const pct = value => value == null ? '-' : `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
const money = value => value == null ? '-' : fmt.format(value);

async function loadDashboard() {
  const response = await fetch(`${DATA_URL}?t=${Date.now()}`);
  if (!response.ok) throw new Error(`dashboard.json load failed: ${response.status}`);
  const data = await response.json();
  if (data.mock_data !== false) throw new Error('mock_data must be false for the published dashboard');
  render(data);
}

function render(data) {
  document.getElementById('lastUpdated').textContent = `마지막 업데이트: ${formatDateTime(data.generated_at)}`;
  document.getElementById('dataBadge').textContent = data.mock_data ? 'mock 차단 필요' : '실제 소스';
  renderTickerCards(data.market_cards || []);
  renderWatchlist((data.market_cards || []).slice(1, 7));
  renderComparison(data.market_comparison || []);
  renderValueChain(data.value_chain || { themes: [] });
  renderFavoriteSources(data.favorite_sources || { sources: [], items: [] });
  renderSourceStatus(data.source_status || []);
  renderSignals(data.signals || []);
  renderCompanyFacts(data.company_metrics || []);
}

function renderTickerCards(cards) {
  const root = document.getElementById('market');
  root.innerHTML = '';
  cards.slice(0, 6).forEach(card => {
    const el = document.createElement('article');
    el.className = 'ticker-card';
    const positive = (card.change_pct || 0) >= 0;
    el.innerHTML = `
      <h3>${escapeHtml(card.name)} <span class="muted">${escapeHtml(card.ticker)}</span></h3>
      <div class="value">${money(card.value)}</div>
      <div class="change ${positive ? 'positive' : 'negative'}">${card.change >= 0 ? '+' : ''}${money(card.change)} (${pct(card.change_pct)})</div>
      <canvas class="spark" width="230" height="48" data-series='${JSON.stringify((card.series || []).map(r => r.close))}'></canvas>
      <div class="card-meta"><span>${card.latest_date || '-'}</span><span>${card.refresh_status}</span></div>
    `;
    root.appendChild(el);
  });
  root.querySelectorAll('canvas.spark').forEach(canvas => drawSparkline(canvas, JSON.parse(canvas.dataset.series || '[]')));
}

function renderWatchlist(cards) {
  const root = document.getElementById('watchlistRows');
  root.innerHTML = cards.map(card => {
    const positive = (card.change_pct || 0) >= 0;
    return `<div class="watch-row"><span>${escapeHtml(card.name)}</span><span class="price">${money(card.value)}</span><span class="${positive ? 'positive' : 'negative'}">${pct(card.change_pct)}</span></div>`;
  }).join('');
}

function renderComparison(series) {
  const canvas = document.getElementById('comparisonChart');
  const ctx = canvas.getContext('2d');
  const rect = canvas.getBoundingClientRect();
  const scale = window.devicePixelRatio || 1;
  canvas.width = Math.max(760, Math.floor(rect.width * scale));
  canvas.height = Math.floor(300 * scale);
  ctx.scale(scale, scale);
  const width = canvas.width / scale;
  const height = canvas.height / scale;
  ctx.clearRect(0, 0, width, height);
  const pad = { l: 44, r: 16, t: 16, b: 36 };
  ctx.strokeStyle = '#e5eaf3';
  ctx.lineWidth = 1;
  for (let i = 0; i < 6; i++) {
    const y = pad.t + (height - pad.t - pad.b) * i / 5;
    ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(width - pad.r, y); ctx.stroke();
  }
  const colors = ['#1d4ed8', '#f97316', '#16a34a', '#7c3aed', '#dc2626'];
  let all = [];
  const normalized = series.slice(0, 5).map((s, idx) => {
    const values = (s.series || []).map(r => r.close).filter(v => typeof v === 'number');
    const base = values[0] || 1;
    const norm = values.map(v => v / base * 100);
    all = all.concat(norm);
    return { name: s.name, values: norm, color: colors[idx % colors.length] };
  }).filter(s => s.values.length > 1);
  const min = Math.min(...all, 90), max = Math.max(...all, 110);
  const span = Math.max(1, max - min);
  normalized.forEach(s => {
    ctx.strokeStyle = s.color; ctx.lineWidth = 2; ctx.beginPath();
    s.values.forEach((v, i) => {
      const x = pad.l + (width - pad.l - pad.r) * i / (s.values.length - 1);
      const y = pad.t + (height - pad.t - pad.b) * (1 - (v - min) / span);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();
  });
  ctx.font = '12px system-ui';
  normalized.forEach((s, i) => {
    const x = pad.l + i * 118;
    ctx.fillStyle = s.color; ctx.fillRect(x, height - 22, 22, 3);
    ctx.fillStyle = '#344054'; ctx.fillText(s.name, x + 28, height - 17);
  });
}

function renderValueChain(valueChain) {
  const root = document.getElementById('valueChainThemes');
  root.innerHTML = (valueChain.themes || []).map(theme => {
    const okReps = (theme.representatives || []).filter(rep => rep.refresh_status === 'ok');
    const returnClass = (theme.basket_return_1m || 0) >= 0 ? 'positive' : 'negative';
    const reps = (theme.representatives || []).slice(0, 4).map(rep => `
      <div class="theme-rep">
        <span>${escapeHtml(rep.company)}</span>
        <strong class="${(rep.return_1m || 0) >= 0 ? 'positive' : 'negative'}">${pct(rep.return_1m)}</strong>
      </div>
    `).join('');
    return `
      <section class="theme-card status-${escapeHtml(theme.refresh_status)}">
        <div class="theme-top"><h3>${escapeHtml(theme.label)}</h3><span>${escapeHtml(theme.refresh_status)}</span></div>
        <div class="theme-return ${returnClass}">${pct(theme.basket_return_1m)}</div>
        <p>${escapeHtml(theme.description)}</p>
        <div class="theme-reps">${reps}</div>
        <small>${okReps.length}/${(theme.representatives || []).length} real-source tickers · 점유율/유료 가격은 fake로 채우지 않음</small>
      </section>
    `;
  }).join('');
}

function renderFavoriteSources(favoriteSources) {
  const sourceRoot = document.getElementById('favoriteSourceRows');
  sourceRoot.innerHTML = (favoriteSources.sources || []).map(source => `
    <div class="favorite-source status-${escapeHtml(source.refresh_status)}">
      <div><strong>${escapeHtml(source.source_name)}</strong><small>${escapeHtml(source.source_type)}</small></div>
      <span>${escapeHtml(source.refresh_status)}</span>
    </div>
  `).join('');
  const itemRoot = document.getElementById('favoriteItemRows');
  const items = (favoriteSources.items || []).slice(0, 5);
  itemRoot.innerHTML = items.length ? items.map(item => `
    <a class="favorite-item" href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">
      <strong>${escapeHtml(item.title)}</strong>
      <span>${escapeHtml(item.published_at || '')}</span>
      <small>${(item.tags || []).map(escapeHtml).join(' · ')}</small>
    </a>
  `).join('') : '<div class="empty-state compact"><strong>자동 수집 항목 없음</strong><p>BOK/Toss는 endpoint 확정 전 manual_real로 표시합니다.</p></div>';
}

function renderSourceStatus(rows) {
  const root = document.getElementById('sourceStatusRows');
  root.innerHTML = rows.map(row => `
    <div class="status-row">
      <div><strong>${escapeHtml(row.area)}</strong><small>${escapeHtml(row.source_name || '')}</small></div>
      <div class="status-${escapeHtml(row.refresh_status)}">${escapeHtml(row.refresh_status)}</div>
    </div>
  `).join('');
}

function renderSignals(signals) {
  const root = document.getElementById('signalRows');
  root.innerHTML = signals.map(s => `
    <tr><td>${escapeHtml(s.label)}</td><td><span class="signal-dot"><span class="dot ${escapeHtml(s.status)}"></span>${escapeHtml(s.status)}</span></td><td>${escapeHtml(s.reason)}</td></tr>
  `).join('');
}

function renderCompanyFacts(metrics) {
  const root = document.getElementById('companyFacts');
  root.innerHTML = metrics.map(company => {
    const rows = Object.entries(company.metrics || {}).map(([key, metric]) => `<div class="fact-row"><span>${labelMetric(key)} · ${escapeHtml(metric.period || '')}</span><strong>${compactUsd(metric.value)}</strong></div>`).join('') || '<p class="muted">실제 SEC fact 수집 실패</p>';
    return `<div class="fact-card"><h3>${escapeHtml(company.company)}</h3>${rows}<div class="card-meta"><span>${escapeHtml(company.refresh_status)}</span><span>SEC</span></div></div>`;
  }).join('');
}

function labelMetric(key) { return { revenue: 'Revenue', gross_profit: 'Gross Profit', net_income: 'Net Income' }[key] || key; }
function compactUsd(value) { if (value == null) return '-'; const abs = Math.abs(value); if (abs >= 1e9) return `$${(value/1e9).toFixed(1)}B`; if (abs >= 1e6) return `$${(value/1e6).toFixed(1)}M`; return `$${fmt.format(value)}`; }
function formatDateTime(iso) { if (!iso) return '-'; return new Date(iso).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul', hour12: false }); }
function escapeHtml(value) { return String(value ?? '').replace(/[&<>"']/g, ch => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[ch])); }

function drawSparkline(canvas, values) {
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  if (!values.length) return;
  const min = Math.min(...values), max = Math.max(...values), span = Math.max(1e-9, max - min);
  ctx.strokeStyle = '#ff1f1f'; ctx.lineWidth = 2; ctx.beginPath();
  values.forEach((v, i) => {
    const x = 4 + (w - 8) * i / Math.max(1, values.length - 1);
    const y = 5 + (h - 10) * (1 - (v - min) / span);
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();
}

document.getElementById('refreshButton').addEventListener('click', () => loadDashboard().catch(showError));
window.addEventListener('resize', () => loadDashboard().catch(showError));
function showError(error) { document.body.insertAdjacentHTML('afterbegin', `<div style="position:fixed;z-index:10;left:250px;top:12px;background:#fee2e2;color:#991b1b;padding:10px 14px;border-radius:8px">${escapeHtml(error.message)}</div>`); }
loadDashboard().catch(showError);
