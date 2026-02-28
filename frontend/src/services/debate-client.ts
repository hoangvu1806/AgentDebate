import { DebateSSEEvent } from "@/types/debate";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface DebateRequestParams {
  topic: string;
  maxRounds?: number;
  enableStreaming?: boolean;
  enableNeutralAgent?: boolean;
}

export function streamDebate(
  params: DebateRequestParams,
  onEvent: (event: DebateSSEEvent) => void,
  onError: (error: Error) => void,
  onComplete: () => void,
): AbortController {
  const controller = new AbortController();

  const body = JSON.stringify({
    topic: params.topic,
    max_rounds: params.maxRounds ?? 3,
    enable_streaming: params.enableStreaming ?? true,
    enable_neutral_agent: params.enableNeutralAgent ?? true,
  });

  fetch(`${API_BASE_URL}/api/debate/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
    signal: controller.signal,
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }
      if (!response.body) {
        throw new Error("Response body is null");
      }
      return readSSEStream(response.body, onEvent);
    })
    .then(() => {
      onComplete();
    })
    .catch((err: unknown) => {
      if (err instanceof DOMException && err.name === "AbortError") {
        return;
      }
      onError(err instanceof Error ? err : new Error(String(err)));
    });

  return controller;
}

async function readSSEStream(
  body: ReadableStream<Uint8Array>,
  onEvent: (event: DebateSSEEvent) => void,
): Promise<void> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    // Keep the last (potentially incomplete) line in the buffer
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith(":")) continue;

      if (trimmed.startsWith("data:")) {
        const jsonStr = trimmed.slice(5).trim();
        if (!jsonStr) continue;

        try {
          const parsed = JSON.parse(jsonStr) as DebateSSEEvent;
          onEvent(parsed);
        } catch {
          // Silently skip malformed JSON lines from SSE
        }
      }
    }
  }
}
