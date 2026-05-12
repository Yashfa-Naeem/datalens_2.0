import { useState } from "react";
import axios from "axios";

const API = "http://localhost:8000/api";

export default function ChatPanel({ datasetId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await axios.post(`${API}/chat`, {
        dataset_id: datasetId,
        message: input,
      });
      const botMsg = { role: "assistant", content: res.data.response };
      setMessages((prev) => [...prev, botMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    <div className="chat-panel">
      <div className="chat-title">💬 Chat with your Data</div>
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-placeholder">
            Ask me anything about your dataset!<br />
            e.g. "Which airline has the most delays?"
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`chat-msg ${msg.role}`}>
            <span className="chat-bubble">{msg.content}</span>
          </div>
        ))}
        {loading && (
          <div className="chat-msg assistant">
            <span className="chat-bubble">Thinking...</span>
          </div>
        )}
      </div>
      <div className="chat-input-row">
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask a question about your data..."
        />
        <button className="chat-send" onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}