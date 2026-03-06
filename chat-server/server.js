const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3002;

// Category mapping
const CAT_CN = {
  'archaeological-sites': '古遗址', 'ancient-tombs': '古墓葬',
  'ancient-buildings': '古建筑', 'stone-carvings': '石窟寺及石刻',
  'modern-historic': '近现代重要史迹', 'others': '其他'
};

// Load all data
const dataDir = path.join(__dirname, 'data');
const allItems = [];
for (const f of fs.readdirSync(dataDir).filter(f => f.endsWith('.json'))) {
  const raw = JSON.parse(fs.readFileSync(path.join(dataDir, f), 'utf8'));
  const items = raw.items || (Array.isArray(raw) ? raw : []);
  allItems.push(...items);
}
console.log(`Loaded ${allItems.length} items`);

// Build indices
const byProvince = {};
const byCategory = {};
const byBatch = {};
const byName = {};

allItems.forEach(item => {
  const p = item.province || '未知';
  const c = CAT_CN[item.category] || item.category || '未知';
  const b = item.batch || 0;
  (byProvince[p] = byProvince[p] || []).push(item);
  (byCategory[c] = byCategory[c] || []).push(item);
  (byBatch[b] = byBatch[b] || []).push(item);
  byName[item.name] = item;
});

// Smart answer engine
function answer(msg) {
  const q = msg.trim();
  
  // 1. Province query: "XX有多少/XX文物/XX的国保"
  for (const [prov, items] of Object.entries(byProvince)) {
    const short = prov.replace(/省|市|自治区|壮族|回族|维吾尔/, '');
    if (q.includes(short) && (q.includes('多少') || q.includes('文物') || q.includes('国保') || q.includes('保护') || q.includes('有哪些') || q.includes('几个') || q.includes('列表') || q.match(new RegExp(`^${short}$`)))) {
      const cats = {};
      items.forEach(i => { const c = CAT_CN[i.category]||i.category; cats[c] = (cats[c]||0)+1; });
      const catStr = Object.entries(cats).sort((a,b) => b[1]-a[1]).map(([k,v]) => `${k} ${v}项`).join('、');
      const famous = items.filter(i => i.batch <= 3).slice(0, 5);
      let reply = `${prov}共有 **${items.length}** 项全国重点文物保护单位 🏛️\n\n`;
      reply += `📊 分类：${catStr}\n\n`;
      if (famous.length) {
        reply += `🌟 早期入选的知名文物：\n` + famous.map(i => `• ${i.name}（${i.era}，第${i.batch}批）`).join('\n');
      }
      return reply;
    }
  }

  // 2. Category query: "古建筑/古遗址Top10/有哪些/推荐"
  for (const [cat, items] of Object.entries(byCategory)) {
    if (q.includes(cat) && (q.includes('Top') || q.includes('top') || q.includes('推荐') || q.includes('著名') || q.includes('有哪些') || q.includes('多少') || q.includes('几个'))) {
      if (q.includes('多少') || q.includes('几个')) {
        return `全国共有 **${items.length}** 项${cat}类文物保护单位 📊`;
      }
      const famous = items.filter(i => i.batch <= 2).slice(0, 10);
      if (!famous.length) famous.push(...items.slice(0, 10));
      return `${cat}推荐 🏯\n\n` +
        famous.map((i, idx) => `${idx+1}. **${i.name}**（${i.era}）— ${i.province}`).join('\n') +
        `\n\n共 ${items.length} 项${cat}类文物。`;
    }
  }

  // 3. Batch query: "第X批"
  const batchMatch = q.match(/第([一二三四五六七八\d])批/);
  if (batchMatch) {
    const batchMap = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8};
    const bnum = batchMap[batchMatch[1]] || parseInt(batchMatch[1]);
    const items = byBatch[bnum] || [];
    if (items.length) {
      const cats = {};
      items.forEach(i => { const c = CAT_CN[i.category]||i.category; cats[c] = (cats[c]||0)+1; });
      const catStr = Object.entries(cats).sort((a,b) => b[1]-a[1]).map(([k,v]) => `${k} ${v}项`).join('、');
      const years = {1:'1961年',2:'1982年',3:'1988年',4:'1996年',5:'2001年',6:'2006年',7:'2013年',8:'2019年'};
      return `第${bnum}批全国重点文物保护单位（${years[bnum] || ''}公布）\n\n` +
        `📊 共 **${items.length}** 项\n分类：${catStr}\n\n` +
        `🌟 代表性文物：\n` + items.slice(0, 8).map(i => `• ${i.name}（${i.province}，${i.era}）`).join('\n');
    }
  }

  // 4. Era query: "唐代/宋代/明清文物"
  const eraPatterns = [
    ['新石器', '新石器时代'], ['商', '商'], ['周', '周'], ['春秋', '春秋'], ['战国', '战国'],
    ['秦', '秦'], ['汉', '汉'], ['三国', '三国'], ['魏晋', '魏|晋'],
    ['南北朝', '南朝|北朝|北魏|东魏|西魏|北齐|北周'],
    ['隋', '隋'], ['唐', '唐'], ['五代', '五代'], ['宋', '宋|北宋|南宋'],
    ['辽', '辽'], ['金', '金'], ['元', '元'], ['明', '明'], ['清', '清'],
    ['民国', '民国'], ['近代', '近代|近现代']
  ];
  for (const [kw, pattern] of eraPatterns) {
    if (q.includes(kw) && (q.includes('文物') || q.includes('有哪些') || q.includes('著名') || q.includes('多少'))) {
      const regex = new RegExp(pattern);
      const items = allItems.filter(i => i.era && regex.test(i.era));
      if (items.length) {
        const sample = items.slice(0, 10);
        return `与"${kw}"相关的文物共 **${items.length}** 项 📜\n\n` +
          sample.map(i => `• **${i.name}**（${i.era}）— ${i.province}`).join('\n') +
          (items.length > 10 ? `\n\n...还有 ${items.length - 10} 项，可在搜索页面查看` : '');
      }
    }
  }

  // 5. Specific item: "介绍XX" / "XX是什么" / "XX在哪"
  const introMatch = q.match(/介绍(?:一下)?(.+)|(.+?)(?:是什么|在哪|在哪里|历史|简介)/);
  if (introMatch) {
    const kw = (introMatch[1] || introMatch[2]).trim();
    const item = allItems.find(i => i.name.includes(kw));
    if (item) {
      return `🏛️ **${item.name}**\n\n` +
        `📍 位置：${item.province} ${item.city || ''}\n` +
        `⏳ 时代：${item.era}\n` +
        `🏷️ 分类：${CAT_CN[item.category] || item.category}\n` +
        `📋 批次：第${item.batch}批\n` +
        `🔢 编号：${item.id}\n` +
        (item.description ? `\n📝 ${item.description}` : '\n💡 详细介绍待补充，欢迎在 Telegram 中问我更多！');
    }
  }

  // 6. "哪个省最多/排名"
  if ((q.includes('哪个省') || q.includes('排名') || q.includes('排行') || q.includes('最多')) && (q.includes('文物') || q.includes('国保') || q.includes('省'))) {
    const sorted = Object.entries(byProvince).sort((a,b) => b[1].length - a[1].length).slice(0, 15);
    return `🏆 全国重点文物保护单位省份排行 Top15：\n\n` +
      sorted.map(([p, items], i) => `${i+1}. ${p}：**${items.length}** 项`).join('\n') +
      `\n\n${sorted[0][0]}以 ${sorted[0][1].length} 项高居榜首！山西、河南、河北是文物大省 🏯`;
  }

  // 7. "总共/一共/总数"
  if (q.includes('总共') || q.includes('一共') || q.includes('总数') || q.includes('总计') || q === '统计') {
    return `📊 数据库共收录 **${allItems.length}** 项全国重点文物保护单位\n\n` +
      `覆盖 ${Object.keys(byProvince).length} 个省份，${Object.keys(byCategory).length} 个分类\n` +
      `从第一批（1961年）到第八批（2019年）`;
  }

  // 8. Keyword search: "塔/寺/庙/桥/城"
  const keywords = ['塔', '寺', '庙', '桥', '城', '墓', '窟', '碑', '楼', '园', '宫', '坊', '祠', '关', '堡'];
  for (const kw of keywords) {
    if (q.includes(kw) && (q.includes('有哪些') || q.includes('多少') || q.includes('搜索') || q.includes('查找') || q.includes('列表'))) {
      const items = allItems.filter(i => i.name.includes(kw));
      if (items.length) {
        const sample = items.slice(0, 12);
        return `名称含"${kw}"的文物共 **${items.length}** 项 🔍\n\n` +
          sample.map(i => `• ${i.name}（${i.province}，${i.era}）`).join('\n') +
          (items.length > 12 ? `\n\n...还有 ${items.length - 12} 项` : '');
      }
    }
  }

  // 9. Direct name search (fuzzy)
  const cleaned = q.replace(/[？?。，,！!有多少的在哪是什么介绍一下查询搜索]/g, '').trim();
  if (cleaned.length >= 2) {
    const matches = allItems.filter(i => i.name.includes(cleaned));
    if (matches.length === 1) {
      const item = matches[0];
      return `🏛️ **${item.name}**\n📍 ${item.province} ${item.city||''} | ⏳ ${item.era} | 🏷️ ${CAT_CN[item.category]||item.category} | 第${item.batch}批\n🔢 ${item.id}`;
    } else if (matches.length > 1 && matches.length <= 20) {
      return `找到 ${matches.length} 条与"${cleaned}"相关的结果：\n\n` +
        matches.map(i => `• **${i.name}**（${i.province}，${i.era}，${CAT_CN[i.category]||''}）`).join('\n');
    } else if (matches.length > 20) {
      return `"${cleaned}"相关的文物共 **${matches.length}** 项，太多了！请缩小范围，比如加上省份名或分类。`;
    }
  }

  // 10. Default: show what I can do
  return `🤔 没找到相关信息。我是文物百科助手，你可以这样问我：\n\n` +
    `📍 "上海有多少文物？"\n` +
    `🏯 "推荐古建筑Top10"\n` +
    `📜 "唐代有哪些文物？"\n` +
    `🔍 "介绍莫高窟"\n` +
    `🏆 "哪个省文物最多？"\n` +
    `📊 "第一批有多少？"\n` +
    `🏛️ 直接输入文物名称搜索\n\n` +
    `更复杂的问题？[在 Telegram 中找我](https://t.me/iBo_assistant_bot) 💬`;
}

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

  if (req.method === 'POST' && req.url === '/chat') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try {
        const { message } = JSON.parse(body);
        if (!message) { res.writeHead(400); res.end('{"error":"no message"}'); return; }
        const reply = answer(message);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ reply }));
      } catch(e) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
  } else if (req.url === '/health') {
    res.writeHead(200); res.end('ok');
  } else {
    res.writeHead(404); res.end('not found');
  }
});

server.listen(PORT, '127.0.0.1', () => console.log(`Heritage chat API on :${PORT}`));
