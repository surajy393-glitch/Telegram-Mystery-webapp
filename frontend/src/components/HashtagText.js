import { useNavigate } from "react-router-dom";

const HashtagText = ({ text, className = "" }) => {
  const navigate = useNavigate();

  const handleHashtagClick = (hashtag) => {
    try {
      if (!hashtag) return;
      // Remove # symbol if present and ensure it's a string
      const searchTerm = String(hashtag).startsWith('#') ? hashtag : `#${hashtag}`;
      // Navigate to search page with the hashtag
      navigate(`/search?q=${encodeURIComponent(searchTerm)}&type=posts`);
    } catch (error) {
      console.error('Error navigating to hashtag search:', error);
    }
  };

  const parseTextWithHashtags = (text) => {
    if (!text || typeof text !== 'string') return text;
    
    try {
      // Regex to find hashtags (# followed by word characters)
      const hashtagRegex = /#(\w+)/g;
      const parts = [];
      let lastIndex = 0;
      let match;
      let matchCount = 0;
      const maxMatches = 50; // Prevent infinite loops

      // Reset regex lastIndex to prevent issues with global flag
      hashtagRegex.lastIndex = 0;

      while ((match = hashtagRegex.exec(text)) !== null && matchCount < maxMatches) {
        matchCount++;
        
        // Safety check for match object
        if (!match || match.length === 0 || typeof match.index !== 'number') {
          break;
        }
        
        // Add text before hashtag
        if (match.index > lastIndex) {
          const beforeText = text.slice(lastIndex, match.index);
          if (beforeText) {
            parts.push(beforeText);
          }
        }
        
        // Get the full hashtag match
        const fullMatch = match[0];
        if (fullMatch && typeof fullMatch === 'string') {
          // Add clickable hashtag
          parts.push(
            <span
              key={`hashtag-${match.index}-${matchCount}`}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                handleHashtagClick(fullMatch);
              }}
              className="text-blue-600 hover:text-blue-800 cursor-pointer font-medium transition-colors select-none"
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleHashtagClick(fullMatch);
                }
              }}
            >
              {fullMatch}
            </span>
          );
        }
        
        lastIndex = match.index + fullMatch.length;
        
        // Prevent infinite loop on zero-length matches
        if (fullMatch.length === 0) {
          break;
        }
      }
      
      // Add remaining text
      if (lastIndex < text.length) {
        const remainingText = text.slice(lastIndex);
        if (remainingText) {
          parts.push(remainingText);
        }
      }
      
      return parts.length > 0 ? parts : text;
    } catch (error) {
      console.error('Error parsing hashtags:', error);
      return text; // Return original text if parsing fails
    }
  };

  return (
    <span className={className}>
      {parseTextWithHashtags(text)}
    </span>
  );
};

export default HashtagText;