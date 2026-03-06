// Chat Widget for iBo Heritage Assistant
(function() {
  const fab = document.getElementById('chatFab');
  const panel = document.getElementById('chatPanel');
  const closeBtn = document.getElementById('chatClose');
  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('chatSend');
  const body = document.getElementById('chatBody');
  let isOpen = false;

  // Toggle panel
  fab.addEventListener('click', () => {
    isOpen = !isOpen;
    panel.classList.toggle('open', isOpen);
    fab.classList.toggle('hidden', isOpen);
    if (isOpen) input.focus();
  });

  closeBtn.addEventListener('click', () => {
    isOpen = false;
    panel.classList.remove('open');
    fab.classList.remove('hidden');
  });

  // Quick action buttons
  document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const q = btn.dataset.q;
      sendMessage(q);
    });
  });

  // Send on Enter
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && input.value.trim()) {
      sendMessage(input.value.trim());
    }
  });

  sendBtn.addEventListener('click', () => {
    if (input.value.trim()) sendMessage(input.value.trim());
  });

  function sendMessage(text) {
    appendMsg('user', text);
    input.value = '';
    
    // Try to answer locally first
    const localAnswer = tryLocalAnswer(text);
    if (localAnswer) {
      setTimeout(() => appendMsg('bot', localAnswer), 300);
    } else {
      // Redirect to Telegram for complex questions
      setTimeout(() => {
        appendMsg('bot', '这个问题我需要更多思考 🤔<br><br>点击下方按钮，我在 Telegram 里详细回答你：');
        const linkDiv = document.createElement('div');
        linkDiv.className = 'chat-msg bot';
        linkDiv.innerHTML = `<a href="https://t.me/iBo_assistant_bot?text=${encodeURIComponent(text)}" target="_blank" class="tg-link">📱 在 Telegram 中继续对话</a>`;
        body.appendChild(linkDiv);
        scrollToBottom();
      }, 500);
    }
  }

  function appendMsg(role, html) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    div.innerHTML = `<div class="chat-bubble">${html}</div>`;
    body.appendChild(div);
    scrollToBottom();
  }

  function scrollToBottom() {
    body.scrollTop = body.scrollHeight;
  }

  // Local answer engine - use the loaded HERITAGE_DATA
  function tryLocalAnswer(q) {
    if (typeof HERITAGE_DATA === 'undefined') return null;
    const data = HERITAGE_DATA;
    const catNames = {
      'archaeological-sites': '古遗址',
      'ancient-tombs': '古墓葬',
      'ancient-buildings': '古建筑',
      'stone-carvings': '石窟寺及石刻',
      'modern-historic': '近现代重要史迹',
      'others': '其他',
    };

    // Province query: "XX有多少文物" / "XX的文物"
    const provMatch = q.match(/([\u4e00-\u9fa5]{2,})(?:有多少|的|文物|保护单位)/);
    if (provMatch) {
      const kw = provMatch[1];
      const items = data.filter(d => (d.province && d.province.includes(kw)) || (d.city && d.city.includes(kw)));
      if (items.length > 0) {
        const prov = items[0].province || kw;
        // Category breakdown
        const cats = {};
        items.forEach(i => { cats[i.category] = (cats[i.category] || 0) + 1; });
        let catList = Object.entries(cats)
          .sort((a,b) => b[1] - a[1])
          .map(([c, n]) => `${catNames[c] || c}: ${n}项`)
          .join('<br>');
        return `${prov}共有 <strong>${items.length}</strong> 项全国重点文物保护单位 🏛️<br><br>分类：<br>${catList}`;
      }
    }

    // "哪个省最多"
    if (q.includes('哪个省') && (q.includes('最多') || q.includes('排名'))) {
      const provCount = {};
      data.forEach(d => { if (d.province) provCount[d.province] = (provCount[d.province] || 0) + 1; });
      const sorted = Object.entries(provCount).sort((a,b) => b[1] - a[1]).slice(0, 10);
      let list = sorted.map(([p, n], i) => `${i+1}. ${p}: ${n}项`).join('<br>');
      return `全国重点文物保护单位省份排行 Top10：<br><br>${list}<br><br>🏆 ${sorted[0][0]}以 ${sorted[0][1]} 项位居榜首！`;
    }

    // "总共/一共多少"
    if (q.includes('总共') || q.includes('一共') || q.includes('总数')) {
      return `目前数据库共收录 <strong>${data.length}</strong> 项全国重点文物保护单位，涵盖第一批（1961年）至第八批（2019年）。`;
    }

    // Category query: "古建筑/古遗址 Top10/推荐"
    for (const [catKey, catName] of Object.entries(catNames)) {
      if (q.includes(catName) && (q.includes('Top') || q.includes('top') || q.includes('推荐') || q.includes('著名'))) {
        const items = data.filter(d => d.category === catKey);
        // Pick first-batch items as "famous"
        const famous = items.filter(d => d.batch <= 3).slice(0, 10);
        if (famous.length > 0) {
          let list = famous.map((d, i) => `${i+1}. <strong>${d.name}</strong>（${d.era}）- ${d.province}`).join('<br>');
          return `${catName}推荐 🏯<br><br>${list}<br><br>共有 ${items.length} 项${catName}类文物。`;
        }
      }
    }

    // Era query: "唐代/宋代/明代 文物"
    const eraMatch = q.match(/([\u4e00-\u9fa5]{1,3}(?:代|朝|时期|时代))/);
    if (eraMatch) {
      const era = eraMatch[1].replace('代', '').replace('朝', '');
      const items = data.filter(d => d.era && d.era.includes(era));
      if (items.length > 0) {
        const sample = items.slice(0, 8);
        let list = sample.map(d => `• <strong>${d.name}</strong> - ${d.province}（${d.era}）`).join('<br>');
        return `与"${era}"相关的文物共 <strong>${items.length}</strong> 项，例如：<br><br>${list}${items.length > 8 ? '<br><br>...还有更多，可在搜索页面查看' : ''}`;
      }
    }

    // Name search: "介绍XX" / "XX是什么"
    const introMatch = q.match(/介绍(?:一下)?(.+)|(.+?)(?:是什么|在哪)/);
    if (introMatch) {
      const kw = (introMatch[1] || introMatch[2]).trim();
      const item = data.find(d => d.name.includes(kw));
      if (item) {
        return `<strong>${item.name}</strong><br><br>` +
          `📍 ${item.province} ${item.city || ''}<br>` +
          `⏳ 时代：${item.era}<br>` +
          `🏷️ 分类：${catNames[item.category] || item.category}<br>` +
          `📋 批次：第${item.batch}批<br>` +
          `🔢 编号：${item.id}` +
          (item.description ? `<br><br>${item.description}` : '<br><br>详细介绍待补充，可以在 Telegram 中问我更多 😊');
      }
    }

    // Generic name search
    const nameItems = data.filter(d => d.name.includes(q.replace(/[？?。，,！!]/g, '').trim()));
    if (nameItems.length === 1) {
      const item = nameItems[0];
      return `<strong>${item.name}</strong><br>` +
        `📍 ${item.province} ${item.city || ''} | ⏳ ${item.era} | 🏷️ ${catNames[item.category] || item.category} | 第${item.batch}批`;
    } else if (nameItems.length > 1 && nameItems.length <= 20) {
      let list = nameItems.map(d => `• ${d.name}（${d.province}, ${d.era}）`).join('<br>');
      return `找到 ${nameItems.length} 条相关结果：<br><br>${list}`;
    }

    return null; // Fall through to Telegram
  }
})();
