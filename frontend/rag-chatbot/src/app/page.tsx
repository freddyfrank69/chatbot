"use client";

import { useState } from "react";
import { ArrowRight } from "lucide-react";

export default function ChatPage() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    // Add typing indicator
    setMessages((prev) => [...prev, { role: "ai", content: "typing" }]);

    try {
      const res = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await res.json();
      const aiMessage = { role: "ai", content: data.response };
      
      // Remove typing indicator and add response
      setMessages((prev) => prev.slice(0, -1).concat(aiMessage));
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div className="app-container">
      {messages.length === 0 && <div className="empty-state">What can I help with?</div>}
      <div className="chat-container">
        <div className="chat-box">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <span className="bubble">
                {msg.content === "typing" ? <TypingIndicator /> : msg.content}
              </span>
            </div>
          ))}
        </div>
        <div className="input-box">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask anything"
            disabled={loading}
          />
          <button onClick={sendMessage} disabled={loading}>
            <ArrowRight size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <span className="typing-indicator">
      <span></span>
      <span></span>
      <span></span>
    </span>
  );
}
