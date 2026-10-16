"use client";

import { useEffect, useRef, useState } from "react";
import type { SourceRef } from "@/lib/types";

interface Props {
  source: SourceRef;
  cite: string;
  onClose: () => void;
}

/** Pulls the most distinctive searchable token out of a citation string,
 * e.g. "Sec. 6-93(a)(1)" -> "6-93", "Table 4.3.9.A" -> "4.3.9.A" */
function searchToken(cite: string): string | null {
  const m = cite.match(/[0-9]+(?:[.\-][0-9]+)+/) ?? cite.match(/[0-9]{2,}/);
  return m ? m[0] : null;
}

export default function SourceViewer({ source, cite, onClose }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const textLayerRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<"loading" | "found" | "not-found" | "error">("loading");
  const [pageInfo, setPageInfo] = useState<{ page: number; count: number } | null>(null);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  useEffect(() => {
    if (source.kind !== "pdf" || !source.file) return;
    let cancelled = false;

    (async () => {
      try {
        const pdfjsLib = await import("pdfjs-dist");
        pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
          "pdfjs-dist/build/pdf.worker.min.mjs",
          import.meta.url
        ).toString();

        const doc = await pdfjsLib.getDocument(source.file).promise;
        if (cancelled) return;

        const token = searchToken(cite);
        let targetPage = 1;
        let matchText: string | null = null;

        if (token) {
          for (let i = 1; i <= doc.numPages; i++) {
            const page = await doc.getPage(i);
            const content = await page.getTextContent();
            const pageText = content.items.map((it: unknown) => (it as { str: string }).str).join(" ");
            if (pageText.toLowerCase().includes(token.toLowerCase())) {
              targetPage = i;
              matchText = token;
              break;
            }
          }
        }

        const page = await doc.getPage(targetPage);
        const viewport = page.getViewport({ scale: 1.4 });
        const canvas = canvasRef.current!;
        const ctx = canvas.getContext("2d")!;
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        await page.render({ canvasContext: ctx, viewport, canvas }).promise;

        // text layer for highlight
        const textLayerDiv = textLayerRef.current!;
        textLayerDiv.innerHTML = "";
        textLayerDiv.style.width = `${viewport.width}px`;
        textLayerDiv.style.height = `${viewport.height}px`;
        const content = await page.getTextContent();
        content.items.forEach((raw: unknown) => {
          const item = raw as { str: string; transform: number[]; width: number; height: number };
          if (!item.str.trim()) return;
          const tx = pdfjsLib.Util.transform(viewport.transform, item.transform);
          const span = document.createElement("span");
          span.textContent = item.str;
          const fontHeight = Math.hypot(tx[2], tx[3]);
          span.style.position = "absolute";
          span.style.left = `${tx[4]}px`;
          span.style.top = `${tx[5] - fontHeight}px`;
          span.style.fontSize = `${fontHeight}px`;
          span.style.whiteSpace = "pre";
          span.style.color = "transparent";
          if (matchText && item.str.toLowerCase().includes(matchText.toLowerCase())) {
            span.style.background = "rgba(255, 210, 60, 0.55)";
            span.style.color = "rgba(0,0,0,0.01)";
            span.style.borderRadius = "2px";
          }
          textLayerDiv.appendChild(span);
        });

        if (!cancelled) {
          setPageInfo({ page: targetPage, count: doc.numPages });
          setStatus(matchText ? "found" : "not-found");
          if (matchText) {
            requestAnimationFrame(() => {
              const firstHighlight = textLayerDiv.querySelector("span[style*='255, 210, 60']");
              firstHighlight?.scrollIntoView({ block: "center", behavior: "smooth" });
            });
          }
        }
      } catch (e) {
        console.error(e);
        if (!cancelled) setStatus("error");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [source, cite]);

  const isPdf = source.kind === "pdf" && source.file;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={onClose}
    >
      <div
        className="bg-(--surface) text-(--ink) rounded-xl max-w-3xl w-full max-h-[88vh] flex flex-col overflow-hidden border border-(--rule)"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 p-4 border-b border-(--rule)">
          <div className="min-w-0">
            <p className="text-xs uppercase tracking-wide text-(--ink-dim) font-semibold">Source</p>
            <p className="font-semibold truncate">{source.title}</p>
            <p className="text-sm text-(--ink-dim)">Citation: {cite}</p>
          </div>
          <button
            onClick={onClose}
            className="shrink-0 rounded-full w-8 h-8 flex items-center justify-center hover:bg-(--surface-2)"
            aria-label="Close"
          >
            &times;
          </button>
        </div>

        <div className="flex-1 overflow-auto bg-(--surface-2) p-4">
          {isPdf ? (
            <>
              {status === "loading" && (
                <p className="text-sm text-(--ink-dim) p-6 text-center">Opening document and searching for &ldquo;{cite}&rdquo;&hellip;</p>
              )}
              {status === "error" && (
                <p className="text-sm text-(--ink-dim) p-6 text-center">Could not render the mirrored PDF in-browser. Use the link below to open it directly.</p>
              )}
              {(status === "found" || status === "not-found") && pageInfo && (
                <p className="text-xs text-(--ink-dim) mb-2">
                  Page {pageInfo.page} of {pageInfo.count}
                  {status === "found" ? " — highlighted match below" : " — exact text match not found automatically; shown at page 1"}
                </p>
              )}
              <div className="relative inline-block bg-white shadow">
                <canvas ref={canvasRef} className="block" />
                <div ref={textLayerRef} className="absolute inset-0" style={{ transformOrigin: "0 0" }} />
              </div>
            </>
          ) : (
            <div className="p-8 text-center space-y-3">
              <p className="text-sm text-(--ink-dim)">
                {source.kind === "nza"
                  ? "This figure comes from the National Zoning Atlas's live Jurisdiction Snapshot page, not a static document — open it directly to verify."
                  : "A local mirror of this document isn't available (the source blocked automated downloads or is a browsable code site, not a PDF) — open the live source to verify this citation."}
              </p>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-(--rule) flex justify-end">
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-(--accent-ink) bg-(--accent) px-4 py-2 rounded-lg hover:opacity-90"
          >
            Open original source &rarr;
          </a>
        </div>
      </div>
    </div>
  );
}
