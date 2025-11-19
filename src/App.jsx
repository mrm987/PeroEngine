import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import LivingCharacter from './components/LivingCharacter'
import WindowControls from './components/WindowControls'
import ChatBubble from './components/ChatBubble'
import ChatInput from './components/ChatInput'

function App() {
    const [serverStatus, setServerStatus] = useState('Initializing...')
    const [currentMessage, setCurrentMessage] = useState('')
    const [isBubbleVisible, setIsBubbleVisible] = useState(false)

    useEffect(() => {
        // Check backend connection
        const checkServer = async () => {
            try {
                const res = await fetch('http://127.0.0.1:8000/')
                const data = await res.json()
                setServerStatus(data.status === 'online' ? 'Connected' : 'Error')
            } catch (err) {
                setServerStatus('Offline')
            }
        }

        checkServer()
        const interval = setInterval(checkServer, 5000)
        return () => clearInterval(interval)
    }, [])

    const handleSendMessage = async (text) => {
        // Optimistic UI? Or wait for response?
        // For now, let's clear previous bubble
        setIsBubbleVisible(false);

        try {
            const res = await fetch('http://127.0.0.1:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();

            // Show response
            setCurrentMessage(data.response);
            setIsBubbleVisible(true);

            // Auto-hide after a few seconds
            setTimeout(() => setIsBubbleVisible(false), 5000);

        } catch (err) {
            console.error("Chat error:", err);
            setCurrentMessage("... (Connection Error)");
            setIsBubbleVisible(true);
        }
    };

    return (
        <div className="app-container">
            <WindowControls />

            <LivingCharacter />

            <ChatBubble
                message={currentMessage}
                isVisible={isBubbleVisible}
            />

            <ChatInput onSendMessage={handleSendMessage} />

            {/* Status Indicator (Subtle) */}
            <div className="status-indicator">
                <div className={`dot ${serverStatus === 'Connected' ? 'online' : 'offline'}`} />
            </div>

            <style>{`
                .app-container {
                    position: relative;
                    width: 100%;
                    height: 100%;
                    overflow: hidden;
                }

                .status-indicator {
                    position: absolute;
                    bottom: 20px;
                    right: 20px;
                    opacity: 0.5;
                    transition: opacity 0.3s;
                }
                
                .status-indicator:hover {
                    opacity: 1;
                }

                .dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: var(--text-muted);
                    box-shadow: 0 0 5px rgba(0,0,0,0.5);
                }

                .dot.online {
                    background: #10b981; /* Emerald 500 */
                    box-shadow: 0 0 8px #10b981;
                }

                .dot.offline {
                    background: #ef4444; /* Red 500 */
                }
            `}</style>
        </div>
    )
}

export default App
