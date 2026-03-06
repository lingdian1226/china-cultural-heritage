/* 全国重点文物保护单位查询系统 */
(function() {
'use strict';

// Category mapping
const CATEGORY_MAP = {
  'archaeological-sites': '古遗址',
  'ancient-tombs': '古墓葬',
  'ancient-buildings': '古建筑',
  'stone-carvings': '石窟寺及石刻',
  'modern-historic': '近现代重要史迹',
  'others': '其他',
  'gardens': '园林'
};

const CATEGORY_COLORS = {
  '古建筑': '#8B0000',
  '古遗址': '#2D5A27',
  '近现代重要史迹': '#1A3C5E',
  '古墓葬': '#4A2D7A',
  '石窟寺及石刻': '#8B6914',
  '其他': '#666',
  '园林': '#2D8A27'
};

// Process data
const data = HERITAGE_DATA.map(item => ({
  ...item,
  categoryName: CATEGORY_MAP[item.category] || item.category,
  batchNum: typeof item.batch === 'number' ? item.batch : parseInt(item.batch) || 0
}));

// State
let currentPage = 1;
const PAGE_SIZE = 50;
let filteredData = [...data];
let sortField = '';
let sortDir = 1;
let expandedRow = null;

// ===== Navigation =====
document.querySelectorAll('.nav-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('page-' + tab.dataset.page).classList.add('active');
  });
});

// ===== Dashboard =====
function initDashboard() {
  // Stats
  const provinces = new Set(data.map(d => d.province));
  const categories = new Set(data.map(d => d.categoryName));
  const batches = new Set(data.filter(d => d.batchNum > 0).map(d => d.batchNum));
  
  document.getElementById('statsGrid').innerHTML = `
    <div class="stat-card"><div class="number">${data.length.toLocaleString()}</div><div class="label">文物保护单位总数</div></div>
    <div class="stat-card"><div class="number">${provinces.size}</div><div class="label">覆盖省份</div></div>
    <div class="stat-card"><div class="number">${batches.size}</div><div class="label">公布批次</div></div>
    <div class="stat-card"><div class="number">${categories.size}</div><div class="label">文物分类</div></div>
  `;
  document.getElementById('footerCount').textContent = data.length.toLocaleString();

  // Batch chart
  const batchCounts = {};
  for (let i = 1; i <= 8; i++) batchCounts[i] = 0;
  data.forEach(d => { if (d.batchNum >= 1 && d.batchNum <= 8) batchCounts[d.batchNum]++; });
  
  new Chart(document.getElementById('batchChart'), {
    type: 'bar',
    data: {
      labels: Object.keys(batchCounts).map(b => '第' + b + '批'),
      datasets: [{
        label: '数量',
        data: Object.values(batchCounts),
        backgroundColor: 'rgba(139, 0, 0, 0.7)',
        borderColor: '#8B0000',
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  });

  // Category chart
  const catCounts = {};
  data.forEach(d => { catCounts[d.categoryName] = (catCounts[d.categoryName] || 0) + 1; });
  const sortedCats = Object.entries(catCounts).sort((a, b) => b[1] - a[1]);
  
  new Chart(document.getElementById('categoryChart'), {
    type: 'doughnut',
    data: {
      labels: sortedCats.map(c => c[0]),
      datasets: [{
        data: sortedCats.map(c => c[1]),
        backgroundColor: sortedCats.map(c => CATEGORY_COLORS[c[0]] || '#999'),
        borderWidth: 2,
        borderColor: '#FFFDF7'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom', labels: { font: { size: 12 } } }
      }
    }
  });

  // Province ranking
  const provCounts = {};
  data.forEach(d => { provCounts[d.province] = (provCounts[d.province] || 0) + 1; });
  const sortedProvs = Object.entries(provCounts).sort((a, b) => b[1] - a[1]);
  const top15 = sortedProvs.slice(0, 15);
  const maxCount = top15[0][1];
  
  document.getElementById('rankingList').innerHTML = top15.map((p, i) => `
    <li class="ranking-item" data-province="${p[0]}">
      <span class="ranking-rank ${i < 3 ? 'top3' : ''}">${i + 1}</span>
      <span class="ranking-name">${p[0]}</span>
      <span class="ranking-bar-wrap"><div class="ranking-bar" style="width:${(p[1]/maxCount*100).toFixed(1)}%"></div></span>
      <span class="ranking-count">${p[1]}</span>
    </li>
  `).join('');

  // Click ranking to go to province
  document.querySelectorAll('.ranking-item').forEach(item => {
    item.addEventListener('click', () => {
      showProvince(item.dataset.province);
    });
  });
}

// ===== Search & Filter =====
function initSearch() {
  // Province dropdown
  const provinces = [...new Set(data.map(d => d.province))].sort();
  const sel = document.getElementById('provinceFilter');
  provinces.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p; opt.textContent = p;
    sel.appendChild(opt);
  });

  // Batch chips
  const batchDiv = document.getElementById('batchFilter');
  for (let i = 1; i <= 8; i++) {
    batchDiv.innerHTML += `<span class="chip active" data-batch="${i}">第${i}批</span>`;
  }

  // Category chips
  const catDiv = document.getElementById('categoryFilter');
  Object.entries(CATEGORY_MAP).forEach(([key, name]) => {
    catDiv.innerHTML += `<span class="chip active" data-category="${key}">${name}</span>`;
  });

  // Chip toggle
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('active');
      applyFilters();
    });
  });

  // Input listeners
  document.getElementById('searchInput').addEventListener('input', () => applyFilters());
  document.getElementById('searchInput').addEventListener('keydown', (e) => { if (e.key === 'Enter') applyFilters(); });
  document.getElementById('searchBtn').addEventListener('click', () => applyFilters());
  document.getElementById('provinceFilter').addEventListener('change', () => applyFilters());
  document.getElementById('eraFilter').addEventListener('input', () => applyFilters());
  document.getElementById('eraFilter').addEventListener('keydown', (e) => { if (e.key === 'Enter') applyFilters(); });

  // Reset button
  document.getElementById('resetBtn').addEventListener('click', () => {
    document.getElementById('searchInput').value = '';
    document.getElementById('provinceFilter').value = '';
    document.getElementById('eraFilter').value = '';
    document.querySelectorAll('.chip').forEach(c => c.classList.add('active'));
    sortField = ''; sortDir = 1;
    document.querySelectorAll('.sort-arrow').forEach(a => a.textContent = '');
    applyFilters();
  });

  // Table sort
  document.querySelectorAll('thead th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const field = th.dataset.sort;
      if (sortField === field) sortDir *= -1;
      else { sortField = field; sortDir = 1; }
      applyFilters();
      // Update arrows
      document.querySelectorAll('.sort-arrow').forEach(a => a.textContent = '');
      th.querySelector('.sort-arrow').textContent = sortDir === 1 ? '▲' : '▼';
    });
  });

  applyFilters();
}

function applyFilters() {
  const query = document.getElementById('searchInput').value.trim().toLowerCase();
  const province = document.getElementById('provinceFilter').value;
  const era = document.getElementById('eraFilter').value.trim().toLowerCase();
  
  const activeBatches = new Set();
  document.querySelectorAll('#batchFilter .chip.active').forEach(c => {
    activeBatches.add(parseInt(c.dataset.batch));
  });
  
  const activeCategories = new Set();
  document.querySelectorAll('#categoryFilter .chip.active').forEach(c => {
    activeCategories.add(c.dataset.category);
  });

  filteredData = data.filter(item => {
    if (query && !item.name.toLowerCase().includes(query) && 
        !item.city.toLowerCase().includes(query)) return false;
    if (province && item.province !== province) return false;
    if (era && !item.era.toLowerCase().includes(era)) return false;
    if (item.batchNum > 0 && !activeBatches.has(item.batchNum)) return false;
    if (!activeCategories.has(item.category)) return false;
    return true;
  });

  // Sort
  if (sortField) {
    filteredData.sort((a, b) => {
      let va = sortField === 'category' ? a.categoryName : a[sortField];
      let vb = sortField === 'category' ? b.categoryName : b[sortField];
      if (sortField === 'batch') { va = a.batchNum; vb = b.batchNum; }
      if (va < vb) return -sortDir;
      if (va > vb) return sortDir;
      return 0;
    });
  }

  currentPage = 1;
  expandedRow = null;
  renderResults();
}

function renderResults() {
  const total = filteredData.length;
  const totalPages = Math.ceil(total / PAGE_SIZE);
  const start = (currentPage - 1) * PAGE_SIZE;
  const pageData = filteredData.slice(start, start + PAGE_SIZE);

  document.getElementById('resultCount').textContent = `共 ${total.toLocaleString()} 条结果`;
  document.getElementById('pageInfo').textContent = totalPages > 0 ? 
    `第 ${currentPage}/${totalPages} 页` : '';

  const tbody = document.getElementById('resultBody');
  tbody.innerHTML = pageData.map((item, idx) => {
    const globalIdx = start + idx;
    const catClass = 'cat-' + (item.category || 'others');
    let html = `<tr class="clickable" data-idx="${globalIdx}">
      <td><strong>${esc(item.name)}</strong></td>
      <td>${esc(item.id)}</td>
      <td>第${item.batchNum || '?'}批</td>
      <td><span class="cat-badge ${catClass}">${esc(item.categoryName)}</span></td>
      <td>${esc(item.province)}</td>
      <td>${esc(item.city)}</td>
      <td>${esc(item.era)}</td>
    </tr>`;
    if (expandedRow === globalIdx) {
      html += `<tr class="detail-row"><td colspan="7">
        <div class="detail-content"><div class="detail-grid">
          <div class="detail-field"><div class="field-label">编号</div><div class="field-value">${esc(item.id)}</div></div>
          <div class="detail-field"><div class="field-label">名称</div><div class="field-value">${esc(item.name)}</div></div>
          <div class="detail-field"><div class="field-label">批次</div><div class="field-value">第${item.batchNum || '?'}批</div></div>
          <div class="detail-field"><div class="field-label">分类</div><div class="field-value">${esc(item.categoryName)}</div></div>
          <div class="detail-field"><div class="field-label">省份</div><div class="field-value">${esc(item.province)}</div></div>
          <div class="detail-field"><div class="field-label">城市</div><div class="field-value">${esc(item.city)}</div></div>
          <div class="detail-field"><div class="field-label">区县</div><div class="field-value">${esc(item.district || '-')}</div></div>
          <div class="detail-field"><div class="field-label">时代</div><div class="field-value">${esc(item.era)}</div></div>
          <div class="detail-field"><div class="field-label">地址</div><div class="field-value">${esc(item.address || '-')}</div></div>
          ${item.description ? `<div class="detail-field" style="grid-column:1/-1"><div class="field-label">简介</div><div class="field-value">${esc(item.description)}</div></div>` : ''}
        </div></div>
      </td></tr>`;
    }
    return html;
  }).join('');

  // Click to expand
  tbody.querySelectorAll('tr.clickable').forEach(tr => {
    tr.addEventListener('click', () => {
      const idx = parseInt(tr.dataset.idx);
      expandedRow = expandedRow === idx ? null : idx;
      renderResults();
    });
  });

  // Pagination
  renderPagination(totalPages);
}

function renderPagination(totalPages) {
  const div = document.getElementById('pagination');
  if (totalPages <= 1) { div.innerHTML = ''; return; }
  
  let html = '';
  html += `<button class="page-btn" ${currentPage===1?'disabled':''} data-p="${currentPage-1}">‹ 上一页</button>`;
  
  const range = getPageRange(currentPage, totalPages);
  range.forEach(p => {
    if (p === '...') html += `<span class="page-btn" style="border:none;cursor:default">…</span>`;
    else html += `<button class="page-btn ${p===currentPage?'active':''}" data-p="${p}">${p}</button>`;
  });
  
  html += `<button class="page-btn" ${currentPage===totalPages?'disabled':''} data-p="${currentPage+1}">下一页 ›</button>`;
  div.innerHTML = html;
  
  div.querySelectorAll('button[data-p]').forEach(btn => {
    btn.addEventListener('click', () => {
      currentPage = parseInt(btn.dataset.p);
      expandedRow = null;
      renderResults();
      document.querySelector('.table-wrap').scrollIntoView({behavior:'smooth'});
    });
  });
}

function getPageRange(cur, total) {
  if (total <= 7) return Array.from({length: total}, (_, i) => i + 1);
  const pages = [];
  pages.push(1);
  if (cur > 3) pages.push('...');
  for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) pages.push(i);
  if (cur < total - 2) pages.push('...');
  pages.push(total);
  return pages;
}

// ===== Province Page =====
function initProvinces() {
  const provCounts = {};
  data.forEach(d => { provCounts[d.province] = (provCounts[d.province] || 0) + 1; });
  const sorted = Object.entries(provCounts).sort((a, b) => b[1] - a[1]);
  
  document.getElementById('provinceList').innerHTML = `
    <div class="card"><h3>🗺️ 选择省份查看文物保护单位</h3>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:0.8rem">
      ${sorted.map(([prov, count]) => `
        <div class="stat-card" style="cursor:pointer;border-top-color:var(--primary)" data-prov="${prov}">
          <div class="number" style="font-size:1.5rem">${count}</div>
          <div class="label">${prov}</div>
        </div>
      `).join('')}
    </div></div>
  `;

  document.querySelectorAll('#provinceList .stat-card').forEach(card => {
    card.addEventListener('click', () => showProvince(card.dataset.prov));
  });

  document.getElementById('backBtn').addEventListener('click', () => {
    document.getElementById('provinceDetail').style.display = 'none';
    document.getElementById('provinceList').style.display = '';
  });
}

function showProvince(province) {
  // Switch to province tab
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelector('[data-page="province"]').classList.add('active');
  document.getElementById('page-province').classList.add('active');
  
  document.getElementById('provinceList').style.display = 'none';
  document.getElementById('provinceDetail').style.display = '';
  document.getElementById('provinceTitle').textContent = province + ' 文物保护单位';

  const provData = data.filter(d => d.province === province);
  
  // Group by category
  const groups = {};
  provData.forEach(item => {
    const cat = item.categoryName;
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(item);
  });

  const catOrder = ['古建筑', '古遗址', '近现代重要史迹', '古墓葬', '石窟寺及石刻', '其他', '园林'];
  
  document.getElementById('provinceContent').innerHTML = catOrder
    .filter(cat => groups[cat])
    .map(cat => `
      <div class="card category-section">
        <h3>${cat}（${groups[cat].length}项）</h3>
        ${groups[cat].sort((a,b) => a.batchNum - b.batchNum).map(item => `
          <div class="heritage-item">
            <span class="item-name">${esc(item.name)}</span>
            <span class="item-meta">第${item.batchNum||'?'}批 · ${esc(item.era)} · ${esc(item.city)}</span>
          </div>
        `).join('')}
      </div>
    `).join('');
}

// Utility
function esc(s) {
  if (!s) return '';
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Init
initDashboard();
initSearch();
initProvinces();

})();
