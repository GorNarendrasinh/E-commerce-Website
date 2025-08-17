const chatbotToggle = document.getElementById('chatbot-toggle');
const chatbot = document.getElementById('simple-chatbot');
const closeBtn = document.getElementById('close-chatbot');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const quickReplies = document.getElementById('quick-replies');

chatbotToggle.onclick = () => {
  chatbot.style.display = 'flex';
  chatInput.focus();
};

closeBtn.onclick = () => {
  chatbot.style.display = 'none';
};

function addMessage(text, sender = 'bot') {
  const msg = document.createElement('div');
  msg.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;
  msg.textContent = text;
  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function botReply(text) {
  const msg = text.toLowerCase();

  if (/hello|hi|hey/.test(msg)) return "Hello! 👋 Welcome to RedStore! We have Men’s Clothing, Women’s Clothing, Kids' Toys and more. How can I help you today?";
  if (/men/.test(msg)) return "Our Men’s Collection includes trendy shirts, casual wear, and more. Would you like to see some popular items?";
  if (/women/.test(msg)) return "Our Women’s Fashion features elegant and stylish outfits perfect for every occasion.";
  if (/kids|toys/.test(msg)) return "We offer a wide range of fun and safe kids’ toys and clothing. Your little ones will love them!";
  if (/clothes|clothing/.test(msg)) return "We have a great collection of clothing for men, women, and kids. What are you interested in?";
  if (/thank/.test(msg)) return "You’re welcome! If you have any other questions, just ask!";

  return "Sorry, I didn’t get that. You can ask me about Men’s Clothing, Women’s Fashion, Kids’ Toys, or say Hello!";
}

chatInput.onkeydown = e => {
  if (e.key === 'Enter' && chatInput.value.trim()) {
    const userText = chatInput.value.trim();
    addMessage(userText, 'user');
    chatInput.value = '';

    setTimeout(() => addMessage(botReply(userText), 'bot'), 600);
  }
};

quickReplies.addEventListener('click', e => {
  if (e.target.classList.contains('quick-btn')) {
    const userText = e.target.textContent;
    addMessage(userText, 'user');

    setTimeout(() => {
      const reply = botReply(userText);
      addMessage(reply, 'bot');
    }, 400);
  }
});

  

