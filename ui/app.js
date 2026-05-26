const chat = document.getElementById('chat');
const input = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const uploadBtn = document.getElementById('uploadBtn');
const filePicker = document.getElementById('filePicker');
const voiceBtn = document.getElementById('voiceBtn');
const tpl = document.getElementById('msgTemplate');

function addMessage(role, content) {
  const node = tpl.content.cloneNode(true);
  node.querySelector('.role').textContent = role;
  node.querySelector('.content').textContent = content;
  node.querySelector('.speak-btn').addEventListener('click', () => speak(content));
  chat.appendChild(node);
  chat.scrollTop = chat.scrollHeight;
}

function speak(text) {
  if (!('speechSynthesis' in window)) return;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1;
  utterance.pitch = 1;
  speechSynthesis.cancel();
  speechSynthesis.speak(utterance);
}

function mockAIResponse(userText) {
  return `Understood. I can help execute this task with routing, tool selection, and autonomous steps:\n\n${userText}`;
}

function sendMessage() {
  const text = input.value.trim();
  if (!text) return;
  addMessage('You', text);
  input.value = '';
  const reply = mockAIResponse(text);
  addMessage('AI Employee', reply);
}

sendBtn.addEventListener('click', sendMessage);
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendMessage();
});

uploadBtn.addEventListener('click', () => filePicker.click());
filePicker.addEventListener('change', () => {
  const names = [...filePicker.files].map((f) => f.name).join(', ');
  if (names) addMessage('System', `Files queued for AI analysis: ${names}`);
});

voiceBtn.addEventListener('click', () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    addMessage('System', 'Voice input is not supported in this browser.');
    return;
  }
  const rec = new SpeechRecognition();
  rec.lang = 'en-US';
  rec.interimResults = false;
  rec.maxAlternatives = 1;
  rec.onresult = (event) => {
    input.value = event.results[0][0].transcript;
    sendMessage();
  };
  rec.onerror = () => addMessage('System', 'Voice input error. Please retry.');
  rec.start();
});

addMessage('AI Employee', 'Welcome. Voice, file uploads, and real-time chat are ready.');
