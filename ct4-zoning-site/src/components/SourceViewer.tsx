"use client";

import { useEffect, useRef, useState } from "react";
import type { SourceRef } from "@/lib/types";

interface Props {
  source: SourceRef;
  cite: string;
  quote: string | null;
  onClose: () => void;
}

interface Item {
  str: string;
  transform: number[];
}

/** Strips whitespace and lowercases, keeping a map back to the original
 * string's indices so a match found in the compact string can be mapped
 * back to real character offsets (robust to PDF line-wrap / spacing noise). */
function compact(s: string): { text: string; map: number[] } {
  const map: number[] = [];
  let text = "";
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (/\s/.test(c)) continue;
    text += c.toLowerCase();
    map.push(i);
  }
  return { text, map };
}

/** Builds a concatenated string + per-item [start,end) spans for a given
 * item ordering, so a match found in the concatenation can be mapped back
 * to which item indices it touches. */
function buildConcat(items: Item[], order: number[]) {
  let text = "";
  const spans = new Array(items.length);
  for (const i of order) {
    const start = text.length;
    text += items[i].str + " ";
    spans[i] = { start, end: start + items[i].str.length };
  }
  return { text, spans };
}

function readingOrder(items: Item[]): number[] {
  const rows = items.map((it, i) => ({ i, x: it.transform[4], y: it.transform[5] }));
  rows.sort((a, b) => {
    const dy = b.y - a.y; // PDF y grows upward; reading order is top-to-bottom
    if (Math.abs(dy) > 3) return dy;
    return a.x - b.x;
  });
  return rows.map((r) => r.i);
}

function searchToken(cite: string): string | null {
  const m = cite.match(/[0-9]+(?:[.\-][0-9]+)+/) ?? cite.match(/[0-9]{2,}/);
  return m ? m[0] : null;
}

/** Tries to find `needle` (already compacted) inside `items`, trying both
 * natural content-stream order and visual reading order, and both the full
 * needle and a shortened prefix. Returns the matched item index range, or
 * null. */
function findMatch(items: Item[], needleCompact: { text: string }): [number, number] | null {
  if (!needleCompact.text) return null;
  const orders: number[][] = [
    items.map((_, i) => i),
    readingOrder(items),
  ];
  for (const order of orders) {
    const { text, spans } = buildConcat(items, order);
    const pageCompact = compact(text);
    for (const needle of [needleCompact.text, needleCompact.text.slice(0, 40)]) {
      if (needle.length < 6) continue;
      const idx = pageCompact.text.indexOf(needle);
      if (idx === -1) continue;
      const startOrig = pageCompact.map[idx];
      const endOrig = pageCompact.map[idx + needle.length - 1] + 1;
      // find which items' spans overlap [startOrig, endOrig) in this order's concat string
      let first = -1;
      let last = -1;
      for (let k = 0; k < items.length; k++) {
        const s = spans[k];
        if (!s) continue;
        if (s.start < endOrig && s.end > startOrig) {
          if (first === -1) first = k;
          last = k;
        }
      }
      if (first !== -1) return [first, last];
    }
  }
  return null;
}

export default function SourceViewer({ source, cite, quote, onClose }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const textLayerRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<"loading" | "found" | "weak" | "not-found" | "error">("loading");
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

        const quoteCompact = quote ? compact(quote) : null;
        const token = searchToken(cite);

        let targetPage = 1;
        let matchIdxRange: [number, number] | null = null;
        let matchQuality: "found" | "weak" = "found";

        // Pass 1: exact (or near-exact) quote match, page by page.
        if (quoteCompact && quoteCompact.text.length > 0) {
          for (let i = 1; i <= doc.numPages; i++) {
            const page = await doc.getPage(i);
            const content = await page.getTextContent();
            const items = content.items as unknown as Item[];
            const m = findMatch(items, quoteCompact);
            if (m) {
              matchIdxRange = m;
              targetPage = i;
              break;
            }
          }
        }

        // Pass 2: fall back to the section/number token from the citation,
        // so the viewer still lands on a relevant page instead of page 1.
        if (!matchIdxRange && token) {
          const tokenCompact = compact(token);
          for (let i = 1; i <= doc.numPages; i++) {
            const page = await doc.getPage(i);
            const content = await page.getTextContent();
            const items = content.items as unknown as Item[];
            const m = findMatch(items, tokenCompact);
            if (m) {
              matchIdxRange = m;
              targetPage = i;
              matchQuality = "weak";
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

        const textLayerDiv = textLayerRef.current!;
        textLayerDiv.innerHTML = "";
        textLayerDiv.style.width = `${viewport.width}px`;
        textLayerDiv.style.height = `${viewport.height}px`;
        const content = await page.getTextContent();

        content.items.forEach((raw: unknown, i: number) => {
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
          if (matchIdxRange && i >= matchIdxRange[0] && i <= matchIdxRange[1]) {
            span.style.background =
              matchQuality === "found" ? "rgba(255, 210, 60, 0.6)" : "rgba(255, 210, 60, 0.35)";
            span.style.color = "rgba(0,0,0,0.01)";
            span.style.borderRadius = "2px";
            span.dataset.hit = "1";
          }
          textLayerDiv.appendChild(span);
        });

        if (!cancelled) {
          setPageInfo({ page: targetPage, count: doc.numPages });
          setStatus(matchIdxRange ? matchQuality : "not-found");
          if (matchIdxRange) {
            requestAnimationFrame(() => {
              const firstHighlight = textLayerDiv.querySelector("span[data-hit='1']");
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
  }, [source, quote, cite]);

  const isPdf = source.kind === "pdf" && source.file;
  const token = searchToken(cite);
  const openUrl =
    source.kind === "link" && token
      ? `${source.url}${source.url.includes("#") ? "" : `#:~:text=${encodeURIComponent(token)}`}`
      : source.url;

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
            <p className="text-sm text-(--ink-dim)">
              Citation: <span className="font-mono">{cite}</span>
            </p>
          </div>
          <button
            onClick={onClose}
            className="shrink-0 rounded-full w-8 h-8 flex items-center justify-center hover:bg-(--surface-2)"
            aria-label="Close"
          >
            &times;
          </button>
        </div>

        {quote && (
          <div className="px-4 pt-3 pb-2 bg-(--surface-2) border-b border-(--rule)">
            <p className="text-xs uppercase tracking-wide text-(--ink-dim) font-semibold mb-1">
              Exact quote
            </p>
            <blockquote className="text-sm italic leading-relaxed border-l-2 border-(--accent) pl-3">
              &ldquo;{quote}&rdquo;
            </blockquote>
          </div>
        )}

        <div className="flex-1 overflow-auto bg-(--surface-2) p-4">
          {!quote && !isPdf && (
            <div className="p-6 text-center space-y-3">
              <p className="text-sm text-(--ink-dim)">
                No verbatim quote has been independently re-verified for this fact yet.
              </p>
              <p className="text-sm text-(--ink-dim)">
                The button below jumps straight to <span className="font-mono">{cite}</span> on
                the live source where possible (most browsers auto-scroll and highlight it).
              </p>
            </div>
          )}
          {!quote && isPdf && (
            <>
              {status === "loading" && (
                <p className="text-sm text-(--ink-dim) p-6 text-center">
                  Opening document and searching for {cite}&hellip;
                </p>
              )}
              {status === "error" && (
                <p className="text-sm text-(--ink-dim) p-6 text-center">
                  Could not render the mirrored PDF in-browser. Use the link below to open it
                  directly.
                </p>
              )}
              {(status === "weak" || status === "not-found") && pageInfo && (
                <p className="text-xs text-(--ink-dim) mb-2">
                  Page {pageInfo.page} of {pageInfo.count}
                  {status === "weak"
                    ? ` — no verified quote yet, but found "${cite}" on this page (highlighted below)`
                    : " — couldn't auto-locate this section in the mirrored PDF; shown at page 1"}
                </p>
              )}
              <div className="relative inline-block bg-white shadow">
                <canvas ref={canvasRef} className="block" />
                <div ref={textLayerRef} className="absolute inset-0" style={{ transformOrigin: "0 0" }} />
              </div>
            </>
          )}
          {quote && isPdf && (
            <>
              {status === "loading" && (
                <p className="text-sm text-(--ink-dim) p-6 text-center">
                  Opening document and searching for the quote above&hellip;
                </p>
              )}
              {status === "error" && (
                <p className="text-sm text-(--ink-dim) p-6 text-center">
                  Could not render the mirrored PDF in-browser. Use the link below to open it
                  directly.
                </p>
              )}
              {(status === "found" || status === "weak" || status === "not-found") && pageInfo && (
                <p className="text-xs text-(--ink-dim) mb-2">
                  Page {pageInfo.page} of {pageInfo.count}
                  {status === "found" && " — highlighted below"}
                  {status === "weak" && ` — couldn't match the exact quote text, but found "${cite}" on this page (highlighted below)`}
                  {status === "not-found" && " — couldn't auto-locate this text in the mirrored PDF; shown at page 1"}
                </p>
              )}
              <div className="relative inline-block bg-white shadow">
                <canvas ref={canvasRef} className="block" />
                <div ref={textLayerRef} className="absolute inset-0" style={{ transformOrigin: "0 0" }} />
              </div>
            </>
          )}
          {quote && !isPdf && (
            <div className="p-8 text-center space-y-3">
              <p className="text-sm text-(--ink-dim)">
                {source.kind === "nza"
                  ? "This figure comes from the National Zoning Atlas's live Jurisdiction Snapshot page, not a static document — open it directly to verify."
                  : "A local mirror of this document isn't available (the source blocked automated downloads, is image-only with no text layer, or is a browsable code site rather than a single PDF). The button below jumps to this section on the live site where possible."}
              </p>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-(--rule) flex justify-end">
          <a
            href={openUrl}
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
