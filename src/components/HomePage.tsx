"use client";

import Image from "next/image";
import { useEffect, useMemo, useState } from "react";
import { ProductStage } from "@/components/ProductStage";

const flavors = [
  { key: "double-litchi", lines: ["Double", "Litchi"], primary: "#3D2B68", secondary: "#9089D3", description: "Une explosion exotique. Une recette intense en litchi qui rappelle les saveurs d’Asie tropicale." },
  { key: "coco-citron", lines: ["Coco", "Citron Vert"], primary: "#27326B", secondary: "#00A6E2", description: "Une parenthèse tropicale. On a mélangé la douceur lactée de la coco et l’acidité du citron vert." },
  { key: "kiwi-concombre", lines: ["Kiwi", "Concombre"], primary: "#024A44", secondary: "#71BD96", description: "Le Ciao Energy le plus rafraîchissant de la gamme. Le kiwi apporte son éclat juteux, le concombre une grande fraîcheur." },
  { key: "peche-blanche", lines: ["Pêche", "Blanche"], primary: "#BA5200", secondary: "#EFB36B", description: "Un instant rempli de douceur. On a créé une energy drink florale et délicatement parfumée à la pêche blanche." },
  { key: "pomme-rhubarbe", lines: ["Pomme", "Rhubarbe"], primary: "#9B0984", secondary: "#E6A0E8", description: "L’energy drink aux fruits du jardin. Une recette qui marie la fraîcheur de la pomme et l’acidité de la rhubarbe." },
  { key: "abricot-framboise", lines: ["Abricot", "Framboise"], primary: "#800027", secondary: "#FF7676", description: "Un duo solaire et gourmand. On a mélangé la douceur de l’abricot et la vivacité de la framboise." },
];

const benefits = [
  { eyebrow: "11G de sucres", title: ["Moins", "de sucre"], body: "Une boisson énergisante moins sucrée, avec exclusivement du sucre de canne, choisi pour son origine végétale et son caractère en bouche." },
  { eyebrow: "Arômes artificiels", title: ["Arômes", "naturels"], body: "Pour leur puissance aromatique et leur richesse gustative, on a soigneusement sélectionné des arômes naturels issus de fruits et de plantes." },
  { eyebrow: "Caféine artificielle", title: ["Caféine issue", "de grains de café"], body: "Pour l’énergie, on a choisi des grains de café, source naturelle de caféine, complétés par du guarana, lui aussi naturel." },
  { eyebrow: "Aspartame · Sucralose · Acésulfame K", title: ["Stevia"], body: "Pour compléter le sucre de canne et apporter douceur et gourmandise, on a choisi un édulcorant d’origine végétale avec des extraits de stévia." },
];

const faqs = [
  ["Qu'est-ce qui distingue Ciao Energy des autres boissons énergisantes ?", "Ciao Energy a été pensée comme la boisson énergisante parfaite. On a fait le choix d'une recette à teneur réduite en sucres, d’arômes naturels, de caféine issue de grains de café et d’un édulcorant d’origine végétale : la stévia."],
  ["Ciao Energy est-elle une boisson pétillante ?", "Oui, Ciao Energy est une boisson gazeuse. On a choisi une effervescence marquée pour amplifier la fraîcheur en bouche."],
  ["Quelle est la teneur en sucres et en calories de Ciao Energy ?", "Ciao Energy contient 4 g de sucre et 17 kcal pour 100 mL. Le sucre de canne est associé aux extraits de stévia."],
  ["Quelles sont les vitamines présentes dans Ciao Energy ?", "Une canette contient de la niacine (B3), de la vitamine B6 et de la biotine (B8), qui contribuent à un métabolisme énergétique normal."],
  ["Ciao Energy contient-elle des colorants artificiels ?", "Non. Nos couleurs sont élaborées à partir de denrées alimentaires colorantes."],
  ["Ciao Energy est-elle une boisson contenant de la taurine ?", "Non. Nous avons préféré des sources végétales de caféine — grains de café et guarana — et une recette simple."],
  ["Ciao Energy peut-elle être consommée par tout le monde ?", "Avec 32 mg de caféine pour 100 mL, sa consommation est déconseillée aux enfants et aux femmes enceintes ou allaitantes."],
  ["Où est embouteillé Ciao Energy ?", "Ciao Energy est embouteillée en France avec des standards de qualité européens."],
  ["Comment conserver ma canette de Ciao Energy ?", "Avant ouverture, conservez-la à température ambiante, à l’abri de la lumière et de la chaleur. Après ouverture, gardez-la au frais et consommez-la sous un jour."],
];

function Hud() {
  return (
    <div className="hud" aria-hidden="true">
      <span className="hud-left">C<br />E<br />_</span>
      <span className="hud-right">_<br />/</span>
      <i className="corner tl" /><i className="corner tr" /><i className="corner bl" /><i className="corner br" />
    </div>
  );
}

function Header({ open, onToggle }: { open: boolean; onToggle: () => void }) {
  return (
    <header className="navbar">
      <button className="sound" type="button" aria-label="Activer ou désactiver le son"><span>ON</span><i /><i /><i /><i /></button>
      <a href="#gamme" className="logo-link" aria-label="Ciao Energy — accueil"><Image src="/assets/logo.svg" alt="Ciao Energy" width={150} height={60} priority /></a>
      <button className={`menu-button ${open ? "open" : ""}`} type="button" onClick={onToggle} aria-expanded={open} aria-controls="site-menu"><span className="menu-grid">••<br />••</span><span>{open ? "FERMER" : "MENU"}</span></button>
      <nav id="site-menu" className={`menu-panel ${open ? "open" : ""}`} aria-hidden={!open}>
        <a href="#gamme">Gamme</a><a href="#benefices">Bénéfices</a><a href="#FAQ">FAQ</a><a href="#newsletter">Newsletter</a><a href="mailto:contact@ciao.ysl.monster">Contact</a>
      </nav>
    </header>
  );
}

function Arrow({ direction, onClick }: { direction: "left" | "right"; onClick: () => void }) {
  return <button type="button" className={`carousel-arrow ${direction}`} onClick={onClick} aria-label={direction === "left" ? "Goût précédent" : "Goût suivant"}>{direction === "left" ? "‹" : "›"}</button>;
}

export default function HomePage() {
  const [index, setIndex] = useState(0);
  const [openMenu, setOpenMenu] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [emailState, setEmailState] = useState<"idle" | "done">("idle");
  const active = flavors[index];
  const texture = `/assets/texture-${active.key}.avif`;
  const allTextures = useMemo(() => flavors.map((item) => `/assets/texture-${item.key}.avif`), []);
  const change = (amount: number) => setIndex((current) => (current + amount + flavors.length) % flavors.length);

  useEffect(() => {
    document.documentElement.style.setProperty("--taste-primary", active.primary);
    document.documentElement.style.setProperty("--taste-secondary", active.secondary);
  }, [active]);

  return (
    <main>
      <Header open={openMenu} onToggle={() => setOpenMenu((value) => !value)} />
      <Hud />

      <section id="gamme" className="hero panel">
        <div className="ambient" />
        <Arrow direction="left" onClick={() => change(-1)} />
        <ProductStage texture={texture} sideTextures={[allTextures[(index + 5) % 6], allTextures[(index + 1) % 6]]} />
        <Arrow direction="right" onClick={() => change(1)} />
        <div className="hero-copy">
          <p className="sr-only">Ciao Energy — L’energy drink parfaite</p>
          <h1 className="display-title">{active.lines.map((line) => <span key={line}>{line}</span>)}</h1>
          <div className="pagination" aria-label="Choisir un goût">
            {flavors.map((flavor, flavorIndex) => <button key={flavor.key} type="button" onClick={() => setIndex(flavorIndex)} aria-label={flavor.lines.join(" ")} aria-pressed={flavorIndex === index}><i className={flavorIndex === index ? "active" : ""} /></button>)}
          </div>
          <a className="discover" href="#profile">Scroller pour découvrir</a>
        </div>
      </section>

      <section id="profile" className="profile panel" style={{ backgroundImage: `url(/assets/background-${active.key}.avif)` }}>
        <div className="shade" />
        <ProductStage texture={texture} className="profile-can" />
        <div className="profile-copy"><h2 className="display-title small">{active.lines.map((line) => <span key={line}>{line}</span>)}</h2><p>{active.description}</p></div>
        <div className="flavor-rail">{flavors.map((flavor, flavorIndex) => <button type="button" key={flavor.key} onClick={() => setIndex(flavorIndex)} className={flavorIndex === index ? "active" : ""}>{String(flavorIndex + 1).padStart(2, "0")}</button>)}</div>
      </section>

      <div id="benefices">
        {benefits.map((benefit, benefitIndex) => {
          const flavor = flavors[(index + benefitIndex) % flavors.length];
          return (
            <section className="benefit panel" key={benefit.eyebrow} style={{ "--benefit-glow": flavor.secondary } as React.CSSProperties}>
              <div className="benefit-copy"><p className="eyebrow"><b>×</b>{benefit.eyebrow}</p><h2 className="display-title medium">{benefit.title.map((line) => <span key={line}>{line}</span>)}</h2><p className="body-copy">{benefit.body}</p></div>
              <ProductStage texture={`/assets/texture-${flavor.key}.avif`} sideTextures={[allTextures[(index + benefitIndex + 1) % 6], allTextures[(index + benefitIndex + 2) % 6]]} className="benefit-stage" />
              <div className="benefit-nav" aria-label="Bénéfices">{benefits.map((_, itemIndex) => <a key={itemIndex} href={`#benefit-${itemIndex + 1}`} className={itemIndex === benefitIndex ? "active" : ""}>{itemIndex + 1}</a>)}</div>
              <span id={`benefit-${benefitIndex + 1}`} className="anchor" />
            </section>
          );
        })}
      </div>

      <section className="argument panel">
        <div className="argument-bg" style={{ backgroundImage: `url(/assets/background-${active.key}.avif)` }} />
        <Image className="zero-mask" src="/assets/zero-bullshit-mask.svg" alt="Zero Bullshit" width={1600} height={500} />
        <ProductStage texture={texture} className="argument-can" />
      </section>

      <section className="packshot panel">
        <ProductStage texture={texture} sideTextures={allTextures} packshot />
        <p className="mono-note">6 RECETTES · 250 ML · ZÉRO BULLSHIT</p>
      </section>

      <section id="FAQ" className="faq-section">
        <h2 className="display-title faq-title"><span>Foire aux</span><span>questions</span></h2>
        <div className="faq-list">
          {faqs.map(([question, answer], faqIndex) => {
            const isOpen = openFaq === faqIndex;
            return <article className={`faq-item ${isOpen ? "open" : ""}`} key={question}><button type="button" onClick={() => setOpenFaq(isOpen ? null : faqIndex)} aria-expanded={isOpen}><span>{question}</span><i>⌄</i></button><div className="faq-answer"><p>{answer}</p></div></article>;
          })}
        </div>
      </section>

      <section id="newsletter" className="newsletter">
        <div className="newsletter-glow" />
        <p className="mono-note">REJOIGNEZ-NOUS</p>
        <h2 className="display-title medium"><span>Entrez dans</span><span>la communauté</span></h2>
        <p className="newsletter-copy">Soyez les premiers au courant de nos actualités et des nouveaux produits Ciao Energy.</p>
        <form onSubmit={(event) => { event.preventDefault(); setEmailState("done"); }}><label><span className="sr-only">Votre adresse mail</span><input type="email" required placeholder="VOTRE ADRESSE MAIL" /></label><button type="submit">S&apos;INSCRIRE</button></form>
        <p className="form-note" role="status">{emailState === "done" ? "Mode démonstration : aucune donnée n’a été envoyée." : "En vous inscrivant vous acceptez notre politique de confidentialité."}</p>
      </section>

      <footer><p>© 2026 CIAO ENERGY — BY SKAALD</p><div><a href="https://www.tiktok.com/@ciaoenergy">TIKTOK</a><a href="/mentions-legales">MENTIONS LÉGALES</a><a href="/cgu">CGU</a><a href="/politique-de-confidentialite">POLITIQUE DE CONFIDENTIALITÉ</a><a href="https://www.instagram.com/ciaoenergy">INSTAGRAM</a></div></footer>
    </main>
  );
}
