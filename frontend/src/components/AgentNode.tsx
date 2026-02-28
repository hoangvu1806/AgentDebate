import { type KeyboardEvent } from "react";
import styles from "./AgentNode.module.css";

interface AgentNodeProps {
  role: "Judge" | "Con" | "Pro" | "Neutral" | "Summary";
  isActive?: boolean;
  onClick?: () => void;
}

export default function AgentNode({ role, isActive = false, onClick }: AgentNodeProps) {
  const getRoleColor = () => {
    switch (role) {
      case "Pro":
        return styles.pro;
      case "Con":
        return styles.con;
      case "Judge":
        return styles.judge;
      case "Neutral":
        return styles.neutral;
      case "Summary":
        return styles.summary;
      default:
        return "";
    }
  };

  return (
    <div 
      className={`${styles.nodeContainer} ${getRoleColor()} ${isActive ? styles.active : ""} ${role === "Judge" ? styles.isJudge : ""} ${role === "Summary" ? styles.isSummary : ""}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e: KeyboardEvent<HTMLDivElement>) => { if(e.key === 'Enter') onClick?.() }}
    >
      <div className={styles.diamondOuter}>
        <div className={styles.diamondInner}>
          <div className={styles.content}>
            <span className={styles.roleText}>{role}</span>
          </div>
        </div>
      </div>
      {isActive && <div className={styles.activeGlow}></div>}
    </div>
  );
}
