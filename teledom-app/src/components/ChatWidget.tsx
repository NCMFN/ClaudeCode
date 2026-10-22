import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Phone } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { companyInfo } from '../data';

interface Message {
  id: string;
  type: 'bot' | 'user';
  text: string;
}

const initialMessages: Message[] = [
  {
    id: '1',
    type: 'bot',
    text: `Hello! Welcome to ${companyInfo.name}. I can help you find the right solution (Broadband, Security, Smart Classroom, etc.) or connect you with our team. How can I assist you today?`
  }
];

const ChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      text: inputValue
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response based on real context
    setTimeout(() => {
      let botResponse = '';
      const input = userMessage.text.toLowerCase();

      if (input.includes('contact') || input.includes('phone') || input.includes('email') || input.includes('address')) {
        botResponse = `You can reach us at:\n📍 ${companyInfo.address}\n📞 ${companyInfo.phones.join(', ')}\n✉️ ${companyInfo.emails[0]}\n\nWould you like me to connect you with our team on WhatsApp?`;
      } else if (input.includes('broadband') || input.includes('internet')) {
        botResponse = "We offer Enterprise Broadband Connectivity Solutions tailored for high-speed, reliable demands. I can route you to a networking specialist.";
      } else if (input.includes('security') || input.includes('camera') || input.includes('snos')) {
        botResponse = "Teledom provides military-grade Security Solutions and our SNOS (Security Network Operating System) platform for comprehensive oversight.";
      } else if (input.includes('human') || input.includes('agent') || input.includes('talk')) {
        botResponse = "I'll help you connect with our team. They typically reply within one business day.";
      } else {
        botResponse = "I'm an AI assistant. I can help answer questions about our specific solutions (like Identity Tracking, Video Communication, or Smart Classrooms), or I can get you in touch with our team.";
      }

      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        text: botResponse
      };

      setMessages(prev => [...prev, botMsg]);
      setIsTyping(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  const openWhatsApp = () => {
    // Format phone number (remove spaces and +)
    const phone = companyInfo.phones[0].replace(/[\s+]/g, '');
    window.open(`https://wa.me/${phone}`, '_blank');
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute bottom-16 right-0 w-80 sm:w-96 bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden flex flex-col h-[500px] max-h-[80vh]"
          >
            {/* Header */}
            <div className="bg-blue-600 text-white p-4 flex justify-between items-center shadow-md z-10">
              <div>
                <h3 className="font-bold text-lg leading-tight">Teledom Assistant</h3>
                <p className="text-blue-100 text-xs">Replies within 1 business day</p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white/80 hover:text-white transition-colors p-1"
                aria-label="Close chat"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Note to developer */}
            <div className="bg-amber-50 border-b border-amber-200 p-2 text-center text-xs text-amber-800">
              Note: This is a frontend simulation. Needs backend (e.g. Dialogflow, Crisp, OpenAI API) for production.
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                      msg.type === 'user'
                        ? 'bg-blue-600 text-white rounded-tr-sm shadow-md'
                        : 'bg-white text-gray-800 border border-gray-100 shadow-sm rounded-tl-sm'
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-100 shadow-sm rounded-2xl rounded-tl-sm px-4 py-3 flex space-x-1 items-center">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            <div className="px-4 py-2 bg-white border-t border-gray-100 flex gap-2">
               <button
                  onClick={openWhatsApp}
                  className="flex-1 flex items-center justify-center gap-2 text-xs font-semibold text-green-700 bg-green-50 hover:bg-green-100 py-2 rounded-md transition-colors"
               >
                  <Phone className="w-3 h-3" />
                  Talk on WhatsApp
               </button>
               <a
                  href={`mailto:${companyInfo.emails[0]}`}
                  className="flex-1 flex items-center justify-center gap-2 text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 py-2 rounded-md transition-colors text-center"
               >
                  Email Us
               </a>
            </div>

            {/* Input */}
            <div className="p-3 bg-white border-t border-gray-200 flex items-center gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask about our solutions..."
                className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
              <button
                onClick={handleSend}
                disabled={!inputValue.trim() || isTyping}
                className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shrink-0 shadow-md"
                aria-label="Send message"
              >
                <Send className="w-4 h-4 ml-0.5" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Toggle Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className={`${
          isOpen ? 'bg-gray-800 hover:bg-gray-900' : 'bg-blue-600 hover:bg-blue-700'
        } text-white w-14 h-14 rounded-full shadow-2xl flex items-center justify-center transition-colors border-2 border-white`}
        aria-label="Toggle chat"
      >
        {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
      </motion.button>
    </div>
  );
};

export default ChatWidget;
