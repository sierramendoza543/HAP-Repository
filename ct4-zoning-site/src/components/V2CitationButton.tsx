"use client";

import { useState } from "react";
import SourceViewer from "@/components/SourceViewer";
import type { SourceRef } from "@/lib/types";

export default function V2CitationButton({
  source,
  cite,
  quote,
}: {
  source: SourceRef;
  cite: string;
  quote: string;
}) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="underline hover:text-(--accent) text-left"
      >
        View quote in PDF
      </button>
      {open && <SourceViewer source={source} cite={cite} quote={quote} onClose={() => setOpen(false)} />}
    </>
  );
}
