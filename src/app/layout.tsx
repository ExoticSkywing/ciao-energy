import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Ciao Energy — L’energy drink parfaite",
  description:
    "Découvrez Ciao Energy : six recettes, moins de sucre, des arômes naturels et une caféine végétale.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr">
      <body style={{ margin: 0 }}>{children}</body>
    </html>
  );
}
