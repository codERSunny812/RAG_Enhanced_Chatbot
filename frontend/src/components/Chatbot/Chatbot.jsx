import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send } from 'lucide-react';
import './Chatbot.css';
import axios from 'axios';

const BASE_URL = "http://localhost:8000";

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hello! I'm IVA, your personal insurance assistant. How can I help you today?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  const toggleChat = () => setIsOpen(!isOpen);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userQuery = input.trim();
    setInput("");

    // Add user message to chat
    setMessages(prev => [...prev, { role: "user", text: userQuery }]);
    setLoading(true);

    try {
      const response = await axios.post(`${BASE_URL}/chat`, {
        query: userQuery,
        chat_history: []
      });

      const data = response.data;

      // Add bot reply with sources
      setMessages(prev => [...prev, {
        role: "bot",
        text: data.answer,
        sources: data.sources
      }]);

    } catch (err) {
      setMessages(prev => [...prev, {
        role: "bot",
        text: "Sorry, I couldn't connect to the server. Please make sure the backend is running."
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chatbot-wrapper">
      {isOpen && (
        <div className={`chat-window ${isOpen ? 'animate-slide-up' : ''}`}>

          {/* Header — unchanged from your original */}
          <div className="chat-header">
            <div className="chat-title">
              <span className="online-indicator"></span>
              Stellar Assistant
            </div>
            <button className="close-btn" onClick={toggleChat}>
              <X size={20} />
            </button>
          </div>

          {/* Chat Body — now renders real messages */}
          <div className="chat-body">
            {messages.map((msg, i) => (
              <div key={i}>
                <div className={`message ${msg.role === "user" ? "user-message" : "bot-message"}`}>
                  {msg.text}
                </div>

                {/* Sources shown below bot messages */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="sources-block">
                    <p className="sources-label">Sources:</p>
                    {msg.sources.map((s, j) => (
                      <p key={j} className="source-item">
                        {j + 1}. {s.source} (chunk {s.chunk_id})
                      </p>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {/* Loading indicator */}
            {loading && (
              <div className="message bot-message typing-indicator">
                <span></span><span></span><span></span>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Footer — now functional */}
          <div className="chat-footer">
            <input
              type="text"
              placeholder="Type your message..."
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button
              className="send-btn"
              onClick={handleSend}
              disabled={loading || !input.trim()}
            >
              <Send size={18} />
            </button>
          </div>

        </div>
      )}

      <button
        className={`chat-toggle-btn ${!isOpen ? 'animate-pulse-btn' : ''}`}
        onClick={toggleChat}
        aria-label="Toggle Chat"
      >
        {isOpen ? <X size={24} /> : <MessageSquare size={24} />}
      </button>
    </div>
  );
};


export default Chatbot;