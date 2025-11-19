import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const LivingCharacter = () => {
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const handleMouseMove = (e) => {
            // Normalize mouse position (-1 to 1)
            const x = (e.clientX / window.innerWidth) * 2 - 1;
            const y = (e.clientY / window.innerHeight) * 2 - 1;
            setMousePos({ x, y });
        };

        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    return (
        <div className="character-container">
            {/* 
        Placeholder for the character. 
        In a real app, this would be a Live2D canvas or a layered image.
        For now, we use a CSS-styled div to represent the "Spirit".
      */}
            <motion.div
                className="character-body"
                animate={{
                    y: [0, -10, 0], // Breathing animation (up/down)
                    scale: [1, 1.02, 1], // Slight expansion
                }}
                transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut"
                }}
                style={{
                    // Parallax effect based on mouse position
                    x: mousePos.x * 10,
                    rotateY: mousePos.x * 5,
                }}
            >
                <div className="character-glow" />
                <div className="character-core">
                    <div className="eyes">
                        <motion.div
                            className="eye left"
                            animate={{
                                x: mousePos.x * 5,
                                y: mousePos.y * 5
                            }}
                        />
                        <motion.div
                            className="eye right"
                            animate={{
                                x: mousePos.x * 5,
                                y: mousePos.y * 5
                            }}
                        />
                    </div>
                </div>
            </motion.div>

            <style>{`
        .character-container {
          width: 100%;
          height: 100%;
          display: flex;
          justify-content: center;
          align-items: center;
          /* Allow dragging the window by grabbing the character area */
          -webkit-app-region: drag; 
        }

        .character-body {
          width: 200px;
          height: 300px;
          position: relative;
          display: flex;
          justify-content: center;
          align-items: center;
        }

        .character-core {
          width: 150px;
          height: 150px;
          background: linear-gradient(135deg, #8b5cf6, #ec4899);
          border-radius: 50%;
          position: relative;
          z-index: 2;
          box-shadow: 0 0 50px rgba(139, 92, 246, 0.4);
        }

        .character-glow {
          position: absolute;
          width: 200%;
          height: 200%;
          background: radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, transparent 70%);
          z-index: 1;
        }

        .eyes {
          position: absolute;
          top: 40%;
          left: 50%;
          transform: translate(-50%, -50%);
          display: flex;
          gap: 40px;
          width: 100%;
          justify-content: center;
        }

        .eye {
          width: 15px;
          height: 25px;
          background: white;
          border-radius: 50%;
          box-shadow: 0 0 10px white;
        }
      `}</style>
        </div>
    );
};

export default LivingCharacter;
