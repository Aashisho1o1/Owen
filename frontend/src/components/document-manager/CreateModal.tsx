import React, { useState } from 'react';

interface CreateModalProps {
  isOpen: boolean;
  title: string;
  placeholder: string;
  onConfirm: (name: string) => Promise<void>;
  onCancel: () => void;
}

/**
 * Molecular component: Create Modal
 * Single Responsibility: Handle creation modal UI for documents/folders
 */
export const CreateModal: React.FC<CreateModalProps> = ({
  isOpen,
  title,
  placeholder,
  onConfirm,
  onCancel
}) => {
  const [itemName, setItemName] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  if (!isOpen) return null;

  const handleConfirm = async () => {
    if (!itemName.trim()) return;
    
    setIsCreating(true);
    try {
      await onConfirm(itemName);
      setItemName('');
    } catch (error) {
      console.error('Failed to create item:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const handleCancel = () => {
    setItemName('');
    onCancel();
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h3>{title}</h3>
        <input
          type="text"
          placeholder={placeholder}
          value={itemName}
          onChange={(e) => setItemName(e.target.value)}
          disabled={isCreating}
        />
        <div className="modal-actions">
          <button 
            onClick={handleConfirm}
            disabled={!itemName.trim() || isCreating}
          >
            {isCreating ? 'Creating...' : 'Create'}
          </button>
          <button onClick={handleCancel} disabled={isCreating}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}; 
 