import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send } from 'lucide-react';

const ChatInput = ({ onSendMessage }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [message, setMessage] = useState('');
    const inputRef = useRef(null);

    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isOpen]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim()) {
            onSendMessage(message);
            setMessage('');
            // Optional: Close after sending? Or keep open?
            // setIsOpen(false); 
        }
    };

    return (
        <div className="chat-input-container">
            <AnimatePresence>
                {isOpen ? (
                    <motion.form
                        initial={{ width: 40, opacity: 0 }}
                        animate={{ width: 300, opacity: 1 }}
                        exit={{ width: 40, opacity: 0 }}
                        className="input-form"
                        onSubmit={handleSubmit}
                    >
                        <input
                            ref={inputRef}
                            type="text"
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            placeholder="Say something..."
                            className="chat-input"
                            onBlur={() => !message && setIsOpen(false)} // Close if empty and lost focus
                        />
                        <button type="submit" className="send-btn">
                            <Send size={16} />
                        </button>
                    </motion.form>
                ) : (
                    <motion.button
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        whileHover={{ scale: 1.1 }}
                        className="toggle-btn"
                        onClick={() => setIsOpen(true)}
                    >
                        <Send size={20} />
                    </motion.button>
                )}
            </AnimatePresence>

            <style>{`
        .chat-input-container {
          position: absolute;
          bottom: 40px;
          left: 50%;
          transform: translateX(-50%);
          z-index: 100;
          height: 40px;
          display: flex;
          justify-content: center;
          align-items: center;
          /* CRITICAL: Allow clicking on this element by disabling window drag */
          -webkit-app-region: no-drag;
        }

        .toggle-btn {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: rgba(20, 20, 30, 0.8);
          border: 1px solid var(--primary);
          color: var(--primary);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          box-shadow: 0 0 10px var(--primary-glow);
          transition: all 0.2s;
        }

        .input-form {
          background: rgba(20, 20, 30, 0.9);
          border: 1px solid var(--primary);
          border-radius: 20px;
          padding: 4px;
          display: flex;
          align-items: center;
          box-shadow: 0 4px 15px rgba(0,0,0,0.3);
          overflow: hidden;
        }

        .chat-input {
          flex: 1;
          background: transparent;
          border: none;
          color: white;
          padding: 8px 16px;
          outline: none;
          font-family: inherit;
          font-size: 14px;
          min-width: 0; /* Flexbox fix */
        }

        .send-btn {
          background: var(--primary);
          border: none;
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          cursor: pointer;
          flex-shrink: 0;
        }
        
        .send-btn:hover {
          background: #7c3aed; /* Violet 600 */
        }
      `}</style>
        </div>
    );
};

export default ChatInput;
