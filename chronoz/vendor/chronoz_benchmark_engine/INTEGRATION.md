# Integrating with a TypeScript/Node CHronoZ agent

Copy this **whole folder** into the external agent project, for example `vendor/chronoz_benchmark_engine`. Supply economic CSV data separately. Install the engine requirements into the Python environment the agent will launch. No original research repository or notebook imports are needed. This deliverable does not make changes in an agent repository.

## Option A: subprocess (canonical V0)

Node/TypeScript → Python CLI → stdout JSON → validate BenchmarkPacket → give packet to the LLM agent.

Keep the engine and data paths in application configuration, resolved to absolute paths before spawning. The data directory can be anywhere readable. Pass arguments as an array with `shell: false`; never interpolate end-user prose into shell commands. The agent selects known series identifiers before calling this boundary.

Minimal TypeScript example (Node, Ajv 8 with Draft 2020-12 support, and ajv-formats installed in the host project):

```typescript
import { spawn } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve, join } from "node:path";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const engineDir = resolve(process.env.CHRONOZ_ENGINE_DIR!);
const dataRoot = resolve(process.env.CHRONOZ_DATA_ROOT!);
const python = process.env.CHRONOZ_PYTHON ?? "python";
const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);
const schema = JSON.parse(readFileSync(
  join(engineDir, "schemas", "benchmark_packet.schema.json"), "utf8"
));
const validate = ajv.compile(schema);

export function benchmark(series: string[]): Promise<unknown> {
  return new Promise((resolvePacket, reject) => {
    const child = spawn(python, [
      join(engineDir, "benchmark_cli.py"),
      "--data-root", dataRoot,
      "--series", ...series,
      "--horizons", "10", "20", "50", "100",
    ], { shell: false, windowsHide: true, stdio: ["ignore", "pipe", "pipe"] });
    let stdout = "";
    let stderr = "";
    let settled = false;
    const fail = (error: Error) => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        reject(error);
      }
    };
    // Host policy: adjust timeout/response cap for the requested number of pairs.
    const timer = setTimeout(() => {
      child.kill();
      fail(new Error("Benchmark request timed out"));
    }, 120_000);
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk: string) => {
      stdout += chunk;
      if (stdout.length > 20_000_000) {
        child.kill();
        fail(new Error("Benchmark response exceeded host limit"));
      }
    });
    child.stderr.on("data", (chunk: string) => { stderr = (stderr + chunk).slice(-100_000); });
    child.on("error", fail);
    child.on("close", (code) => {
      clearTimeout(timer);
      if (settled) return;
      if (code !== 0) return fail(new Error(`Benchmark failed (${code}): ${stderr}`));
      try {
        const packet: unknown = JSON.parse(stdout);
        if (!validate(packet)) {
          return fail(new Error(`Invalid BenchmarkPacket: ${ajv.errorsText(validate.errors)}`));
        }
        settled = true;
        resolvePacket(packet);
      } catch (error) {
        fail(error instanceof Error ? error : new Error(String(error)));
      }
    });
  });
}

// Supply only validated identifiers chosen by the host agent.
const packet = await benchmark(["PPIACO", "INDPRO", "TCU"]);
// Pass this validated measurement packet into the agent's own reasoning context.
```

Set all three environment variables deliberately; avoid deriving paths from where a request happens to execute. `CHRONOZ_PYTHON` can name a virtual environment interpreter. No shell activation is necessary. The portable CLI file resolves its own imports and resources regardless of child cwd. The installed `chronoz-benchmark` command is an alternative when deploying a wheel.

On success stdout contains one JSON document and exit code is zero. Diagnostics go to stderr. On failure, treat a nonzero exit as a failed measurement call; do not let the LLM interpret partial output. Null fields are expected contract values for unsupported/insufficient measurements. Inspect per-indicator, per-relationship and per-window warnings. Host timeouts and size limits above are application defaults, not engine methodology.

`get_packet()` loads inputs once per call, but does not make an atomic filesystem snapshot across CSVs. Arrange immutable data snapshots or atomic directory publication in the host if updates are concurrent. `as_of` is generation time. Neither `latest_date` nor `data_root` proves when information was publicly available. Historical relationship metadata stays at its bundled research snapshot, even when fresh external data is supplied.

## Option B: Python service later

BenchmarkService → an isolated FastAPI wrapper → HTTP JSON.

The same Python API can later serve an endpoint whose structured request contains `series_ids` and `horizons`. Construct `BenchmarkService` with a server-configured data root and config root, call `get_packet()`, return `packet.to_dict()`, and map invalid identifiers/config/data to appropriate error responses. Keep CPU/data access work out of the event loop or use a synchronous endpoint. The host owns authentication, concurrency, request limits, data snapshots and deployment.

No FastAPI dependency, server, port, authentication policy or HTTP integration is implemented here. Subprocess remains the supported V0 transport; the Python service API is the reusable boundary for a later wrapper.

## Agent consumption

The downstream agent can use the packet in this sequence:

1. Read end-user evidence.
2. Identify candidate economic concepts.
3. Choose relevant registered series.
4. Call the benchmark engine.
5. Inspect historical position using the selected family's score type.
6. Inspect rolling 10/20/50/100 structure and actual n.
7. Inspect acceleration and unavailable inputs.
8. Inspect contemporaneous and descriptive timing relationships.
9. Inspect redundancy candidates without automatically deleting variables.
10. Compare benchmark findings with user evidence.
11. Identify contradictions and missing information.
12. Generate hypotheses and falsifiers.

The engine itself performs none of these reasoning steps. It only calculates requested measurements. Discrete PMF probabilities must not be treated as z-scores; regime/epoch primary scores must not be replaced with global diagnostics; retrospective calibration must not be presented as a real-time backtest. Relationship percent changes differ from the benchmark's log deltas. Correlation != causality; lead-lag is descriptive timing association only; redundancy != automatic deletion.

## Copy/deployment checklist

Keep the Python package, config, schema, CLI, VERSION and dependency metadata together. Preserve tests/docs/examples for review. Install dependencies, set the external data path, run the tests, call the CLI from the host's working directory, parse stdout, and validate against the bundled schema. `config_root` overrides require a complete config directory. The creation-time export scripts and original research repository are unnecessary for deployed calls.
