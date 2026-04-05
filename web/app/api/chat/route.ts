import Anthropic from '@anthropic-ai/sdk';
import { SCHOLAR_SYSTEM_PROMPT } from '@/lib/prompts';
import { classifyIntent, getDirectResponse, buildContext, shouldEscalateToSonnet } from '@/lib/chat-context';
import type { ChatMessage } from '@/types';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { messages, model: requestedModel } = body as {
      messages: ChatMessage[];
      model?: 'haiku' | 'sonnet';
    };

    if (!messages || messages.length === 0) {
      return new Response(JSON.stringify({ error: 'No messages provided.' }), {
        status: 400, headers: { 'Content-Type': 'application/json' },
      });
    }

    const lastMessage = messages[messages.length - 1];
    if (lastMessage.role !== 'user') {
      return new Response(JSON.stringify({ error: 'Last message must be from user.' }), {
        status: 400, headers: { 'Content-Type': 'application/json' },
      });
    }

    const userMessage = lastMessage.content;
    const intent = classifyIntent(userMessage);

    // Direct responses skip Claude entirely
    const directResponse = getDirectResponse(intent);
    if (directResponse) {
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'text', text: directResponse })}\n\n`));
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'done' })}\n\n`));
          controller.close();
        },
      });
      return new Response(stream, {
        headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive' },
      });
    }

    // Build context from database
    const dbContext = await buildContext(intent, userMessage);

    // Select model
    let modelId = 'claude-haiku-4-5-20251001';
    if (requestedModel === 'sonnet' || shouldEscalateToSonnet(messages, userMessage)) {
      modelId = 'claude-sonnet-4-6';
    }

    const systemPrompt = SCHOLAR_SYSTEM_PROMPT + '\n\n=== CONTEXT FROM DATABASE ===\n' + dbContext;
    const claudeMessages = messages.map((m) => ({
      role: m.role as 'user' | 'assistant',
      content: m.content,
    }));

    // Check for API key
    if (!process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_API_KEY === 'sk-ant-PLACEHOLDER') {
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'text', text: 'The AI assistant is not configured yet. Please add your Anthropic API key to web/.env.local' })}\n\n`));
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'done' })}\n\n`));
          controller.close();
        },
      });
      return new Response(stream, {
        headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive' },
      });
    }

    const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

    const stream = anthropic.messages.stream({
      model: modelId,
      max_tokens: 2048,
      system: systemPrompt,
      messages: claudeMessages,
    });

    const encoder = new TextEncoder();
    const readable = new ReadableStream({
      async start(controller) {
        try {
          for await (const event of stream) {
            if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
              const data = JSON.stringify({ type: 'text', text: event.delta.text });
              controller.enqueue(encoder.encode(`data: ${data}\n\n`));
            }
          }
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'done', model: modelId })}\n\n`));
          controller.close();
        } catch (error: unknown) {
          const message = error instanceof Error ? error.message : 'An error occurred';
          const errData = JSON.stringify({ type: 'error', message });
          controller.enqueue(encoder.encode(`data: ${errData}\n\n`));
          controller.close();
        }
      },
    });

    return new Response(readable, {
      headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive' },
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Internal server error';
    return new Response(JSON.stringify({ error: message }), {
      status: 500, headers: { 'Content-Type': 'application/json' },
    });
  }
}
