(function() {
  var script = document.currentScript;
  var apiUrl = script?.dataset?.apiUrl || '/api';
  var position = script?.dataset?.position || 'bottom-right';
  
  var widget = document.createElement('div');
  widget.id = 'opentoad-widget';
  widget.innerHTML = `
    <div id="opentoad-chat" class="hidden">
      <div id="opentoad-messages">
        <div class="message assistant">你好！我是 OpenToad AI 助手</div>
      </div>
      <div id="opentoad-input-container">
        <input id="opentoad-input" type="text" placeholder="发送消息..." />
        <button id="opentoad-send">发送</button>
      </div>
    </div>
    <button id="opentoad-toggle">🤖</button>
  `;
  
  var style = document.createElement('style');
  style.textContent = `
    #opentoad-widget { position: fixed; ${position}: 20px; z-index: 999999; }
    #opentoad-widget * { margin: 0; padding: 0; box-sizing: border-box; }
    #opentoad-toggle { width: 60px; height: 60px; border-radius: 50%; border: none; background: linear-gradient(135deg, #667eea, #764ba2); color: white; font-size: 28px; cursor: pointer; box-shadow: 0 4px 15px rgba(102,126,234,0.4); }
    #opentoad-chat { position: absolute; bottom: 80px; right: 0; width: 380px; height: 500px; background: white; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); display: flex; flex-direction: column; overflow: hidden; }
    #opentoad-chat.hidden { display: none; }
    #opentoad-messages { flex: 1; padding: 16px; overflow-y: auto; background: #f8f9fa; }
    .message { margin-bottom: 12px; padding: 10px 14px; border-radius: 12px; max-width: 85%; line-height: 1.5; }
    .message.user { background: linear-gradient(135deg, #667eea, #764ba2); color: white; margin-left: auto; border-bottom-right-radius: 4px; }
    .message.assistant { background: white; color: #333; border: 1px solid #e5e7eb; border-bottom-left-radius: 4px; }
    #opentoad-input-container { padding: 12px; border-top: 1px solid #e5e7eb; display: flex; gap: 8px; }
    #opentoad-input { flex: 1; padding: 10px 14px; border: 1px solid #e5e7eb; border-radius: 20px; outline: none; font-size: 14px; }
    #opentoad-input:focus { border-color: #667eea; }
    #opentoad-send { padding: 10px 16px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 20px; cursor: pointer; font-size: 14px; }
  `;
  
  document.head.appendChild(style);
  document.body.appendChild(widget);
  
  var toggle = document.getElementById('opentoad-toggle');
  var chat = document.getElementById('opentoad-chat');
  var input = document.getElementById('opentoad-input');
  var sendBtn = document.getElementById('opentoad-send');
  var messages = document.getElementById('opentoad-messages');
  
  toggle.addEventListener('click', function() {
    chat.classList.toggle('hidden');
    if (!chat.classList.contains('hidden')) input.focus();
  });
  
  function addMessage(content, isUser) {
    var div = document.createElement('div');
    div.className = 'message ' + (isUser ? 'user' : 'assistant');
    div.textContent = content;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }
  
  function sendMessage() {
    var content = input.value.trim();
    if (!content) return;
    input.value = '';
    addMessage(content, true);
    
    var sessionId = localStorage.getItem('opentoad-session') || crypto.randomUUID();
    localStorage.setItem('opentoad-session', sessionId);
    
    fetch(apiUrl + '/webhook', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: content, sessionId: sessionId })
    }).then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.reply) addMessage(data.reply, false);
      }).catch(function() {
        addMessage('抱歉，发送失败了。', false);
      });
  }
  
  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') sendMessage();
  });
})();