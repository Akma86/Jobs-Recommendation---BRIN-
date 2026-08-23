import React from 'react';

/**
 * FormattedText: Safely parses Markdown inline syntax (**bold**, *italic*, `code`, _underline_)
 * and renders clean, styled React elements without leaving raw markdown symbols like '**' or '`'.
 */
export function FormattedText({ text, style, className, strongColor = '#0F172A' }) {
  if (!text) return null;
  if (typeof text !== 'string') return text;

  const parts = [];
  const tokenRegex = /(\*\*([^*]+)\*\*|`([^`]+)`|\*([^*]+)\*|_([^_]+)_)/g;
  let lastIndex = 0;
  let match;
  let key = 0;

  while ((match = tokenRegex.exec(text)) !== null) {
    // Push plain text prior to match
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }

    const fullMatch = match[0];
    if (fullMatch.startsWith('**') && fullMatch.endsWith('**')) {
      parts.push(
        <strong key={`bold-${key++}`} style={{ fontWeight: 800, color: strongColor }}>
          {match[2]}
        </strong>
      );
    } else if (fullMatch.startsWith('`') && fullMatch.endsWith('`')) {
      parts.push(
        <code 
          key={`code-${key++}`} 
          style={{ 
            background: 'rgba(37, 99, 235, 0.09)', 
            color: '#1E40AF', 
            padding: '0.15rem 0.45rem', 
            borderRadius: '6px', 
            fontFamily: 'monospace',
            fontSize: '0.86em',
            fontWeight: 700 
          }}
        >
          {match[3]}
        </code>
      );
    } else if (fullMatch.startsWith('*') && fullMatch.endsWith('*')) {
      parts.push(<em key={`em-${key++}`}>{match[4]}</em>);
    } else if (fullMatch.startsWith('_') && fullMatch.endsWith('_')) {
      parts.push(<em key={`em2-${key++}`}>{match[5]}</em>);
    }

    lastIndex = tokenRegex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return (
    <span style={style} className={className}>
      {parts}
    </span>
  );
}

export default FormattedText;
