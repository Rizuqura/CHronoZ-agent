import type { Finding } from "./finding";

export type ClassificationRunResult = {
  runStatus:
    | "completed"
    | "partial_success"
    | "failed";

  sourceFile: string;

  observationsDetected: number;
  observationsSelected: number;
  observationsProcessed: number;
  observationsFailed: number;

  stoppedAt?: string;

  stopReason:
    | "completed"
    | "max_observations_reached"
    | "malformed_llm_output"
    | "rate_limited"
    | "provider_error";

  findings: Finding[];

  failedEvidenceIds: string[];
};