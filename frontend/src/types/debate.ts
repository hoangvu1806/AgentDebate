export type AgentRole = "PRO" | "CON" | "NEUTRAL" | "JUDGE" | "SUMMARY";

export interface AgentState {
  role: AgentRole;
  reasoning: string;
  conclusion: string;
  isActive: boolean;
  streamBuffer: string;
}

export interface RoundSnapshot {
  round: number;
  agents: Record<AgentRole, AgentState>;
}

export interface DebateSession {
  topic: string;
  currentRound: number;
  viewingRound: number;
  maxRounds: number;
  isRunning: boolean;
  activeAgent: AgentRole | null;
  agents: Record<AgentRole, AgentState>;
  roundHistory: RoundSnapshot[];
}

export interface TopicReadyEvent {
  type: "topic_ready";
  topic: string;
  user_context: string;
}

export interface NodeStartEvent {
  type: "node_start";
  agent: AgentRole;
}

export interface StreamTokenEvent {
  type: "stream_token";
  agent: AgentRole;
  token: string;
}

export interface NodeEndEvent {
  type: "node_end";
  agent: AgentRole;
  reasoning: string;
  conclusion: string;
  round: number;
}

export interface DebateEndEvent {
  type: "debate_end";
}

export interface DebateErrorEvent {
  type: "debate_error";
  message: string;
}

export type DebateSSEEvent =
  | TopicReadyEvent
  | NodeStartEvent
  | StreamTokenEvent
  | NodeEndEvent
  | DebateErrorEvent
  | DebateEndEvent;
