'use client';

import { useState, useRef, useEffect } from 'react';
import { sendMessageToOrchestrator } from '@/lib/api';

export default function PitchQuestChat() {
    // Load saved session from localStorage on component mount
    const [sessionId, setSessionId] = useState<string | null>(() => {
        if (typeof window !== 'undefined') {
            return localStorage.getItem('pitchquest_session_id');
        }
        return null;
    });

    const [messages, setMessages] = useState<Array<{ role: string, content: string }>>(() => {
        if (typeof window !== 'undefined') {
            const saved = localStorage.getItem('pitchquest_messages');
            return saved ? JSON.parse(saved) : [];
        }
        return [];
    });

    const [currentPhase, setCurrentPhase] = useState<'mentor' | 'investor' | 'evaluator'>(() => {
        if (typeof window !== 'undefined') {
            const saved = localStorage.getItem('pitchquest_phase');
            return saved ? saved as any : 'mentor';
        }
        return 'mentor';
    });

    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedInvestor, setSelectedInvestor] = useState<string>('');

    // Auto-scroll to bottom
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Save to localStorage whenever state changes
    useEffect(() => {
        if (sessionId) {
            localStorage.setItem('pitchquest_session_id', sessionId);
        }
    }, [sessionId]);

    useEffect(() => {
        localStorage.setItem('pitchquest_messages', JSON.stringify(messages));
    }, [messages]);

    useEffect(() => {
        localStorage.setItem('pitchquest_phase', currentPhase);
    }, [currentPhase]);

    // Send first message only if no existing session
    useEffect(() => {
        if (messages.length === 0) {
            const initialMessage = "Hi, I want to practice my pitch";
            handleSendMessage(initialMessage, true);
        }
    }, []);

    const handleSendMessage = async (messageText?: string, isAutomatic = false) => {
        const textToSend = messageText || inputValue.trim();
        if (textToSend === '') return;

        // Add user message to chat (unless it's the automatic first message)
        if (!isAutomatic) {
            const userMessage = {
                role: 'user',
                content: textToSend
            };
            setMessages(prev => [...prev, userMessage]);
        }

        setInputValue('');
        setIsLoading(true);
        setError(null);

        try {
            const response = await sendMessageToOrchestrator(
                textToSend,
                sessionId,
                selectedInvestor || null
            );

            if (!sessionId && response.session_id) {
                setSessionId(response.session_id);
            }

            const aiMessage = {
                role: 'assistant',
                content: response.response
            };
            setMessages(prev => [...prev, aiMessage]);

            if (response.current_phase) {
                setCurrentPhase(response.current_phase);
            }

        } catch (err) {
            setError('Failed to send message. Is your backend running?');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !isLoading) {
            handleSendMessage();
        }
    };

    // Clear session button
    const handleNewSession = () => {
        localStorage.clear();
        setSessionId(null);
        setMessages([]);
        setCurrentPhase('mentor');
        setSelectedInvestor('');
        window.location.reload();
    };

    // Format message content (basic markdown support)
    const formatMessage = (content: string) => {
        // Convert headers (your evaluator uses these)
        content = content.replace(/^# (.*?)$/gm, '<h1 style="color: #5a4a42; margin: 24px 0 16px 0; font-weight: 700; font-size: 20px;">$1</h1>');
        content = content.replace(/^## (.*?)$/gm, '<h2 style="color: #5a4a42; margin: 20px 0 12px 0; font-weight: 600; font-size: 18px;">$1</h2>');
        content = content.replace(/^### (.*?)$/gm, '<h3 style="color: #5a4a42; margin: 16px 0 8px 0; font-weight: 600; font-size: 16px;">$1</h3>');

        // Convert **bold** to <strong>
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #5a4a42;">$1</strong>');

        // Convert *italic* to <em>
        content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Convert bullet points (your evaluator uses these)
        content = content.replace(/^- (.*?)$/gm, '<div style="margin: 4px 0; padding-left: 16px;">• $1</div>');
        content = content.replace(/^• (.*?)$/gm, '<div style="margin: 4px 0; padding-left: 16px;">• $1</div>');

        // Convert numbered lists
        content = content.replace(/^\d+\. (.*?)$/gm, '<div style="margin: 4px 0; padding-left: 16px;">$&</div>');

        // Convert horizontal rules (separators)
        content = content.replace(/^---$/gm, '<hr style="margin: 20px 0; border: none; border-top: 1px solid #e0d5cc;">');

        // Convert line breaks
        content = content.replace(/\n/g, '<br />');

        return content;
    };

    return (
        <div className="min-h-screen" style={{ backgroundColor: '#fbf9f7', fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" }}>
            <style jsx global>{`
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
                
                * {
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                }
                
                /* Custom scrollbar */
                ::-webkit-scrollbar {
                    width: 8px;
                    height: 8px;
                }
                
                ::-webkit-scrollbar-track {
                    background: #f0e8e2;
                    border-radius: 4px;
                }
                
                ::-webkit-scrollbar-thumb {
                    background: #d4886a;
                    border-radius: 4px;
                }
                
                ::-webkit-scrollbar-thumb:hover {
                    background: #c7785a;
                }
            `}</style>

            <div className="flex flex-col h-screen">
                {/* Header */}
                <div style={{ backgroundColor: 'white', borderBottom: '1px solid #f0e8e2' }} className="px-4 sm:px-6 py-4">
                    <div className="max-w-6xl mx-auto flex justify-between items-center">
                        {/* Logo */}
                        <div className="flex items-center gap-3">
                            <div style={{
                                background: 'linear-gradient(135deg, #d4886a, #a08b7c)',
                                width: '36px',
                                height: '36px',
                                borderRadius: '8px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'white',
                                fontWeight: 'bold',
                                fontSize: '18px'
                            }}>
                                P
                            </div>
                            <span style={{
                                fontSize: '20px',
                                fontWeight: '600',
                                color: '#5a4a42',
                                letterSpacing: '-0.5px'
                            }}>
                                PitchQuest
                            </span>
                        </div>

                        {/* Progress Indicator */}
                        <div className="hidden sm:flex items-center gap-6">
                            {[
                                { name: 'Mentor', key: 'mentor' },
                                { name: 'Investor', key: 'investor' },
                                { name: 'Evaluator', key: 'evaluator' }
                            ].map((phase, index, phases) => (
                                <div key={phase.key} className="flex items-center">
                                    <div className="flex items-center gap-2">
                                        <div style={{
                                            width: currentPhase === phase.key ? '10px' : '8px',
                                            height: currentPhase === phase.key ? '10px' : '8px',
                                            borderRadius: '50%',
                                            backgroundColor: currentPhase === phase.key
                                                ? '#d4886a'
                                                : phases.findIndex(p => p.key === currentPhase) > index
                                                    ? '#8b6f5c'
                                                    : '#e0d5cc',
                                            transition: 'all 0.3s',
                                            boxShadow: currentPhase === phase.key ? '0 0 0 3px rgba(212, 136, 106, 0.2)' : 'none'
                                        }} />
                                        <span style={{
                                            fontSize: '14px',
                                            fontWeight: currentPhase === phase.key ? '600' : '400',
                                            color: currentPhase === phase.key ? '#5a4a42' : '#a08b7c',
                                            transition: 'all 0.3s'
                                        }}>
                                            {phase.name}
                                        </span>
                                    </div>
                                    {index < phases.length - 1 && (
                                        <span style={{ margin: '0 12px', color: '#e0d5cc' }}>→</span>
                                    )}
                                </div>
                            ))}
                        </div>

                        {/* New Session Button */}
                        <button
                            onClick={handleNewSession}
                            style={{
                                padding: '8px 16px',
                                backgroundColor: '#f5e6db',
                                border: 'none',
                                borderRadius: '8px',
                                color: '#8b6f5c',
                                fontSize: '14px',
                                fontWeight: '500',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f0dccf'}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#f5e6db'}
                        >
                            New Session
                        </button>
                    </div>
                </div>

                {/* Mobile Progress */}
                <div className="sm:hidden px-4 py-2" style={{ backgroundColor: '#f5f1ed' }}>
                    <div className="flex justify-center items-center gap-4">
                        {['mentor', 'investor', 'evaluator'].map((phase) => (
                            <span
                                key={phase}
                                style={{
                                    fontSize: '12px',
                                    fontWeight: currentPhase === phase ? '600' : '400',
                                    color: currentPhase === phase ? '#5a4a42' : '#a08b7c',
                                    textTransform: 'capitalize'
                                }}
                            >
                                {phase}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Error display */}
                {error && (
                    <div className="px-4 py-2" style={{ backgroundColor: '#fff5f5' }}>
                        <div className="max-w-6xl mx-auto">
                            <div style={{ color: '#c7785a', fontSize: '14px' }}>
                                {error}
                            </div>
                        </div>
                    </div>
                )}

                {/* Chat Area - Maximized */}
                <div className="flex-1 overflow-y-auto" style={{ backgroundColor: '#fbf9f7' }}>
                    <div className="max-w-4xl mx-auto p-4 sm:p-6">
                        {messages.map((message, index) => (
                            <div key={index} className={`mb-6 flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`flex gap-3 max-w-[85%] sm:max-w-[75%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                    {/* Avatar */}
                                    <div style={{
                                        width: '36px',
                                        height: '36px',
                                        borderRadius: '50%',
                                        backgroundColor: message.role === 'user' ? '#d4886a' : '#f5e6db',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        flexShrink: 0,
                                        fontSize: '14px',
                                        fontWeight: '600',
                                        color: message.role === 'user' ? 'white' : '#8b6f5c'
                                    }}>
                                        {message.role === 'user' ? 'Y' : currentPhase.charAt(0).toUpperCase()}
                                    </div>

                                    {/* Message */}
                                    <div>
                                        <div style={{
                                            fontSize: '12px',
                                            color: '#8b7568',
                                            marginBottom: '4px',
                                            fontWeight: '500'
                                        }} className={message.role === 'user' ? 'text-right' : 'text-left'}>
                                            {message.role === 'user' ? 'You' : currentPhase.charAt(0).toUpperCase() + currentPhase.slice(1)}
                                        </div>
                                        <div
                                            style={{
                                                padding: '12px 16px',
                                                borderRadius: '12px',
                                                backgroundColor: message.role === 'user' ? '#d4886a' : 'white',
                                                color: message.role === 'user' ? 'white' : '#5a4a42',
                                                border: message.role === 'user' ? 'none' : '1px solid #f0e8e2',
                                                fontSize: '15px',
                                                lineHeight: '1.6',
                                                letterSpacing: '0.01em'
                                            }}
                                            dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }}
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex justify-start mb-6">
                                <div className="flex gap-3">
                                    <div style={{
                                        width: '36px',
                                        height: '36px',
                                        borderRadius: '50%',
                                        backgroundColor: '#f5e6db',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontSize: '14px',
                                        fontWeight: '600',
                                        color: '#8b6f5c'
                                    }}>
                                        {currentPhase.charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '12px', color: '#8b7568', marginBottom: '4px', fontWeight: '500' }}>
                                            {currentPhase.charAt(0).toUpperCase() + currentPhase.slice(1)}
                                        </div>
                                        <div style={{
                                            padding: '12px 16px',
                                            backgroundColor: 'white',
                                            border: '1px solid #f0e8e2',
                                            borderRadius: '12px'
                                        }}>
                                            <span style={{ color: '#a08b7c' }}>Thinking...</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                </div>

                {/* Input Area with Always-Visible Investor Dropdown */}
                <div style={{
                    backgroundColor: 'white',
                    borderTop: '1px solid #f0e8e2',
                    padding: '20px'
                }}>
                    <div className="max-w-4xl mx-auto">
                        <div className="flex gap-2 sm:gap-3 items-center">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder={isLoading ? "Wait for response..." : "Type your response..."}
                                disabled={isLoading}
                                style={{
                                    flex: 1,
                                    padding: '12px 18px',
                                    border: '1px solid #e0d5cc',
                                    borderRadius: '10px',
                                    fontSize: '15px',
                                    backgroundColor: '#fbf9f7',
                                    color: '#5a4a42',
                                    outline: 'none',
                                    transition: 'all 0.2s',
                                    fontFamily: 'Inter, sans-serif',
                                    letterSpacing: '0.01em'
                                }}
                                onFocus={(e) => {
                                    e.target.style.borderColor = '#d4886a';
                                    e.target.style.backgroundColor = 'white';
                                }}
                                onBlur={(e) => {
                                    e.target.style.borderColor = '#e0d5cc';
                                    e.target.style.backgroundColor = '#fbf9f7';
                                }}
                            />

                            {/* Always-Visible Investor Dropdown */}
                            <select
                                value={selectedInvestor}
                                onChange={(e) => setSelectedInvestor(e.target.value)}
                                style={{
                                    padding: '12px 14px',
                                    border: '1px solid #e0d5cc',
                                    borderRadius: '10px',
                                    fontSize: '14px',
                                    backgroundColor: selectedInvestor ? '#f5e6db' : 'white',
                                    color: '#5a4a42',
                                    cursor: 'pointer',
                                    outline: 'none',
                                    fontWeight: selectedInvestor ? '500' : '400',
                                    fontFamily: 'Inter, sans-serif',
                                    minWidth: '140px'
                                }}
                            >
                                <option value="">Select...</option>
                                <option value="aria">👩‍💼 Aria</option>
                                <option value="anna">👩‍💻 Anna</option>
                                <option value="adam">👨‍💼 Adam</option>
                                <option value="random">🎲 Random</option>
                            </select>

                            <button
                                onClick={() => handleSendMessage()}
                                disabled={isLoading}
                                style={{
                                    padding: '12px 24px',
                                    backgroundColor: isLoading ? '#e0d5cc' : '#d4886a',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '10px',
                                    fontWeight: '600',
                                    fontSize: '15px',
                                    cursor: isLoading ? 'not-allowed' : 'pointer',
                                    transition: 'all 0.2s',
                                    fontFamily: 'Inter, sans-serif',
                                    letterSpacing: '0.02em'
                                }}
                                onMouseEnter={(e) => {
                                    if (!isLoading) {
                                        e.currentTarget.style.backgroundColor = '#c7785a';
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    if (!isLoading) {
                                        e.currentTarget.style.backgroundColor = '#d4886a';
                                    }
                                }}
                            >
                                {isLoading ? '...' : 'Send'}
                            </button>
                        </div>

                        {/* Optional: Show selected investor info */}
                        {selectedInvestor && selectedInvestor !== 'random' && (
                            <div style={{
                                marginTop: '8px',
                                fontSize: '12px',
                                color: '#8b7568'
                            }}>
                                {selectedInvestor === 'aria' && '💡 Aria Iyer - Friendly & Strategic Focus'}
                                {selectedInvestor === 'anna' && '💡 Anna Ito - Technical & Rigorous Analysis'}
                                {selectedInvestor === 'adam' && '💡 Adam Ingram - Supportive & Enthusiastic'}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}