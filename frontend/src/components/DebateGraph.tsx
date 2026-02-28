"use client";

import { useRef, useState } from "react";
import styles from "./DebateGraph.module.css";
import AgentNode from "./AgentNode";
import AgentDetailView from "./AgentDetailView";
import { AgentRole, AgentState } from "@/types/debate";

type UIRole = "Judge" | "Con" | "Pro" | "Neutral" | "Summary";

const UI_TO_API: Record<UIRole, AgentRole> = {
  Pro: "PRO",
  Con: "CON",
  Neutral: "NEUTRAL",
  Judge: "JUDGE",
  Summary: "SUMMARY",
};

const API_TO_UI: Record<AgentRole, UIRole> = {
  PRO: "Pro",
  CON: "Con",
  NEUTRAL: "Neutral",
  JUDGE: "Judge",
  SUMMARY: "Summary",
};

interface DebateGraphProps {
  onToggleDetail?: (isOpen: boolean) => void;
  agents: Record<AgentRole, AgentState>;
  activeAgent: AgentRole | null;
}

export default function DebateGraph({ onToggleDetail, agents, activeAgent }: DebateGraphProps) {
  const [selectedAgent, setSelectedAgent] = useState<UIRole | null>(null);
  const [zoomingAgent, setZoomingAgent] = useState<UIRole | null>(null);
  const frozenAgentsRef = useRef<Record<AgentRole, AgentState> | null>(null);

  const updateFrozenSnapshot = () => {
    const existing = frozenAgentsRef.current;
    if (!existing) {
      frozenAgentsRef.current = structuredClone(agents);
      return;
    }
    const merged = { ...existing };
    for (const role of Object.keys(agents) as AgentRole[]) {
      const live = agents[role];
      if (live.reasoning || live.streamBuffer) {
        merged[role] = { ...live };
      }
    }
    frozenAgentsRef.current = merged;
  };

  const handleNodeClick = (role: UIRole) => {
    setZoomingAgent(role);
    updateFrozenSnapshot();
    setTimeout(() => {
      setSelectedAgent(role);
      setZoomingAgent(null);
      onToggleDetail?.(true);
    }, 250);
  };

  const handleBack = () => {
    frozenAgentsRef.current = null;
    setSelectedAgent(null);
    onToggleDetail?.(false);
  };

  const handleNavigate = (role: UIRole) => {
    setSelectedAgent(role);
  };

  const isNodeActive = (uiRole: UIRole): boolean => {
    if (!activeAgent) return false;
    return API_TO_UI[activeAgent] === uiRole;
  };

  const getAgentReasoning = (uiRole: UIRole): string => {
    const apiRole = UI_TO_API[uiRole];
    const liveState = agents[apiRole];
    const frozenState = frozenAgentsRef.current?.[apiRole];

    if (liveState.streamBuffer) return liveState.streamBuffer;
    if (liveState.reasoning) return liveState.reasoning;
    if (frozenState?.reasoning) return frozenState.reasoning;
    return "";
  };

  if (selectedAgent) {
    const reasoningText = getAgentReasoning(selectedAgent);
    return (
      <div className={styles.graphContainer}>
        <AgentDetailView
          role={selectedAgent}
          reasoningText={reasoningText}
          onBack={handleBack}
          onNavigate={handleNavigate}
        />
      </div>
    );
  }

  return (
    <div className={styles.graphContainer}>
      <div className={styles.connections}>
        <div className={`${styles.line} ${styles.lineVertical}`}></div>
        <div className={`${styles.line} ${styles.lineHorizontal}`}></div>
      </div>

      <div className={styles.nodesWrapper}>
        <div className={`${styles.nodePosition} ${styles.topNode} ${zoomingAgent === 'Judge' ? styles.zoomActive : zoomingAgent ? styles.fadeOut : ''}`}>
          <AgentNode role="Judge" isActive={isNodeActive("Judge")} onClick={() => handleNodeClick("Judge")} />
        </div>
        <div className={`${styles.nodePosition} ${styles.leftNode} ${zoomingAgent === 'Con' ? styles.zoomActive : zoomingAgent ? styles.fadeOut : ''}`}>
          <AgentNode role="Con" isActive={isNodeActive("Con")} onClick={() => handleNodeClick("Con")} />
        </div>
        <div className={`${styles.nodePosition} ${styles.rightNode} ${zoomingAgent === 'Pro' ? styles.zoomActive : zoomingAgent ? styles.fadeOut : ''}`}>
          <AgentNode role="Pro" isActive={isNodeActive("Pro")} onClick={() => handleNodeClick("Pro")} />
        </div>
        <div className={`${styles.nodePosition} ${styles.bottomNode} ${zoomingAgent === 'Neutral' ? styles.zoomActive : zoomingAgent ? styles.fadeOut : ''}`}>
          <AgentNode role="Neutral" isActive={isNodeActive("Neutral")} onClick={() => handleNodeClick("Neutral")} />
        </div>

        {(agents.SUMMARY.reasoning || agents.SUMMARY.streamBuffer || isNodeActive("Summary")) && (
          <div className={`${styles.nodePosition} ${styles.centerNode} ${zoomingAgent === 'Summary' ? styles.zoomActive : zoomingAgent ? styles.fadeOut : ''}`}>
            <AgentNode role="Summary" isActive={isNodeActive("Summary")} onClick={() => handleNodeClick("Summary")} />
          </div>
        )}
      </div>
    </div>
  );
}
