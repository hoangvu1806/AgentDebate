"use client";

import { useCallback, useRef, useState } from "react";
import { streamDebate } from "@/services/debate-client";
import {
  AgentRole,
  AgentState,
  DebateSession,
  DebateSSEEvent,
  RoundSnapshot,
} from "@/types/debate";

const AGENT_ROLES: AgentRole[] = ["PRO", "CON", "NEUTRAL", "JUDGE", "SUMMARY"];

function createEmptyAgentState(role: AgentRole): AgentState {
  return {
    role,
    reasoning: "",
    conclusion: "",
    isActive: false,
    streamBuffer: "",
  };
}

function createEmptyAgents(): Record<AgentRole, AgentState> {
  const agents = {} as Record<AgentRole, AgentState>;
  for (const role of AGENT_ROLES) {
    agents[role] = createEmptyAgentState(role);
  }
  return agents;
}

function createInitialSession(topic: string, maxRounds: number): DebateSession {
  return {
    topic,
    currentRound: 1,
    viewingRound: 1,
    maxRounds,
    isRunning: false,
    activeAgent: null,
    agents: createEmptyAgents(),
    roundHistory: [],
  };
}

function snapshotCurrentRound(session: DebateSession): RoundSnapshot {
  const agentsCopy = {} as Record<AgentRole, AgentState>;
  for (const role of AGENT_ROLES) {
    agentsCopy[role] = { ...session.agents[role], isActive: false, streamBuffer: "" };
  }
  return { round: session.currentRound, agents: agentsCopy };
}

export function useDebate() {
  const [session, setSession] = useState<DebateSession>(
    createInitialSession("", 3),
  );
  const [error, setError] = useState<string | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const handleEvent = useCallback((event: DebateSSEEvent) => {
    switch (event.type) {
      case "topic_ready":
        setSession((prev) => ({ ...prev, topic: event.topic }));
        break;

      case "node_start":
        setSession((prev) => {
          // When PRO starts again after JUDGE has completed, it's a new round
          const isNewRound = event.agent === "PRO" &&
            prev.agents.JUDGE.reasoning !== "";
          
          let history = prev.roundHistory;
          let agents = prev.agents;
          let currentRound = prev.currentRound;

          if (isNewRound) {
            history = [...history, snapshotCurrentRound(prev)];
            agents = createEmptyAgents();
            currentRound = prev.currentRound + 1;
          }

          const updatedAgents = {} as Record<AgentRole, AgentState>;
          for (const role of AGENT_ROLES) {
            updatedAgents[role] = {
              ...agents[role],
              isActive: role === event.agent,
              streamBuffer: role === event.agent ? "" : agents[role].streamBuffer,
            };
          }

          return {
            ...prev,
            currentRound,
            viewingRound: currentRound,
            activeAgent: event.agent,
            agents: updatedAgents,
            roundHistory: history,
          };
        });
        break;

      case "stream_token":
        setSession((prev) => ({
          ...prev,
          agents: {
            ...prev.agents,
            [event.agent]: {
              ...prev.agents[event.agent],
              streamBuffer: prev.agents[event.agent].streamBuffer + event.token,
            },
          },
        }));
        break;

      case "node_end":
        setSession((prev) => ({
          ...prev,
          agents: {
            ...prev.agents,
            [event.agent]: {
              ...prev.agents[event.agent],
              reasoning: event.reasoning,
              conclusion: event.conclusion,
              isActive: false,
              streamBuffer: "",
            },
          },
          activeAgent: null,
        }));
        break;

      case "debate_end":
        setSession((prev) => {
          // Snapshot the final round
          const finalHistory = [...prev.roundHistory, snapshotCurrentRound(prev)];
          return {
            ...prev,
            isRunning: false,
            activeAgent: null,
            roundHistory: finalHistory,
          };
        });
        break;

      case "debate_error":
        setSession((prev) => ({
           ...prev,
           isRunning: false,
           activeAgent: null,
        }));
        setError(event.message);
        break;
    }
  }, []);

  const startDebate = useCallback(
    (topic: string, maxRounds: number = 3) => {
      controllerRef.current?.abort();

      const newSession = createInitialSession(topic, maxRounds);
      newSession.isRunning = true;
      setSession(newSession);
      setError(null);

      controllerRef.current = streamDebate(
        { topic, maxRounds },
        handleEvent,
        (err) => {
          setError(err.message);
          setSession((prev) => ({ ...prev, isRunning: false }));
        },
        () => {
          setSession((prev) => ({ ...prev, isRunning: false }));
        },
      );
    },
    [handleEvent],
  );

  const stopDebate = useCallback(() => {
    controllerRef.current?.abort();
    controllerRef.current = null;
    setSession((prev) => ({ ...prev, isRunning: false, activeAgent: null }));
  }, []);

  const goToRound = useCallback((round: number) => {
    setSession((prev) => {
      const maxAvailable = prev.roundHistory.length > 0
        ? prev.roundHistory[prev.roundHistory.length - 1].round
        : prev.currentRound;
      const clamped = Math.max(1, Math.min(round, maxAvailable));
      return { ...prev, viewingRound: clamped };
    });
  }, []);

  const goToPrevRound = useCallback(() => {
    setSession((prev) => {
      if (prev.viewingRound <= 1) return prev;
      return { ...prev, viewingRound: prev.viewingRound - 1 };
    });
  }, []);

  const goToNextRound = useCallback(() => {
    setSession((prev) => {
      const maxAvailable = prev.isRunning
        ? prev.currentRound
        : prev.roundHistory.length;
      if (prev.viewingRound >= maxAvailable) return prev;
      return { ...prev, viewingRound: prev.viewingRound + 1 };
    });
  }, []);

  // Resolve which agents to display based on viewingRound
  const isViewingLive = session.viewingRound === session.currentRound;
  const displayAgents = isViewingLive
    ? session.agents
    : (session.roundHistory.find((s) => s.round === session.viewingRound)?.agents ?? session.agents);
  const displayActiveAgent = isViewingLive ? session.activeAgent : null;

  return {
    session,
    error,
    startDebate,
    stopDebate,
    goToRound,
    goToPrevRound,
    goToNextRound,
    displayAgents,
    displayActiveAgent,
    isViewingLive,
  };
}
