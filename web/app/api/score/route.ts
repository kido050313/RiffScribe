import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

export async function GET() {
  try {
    const repoRoot = resolve(process.cwd(), "..");
    const scorePath = resolve(repoRoot, "output", "exports", "test1.musicxml");
    const fileBuffer = await readFile(scorePath);

    return new Response(new Uint8Array(fileBuffer), {
      headers: {
        "Content-Type": "application/vnd.recordare.musicxml+xml; charset=utf-8",
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to read MusicXML.";
    return Response.json({ error: message }, { status: 500 });
  }
}
