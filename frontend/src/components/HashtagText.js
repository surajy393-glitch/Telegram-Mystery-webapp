import { useNavigate } from "react-router-dom";

const HashtagText = ({ text, className = "" }) => {
  const navigate = useNavigate();

  const handleHashtagClick = (hashtag) => {
    // Remove # symbol if present
    const searchTerm = hashtag.startsWith('#') ? hashtag : `#${hashtag}`;
    // Navigate to search page with the hashtag
    navigate(`/search?q=${encodeURIComponent(searchTerm)}&type=posts`);
  };

  const parseTextWithHashtags = (text) => {
    if (!text) return text;
    
    // Regex to find hashtags (# followed by word characters)
    const hashtagRegex = /#(\w+)/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = hashtagRegex.exec(text)) !== null) {
      // Add text before hashtag
      if (match.index > lastIndex) {
        parts.push(text.slice(lastIndex, match.index));
      }
      
      // Add clickable hashtag
      parts.push(
        <span
          key={match.index}
          onClick={(e) => {
            e.stopPropagation();
            handleHashtagClick(match[0]);
          }}
          className="text-blue-600 hover:text-blue-800 cursor-pointer font-medium transition-colors"
        >
          {match[0]}
        </span>
      );
      
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }
    
    return parts.length > 0 ? parts : text;
  };

  return (
    <span className={className}>
      {parseTextWithHashtags(text)}
    </span>
  );
};

export default HashtagText;