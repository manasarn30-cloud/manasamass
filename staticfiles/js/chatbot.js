/**
 * STREAMFLIX — FLOATING AI SUPPORT ASSISTANT
 * Connects directly to Django `/api/chatbot/` and `/api/chatbot/feedback/`.
 * Persists session conversation across page navigation using sessionStorage.
 */

document.addEventListener('DOMContentLoaded', () => {
  initChatbot();
});

function initChatbot() {
  const triggerBtn = document.getElementById('chatbot-trigger');
  const panel = document.getElementById('chatbot-panel');
  const closeBtn = document.getElementById('chatbot-close');
  const input = document.getElementById('chatbot-input');
  const sendBtn = document.getElementById('chatbot-send');
  const messagesContainer = document.getElementById('chatbot-messages');
  const typingIndicator = document.getElementById('chatbot-typing');

  if (!triggerBtn || !panel || !input || !sendBtn || !messagesContainer) {
    return;
  }

  // Generate or retrieve persistent conversation ID
  let conversationId = sessionStorage.getItem('streamflix_chat_id');
  if (!conversationId) {
    conversationId = 'conv_' + Math.random().toString(36).substring(2, 11) + '_' + Date.now();
    sessionStorage.setItem('streamflix_chat_id', conversationId);
  }

  let chatState = sessionStorage.getItem('streamflix_chat_state') || 'idle';

  // Open / Close actions
  const openChat = () => {
    panel.classList.add('active');
    triggerBtn.classList.add('open');
    input.focus();
    scrollToBottom();
  };

  const closeChat = () => {
    panel.classList.remove('active');
    triggerBtn.classList.remove('open');
  };

  triggerBtn.addEventListener('click', () => {
    if (panel.classList.contains('active')) {
      closeChat();
    } else {
      openChat();
    }
  });

  if (closeBtn) closeBtn.addEventListener('click', closeChat);

  // Hook all "Ask the Assistant" buttons across the application (404, 500, error pages, FAQ)
  document.addEventListener('click', (e) => {
    const askAssistantBtn = e.target.closest('[data-open-assistant]');
    if (askAssistantBtn) {
      e.preventDefault();
      openChat();
      const queryPrompt = askAssistantBtn.dataset.openAssistant;
      if (queryPrompt && queryPrompt !== 'true') {
        input.value = queryPrompt;
        handleSendMessage();
      }
    }
  });

  // Load message history from sessionStorage if available
  loadChatHistory();

  // Handle Quick Action Chips
  document.addEventListener('click', (e) => {
    const chip = e.target.closest('.quick-chip');
    if (chip) {
      const prompt = chip.dataset.prompt || chip.textContent.trim();
      input.value = prompt;
      handleSendMessage();
    }
  });

  // Handle Enter to send
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  sendBtn.addEventListener('click', handleSendMessage);

  async function handleSendMessage() {
    const text = input.value.trim();
    if (!text) return;

    // Append User Message to UI
    appendMessage('user', text);
    input.value = '';
    sendBtn.disabled = true;

    // Show typing indicator
    if (typingIndicator) typingIndicator.classList.add('active');
    scrollToBottom();

    try {
      const csrfToken = getCsrfToken();
      const response = await fetch('/api/chatbot/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
          message: text,
          conversation_id: conversationId,
          state: chatState
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const data = await response.json();

      // Update state
      if (data.state) {
        chatState = data.state;
        sessionStorage.setItem('streamflix_chat_state', chatState);
      }

      // Append Assistant response
      appendMessage('assistant', data.reply, {
        type: data.type,
        ticketOffer: data.ticket_offer,
        ticketRef: data.ticket_ref,
        ticketUrl: data.ticket_url,
        faqId: data.faq_id,
        category: data.category
      });

    } catch (err) {
      console.error('Chatbot API communication error:', err);
      appendMessage('assistant', "⚠️ I'm currently unable to reach the support database. Please check your internet connection or try again in a few moments.");
    } finally {
      if (typingIndicator) typingIndicator.classList.remove('active');
      sendBtn.disabled = false;
      scrollToBottom();
    }
  }

  function appendMessage(role, text, metadata = {}) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'chat-message-bubble';

    // Format basic markdown (bold, lists, links)
    bubble.innerHTML = formatMarkdown(text);

    // If ticket escalation was offered, add explicit ticket creation button
    if (metadata.ticketOffer && role === 'assistant') {
      const ticketAction = document.createElement('div');
      ticketAction.className = 'chat-ticket-action';
      ticketAction.innerHTML = `
        <span style="font-size: 0.8rem; color: var(--text-muted);">Would you like our engineering team to inspect this?</span>
        <button class="chat-ticket-btn" data-confirm-ticket="true">Yes, Open Support Ticket</button>
      `;
      ticketAction.querySelector('button').addEventListener('click', () => {
        input.value = "Yes, create support ticket";
        handleSendMessage();
      });
      bubble.appendChild(ticketAction);
    }

    // If ticket was created, add view link
    if (metadata.ticketUrl && role === 'assistant') {
      const ticketLink = document.createElement('div');
      ticketLink.style.marginTop = '0.5rem';
      ticketLink.innerHTML = `<a href="${metadata.ticketUrl}" class="btn btn-sm btn-primary" style="display: inline-block;">View Ticket Details</a>`;
      bubble.appendChild(ticketLink);
    }

    // Feedback buttons for assistant responses
    if (role === 'assistant' && !metadata.ticketOffer && metadata.type !== 'ticket_created') {
      const feedbackRow = document.createElement('div');
      feedbackRow.className = 'chat-feedback-row';
      feedbackRow.innerHTML = `
        <span>Was this helpful?</span>
        <button class="chat-feedback-btn" data-rating="helpful">👍 Yes</button>
        <button class="chat-feedback-btn" data-rating="not_helpful">👎 No</button>
      `;

      feedbackRow.querySelectorAll('.chat-feedback-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          submitFeedback(btn.dataset.rating, text, btn, feedbackRow);
        });
      });

      bubble.appendChild(feedbackRow);
    }

    // Timestamp
    const timeSpan = document.createElement('span');
    timeSpan.className = 'chat-time';
    const now = new Date();
    timeSpan.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    bubble.appendChild(timeSpan);

    msgDiv.appendChild(bubble);
    messagesContainer.appendChild(msgDiv);

    // Save to sessionStorage
    saveMessageToSession(role, text, metadata);
    scrollToBottom();
  }

  async function submitFeedback(rating, messageSnippet, btn, container) {
    container.querySelectorAll('.chat-feedback-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    try {
      const csrfToken = getCsrfToken();
      await fetch('/api/chatbot/feedback/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          message_id: 'msg_' + Date.now(),
          rating: rating,
          feedback_text: `User rated "${rating}" on: ${messageSnippet.substring(0, 80)}`
        })
      });
      container.innerHTML = `<span style="color: var(--success); font-size: 0.75rem;">✓ Thank you for your feedback!</span>`;
    } catch (e) {
      console.warn("Feedback logging error:", e);
    }
  }

  function scrollToBottom() {
    setTimeout(() => {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 50);
  }

  function saveMessageToSession(role, text, metadata) {
    try {
      let history = JSON.parse(sessionStorage.getItem('streamflix_chat_history') || '[]');
      history.push({ role, text, metadata, timestamp: Date.now() });
      if (history.length > 30) history = history.slice(-30); // keep last 30 turns
      sessionStorage.setItem('streamflix_chat_history', JSON.stringify(history));
    } catch (e) {
      console.warn('Could not write to sessionStorage:', e);
    }
  }

  function loadChatHistory() {
    try {
      const raw = sessionStorage.getItem('streamflix_chat_history');
      if (!raw) return;
      const history = JSON.parse(raw);
      if (Array.isArray(history) && history.length > 0) {
        history.forEach(item => {
          appendMessageFromHistory(item.role, item.text, item.metadata);
        });
      }
    } catch (e) {
      console.warn('Could not read chat history from sessionStorage:', e);
    }
  }

  function appendMessageFromHistory(role, text, metadata = {}) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${role}`;
    const bubble = document.createElement('div');
    bubble.className = 'chat-message-bubble';
    bubble.innerHTML = formatMarkdown(text);
    msgDiv.appendChild(bubble);
    messagesContainer.appendChild(msgDiv);
  }

  function formatMarkdown(text) {
    if (!text) return '';
    let html = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>')
      .replace(/•\s+(.*)/g, '<li style="margin-left: 1rem;">$1</li>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>');
    return html;
  }

  function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    if (match) return match[1];
    const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : '';
  }
}
