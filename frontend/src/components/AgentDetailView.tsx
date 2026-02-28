import ReactMarkdown from "react-markdown";
import AgentNode from "./AgentNode";
import styles from "./AgentDetailView.module.css";

export type UIRole = "Judge" | "Con" | "Pro" | "Neutral" | "Summary";

interface AgentDetailViewProps {
  role: UIRole;
  reasoningText: string;
  onBack: () => void;
  onNavigate: (role: UIRole) => void;
}

const NAV_MAP: Record<UIRole, { left: UIRole; right: UIRole }> = {
  Judge: { left: "Con", right: "Pro" },
  Pro: { left: "Judge", right: "Neutral" },
  Neutral: { left: "Con", right: "Pro" },
  Con: { left: "Neutral", right: "Judge" },
  Summary: { left: "Con", right: "Pro" },
};

export default function AgentDetailView({ role, reasoningText, onBack, onNavigate }: AgentDetailViewProps) {
  const getRoleClass = () => {
    switch (role) {
      case "Pro": return styles.pro;
      case "Con": return styles.con;
      case "Judge": return styles.judge;
      case "Neutral": return styles.neutral;
      case "Summary": return styles.summary;
      default: return "";
    }
  };

  const { left, right } = NAV_MAP[role];

  return (
    <div className={`${styles.container} ${getRoleClass()}`}>
      <div className={styles.leftNav} onClick={() => onNavigate(left)}>
        <AgentNode role={left} isActive={false} onClick={() => onNavigate(left)} />
      </div>
      <div className={styles.rightNav} onClick={() => onNavigate(right)}>
        <AgentNode role={right} isActive={false} onClick={() => onNavigate(right)} />
      </div>

      <div key={role} className={styles.mainContent}>
        <div className={styles.header}>
          <div className={styles.roleTitle}>{role.toUpperCase()} REASONING</div>
          <button className={styles.backBtn} onClick={onBack}>
            Close
          </button>
        </div>
        
        <div className={styles.textContent}>
          {reasoningText ? (
            <div className={styles.markdown}>
              <ReactMarkdown>{reasoningText}</ReactMarkdown>
            </div>
          ) : (
            <p className={styles.waiting}>Waiting for agent response...</p>
          )}
        </div>
      </div>
    </div>
  );
}
