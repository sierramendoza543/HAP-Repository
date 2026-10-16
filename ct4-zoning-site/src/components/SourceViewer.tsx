"use client";

import { useEffect, useRef, useState } from "react";
import type { SourceRef } from "@/lib/types";

interface Props {
  source: SourceRef;
  cite: string;
  quote: string | null;
  onClose: () => void;
}

interface Span {
  start: number;
  end: number; // exclusive, in concatText
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

export default function SourceViewer({ source, cite, quote, onClose }: Props) {
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

        let targetPage = 1;
        let matchRange: [number, number] | null = null;
        const compactQuote = quote ? compact(quote) : null;

        if (compactQuote && compactQuote.text.length > 0) {
          for (let i = 1; i <= doc.numPages; i++) {
            const page = await doc.getPage(i);
            const content = await page.getTextContent();
            let concatText = "";
            for (const raw of content.items) {
              const item = raw as { str: string };
              concatText += item.str + " ";
            }
            const compactPage = compact(concatText);
            let idx = compactPage.text.indexOf(compactQuote.text);
            let matchLen = compactQuote.text.length;
            if (idx === -1 && compactQuote.text.length > 40) {
              // tolerate OCR/typography drift by matching a shorter leading chunk
              const shortQuote = compactQuote.text.slice(0, 40);
              idx = compactPage.text.indexOf(shortQuote);
              matchLen = shortQuote.length;
            }
            if (idx !== -1) {
              const startOrig = compactPage.map[idx];
              const endOrig = compactPage.map[idx + matchLen - 1] + 1;
              matchRange = [startOrig, endOrig];
              targetPage = i;
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

        // Rebuild spans with offsets matching the same concatenation scheme used above.
        let cursor = 0;
        const spans: Span[] = [];
        for (const raw of content.items) {
          const item = raw as { str: string };
          const start = cursor;
          cursor += item.str.length;
          const end = cursor;
          cursor += 1; // the " " separator
          spans.push({ start, end });
        }

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
          if (matchRange) {
            const s = spans[i];
            const overlaps = s.start < matchRange[1] && s.end > matchRange[0];
            if (overlaps) {
              span.style.background = "rgba(255, 210, 60, 0.6)";
              span.style.color = "rgba(0,0,0,0.01)";
              span.style.borderRadius = "2px";
              span.dataset.hit = "1";
            }
          }
          textLayerDiv.appendChild(span);
        });

        if (!cancelled) {
          setPageInfo({ page: targetPage, count: doc.numPages });
          setStatus(matchRange ? "found" : "not-found");
          if (matchRange) {
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
  }, [source, quote]);

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
          {!quote && (
            <p className="text-sm text-(--ink-dim) p-4 text-center">
              No verbatim quote has been independently re-verified for this fact yet &mdash; only
              the section citation above. Open the original source to confirm it yourself.
            </p>
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
              {(status === "found" || status === "not-found") && pageInfo && (
                <p className="text-xs text-(--ink-dim) mb-2">
                  Page {pageInfo.page} of {pageInfo.count}
                  {status === "found"
                    ? " — highlighted below"
                    : " — could not auto-locate this exact text in the mirrored PDF (it may be on a page the extractor couldn't match); shown at page 1"}
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
                  : "A local mirror of this document isn't available (the source blocked automated downloads, is image-only with no text layer, or is a browsable code site rather than a single PDF) — open the live source to verify the quote above."}
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
