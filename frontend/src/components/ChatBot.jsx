import { useState, useRef, useEffect } from 'react';
import { FaCommentDots, FaTimes, FaPaperPlane, FaPlus, FaMinus } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';
import { chatAPI } from '../services/api';
import { Link } from 'react-router-dom';
import StarRating from './StarRating';
import toast from 'react-hot-toast';

const QUICK_ACTIONS = [
  'Find dinner tonight',
  'Best rated near me',
  'Vegan options',
];

function ChatRestaurantCard({ restaurant, onMinimize }) {
  const { id, name, cuisine_type, city, pricing_tier, average_rating = 0, photos } = restaurant || {};

  const CUISINE_IMAGE_MAP = {
    'Pizza': '1513104890138-7c749659a591',
    'Mexican': '1504674900247-0877df9cc836',
    'Italian': '1501339847302-ac426a4a7cbb',
    'Japanese': '1580822184713-fc5400e7fe10',
    'Chinese': '1540189549336-e6e99c3679fe',
    'American': '1550966871-3ed3cdb5ed0c',
    'Thai': '1559314809-0d155014e29e',
    'Indian': '1517248135467-4c7edcad34c4',
    'Vegan': '1512621776951-a57141f2eefd',
  };
  const GENERIC = ['1546069901-ba9599a7e63c', '1519708227418-c8fd9a32b7a2'];
  const getImg = () => {
    const key = Object.keys(CUISINE_IMAGE_MAP).find(k =>
      `${cuisine_type} ${name}`.toLowerCase().includes(k.toLowerCase())
    );
    const imgId = key ? CUISINE_IMAGE_MAP[key] : GENERIC[0];
    return `https://images.unsplash.com/photo-${imgId}?auto=format&fit=crop&w=200&q=80`;
  };
  const imageUrl = photos?.length > 0 ? photos[0] : getImg();
  const priceDisplay = pricing_tier ? '$'.repeat(Number(pricing_tier) || 1) : null;

  return (
    <Link
      to={`/restaurants/${id}`}
      onClick={onMinimize}
      className="flex gap-2 p-2 bg-white rounded-lg border border-gray-100 hover:border-red-200 hover:shadow-sm transition-all"
    >
      <div className="w-12 h-12 flex-shrink-0 rounded-md overflow-hidden bg-gray-200">
        <img src={imageUrl} alt={name} className="w-full h-full object-cover" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-gray-900 truncate">{name}</p>
        <p className="text-xs text-gray-500 truncate">{cuisine_type}{city && ` • ${city}`}</p>
        <div className="flex items-center gap-1 mt-0.5">
          <StarRating rating={Number(average_rating) || 0} size="sm" />
          <span className="text-xs text-gray-500">{(Number(average_rating) || 0).toFixed(1)}</span>
          {priceDisplay && <span className="text-xs text-gray-400 ml-1">{priceDisplay}</span>}
        </div>
      </div>
    </Link>
  );
}

export default function ChatBot() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Listen for open-chatbot event from Explore page
  useEffect(() => {
    const handler = () => {
      setIsOpen(true);
      setIsMinimized(false);
    };
    window.addEventListener('open-chatbot', handler);
    return () => window.removeEventListener('open-chatbot', handler);
  }, []);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen, isMinimized]);

  if (!user) return null;

  const sendMessage = async (text) => {
    const trimmed = (text || input).trim();
    if (!trimmed) return;

    setIsMinimized(false);

    const userMessage = { role: 'user', content: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    const conversationHistory = messages.map((m) => ({ role: m.role, content: m.content }));

    try {
      const { data } = await chatAPI.send({
        message: trimmed,
        conversation_history: conversationHistory,
      });
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: data.response,
        restaurants: data.restaurants || [],
      }]);
    } catch (err) {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: 'Sorry, I could not process your request. Please try again.',
        restaurants: [],
      }]);
      toast.error('Failed to get AI response');
    } finally {
      setLoading(false);
    }
  };

  const handleMinimize = () => setIsMinimized(true);
  const handleNewConversation = () => { setMessages([]); setInput(''); };

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => {
          if (isOpen && !isMinimized) {
            setIsOpen(false);
          } else {
            setIsOpen(true);
            setIsMinimized(false);
          }
        }}
        className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full shadow-lg flex items-center justify-center bg-red-600 text-white hover:bg-red-700 transition-all"
        aria-label="Toggle chat"
      >
        {isOpen && !isMinimized ? <FaTimes size={22} /> : <FaCommentDots size={22} />}
      </button>

      {/* Minimized pill */}
      {isOpen && isMinimized && (
        <button
          onClick={() => setIsMinimized(false)}
          className="fixed bottom-24 right-6 z-40 flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-full shadow-lg hover:bg-red-700 transition-all text-sm font-semibold"
        >
          <FaCommentDots size={14} /> AI Assistant
        </button>
      )}

      {/* Full chat window */}
      {isOpen && !isMinimized && (
        <div className="fixed bottom-24 right-6 z-40 w-[380px] max-w-[calc(100vw-3rem)] h-[520px] bg-white rounded-xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-red-600 text-white">
            <h3 className="font-semibold">AI Restaurant Assistant</h3>
            <div className="flex items-center gap-2">
              <button
                onClick={handleNewConversation}
                className="flex items-center gap-1 text-sm px-2 py-1 rounded hover:bg-red-700 transition-colors"
                title="New conversation"
              >
                <FaPlus size={11} /> New
              </button>
              <button
                onClick={handleMinimize}
                className="p-1 rounded hover:bg-red-700 transition-colors"
                title="Minimize"
              >
                <FaMinus size={13} />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.length === 0 && (
              <div className="space-y-3">
                <p className="text-sm text-gray-600">Hi! How can I help you find a restaurant?</p>
                <div className="flex flex-wrap gap-2">
                  {QUICK_ACTIONS.map((action) => (
                    <button
                      key={action}
                      onClick={() => sendMessage(action)}
                      className="px-3 py-1.5 text-sm bg-white border border-gray-200 rounded-full hover:border-red-400 hover:bg-red-50 text-gray-700 transition-colors"
                    >
                      {action}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-4 py-2 ${
                  msg.role === 'user'
                    ? 'bg-blue-500 text-white rounded-br-md'
                    : 'bg-gray-200 text-gray-900 rounded-bl-md'
                }`}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  {msg.restaurants?.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {msg.restaurants.map((r) => (
                        <ChatRestaurantCard key={r.id} restaurant={r} onMinimize={handleMinimize} />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-200 rounded-2xl rounded-bl-md px-4 py-2 flex items-center gap-3">
                  <div className="flex gap-1">
                    <span className="w-1.5 h-1.5 bg-gray-600 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="w-1.5 h-1.5 bg-gray-600 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                    <span className="w-1.5 h-1.5 bg-gray-600 rounded-full animate-bounce"></span>
                  </div>
                  <span className="text-xs text-gray-500 font-medium italic">Assistant is thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t border-gray-200 bg-white">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                placeholder="Ask about restaurants..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent text-sm"
                disabled={loading}
              />
              <button
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <FaPaperPlane size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}