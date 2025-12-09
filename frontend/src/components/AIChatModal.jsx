import { useState, useRef, useEffect } from 'react';
import knowledgeCrystalService from '../services/knowledgeCrystalService';

export default function AIChatModal({ onClose, userRole }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hello! I'm your Knowledge Crystal AI assistant. I can help you find information from all uploaded documents. ${
        userRole === 'agent' 
          ? 'Ask me about mission documents, previous operations, or country-specific information.' 
          : userRole === 'technician'
          ? 'Ask me about technical documentation, equipment setup, or troubleshooting guides.'
          : 'Ask me anything about the documents in the knowledge base.'
      }`,
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');

    // Add user message
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);

    try {
      setIsLoading(true);

      // Determine user_role based on user role
      let user_role = 'agent';
      if (userRole === 'agent') {
        user_role = 'agent';
      } else if (userRole === 'technician') {
        user_role = 'technician';
      }

      // Send chat request
      const response = await knowledgeCrystalService.chatWithAI({
        query: userMessage,
        user_role: user_role,
        limit: 5,
      });

      // Extract response
      const aiResponse = response.data?.answer || 'Sorry, I could not find an answer to your question.';
      const matchedDocs = response.data?.matched_documents || [];

      // Format response with sources
      let formattedResponse = aiResponse;
      
      if (matchedDocs.length > 0) {
        formattedResponse += '\n\n**Sources:**\n';
        matchedDocs.forEach((doc, index) => {
          formattedResponse += `${index + 1}. ${doc.title || 'Untitled Document'}\n`;
        });
      }

      // Add AI response
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: formattedResponse },
      ]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error while processing your request. Please try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={styles.header}>
          <div>
            <h2 style={styles.title}>AI Assistant</h2>
            <p style={styles.subtitle}>Chat with Knowledge Crystal</p>
          </div>
          <button onClick={onClose} style={styles.closeButton}>×</button>
        </div>

        {/* Messages */}
        <div style={styles.messagesContainer}>
          {messages.map((message, index) => (
            <div
              key={index}
              style={{
                ...styles.messageWrapper,
                ...(message.role === 'user' ? styles.userMessageWrapper : styles.assistantMessageWrapper),
              }}
            >
              <div
                style={{
                  ...styles.message,
                  ...(message.role === 'user' ? styles.userMessage : styles.assistantMessage),
                }}
              >
                {message.role === 'assistant' && (
                  <div style={styles.avatarContainer}>
                    <span style={styles.avatar}>🤖</span>
                  </div>
                )}
                <div style={styles.messageContent}>
                  {message.content.split('\n').map((line, i) => {
                    // Format bold text
                    const formattedLine = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                    return (
                      <p 
                        key={i} 
                        style={styles.messageParagraph}
                        dangerouslySetInnerHTML={{ __html: formattedLine }}
                      />
                    );
                  })}
                </div>
                {message.role === 'user' && (
                  <div style={styles.avatarContainer}>
                    <span style={styles.avatar}>👤</span>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div style={{ ...styles.messageWrapper, ...styles.assistantMessageWrapper }}>
              <div style={{ ...styles.message, ...styles.assistantMessage }}>
                <div style={styles.avatarContainer}>
                  <span style={styles.avatar}>🤖</span>
                </div>
                <div style={styles.loadingDots}>
                  <span>•</span>
                  <span>•</span>
                  <span>•</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div style={styles.inputContainer}>
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about the documents..."
            style={styles.input}
            rows="3"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!inputMessage.trim() || isLoading}
            style={{
              ...styles.sendButton,
              ...((!inputMessage.trim() || isLoading) && styles.sendButtonDisabled),
            }}
          >
            {isLoading ? '...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(10, 14, 39, 0.85)',
    backdropFilter: 'blur(8px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    padding: '20px',
  },
  modal: {
    backgroundColor: '#1a1f3a',
    borderRadius: '12px',
    width: '100%',
    maxWidth: '800px',
    height: '80vh',
    display: 'flex',
    flexDirection: 'column',
    border: '1px solid #2d3354',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 24px',
    borderBottom: '1px solid #2d3354',
  },
  title: {
    color: '#29a399',
    fontSize: '1.5rem',
    fontWeight: '600',
    margin: 0,
  },
  subtitle: {
    color: '#8b92b0',
    fontSize: '0.85rem',
    margin: '4px 0 0 0',
  },
  closeButton: {
    background: 'none',
    border: 'none',
    color: '#8b92b0',
    fontSize: '2rem',
    cursor: 'pointer',
    padding: 0,
    width: '32px',
    height: '32px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  messagesContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  messageWrapper: {
    display: 'flex',
    width: '100%',
  },
  userMessageWrapper: {
    justifyContent: 'flex-end',
  },
  assistantMessageWrapper: {
    justifyContent: 'flex-start',
  },
  message: {
    display: 'flex',
    gap: '12px',
    maxWidth: '80%',
    padding: '12px 16px',
    borderRadius: '12px',
    alignItems: 'flex-start',
  },
  userMessage: {
    backgroundColor: '#29a399',
    color: 'white',
  },
  assistantMessage: {
    backgroundColor: '#0a0e27',
    color: '#c5c7d4',
    border: '1px solid #2d3354',
  },
  avatarContainer: {
    flexShrink: 0,
  },
  avatar: {
    fontSize: '1.5rem',
  },
  messageContent: {
    flex: 1,
  },
  messageParagraph: {
    margin: '4px 0',
    lineHeight: '1.5',
  },
  loadingDots: {
    display: 'flex',
    gap: '4px',
    padding: '8px',
  },
  inputContainer: {
    padding: '20px 24px',
    borderTop: '1px solid #2d3354',
    display: 'flex',
    gap: '12px',
  },
  input: {
    flex: 1,
    padding: '12px',
    backgroundColor: '#0a0e27',
    border: '1px solid #2d3354',
    borderRadius: '8px',
    color: 'white',
    fontSize: '1rem',
    fontFamily: 'inherit',
    resize: 'none',
  },
  sendButton: {
    padding: '12px 24px',
    backgroundColor: '#29a399',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: '600',
    whiteSpace: 'nowrap',
    alignSelf: 'flex-end',
  },
  sendButtonDisabled: {
    backgroundColor: '#2d3354',
    cursor: 'not-allowed',
  },
};

// Add CSS animation for loading dots
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes blink {
    0%, 20% { opacity: 0.2; }
    40% { opacity: 1; }
    100% { opacity: 0.2; }
  }
  
  .loading-dots span {
    animation: blink 1.4s infinite;
  }
  
  .loading-dots span:nth-child(2) {
    animation-delay: 0.2s;
  }
  
  .loading-dots span:nth-child(3) {
    animation-delay: 0.4s;
  }
`;
document.head.appendChild(styleSheet);
