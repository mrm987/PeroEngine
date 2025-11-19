import React from 'react';
import { X, Minus } from 'lucide-react';

const { ipcRenderer } = window.require('electron');

const WindowControls = () => {
    const handleMinimize = () => {
        ipcRenderer.send('minimize-window');
    };

    const handleClose = () => {
        ipcRenderer.send('close-window');
    };

    return (
        <div className="window-controls">
            <button onClick={handleMinimize} className="control-btn minimize">
                <Minus size={16} />
            </button>
            <button onClick={handleClose} className="control-btn close">
                <X size={16} />
            </button>

            <style>{`
        .window-controls {
          position: absolute;
          top: 10px;
          right: 10px;
          display: flex;
          gap: 8px;
          z-index: 1000;
          /* Ensure controls are clickable even if window is draggable */
          -webkit-app-region: no-drag; 
        }
        
        .control-btn {
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(255, 255, 255, 0.1);
          color: var(--text-muted);
          width: 28px;
          height: 28px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .control-btn:hover {
          background: rgba(255, 255, 255, 0.1);
          color: var(--text-main);
        }
        
        .control-btn.close:hover {
          background: rgba(239, 68, 68, 0.5); /* Red-500 */
          border-color: rgba(239, 68, 68, 0.5);
        }
      `}</style>
        </div>
    );
};

export default WindowControls;
