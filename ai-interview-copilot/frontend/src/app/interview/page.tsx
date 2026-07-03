"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

interface Question {
  id: number;
  type: string;
  question: string;
  focus_area: string;
  difficulty: string;
}

interface Evaluation {
  score: number;
  strengths: string[];
  weaknesses: string[];
  suggested_answer: string;
  tips: string[];
  overall: string;
}

export default function InterviewPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get("session") || "";

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [transcript, setTranscript] = useState("");
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);

  useEffect(() => {
    if (!sessionId) return;
    fetch(`/api/v1/sessions/${sessionId}`)
      .then((r) => r.json())
      .then((data) => {
        setQuestions(data.questions || []);
        setLoading(false);
      });
  }, [sessionId]);

  const startRecording = async () => {
    chunks.current = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
    mediaRecorder.current = recorder;
    recorder.ondataavailable = (e) => chunks.current.push(e.data);
    recorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      const blob = new Blob(chunks.current, { type: "audio/webm" });
      const form = new FormData();
      form.append("file", blob, "answer.webm");
      const res = await fetch("/api/v1/audio/transcribe", { method: "POST", body: form });
      const data = await res.json();
      setTranscript(data.text || "");
    };
    recorder.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorder.current?.stop();
    setRecording(false);
  };

  const submitAnswer = async () => {
    if (!transcript.trim()) return;
    setSubmitting(true);
    const q = questions[currentIdx];
    const res = await fetch(`/api/v1/sessions/${sessionId}/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        question_id: q.id,
        question: q.question,
        answer: transcript,
      }),
    });
    const data = await res.json();
    setEvaluation(data);
    setEvaluations((prev) => [...prev, data]);
    setSubmitting(false);
  };

  const nextQuestion = () => {
    if (currentIdx < questions.length - 1) {
      setCurrentIdx((i) => i + 1);
      setTranscript("");
      setEvaluation(null);
    }
  };

  const finishInterview = () => {
    router.push(`/dashboard`);
  };

  if (loading) return <div style={centerStyle}>Loading questions...</div>;

  const q = questions[currentIdx];
  const isLast = currentIdx === questions.length - 1;

  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: "2rem 1rem" }}>
      <div style={{ marginBottom: "1.5rem" }}>
        <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "0.25rem" }}>
          Question {currentIdx + 1} of {questions.length}
        </div>
        <div style={{
          height: 4, background: "var(--border)", borderRadius: 2,
          overflow: "hidden",
        }}>
          <div style={{
            width: `${((currentIdx + 1) / questions.length) * 100}%`,
            height: "100%", background: "var(--primary)", transition: "width 0.3s",
          }} />
        </div>
      </div>

      <div style={{
        background: "var(--surface)", borderRadius: 12, padding: "1.5rem",
        border: "1px solid var(--border)", marginBottom: "1.5rem",
      }}>
        <div style={{ fontSize: "0.8rem", color: "var(--primary)", fontWeight: 600, marginBottom: "0.5rem" }}>
          {q.type?.toUpperCase()} · {q.difficulty}
        </div>
        <div style={{ fontSize: "1.1rem", lineHeight: 1.6 }}>{q.question}</div>
      </div>

      <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1.5rem" }}>
        <button
          onClick={recording ? stopRecording : startRecording}
          style={{
            ...btn, flex: 1,
            background: recording ? "#ef4444" : "var(--primary)",
          }}
        >
          {recording ? "⏹ Stop Recording" : "🎤 Record Answer"}
        </button>
      </div>

      {transcript && (
        <div style={{
          background: "var(--surface)", borderRadius: 12, padding: "1.25rem",
          border: "1px solid var(--border)", marginBottom: "1rem",
        }}>
          <div style={{ fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.5rem" }}>
            Your Answer
          </div>
          <p style={{ color: "var(--text-muted)", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>
            {transcript}
          </p>
          <button onClick={submitAnswer} disabled={submitting} style={{ ...btn, marginTop: "0.75rem" }}>
            {submitting ? "Evaluating..." : "Submit for Evaluation"}
          </button>
        </div>
      )}

      {evaluation && (
        <div style={{
          background: "var(--surface)", borderRadius: 12, padding: "1.25rem",
          border: "1px solid var(--border)",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h3 style={{ margin: 0 }}>Evaluation</h3>
            <span style={{
              fontSize: "1.5rem", fontWeight: 700,
              color: evaluation.score >= 7 ? "#22c55e" : evaluation.score >= 4 ? "#eab308" : "#ef4444",
            }}>
              {evaluation.score}/10
            </span>
          </div>

          <div style={{ marginBottom: "0.75rem" }}>
            <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "#22c55e", marginBottom: "0.3rem" }}>Strengths</div>
            <ul style={{ margin: 0, paddingLeft: "1.25rem", color: "var(--text-muted)", fontSize: "0.9rem" }}>
              {evaluation.strengths.map((s, i) => <li key={i}>{s}</li>)}
            </ul>
          </div>

          <div style={{ marginBottom: "0.75rem" }}>
            <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "#ef4444", marginBottom: "0.3rem" }}>To Improve</div>
            <ul style={{ margin: 0, paddingLeft: "1.25rem", color: "var(--text-muted)", fontSize: "0.9rem" }}>
              {evaluation.weaknesses.map((w, i) => <li key={i}>{w}</li>)}
            </ul>
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <div style={{ fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem" }}>Tips</div>
            {evaluation.tips.map((t, i) => (
              <div key={i} style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "0.2rem" }}>• {t}</div>
            ))}
          </div>

          <div style={{
            background: "var(--bg)", borderRadius: 8, padding: "0.75rem",
            fontSize: "0.9rem", color: "var(--text-muted)", marginBottom: "1rem",
          }}>
            <strong>Suggested Answer:</strong> {evaluation.suggested_answer}
          </div>

          <div style={{ display: "flex", gap: "0.75rem" }}>
            {!isLast && (
              <button onClick={nextQuestion} style={{ ...btn, flex: 1 }}>Next Question →</button>
            )}
            <button onClick={finishInterview} style={{ ...btn, flex: 1, background: "var(--border)" }}>
              {isLast ? "Finish & Get Feedback →" : "End Early"}
            </button>
          </div>
        </div>
      )}
    </main>
  );
}

const btn: React.CSSProperties = {
  padding: "0.7rem 1.25rem",
  borderRadius: 8,
  border: "none",
  color: "white",
  fontWeight: 600,
  cursor: "pointer",
  fontSize: "0.9rem",
};

const centerStyle: React.CSSProperties = {
  display: "flex", justifyContent: "center", alignItems: "center",
  minHeight: "60vh", color: "var(--text-muted)",
};
