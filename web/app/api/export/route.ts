import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { randomUUID } from "node:crypto";
import { spawn } from "node:child_process";

type ExportFormat = "midi" | "musicxml";

type ExportRequest = {
  analysis: unknown;
  format: ExportFormat;
};

function isExportFormat(value: string): value is ExportFormat {
  return value === "midi" || value === "musicxml";
}

function runPythonExport(
  pythonExecutable: string,
  scriptPath: string,
  inputPath: string,
  format: ExportFormat,
  outputPath: string,
) {
  return new Promise<void>((resolvePromise, rejectPromise) => {
    const args = [scriptPath, "--input", inputPath];
    if (format === "midi") {
      args.push("--midi-output", outputPath, "--skip-musicxml");
    } else {
      args.push("--musicxml-output", outputPath, "--skip-midi");
    }

    const child = spawn(pythonExecutable, args, {
      cwd: resolve(process.cwd(), ".."),
      stdio: ["ignore", "pipe", "pipe"],
    });

    let stderr = "";
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    child.on("error", (error) => rejectPromise(error));
    child.on("close", (code) => {
      if (code === 0) {
        resolvePromise();
        return;
      }
      rejectPromise(new Error(stderr || `Export script failed with exit code ${code}.`));
    });
  });
}

export async function POST(request: Request) {
  const body = (await request.json()) as ExportRequest;
  if (!body || !isExportFormat(body.format)) {
    return Response.json({ error: "Invalid export format." }, { status: 400 });
  }

  const repoRoot = resolve(process.cwd(), "..");
  const pythonExecutable = resolve(repoRoot, ".venv", "Scripts", "python.exe");
  const exportScript = resolve(repoRoot, "analyzer", "export.py");
  const tempDir = await mkdtemp(join(tmpdir(), "guitar-export-"));
  const baseName = `analysis-${randomUUID()}`;
  const inputPath = join(tempDir, `${baseName}.json`);
  const outputExtension = body.format === "midi" ? "mid" : "musicxml";
  const outputPath = join(tempDir, `${baseName}.${outputExtension}`);

  try {
    await writeFile(inputPath, JSON.stringify(body.analysis, null, 2), "utf-8");
    await runPythonExport(pythonExecutable, exportScript, inputPath, body.format, outputPath);
    const fileBuffer = await readFile(outputPath);

    return new Response(new Uint8Array(fileBuffer), {
      headers: {
        "Content-Type":
          body.format === "midi" ? "audio/midi" : "application/vnd.recordare.musicxml+xml",
        "Content-Disposition": `attachment; filename="guitar-draft.${outputExtension}"`,
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Export failed.";
    return Response.json({ error: message }, { status: 500 });
  } finally {
    await rm(tempDir, { recursive: true, force: true });
  }
}
