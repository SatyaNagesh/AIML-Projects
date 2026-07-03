"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  const [role, setRole] = useState("");
  const [level, setLevel] = useState("mid");
  const [resume, setResume] = useState("");
  const [loading, setLoading] = useState(false);

  const startInterview = async () => {
    setLoading(true);
    const res = await fetch("/api/v1/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role, resume, experience_level: level }),
    });
    const data = await res.json();
    router.push(`/interview?session=${data.session_id}`);
  };

  return (
    <main style={{ maxWidth: 640, margin: "0 auto", padding: "3rem 1rem" }}>
      <h1 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        AI Interview Copilot
      </h1>
      <p style={{ color: "var(--text-muted)", marginBottom: "2rem" }}>
        Practice interviews with real-time voice, evaluation, and feedback.
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        <div>
          <label style={{ display: "block", marginBottom: "0.4rem", fontSize: "0.9rem", fontWeight: 500 }}>
            Target Role
          </label>
          <input
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="e.g. Senior Frontend Engineer"
            style={inputStyle}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "0.4rem", fontSize: "0.9rem", fontWeight: 500 }}>
            Experience Level
          </label>
          <select value={level} onChange={(e) => setLevel(e.target.value)} style={inputStyle}>
            <option value="junior">Junior (0-2 yrs)</option>
            <option value="mid">Mid (3-5 yrs)</option>
            <option value="senior">Senior (6+ yrs)</option>
          </select>
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "0.4rem", fontSize: "0.9rem", fontWeight: 500 }}>
            Resume (paste text)
          </label>
          <textarea
            value={resume}
            onChange={(e) => setResume(e.target.value)}
            placeholder="Paste your resume or key skills..."
            rows={6}
            style={{ ...inputStyle, resize: "vertical" }}
          />
        </div>

        <button
          onClick={startInterview}
          disabled={loading}
          style={{
            ...buttonStyle,
            opacity: loading ? 0.6 : 1,
            marginTop: "0.5rem",
          }}
        >
          {loading ? "Starting..." : "Start Mock Interview"}
        </button>
      </div>

      <div style={{ marginTop: "3rem", textAlign: "center" }}>
        <a href="/dashboard" style={{ color: "var(--primary)", textDecoration: "none" }}>
          View Progress Dashboard →
        </a>
      </div>
    </main>
  );
}

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "0.75rem",
  borderRadius: 8,
  border: "1px solid var(--border)",
  background: "var(--surface)",
  color: "var(--text)",
  fontSize: "0.95rem",
  outline: "none",
  boxSizing: "border-box",
};

const buttonStyle: React.CSSProperties = {
  ...inputStyle,
  background: "var(--primary)",
  border: "none",
  fontWeight: 600,
  cursor: "pointer",
};
