import React from 'react';
import { DocumentTemplate } from '../../services/api';

interface TemplateItemProps {
  template: DocumentTemplate;
  onUseTemplate: (templateId: string, templateName: string) => void;
}

/**
 * Molecular component: Template Item
 * Single Responsibility: Display individual template with use action
 */
export const TemplateItem: React.FC<TemplateItemProps> = ({
  template,
  onUseTemplate
}) => {
  const handleUseTemplate = () => {
    onUseTemplate(template.id, template.name);
  };

  return (
    <div className="template-item">
      <div className="template-icon">📋</div>
      
      <div className="template-info">
        <div className="template-name">{template.name}</div>
        <div className="template-preview">{template.preview_text}</div>
      </div>
      
      <div className="template-actions">
        <button onClick={handleUseTemplate}>
          ✨ Use Template
        </button>
      </div>
    </div>
  );
}; 
 