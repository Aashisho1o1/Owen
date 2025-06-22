import React from 'react';
import { DocumentTemplate } from '../../services/api';
import { TemplateItem } from './TemplateItem';

interface TemplatesViewProps {
  templates: DocumentTemplate[];
  onUseTemplate: (templateId: string, templateName: string) => void;
}

/**
 * Organism component: Templates View
 * Single Responsibility: Display and manage template collection
 */
export const TemplatesView: React.FC<TemplatesViewProps> = ({
  templates,
  onUseTemplate
}) => {
  return (
    <div className="templates-grid">
      {templates.map(template => (
        <TemplateItem
          key={template.id}
          template={template}
          onUseTemplate={onUseTemplate}
        />
      ))}
    </div>
  );
}; 
 