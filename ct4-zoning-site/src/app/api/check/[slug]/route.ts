import { NextRequest, NextResponse } from "next/server";
import crypto from "node:crypto";
import { getTown } from "@/lib/towns";

export const runtime = "nodejs";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;
  const town = getTown(slug);
  if (!town) {
    return NextResponse.json({ error: "Unknown town" }, { status: 404 });
  }

  const source = town.primary_source;
  const checkedAt = new Date().toISOString();

  if (source.kind !== "pdf") {
    // No local baseline for link/nza sources — just confirm the source is still reachable.
    try {
      const res = await fetch(source.url, { method: "HEAD", redirect: "follow" });
      return NextResponse.json({
        status: res.ok ? "no-baseline" : "unreachable",
        httpStatus: res.status,
        checkedAt,
        message: res.ok
          ? "This source has no local mirror to hash-compare against (it's a browsable site or was blocked at ingest time). Confirmed the live URL is still reachable — open it to manually verify nothing material has changed."
          : `Live source returned HTTP ${res.status}. It may have moved.`,
      });
    } catch {
      return NextResponse.json({
        status: "error",
        checkedAt,
        message: "Could not reach the live source URL from this server.",
      });
    }
  }

  if (!source.content_hash) {
    return NextResponse.json({
      status: "no-baseline",
      checkedAt,
      message: "No stored hash to compare against yet for this document.",
    });
  }

  try {
    const res = await fetch(source.url, { redirect: "follow" });
    if (!res.ok) {
      return NextResponse.json({
        status: "unreachable",
        httpStatus: res.status,
        checkedAt,
        message: `Live source returned HTTP ${res.status}. It may have moved or been taken down.`,
      });
    }
    const buf = Buffer.from(await res.arrayBuffer());
    const liveHash = crypto.createHash("sha256").update(buf).digest("hex");
    const changed = liveHash !== source.content_hash;

    return NextResponse.json({
      status: changed ? "changed" : "up-to-date",
      checkedAt,
      liveHash,
      storedHash: source.content_hash,
      liveSizeBytes: buf.byteLength,
      storedSizeBytes: source.mirrored_size_bytes,
      message: changed
        ? "The live document's content no longer matches the mirrored copy used for this research pass. The zoning text has likely changed and this town needs to be re-researched."
        : "The live document matches the mirrored copy byte-for-byte. No re-research needed.",
    });
  } catch {
    return NextResponse.json({
      status: "error",
      checkedAt,
      message: "Could not fetch the live source URL from this server (it may block automated requests).",
    });
  }
}
