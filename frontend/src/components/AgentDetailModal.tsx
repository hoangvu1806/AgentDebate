import { useEffect, type MouseEvent } from "react";
import styles from "./AgentDetailModal.module.css";

interface AgentDetailModalProps {
  role: "Judge" | "Con" | "Pro" | "Neutral";
  onClose: () => void;
}

export default function AgentDetailModal({ role, onClose }: AgentDetailModalProps) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  const getRoleClass = () => {
    switch (role) {
      case "Pro":
        return styles.pro;
      case "Con":
        return styles.con;
      case "Judge":
        return styles.judge;
      case "Neutral":
        return styles.neutral;
      default:
        return "";
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div 
        className={`${styles.modal} ${getRoleClass()}`} 
        onClick={(e: MouseEvent) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <button className={styles.closeBtn} onClick={onClose} aria-label="Close modal">
          <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className={styles.header}>
          <div className={styles.roleBadge}>{role.toUpperCase()}</div>
          <h2 className={styles.title}>SYSTEM REASONING LOG</h2>
        </div>

        <div className={styles.content}>
          <div className={styles.metricsGrid}>
            <div className={styles.metricBox}>
              <span className={styles.metricLabel}>CONFIDENCE</span>
              <span className={styles.metricValue}>94.2%</span>
            </div>
            <div className={styles.metricBox}>
              <span className={styles.metricLabel}>STATUS</span>
              <span className={styles.metricValueGlow}>ACTIVE</span>
            </div>
            <div className={styles.metricBox}>
              <span className={styles.metricLabel}>LATENCY</span>
              <span className={styles.metricValue}>12ms</span>
            </div>
          </div>

          <div className={styles.reasoningConsole}>
            <div className={styles.scanline}></div>
            <div className={styles.consoleHeader}>
              <span>[root@{role.toLowerCase()}_agent] ~ ./analyze_pattern.sh</span>
            </div>
            <div className={styles.consoleBody}>
              <p>&gt; Initializing neural pathways...</p>
              <p>&gt; Decoding primary arguments from current round...</p>
              <p className={styles.highlight}>&gt; WARNING: Logical fallacy detected in opponent&apos;s premise.</p>
              <p>&gt; Cross-referencing with knowledge base...</p>
              <p>&gt; Formulating optimal counter-argument framework.</p>
              <p>&gt; Synthesizing response<span className={styles.cursorWait}>_</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
