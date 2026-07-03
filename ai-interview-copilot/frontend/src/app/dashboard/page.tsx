"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Session {
  session_id: string;
  role: string;
  status: string;
  question_count: number;
  average_score: number;
  feedback: Record<string, any>;
  created_at: string;
}

export default function Dashboard() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/sessions")
      .then((r) => r.json())
      .then(setSessions)
      .finally(() => setLoading(false));
  }, []);

  const avgScore = sessions.length
    ? (sessions.reduce((sum, s) => sum + s.average_score, 0) / sessions.length).toFixed(1)
    : "—";
  const completed = sessions.filter((s) => s.status === "completed").length;

  return (
    <main style={{ maxWidth: 800, margin: "0 auto", padding: "2rem 1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1 style={{ margin: 0, fontSize: "1.5rem" }}>Progress Dashboard</h1>
        <Link href="/" style={{ color: "var(--primary)", textDecoration: "none", fontSize: "0.9rem" }}>
          ← New Interview
        </Link>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem", marginBottom: "2rem" }}>
        {[
          { label: "Total Sessions", value: sessions.length },
          { label: "Completed", value: completed },
          { label: "Avg Score", value: avgScore },
        ].map((stat) => (
          <div key={stat.label} style={{
            background: "var(--surface)", borderRadius: 12, padding: "1.25rem",
            border: "1px solid var(--border)", textAlign: "center",
          }}>
            <div style={{ fontSize: "1.8rem", fontWeight: 700 }}>{stat.value}</div>
            <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {loading ? (
        <div style={{ textAlign: "center", color: "var(--text-muted)", padding: "2rem" }}>Loading...</div>
      ) : sessions.length === 0 ? (
        <div style={{ textAlign: "center", color: "var(--text-muted)", padding: "2rem" }}>
          No sessions yet.{' '}
          <Link href="/" style={{ color: "var(--primary)" }}>Start your first interview</Link>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {sessions.map((s) => (
            <div key={s.session_id} style={{
              background: "var(--surface)", borderRadius: 12, padding: "1.25rem",
              border: "1px solid var(--border)", display: "flex", justifyContent: "space-between",
              alignItems: "center",
            }}>
              <div>
                <div style={{ fontWeight: 600 }}>{s.role || "General Interview"}</div>
                <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
                  {s.question_count} questions · {new Date(s.created_at).toLocaleDateString()}
                </div>
                {s.feedback?.summary && (
                  <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginTop: "0.3rem" }}>
                    {s.feedback.summary.slice(0, 100)}...
                  </div>
                )}
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{
                  fontSize: "1.2rem", fontWeight: 700,
                  color: s.average_score >= 7 ? "#22c55e" : s.average_score >= 4 ? "#eab308" : "#ef4444",
                }}>
                  {s.average_score}
                </div>
                <div style={{
                  fontSize: "0.75rem", padding: "0.15rem 0.5rem", borderRadius: 4,
                  background: s.status === "completed" ? "#22c55e22" : "var(--border)",
                  color: s.status === "completed" ? "#22c55e" : "var(--text-muted)",
                  display: "inline-block", marginTop: "0.25rem",
                }}>
                  {s.status}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
