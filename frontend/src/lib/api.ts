// Fixed api.ts - Now includes investor selection
// src/lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

console.log('API_BASE_URL:', API_BASE_URL); // Add this temporarily to debug


export async function sendMessageToOrchestrator(
    message: string,
    sessionId?: string | null,
    selectedInvestor?: string | null  // 🔧 ADD: investor selection parameter
) {
    try {
        const requestBody: any = {
            message: message,
            session_id: sessionId || null,
            selected_investor?: string | null;
        };

        // 🔧 ADD: Include investor selection if provided
        if (selectedInvestor) {
            requestBody.selected_investor = selectedInvestor;
        }

        const response = await fetch(`${API_BASE_URL}/orchestrator/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to send message:', error);
        throw error;
    }
}