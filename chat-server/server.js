const http = require('http');
const fs = require('fs');
const path = require('path');

// Config
const PORT = 3002;
const GW_URL = 'http://127.0.0.1:3001'; // SSH tunnel to OpenClaw gateway
const GW_TOKEN = 'f67312b0d5ca5b31e29ffca0337a896cb1629272709a4b38e2718405dc34060e';
const MODEL = 'deepseek/deepseek-chat';

// Load heritage data for context injection
let heritageContext = '';
let allItems = [];
const catMap = {
  'archaeological-sites': '古遗址', 'ancient-tombs': '古墓葬',
  'ancient-buildings': '古建筑', 'stone-carvings': '石窟寺及石刻',
  'modern-historic': '近现代重要史迹', 'others': '其他'
};

try {
  const dataDir = path.join(__dirname, '..', 'data', 'national-level');
  const files = fs.readdirSync(dataDir).filter(f => f.endsWith('.json'));
  const provStats = {}, catStats = {};

  for (const file of files) {
    const raw = JSON.parse(fs.readFileSync(path.join(dataDir, file), 'utf8'));
    const items = raw.items || (Array.isArray(raw) ? raw : []);
    allItems.push(...items);
  }

  allItems.forEach(i => {
    provStats[i.province] = (provStats[i.province] || 0) + 1;
    catStats[catMap[i.category] || i.category] = (catStats[catMap[i.category] || i.category] || 0) + 1;
  });

  heritageContext = `数据库共${allItems.length}项全国重点文物保护单位，31省份，8批次(1961-2019)。\n`;
  heritageContext += 'TOP10省: ' + Object.entries(provStats).sort((a,b) => b[1]-a[1]).slice(0,10).map(([p,c]) => `${p}${c}`).join('、') + '\n';
  heritageContext += '分类: ' + Object.entries(catStats).sort((a,b) => b[1]-a[1]).map(([k,v]) => `${k}${v}`).join('、');

  console.log(`Loaded ${allItems.length} items`);
} catch(e) {
  console.error('Data load error:', e.message);
}

function searchItems(q, limit = 15) {
  const kw = q.toLowerCase().replace(/[？?！!。，,\s]/g, '');
  if (!kw) return '';
  const results = allItems.filter(i =>
    i.name.includes(kw) || (i.province && i.province.includes(kw)) ||
    (i.city && i.city.includes(kw)) || (i.era && i.era.includes(kw))
  ).slice(0, limit);
  if (!results.length) return '';
  return results.map(i =>
    `${i.name} | ${i.id} | ${i.province} ${i.city||''} | ${i.era} | ${catMap[i.category]||i.category} | 第${i.batch}批`
  ).join('\n');
}

function getProvinceStats(prov) {
  const items = allItems.filter(i => i.province && i.province.includes(prov));
  if (!items.length) return '';
  const cats = {};
  items.forEach(i => { const c = catMap[i.category]||i.category; cats[c] = (cats[c]||0)+1; });
  return `${items[0].province}共${items.length}项。分类: ${Object.entries(cats).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`${k}${v}`).join('、')}\n` +
    '代表: ' + items.slice(0, 10).map(i => i.name).join('、');
}

const SYSTEM = `你是 iBo ⚡，一个中国文化遗产百科助手，部署在全国重点文物保护单位查询网站上。

${heritageContext}

规则:
- 用中文回答，简洁有趣
- 尽量基于提供的数据回答
- 可以用emoji让回答更生动
- 回复控制在200字以内
- 如果用户问的不是文物相关问题，友好地引导回文物话题`;

// Forward to OpenClaw gateway
function callGateway(messages) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: MODEL,
      messages: messages,
      max_tokens: 600,
      temperature: 0.7
    });

    const req = http.request({
      hostname: '127.0.0.1', port: 3001,
      path: '/v1/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${GW_TOKEN}`,
        'Content-Length': Buffer.byteLength(body)
      }
    }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const r = JSON.parse(data);
          if (r.choices && r.choices[0]) resolve(r.choices[0].message.content);
          else reject(new Error('Bad response: ' + data.slice(0, 200)));
        } catch(e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.setTimeout(45000, () => { req.destroy(); reject(new Error('timeout')); });
    req.write(body);
    req.end();
  });
}

const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

  if (req.method === 'POST' && req.url === '/chat') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', async () => {
      try {
        const { message, history } = JSON.parse(body);
        if (!message) { res.writeHead(400); res.end('{"error":"no message"}'); return; }

        // Build context
        let ctx = '';
        const provMatch = message.match(/([\u4e00-\u9fa5]{2,8}(?:省|市|自治区)?)/g);
        if (provMatch) {
          for (const m of provMatch) {
            const info = getProvinceStats(m);
            if (info) { ctx += '\n[省份数据] ' + info; break; }
          }
        }
        const search = searchItems(message);
        if (search) ctx += '\n[搜索结果]\n' + search;

        const msgs = [
          { role: 'system', content: SYSTEM + ctx },
          ...(history || []).slice(-4),
          { role: 'user', content: message }
        ];

        const reply = await callGateway(msgs);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ reply }));
      } catch(e) {
        console.error('Error:', e.message);
        res.writeHead(500);
        res.end(JSON.stringify({ error: '服务暂时不可用，请稍后重试' }));
      }
    });
  } else if (req.url === '/health') {
    res.writeHead(200); res.end('ok');
  } else {
    res.writeHead(404); res.end('not found');
  }
});

server.listen(PORT, '127.0.0.1', () => console.log(`Chat API on :${PORT}`));
