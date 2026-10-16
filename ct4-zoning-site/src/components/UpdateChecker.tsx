"use client";

import { useState } from "react";

interface CheckResult {
  status: "changed" | "up-to-date" | "no-baseline" | "unreachable" | "error";
  checkedAt: string;
  message: string;
}

export default function UpdateChecker({ slug }: { slug: string }) {
  const [state, setState] = useState<"idle" | "loading" | "done">("idle");
  const [result, setResult] = useState<CheckResult | null>(null);

  async function run() {
    setState("loading");
    try {
      const res = await fetch(`/api/check/${slug}`);
      const data = (await res.json()) as CheckResult;
      setResult(data);
    } catch {
      setResult({
        status: "error",
        checkedAt: new Date().toISOString(),
        message: "Request failed.",
      });
    }
    setState("done");
  }

  const palette: Record<string, string> = {
    changed: "border-(--maybe) bg-(--maybe)/10 text-(--ink)",
    "up-to-date": "border-(--allow) bg-(--allow)/10 text-(--ink)",
    "no-baseline": "border-(--rule) bg-(--surface-2) text-(--ink-dim)",
    unreachable: "border-(--prohibit) bg-(--prohibit)/10 text-(--ink)",
    error: "border-(--prohibit) bg-(--prohibit)/10 text-(--ink)",
  };

  const labels: Record<string, string> = {
    changed: "Changes detected",
    "up-to-date": "Up to date",
    "no-baseline": "No baseline",
    unreachable: "Source unreachable",
    error: "Check failed",
  };

  return (
    <div className="flex flex-col gap-2">
      <button
        onClick={run}
        disabled={state === "loading"}
        className="self-start text-sm font-medium border border-(--rule) rounded-lg px-4 py-2 hover:border-(--accent) hover:text-(--accent) transition-colors disabled:opacity-50"
      >
        {state === "loading" ? "Checking live source…" : "Check for zoning changes"}
      </button>
      {result && (
        <div className={`text-sm rounded-lg border px-3 py-2 ${palette[result.status]}`}>
          <span className="font-semibold">{labels[result.status]}.</span> {result.message}
          {result.status === "changed" && (
            <p className="mt-1 text-xs opacity-80">
              This town needs a fresh research pass to update the data on this page.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
