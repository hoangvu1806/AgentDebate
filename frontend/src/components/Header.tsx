import styles from "./Header.module.css";

interface HeaderProps {
  topic: string;
}

export default function Header({ topic }: HeaderProps) {
  return (
    <header className={styles.header}>
      <button className={styles.menuButton} aria-label="Menu">
        <div className={styles.diamondOuter}>
          <div className={styles.diamondInner}></div>
        </div>
      </button>

      <div className={styles.topicContainer}>
        <div className={styles.topicLabel}>TOPIC</div>
        <h1 className={styles.topicText}>{topic}</h1>
      </div>

      <button className={styles.profileButton} aria-label="Profile">
        <div className={styles.profileInner}></div>
      </button>
    </header>
  );
}
