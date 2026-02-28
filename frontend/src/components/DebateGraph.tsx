"use client";

import { useState } from "react";
import styles from "./DebateGraph.module.css";
import AgentNode from "./AgentNode";
import AgentDetailView from "./AgentDetailView";
import { AgentRole, AgentState } from "@/types/debate";

type UIRole = "Judge" | "Con" | "Pro" | "Neutral" | "Summary";

function apiRoleToUI(role: AgentRole): UIRole {
  const map: Record<AgentRole, UIRole> = {
    PRO: "Pro",
    CON: "Con",
    NEUTRAL: "Neutral",
    JUDGE: "Judge",
    SUMMARY: "Summary",
  };
  return map[role];
}

interface DebateGraphProps {
  onToggleDetail?: (isOpen: boolean) => void;
  agents: Record<AgentRole, AgentState>;
  activeAgent: AgentRole | null;
}

export default function DebateGraph({ onToggleDetail, agents, activeAgent }: DebateGraphProps) {
  const [selectedAgent, setSelectedAgent] = useState<UIRole | null>(null);
  const [zoomingAgent, setZoomingAgent] = useState<UIRole | null>(null);

  const handleNodeClick = (role: UIRole) => {
    setZoomingAgent(role);
    setTimeout(() => {
      setSelectedAgent(role);
      setZoomingAgent(null);
      onToggleDetail?.(true);
    }, 250);
  };

  const handleBack = () => {
    setSelectedAgent(null);
    onToggleDetail?.(false);
  };

  const isNodeActive = (uiRole: UIRole): boolean => {
    if (!activeAgent) return false;
    return apiRoleToUI(activeAgent) === uiRole;
  };

  const getAgentReasoning = (uiRole: UIRole): string => {
    const roleMap: Record<UIRole, AgentRole> = {
      Pro: "PRO",
      Con: "CON",
      Neutral: "NEUTRAL",
      Judge: "JUDGE",
      Summary: "SUMMARY",
    };
    const apiRole = roleMap[uiRole];
    const agentState = agents[apiRole];

    // Prioritize live stream buffer if agent is actively streaming
    if (agentState.streamBuffer) return agentState.streamBuffer;
    if (agentState.reasoning) return agentState.reasoning;
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
          onNavigate={setSelectedAgent}
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
        
        {/* Only show Summary node if it has text (meaning debate reached the end) or is currently active */}
        {(agents.SUMMARY.reasoning || agents.SUMMARY.streamBuffer || isNodeActive("Summary")) && (
          <div className={`${styles.nodePosition} ${styles.centerNode} ${zoomingAgent === 'Summary' ? styles.zoomActive : zoomingAgent ? styles.fadeOut : ''}`}>
            <AgentNode role="Summary" isActive={isNodeActive("Summary")} onClick={() => handleNodeClick("Summary")} />
          </div>
        )}
      </div>
    </div>
  );
}
