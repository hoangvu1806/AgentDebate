"use client";

import styles from "./page.module.css";
import Header from "@/components/Header";
import DebateGraph from "@/components/DebateGraph";
import ChatInput from "@/components/ChatInput";
import { useState } from "react";
import { useDebate } from "@/hooks/useDebate";

export default function Home() {
  const [showNav, setShowNav] = useState(true);
  const [roundTransition, setRoundTransition] = useState<"left" | "right" | null>(null);

  const {
    session,
    error,
    startDebate,
    stopDebate,
    goToPrevRound,
    goToNextRound,
    displayAgents,
    displayActiveAgent,
    isViewingLive,
  } = useDebate();

  const handleTopicSubmit = (topic: string) => {
    if (session.isRunning) {
      stopDebate();
      return;
    }
    startDebate(topic);
  };

  const handlePrevRound = () => {
    if (session.viewingRound <= 1) return;
    setRoundTransition("left");
    setTimeout(() => {
      goToPrevRound();
      setRoundTransition(null);
    }, 300);
  };

  const handleNextRound = () => {
    const maxAvailable = session.isRunning
      ? session.currentRound
      : session.roundHistory.length;
    if (session.viewingRound >= maxAvailable) return;
    setRoundTransition("right");
    setTimeout(() => {
      goToNextRound();
      setRoundTransition(null);
    }, 300);
  };

  const topic = session.topic
    || (session.isRunning ? "Extracting topic..." : "AI Debate System");
  const roundLabel = session.isRunning && isViewingLive
    ? `ROUND ${session.currentRound}`
    : session.roundHistory.length > 0
      ? `ROUND ${session.viewingRound}`
      : "READY";

  const totalRounds = session.isRunning
    ? session.currentRound
    : session.roundHistory.length;
  const progressPercent = totalRounds > 0
    ? Math.round((session.viewingRound / totalRounds) * 100)
    : 0;

  const hasPrev = session.viewingRound > 1;
  const hasNext = session.viewingRound < totalRounds;

  const graphTransitionClass = roundTransition === "left"
    ? styles.slideOutRight
    : roundTransition === "right"
      ? styles.slideOutLeft
      : styles.slideIn;

  return (
    <main className={styles.container}>
      <Header topic={topic} />
      
      <div className={styles.content}>
        <div className={styles.roundTracker}>
          <span className={styles.roundText}>{roundLabel}</span>
          <div className={styles.roundProgress}>
            <div className={styles.progressBar} style={{ width: `${progressPercent}%` }}></div>
          </div>
          {isViewingLive && session.isRunning && (
            <span className={styles.liveIndicator}>DEBATING...</span>
          )}
        </div>

        {showNav && (
          <>
            <button
              className={`${styles.navButton} ${styles.prevButton} ${!hasPrev ? styles.navDisabled : ""}`}
              aria-label="Previous round"
              onClick={handlePrevRound}
              disabled={!hasPrev}
            >
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="m15 18-6-6 6-6"/>
              </svg>
            </button>

            <button
              className={`${styles.navButton} ${styles.nextButton} ${!hasNext ? styles.navDisabled : ""}`}
              aria-label="Next round"
              onClick={handleNextRound}
              disabled={!hasNext}
            >
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="m9 18 6-6-6-6"/>
              </svg>
            </button>
          </>
        )}

        <div className={`${styles.graphWrapper} ${graphTransitionClass}`}>
          <DebateGraph
            onToggleDetail={(isOpen: boolean) => setShowNav(!isOpen)}
            agents={displayAgents}
            activeAgent={displayActiveAgent}
          />
        </div>

        {error && (
          <div className={styles.errorBanner}>{error}</div>
        )}
      </div>
      
      <ChatInput
        onSubmit={handleTopicSubmit}
        disabled={session.isRunning}
      />
    </main>
  );
}
