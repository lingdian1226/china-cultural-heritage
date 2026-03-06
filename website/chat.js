// Chat Widget - iBo Heritage Assistant
(function() {
  const fab = document.getElementById('chatFab');
  const panel = document.getElementById('chatPanel');
  const closeBtn = document.getElementById('chatClose');
  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('chatSend');
  const body = document.getElementById('chatBody');
  let isOpen = false;
  let chatHistory = [];
  let isLoading = false;

  const API_URL = '/heritage/api/chat';

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
      if (!isLoading) sendMessage(btn.dataset.q);
    });
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && input.value.trim() && !isLoading) {
      sendMessage(input.value.trim());
    }
  });

  sendBtn.addEventListener('click', () => {
    if (input.value.trim() && !isLoading) sendMessage(input.value.trim());
  });

  async function sendMessage(text) {
    if (isLoading) return;
    appendMsg('user', escHtml(text));
    input.value = '';
    
    // Add to history
    chatHistory.push({ role: 'user', content: text });
    
    // Show typing indicator
    isLoading = true;
    const typingEl = showTyping();
    
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: chatHistory.slice(-6)
        })
      });
      
      removeTyping(typingEl);
      
      if (response.ok) {
        const data = await response.json();
        const reply = data.reply || '抱歉，我没有理解你的问题 😅';
        appendMsg('bot', formatReply(reply));
        chatHistory.push({ role: 'assistant', content: reply });
      } else {
        appendMsg('bot', '服务暂时不可用，请稍后重试 🔧');
      }
    } catch (e) {
      removeTyping(typingEl);
      appendMsg('bot', '网络连接失败，请检查网络后重试 🌐');
    }
    
    isLoading = false;
    // Keep history manageable
    if (chatHistory.length > 20) chatHistory = chatHistory.slice(-12);
  }

  function appendMsg(role, html) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    div.innerHTML = `<div class="chat-bubble">${html}</div>`;
    body.appendChild(div);
    scrollToBottom();
  }

  function showTyping() {
    const div = document.createElement('div');
    div.className = 'chat-msg bot typing-indicator';
    div.innerHTML = '<div class="chat-bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>';
    body.appendChild(div);
    scrollToBottom();
    return div;
  }

  function removeTyping(el) {
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  function scrollToBottom() {
    body.scrollTop = body.scrollHeight;
  }

  function escHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function formatReply(text) {
    // Convert markdown-like formatting to HTML
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>')
      .replace(/^- /gm, '• ')
      .replace(/`(.*?)`/g, '<code>$1</code>');
  }
})();
