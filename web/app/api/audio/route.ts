import { readFile } from "node:fs/promises";
import { join } from "node:path";

const AUDIO_PATH = join(
  process.cwd(),
  "..",
  "output",
  "separated",
  "htdemucs",
  "test1",
  "other.wav",
);

export async function GET() {
  const audioBuffer = await readFile(AUDIO_PATH);
  const body = new Uint8Array(audioBuffer);

  return new Response(body, {
    headers: {
      "Content-Type": "audio/wav",
      "Content-Length": String(body.byteLength),
      "Accept-Ranges": "bytes",
      "Cache-Control": "no-store",
    },
  });
}
