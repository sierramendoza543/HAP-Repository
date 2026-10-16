export type SourceKind = "pdf" | "link" | "nza";

export interface SourceRef {
  kind: SourceKind;
  id: string;
  url: string;
  title: string;
  /** Present only when kind === "pdf": path under /public to the mirrored file */
  file?: string;
  /** Present only when kind === "pdf": sha256 of the mirrored file, for change detection */
  content_hash?: string;
  mirrored_size_bytes?: number;
}

export interface NzaMetric {
  label: string;
  value: number;
  unit: string;
  source: SourceRef;
}

export interface DistrictFact {
  label: string;
  value: string;
  source: SourceRef;
  cite: string;
  /** Verbatim text pulled from the source document, when we have one we
   * independently verified against the PDF's own text. Null means we only
   * have a section/page citation, not a confirmed exact quote. */
  quote: string | null;
}

export interface DistrictBlock {
  district: string;
  facts: DistrictFact[];
}

export interface Town {
  slug: string;
  name: string;
  jurisdiction_id: number;
  population: number;
  land_area_acres: number | null;
  districts_analyzed: number;
  composite_score: number;
  last_checked: string;
  nza_metrics: NzaMetric[];
  primary_source: SourceRef;
  restrictive: DistrictBlock;
  permissive: DistrictBlock;
  caveat: string;
}
