import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowUpRight } from "lucide-react";
import districts from "../grantees.json";

const logos = ["ahc.png", "avc.svg", "citrus.svg", "kern.png", "mtsac.svg", "nocccd.svg", "peralta-seal.png", "sdccd.svg", "smc.svg", "scccd-mark.png", "wvm.svg"];
const liftIds = new Set(["avc", "citrus", "peralta", "wvm"]);
const impactWords = [
  { display: "Recruit", label: "Equitable recruitment" },
  { display: "Mentor", label: "Mentorship pathways" },
  { display: "Develop", label: "Faculty development" },
  { display: "Belong", label: "Workplace belonging" },
  { display: "Advance", label: "Inclusive advancement" },
  { display: "Sustain", label: "Evidence-led practice" },
];
const pointY = [318, 338, 307, 332, 300, 326, 310, 340, 304, 334, 314];

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export function DistrictGraph({ onEnterFilm }: { onEnterFilm: () => void }) {
  const [selected, setSelected] = useState(3);
  const [word, setWord] = useState(0);
  const [visible, setVisible] = useState(false);
  const section = useRef<HTMLElement>(null);
  const district = districts[selected];
  const selectedIsLift = liftIds.has(district.id);
  const related = useMemo(
    () => districts.map((item, index) => ({ item, index })).filter(({ item }) => liftIds.has(item.id) === selectedIsLift),
    [selectedIsLift],
  );
  const constellationPoints = related.map(({ index }) => `${45 + index * 91},${pointY[index]}`).join(" ");

  useEffect(() => {
    const node = section.current;
    if (!node) return;
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) setVisible(true);
    }, { threshold: 0.2 });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const timer = window.setInterval(() => setWord((current) => (current + 1) % impactWords.length), 1900);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <section ref={section} className={`impact-network${visible ? " is-visible" : ""}`} aria-labelledby="impact-network-title">
      <div className="impact-loop-panel">
        <div className="impact-word-window" aria-label={`Current impact initiative: ${impactWords[word].label}`}>
          <span className="impact-reel-arrow" aria-hidden="true">→</span>
          <div className="impact-word-reel" key={word} aria-hidden="true">
            {[-3, -2, -1, 0, 1, 2, 3].map((offset) => {
              const item = impactWords[(word + offset + impactWords.length) % impactWords.length];
              return <span className={offset === 0 ? "active" : ""} key={`${word}-${offset}`}>{item.display}</span>;
            })}
          </div>
        </div>
      </div>

      <div className="district-explorer">
        <div className="district-explorer-heading">
          <div>
            <p className="eyebrow">2026–28 district initiatives</p>
            <h3 id="impact-network-title">One initiative. Multi-District projects,</h3>
          </div>
          <p>Select a district logo to explore its budget, project, and intended impact.</p>
        </div>

        <div className="district-beam-stage">
          <svg className="tier-constellation" viewBox="0 0 1000 360" preserveAspectRatio="none" aria-hidden="true">
            <polyline points={constellationPoints} />
            {related.map(({ item, index }) => (
              <g key={item.id}>
                <line x1={45 + index * 91} y1={pointY[index]} x2={45 + index * 91} y2="360" />
                <circle className={selected === index ? "selected" : ""} cx={45 + index * 91} cy={pointY[index]} r={selected === index ? 8 : 4} />
              </g>
            ))}
          </svg>

          <article className="district-insight" id="district-award-detail" key={district.id} aria-live="polite">
            <div className="district-insight-topline">
              <span>{selectedIsLift ? "Tier 2 · LIFT" : "Tier 1"}</span>
              <strong>{money.format(district.award)}</strong>
            </div>
            <p>{district.city} · {district.focus}</p>
            <h4>{district.name}</h4>
            <div className="district-insight-grid">
              <div><span>Project</span><p>{district.description}</p></div>
              <div><span>Intended impact</span><p>{district.impact}</p></div>
            </div>
            <button onClick={onEnterFilm}>View initiative chapter <ArrowUpRight size={15} /></button>
          </article>
        </div>

        <div className="district-logo-rail" role="group" aria-label="District initiatives in alphabetical order">
          {districts.map((item, index) => {
            const itemIsLift = liftIds.has(item.id);
            const isRelated = itemIsLift === selectedIsLift;
            return (
              <button
                className={isRelated ? "is-related" : ""}
                key={item.id}
                aria-pressed={selected === index}
                aria-controls="district-award-detail"
                aria-label={`${item.name}, ${money.format(item.award)}, ${itemIsLift ? "Tier 2 LIFT" : "Tier 1"}`}
                onClick={() => setSelected(index)}
              >
                <img src={`./district-logos/${logos[index]}`} alt="" />
                <span>{item.shortName}</span>
                <i aria-hidden="true" />
              </button>
            );
          })}
        </div>
        <p className="district-tier-key"><span>Tier 1</span><span>Tier 2 · LIFT</span> Related districts connect automatically.</p>
      </div>
    </section>
  );
}
