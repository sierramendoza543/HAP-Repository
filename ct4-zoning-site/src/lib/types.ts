export type SourceKind = "pdf" | "link" | "nza";

export interface SourceRef {
  kind: SourceKind;
  id: string;
  url: string;
  title: string;
  file?: string;
  content_hash?: string;
  mirrored_size_bytes?: number;
}

export interface NzaMetric {
  label: string;
  value: number;
  unit: string;
  source: SourceRef;
}

export type VariableCategory =
  | "Use Permissions"
  | "Dimensional Standards"
  | "ADU Policy"
  | "Parking"
  | "Approval Process"
  | "Overlays & Affordability";

export interface Variable {
  category: VariableCategory;
  district: string; // e.g. "R-20", "R-MF", "Town-wide"
  label: string;
  value: string;
  source: SourceRef;
  cite: string;
  quote: string | null;
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
  restrictive_district: string;
  permissive_district: string;
  variables: Variable[];
  nza_metrics: NzaMetric[];
  primary_source: SourceRef;
  caveat: string;
}
