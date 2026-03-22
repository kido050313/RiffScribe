import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Guitar Transcription PoC",
  description: "Rhythm-first electric guitar transcription prototype"
};

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
