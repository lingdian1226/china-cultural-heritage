// iBo Heritage Chat - Smart Local Engine
(function() {
  const fab = document.getElementById('chatFab');
  const panel = document.getElementById('chatPanel');
  const closeBtn = document.getElementById('chatClose');
  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('chatSend');
  const body = document.getElementById('chatBody');
  let isOpen = false;

  fab.addEventListener('click', () => { isOpen = !isOpen; panel.classList.toggle('open', isOpen); fab.classList.toggle('hidden', isOpen); if (isOpen) input.focus(); });
  closeBtn.addEventListener('click', () => { isOpen = false; panel.classList.remove('open'); fab.classList.remove('hidden'); });
  document.querySelectorAll('.quick-btn').forEach(btn => { btn.addEventListener('click', () => sendMessage(btn.dataset.q)); });
  input.addEventListener('keydown', e => { if (e.key === 'Enter' && input.value.trim()) sendMessage(input.value.trim()); });
  sendBtn.addEventListener('click', () => { if (input.value.trim()) sendMessage(input.value.trim()); });

  function sendMessage(text) {
    appendMsg('user', text);
    input.value = '';
    setTimeout(() => {
      const answer = smartAnswer(text);
      appendMsg('bot', answer);
    }, 200 + Math.random() * 300);
  }

  function appendMsg(role, html) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    div.innerHTML = `<div class="chat-bubble">${html}</div>`;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }

  // ===== Smart Answer Engine =====
  const data = typeof HERITAGE_DATA !== 'undefined' ? HERITAGE_DATA : [];
  const catNames = {
    'archaeological-sites': '古遗址', 'ancient-tombs': '古墓葬',
    'ancient-buildings': '古建筑', 'stone-carvings': '石窟寺及石刻',
    'modern-historic': '近现代重要史迹', 'others': '其他'
  };
  const catKeys = Object.fromEntries(Object.entries(catNames).map(([k,v]) => [v,k]));

  // Province short → full mapping for search
  const provShort = {
    '北京':'北京市','天津':'天津市','上海':'上海市','重庆':'重庆市',
    '河北':'河北省','山西':'山西省','辽宁':'辽宁省','吉林':'吉林省',
    '黑龙江':'黑龙江省','江苏':'江苏省','浙江':'浙江省','安徽':'安徽省',
    '福建':'福建省','江西':'江西省','山东':'山东省','河南':'河南省',
    '湖北':'湖北省','湖南':'湖南省','广东':'广东省','海南':'海南省',
    '四川':'四川省','贵州':'贵州省','云南':'云南省','陕西':'陕西省',
    '甘肃':'甘肃省','青海':'青海省','内蒙古':'内蒙古自治区',
    '广西':'广西壮族自治区','西藏':'西藏自治区','宁夏':'宁夏回族自治区',
    '新疆':'新疆维吾尔自治区'
  };

  function findProvince(text) {
    // Try full name first
    for (const d of data) {
      if (d.province && text.includes(d.province)) return d.province;
    }
    // Try short name
    for (const [short, full] of Object.entries(provShort)) {
      if (text.includes(short)) return full;
    }
    return null;
  }

  function findCategory(text) {
    for (const [cn, key] of Object.entries(catKeys)) {
      if (text.includes(cn)) return { key, name: cn };
    }
    if (text.includes('古塔') || text.includes('塔')) return { key: 'ancient-buildings', name: '古建筑', subFilter: '塔' };
    if (text.includes('寺庙') || text.includes('寺') || text.includes('庙')) return { key: 'ancient-buildings', name: '古建筑', subFilter: '寺|庙' };
    if (text.includes('桥')) return { key: 'ancient-buildings', name: '古建筑', subFilter: '桥' };
    if (text.includes('城墙') || text.includes('城')) return { key: null, name: null, subFilter: '城' };
    return null;
  }

  function findEra(text) {
    const eras = ['新石器','商','周','春秋','战国','秦','汉','三国','晋','南北朝',
      '隋','唐','五代','宋','辽','金','元','明','清','民国','近代','现代',
      '北魏','北齐','东汉','西汉','南宋','北宋','西夏','东晋','西晋'];
    for (const era of eras) {
      if (text.includes(era)) return era;
    }
    return null;
  }

  function provStats(province) {
    const items = data.filter(d => d.province === province);
    if (!items.length) return null;
    const cats = {};
    items.forEach(i => { const c = catNames[i.category] || i.category; cats[c] = (cats[c]||0)+1; });
    const bats = {};
    items.forEach(i => { if(i.batch) bats[i.batch] = (bats[i.batch]||0)+1; });
    return { items, cats, bats, total: items.length };
  }

  function smartAnswer(q) {
    const clean = q.replace(/[？?！!。，,、\s]+/g, '');
    
    // === Total count ===
    if (/总共|一共|总数|全部|总计|多少项|数据库/.test(q) && !/哪|什么省|什么市/.test(q)) {
      const provSet = new Set(data.map(d => d.province));
      return `📊 数据库共收录 <strong>${data.length}</strong> 项全国重点文物保护单位<br><br>` +
        `🗺️ 覆盖 ${provSet.size} 个省份<br>` +
        `📅 从第一批（1961年）到第八批（2019年）<br><br>` +
        `你可以问我任何省份、分类或朝代的文物信息 😊`;
    }

    // === Province query ===
    const prov = findProvince(q);
    if (prov && (/多少|几个|几项|有哪些|列表|统计|文物/.test(q) || q.length < 10)) {
      const ps = provStats(prov);
      if (!ps) return `没有找到${prov}的数据 🤔`;
      let catList = Object.entries(ps.cats).sort((a,b) => b[1]-a[1]).map(([k,v]) => `${k} ${v}项`).join('<br>');
      let famous = ps.items.filter(i => i.batch && i.batch <= 3).slice(0, 5);
      let famousStr = famous.length ? '<br><br>🌟 代表性文物：<br>' + famous.map(i => `• ${i.name}（${i.era}）`).join('<br>') : '';
      return `🏛️ <strong>${prov}</strong>共有 <strong>${ps.total}</strong> 项全国重点文物保护单位<br><br>` +
        `📋 分类：<br>${catList}${famousStr}`;
    }

    // === Province + Category ===
    const cat = findCategory(q);
    if (prov && cat) {
      let items = data.filter(d => d.province === prov);
      if (cat.key) items = items.filter(d => d.category === cat.key);
      if (cat.subFilter) items = items.filter(d => new RegExp(cat.subFilter).test(d.name));
      if (!items.length) return `${prov}没有找到相关的${cat.name || ''}文物 🤷`;
      let list = items.slice(0, 20).map(i => `• <strong>${i.name}</strong>（${i.era}）第${i.batch}批`).join('<br>');
      return `${prov}的${cat.name || ''}${cat.subFilter ? `(含"${cat.subFilter}")` : ''} 共 <strong>${items.length}</strong> 项：<br><br>${list}` +
        (items.length > 20 ? `<br><br>...还有 ${items.length - 20} 项，去搜索页面查看更多` : '');
    }

    // === Ranking ===
    if (/哪个省|排名|排行|最多|第一/.test(q)) {
      if (cat && cat.key) {
        // Category ranking by province
        const pc = {};
        data.filter(d => d.category === cat.key).forEach(d => { pc[d.province] = (pc[d.province]||0)+1; });
        const sorted = Object.entries(pc).sort((a,b) => b[1]-a[1]).slice(0, 10);
        let list = sorted.map(([p,c], i) => `${i+1}. ${p} <strong>${c}</strong>项`).join('<br>');
        return `🏆 ${cat.name}省份排行 Top10：<br><br>${list}`;
      }
      const pc = {};
      data.forEach(d => { pc[d.province] = (pc[d.province]||0)+1; });
      const sorted = Object.entries(pc).sort((a,b) => b[1]-a[1]).slice(0, 10);
      let list = sorted.map(([p,c], i) => `${i+1}. ${p} <strong>${c}</strong>项`).join('<br>');
      return `🏆 全国重点文物保护单位省份排行 Top10：<br><br>${list}<br><br>` +
        `${sorted[0][0]}以 ${sorted[0][1]} 项位居榜首！`;
    }

    // === Category query ===
    if (cat && !prov) {
      let items = cat.key ? data.filter(d => d.category === cat.key) : data;
      if (cat.subFilter) items = items.filter(d => new RegExp(cat.subFilter).test(d.name));
      
      if (/Top|top|推荐|著名|有名/.test(q)) {
        const famous = items.filter(i => i.batch && i.batch <= 2).slice(0, 10);
        const show = famous.length ? famous : items.slice(0, 10);
        let list = show.map((d, i) => `${i+1}. <strong>${d.name}</strong>（${d.era}）- ${d.province}`).join('<br>');
        return `🏯 ${cat.name || ''}${cat.subFilter ? `(含"${cat.subFilter}")` : ''} 推荐：<br><br>${list}<br><br>共 ${items.length} 项`;
      }
      
      return `📊 ${cat.name || '文物'}${cat.subFilter ? `(含"${cat.subFilter}")` : ''} 共 <strong>${items.length}</strong> 项<br><br>` +
        `部分列表：<br>` + items.slice(0, 10).map(d => `• ${d.name} - ${d.province}（${d.era}）`).join('<br>') +
        (items.length > 10 ? `<br><br>...还有更多，可在搜索页面查看` : '');
    }

    // === Era query ===
    const era = findEra(q);
    if (era) {
      const items = data.filter(d => d.era && d.era.includes(era));
      if (!items.length) return `没有找到${era}时期的文物记录 🤔`;
      const provs = {};
      items.forEach(i => { provs[i.province] = (provs[i.province]||0)+1; });
      const topProvs = Object.entries(provs).sort((a,b) => b[1]-a[1]).slice(0, 5);
      let list = items.slice(0, 10).map(d => `• <strong>${d.name}</strong> - ${d.province}（${catNames[d.category]||''}）`).join('<br>');
      return `📜 ${era}时期文物共 <strong>${items.length}</strong> 项<br><br>` +
        `主要分布: ${topProvs.map(([p,c]) => `${p}(${c})`).join('、')}<br><br>` +
        `代表文物：<br>${list}` +
        (items.length > 10 ? `<br><br>...还有 ${items.length - 10} 项` : '');
    }

    // === Batch query ===
    const batchMatch = q.match(/第([一二三四五六七八1-8])批/);
    if (batchMatch) {
      const numMap = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8};
      const bn = numMap[batchMatch[1]] || parseInt(batchMatch[1]);
      let items = data.filter(d => d.batch === bn);
      
      if (cat) {
        if (cat.key) items = items.filter(d => d.category === cat.key);
        if (cat.subFilter) items = items.filter(d => new RegExp(cat.subFilter).test(d.name));
      }
      
      const cats = {};
      items.forEach(i => { const c = catNames[i.category]||i.category; cats[c] = (cats[c]||0)+1; });
      let catStr = Object.entries(cats).sort((a,b) => b[1]-a[1]).map(([k,v]) => `${k} ${v}项`).join('、');
      const years = {1:1961,2:1982,3:1988,4:1996,5:2001,6:2006,7:2013,8:2019};
      return `📅 第${bn}批全国重点文物保护单位（${years[bn]}年公布）<br><br>` +
        `共 <strong>${items.length}</strong> 项${cat ? (cat.name||'') : ''}<br>` +
        (!cat ? `分类: ${catStr}<br><br>` : '<br>') +
        `部分列表：<br>` + items.slice(0, 10).map(d => `• ${d.name} - ${d.province}（${d.era}）`).join('<br>') +
        (items.length > 10 ? `<br><br>...还有 ${items.length - 10} 项` : '');
    }

    // === Name search / "介绍" ===
    const introMatch = q.match(/介绍(?:一下)?(.+)|(.+?)(?:是什么|在哪|在哪里|的(?:介绍|信息|资料))/);
    if (introMatch) {
      const kw = (introMatch[1] || introMatch[2]).replace(/[？?！!。，,\s]/g, '').trim();
      return searchByName(kw);
    }

    // === Generic search ===
    const searchResult = searchByName(clean);
    if (searchResult !== null) return searchResult;

    // === Fallback ===
    return `🤔 这个问题我暂时回答不了...<br><br>你可以试试：<br>` +
      `• 问某个省份有多少文物<br>• 查某个朝代的文物<br>• 搜索某个具体文物的名称<br>• 问哪个省文物最多<br><br>` +
      `或者去 <a href="https://t.me/iBo_assistant_bot" target="_blank">Telegram</a> 找我深入聊 💬`;
  }

  function searchByName(kw) {
    if (!kw || kw.length < 2) return null;
    const exact = data.filter(d => d.name === kw);
    if (exact.length === 1) return itemDetail(exact[0]);
    
    const items = data.filter(d => d.name.includes(kw));
    if (items.length === 1) return itemDetail(items[0]);
    if (items.length > 1 && items.length <= 30) {
      let list = items.map(d => `• <strong>${d.name}</strong> - ${d.province}（${d.era}，第${d.batch}批）`).join('<br>');
      return `🔍 找到 <strong>${items.length}</strong> 条含"${kw}"的结果：<br><br>${list}`;
    }
    if (items.length > 30) {
      return `🔍 找到 <strong>${items.length}</strong> 条含"${kw}"的结果，太多了！请用更具体的关键词，或到搜索页面筛选。`;
    }
    return null;
  }

  function itemDetail(item) {
    return `🏛️ <strong>${item.name}</strong><br><br>` +
      `📍 ${item.province} ${item.city || ''}<br>` +
      `⏳ 时代: ${item.era}<br>` +
      `🏷️ 分类: ${catNames[item.category] || item.category}<br>` +
      `📅 批次: 第${item.batch}批<br>` +
      `🔢 编号: ${item.id}` +
      (item.description ? `<br><br>📖 ${item.description}` : '') +
      `<br><br>想了解更多？在 <a href="https://t.me/iBo_assistant_bot?text=${encodeURIComponent('介绍一下'+item.name)}" target="_blank">Telegram</a> 问我 😊`;
  }

})();
