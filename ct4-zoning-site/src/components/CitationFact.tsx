"use client";

import { useState } from "react";
import type { SourceRef } from "@/lib/types";
import SourceViewer from "./SourceViewer";

export function CitationBadge({
  source,
  cite,
  compact = false,
}: {
  source: SourceRef;
  cite: string;
  compact?: boolean;
}) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        title={`Source: ${source.title} — ${cite}`}
        className={
          compact
            ? "underline decoration-dotted decoration-(--rule) underline-offset-2 hover:decoration-(--accent) hover:text-(--accent) transition-colors cursor-help"
            : "inline-flex items-center gap-1 text-xs rounded-full border border-(--rule) px-2 py-0.5 text-(--ink-dim) hover:border-(--accent) hover:text-(--accent) transition-colors cursor-pointer"
        }
      >
        {compact ? null : "¶ "}
        {cite}
      </button>
      {open && <SourceViewer source={source} cite={cite} onClose={() => setOpen(false)} />}
    </>
  );
}
