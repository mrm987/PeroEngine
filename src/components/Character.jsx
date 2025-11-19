import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

const Character = ({ imageSrc }) => {
    // Breathing animation variants
    const breathing = {
        initial: { scale: 1, y: 0 },
        animate: {
            scale: [1, 1.02, 1],
            y: [0, -5, 0],
            transition: {
                duration: 4,
                ease: "easeInOut",
                repeat: Infinity,
            },
        },
    };

    if (!imageSrc) return null;

    return (
        <div className="character-container">
            <motion.div
                className="character-wrapper"
                variants={breathing}
                initial="initial"
                animate="animate"
            >
                <img src={imageSrc} alt="Character" className="character-image" />

                {/* Glow effect behind the character */}
                <div className="character-glow" />
            </motion.div>
        </div>
    );
};

export default Character;
