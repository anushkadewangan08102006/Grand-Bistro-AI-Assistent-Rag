import React from 'react';

/**
 * Clean and robust Markdown renderer for culinary assistant answers.
 * Parses headers, tables, lists, bold, italics, blockquotes, and links.
 */
export default function MarkdownView({ content, isDark = true }) {
  if (!content) return null;

  const lines = content.split('\n');
  const elements = [];
  let i = 0;

  const parseInline = (text) => {
    if (!text) return '';
    // Format bold **text**
    const parts = [];
    // Regex for bold **...**, link [...](...), code `...`
    const regex = /(\*\*.*?\*\*|`.*?`|\[.*?\]\(.*?\))/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }
      const token = match[0];
      if (token.startsWith('**') && token.endsWith('**')) {
        parts.push(
          <strong key={match.index} className="font-bold text-amber-400">
            {token.slice(2, -2)}
          </strong>
        );
      } else if (token.startsWith('`') && token.endsWith('`')) {
        parts.push(
          <code key={match.index} className="px-1.5 py-0.5 rounded bg-stone-800 text-amber-300 font-mono text-xs">
            {token.slice(1, -1)}
          </code>
        );
      } else if (token.startsWith('[') && token.includes('](')) {
        const linkText = token.substring(1, token.indexOf(']('));
        const linkUrl = token.substring(token.indexOf('](') + 2, token.length - 1);
        parts.push(
          <a
            key={match.index}
            href={linkUrl}
            target="_blank"
            rel="noreferrer"
            className="text-amber-400 underline font-semibold hover:text-amber-300"
          >
            {linkText}
          </a>
        );
      }
      lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }

    return parts.length > 0 ? parts : text;
  };

  while (i < lines.length) {
    const line = lines[i];

    // Empty line
    if (!line.trim()) {
      i++;
      continue;
    }

    // Header 3
    if (line.startsWith('### ')) {
      elements.push(
        <h3 key={i} className="text-base font-bold font-serif-luxury text-amber-400 mt-3 mb-2 flex items-center gap-2">
          {parseInline(line.replace('### ', ''))}
        </h3>
      );
      i++;
      continue;
    }

    // Header 4
    if (line.startsWith('#### ')) {
      elements.push(
        <h4 key={i} className="text-sm font-bold uppercase tracking-wider text-stone-300 mt-2.5 mb-1.5">
          {parseInline(line.replace('#### ', ''))}
        </h4>
      );
      i++;
      continue;
    }

    // Blockquote
    if (line.startsWith('> ')) {
      elements.push(
        <blockquote
          key={i}
          className={`border-l-3 border-amber-500 pl-3 py-1 my-2 text-xs italic ${
            isDark ? 'bg-amber-950/20 text-stone-300' : 'bg-amber-50 text-stone-700'
          } rounded-r-lg`}
        >
          {parseInline(line.replace('> ', ''))}
        </blockquote>
      );
      i++;
      continue;
    }

    // Table detection: starts with '|'
    if (line.trim().startsWith('|') && line.includes('|')) {
      const tableLines = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        tableLines.push(lines[i].trim());
        i++;
      }

      if (tableLines.length >= 2) {
        const headerCells = tableLines[0]
          .split('|')
          .slice(1, -1)
          .map((c) => c.trim());
        
        // Skip separator line if present (e.g. |:---|:---|)
        const dataRows = tableLines.slice(1).filter((l) => !l.includes('---'));

        elements.push(
          <div key={`table-${i}`} className="my-3 overflow-x-auto rounded-xl border border-stone-800 shadow-sm">
            <table className="w-full text-left text-xs">
              <thead className={isDark ? 'bg-stone-950 text-stone-300 font-mono uppercase' : 'bg-stone-100 text-stone-700 font-mono uppercase'}>
                <tr>
                  {headerCells.map((h, hIdx) => (
                    <th key={hIdx} className="py-2.5 px-3.5 border-b border-stone-800 font-semibold tracking-wider">
                      {parseInline(h)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className={`divide-y divide-stone-800/60 ${isDark ? 'bg-stone-900/50' : 'bg-white'}`}>
                {dataRows.map((r, rIdx) => {
                  const cells = r
                    .split('|')
                    .slice(1, -1)
                    .map((c) => c.trim());
                  return (
                    <tr key={rIdx} className="hover:bg-amber-500/5 transition">
                      {cells.map((cell, cIdx) => (
                        <td key={cIdx} className="py-2.5 px-3.5 text-stone-200">
                          {/* Handle <br> inside cells */}
                          {cell.split('<br>').map((sub, sIdx) => (
                            <React.Fragment key={sIdx}>
                              {sIdx > 0 && <br />}
                              {parseInline(sub.trim())}
                            </React.Fragment>
                          ))}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        );
        continue;
      }
    }

    // Bullet List: starts with '* ' or '- '
    if (line.trim().startsWith('* ') || line.trim().startsWith('- ')) {
      const listItems = [];
      while (i < lines.length && (lines[i].trim().startsWith('* ') || lines[i].trim().startsWith('- '))) {
        listItems.push(lines[i].trim().substring(2));
        i++;
      }
      elements.push(
        <ul key={`list-${i}`} className="my-2 space-y-1 text-xs text-stone-200 pl-2">
          {listItems.map((item, itemIdx) => (
            <li key={itemIdx} className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0" />
              <span>{parseInline(item)}</span>
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // Numbered list: e.g. '1. '
    if (/^\d+\.\s/.test(line.trim())) {
      const numItems = [];
      while (i < lines.length && /^\d+\.\s/.test(lines[i].trim())) {
        numItems.push(lines[i].trim().replace(/^\d+\.\s*/, ''));
        i++;
      }
      elements.push(
        <ol key={`num-list-${i}`} className="my-2 space-y-1 text-xs text-stone-200 pl-2">
          {numItems.map((item, itemIdx) => (
            <li key={itemIdx} className="flex items-start gap-2">
              <span className="font-mono text-amber-400 font-bold text-xs">{itemIdx + 1}.</span>
              <span>{parseInline(item)}</span>
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // Standard paragraph
    elements.push(
      <p key={i} className="text-xs sm:text-sm leading-relaxed my-1.5 text-stone-200">
        {parseInline(line)}
      </p>
    );
    i++;
  }

  return <div className="space-y-1">{elements}</div>;
}
