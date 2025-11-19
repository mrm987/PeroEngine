import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ChatBubble = ({ message, isVisible }) => {
    return (
        <AnimatePresence>
            {isVisible && message && (
                <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.9 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.9 }}
                    className="chat-bubble"
                >
                    <div className="bubble-content">
                        {message}
                    </div>
                    <div className="bubble-tail" />

                    <style>{`
            .chat-bubble {
              position: absolute;
              bottom: 120px; /* Position above the character/input */
              left: 50%;
              transform: translateX(-50%) !important; /* Override framer-motion transform for centering */
              background: rgba(20, 20, 30, 0.9);
              border: 1px solid var(--primary);
              padding: 12px 20px;
              border-radius: 16px;
              border-bottom-left-radius: 4px;
              max-width: 280px;
              box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
              z-index: 100;
              pointer-events: none; /* Let clicks pass through */
            }

            .bubble-content {
              color: var(--text-main);
              font-size: 14px;
              line-height: 1.4;
              text-align: center;
            }

            .bubble-tail {
              position: absolute;
              bottom: -6px;
              left: 20px;
              width: 12px;
              height: 12px;
              background: rgba(20, 20, 30, 0.9);
              border-bottom: 1px solid var(--primary);
              border-right: 1px solid var(--primary);
              transform: rotate(45deg);
            }
          `}</style>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default ChatBubble;
