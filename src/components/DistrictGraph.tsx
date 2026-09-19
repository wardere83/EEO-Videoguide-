import { useState } from "react";
import type { CSSProperties } from "react";
import { ArrowUpRight } from "lucide-react";
import districts from "../grantees.json";

const positions = [
  [11, 18], [31, 9], [53, 8], [74, 11], [91, 25], [93, 54],
  [82, 80], [60, 91], [37, 91], [16, 79], [7, 50],
];

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export function DistrictGraph({ onEnterFilm }: { onEnterFilm: () => void }) {
  const [selected, setSelected] = useState(3);
  const district = districts[selected];

  return (
    <section className="award-network" aria-labelledby="award-network-title">
      <div className="award-network-heading">
        <div>
          <p className="eyebrow">2026–28 award network</p>
          <h3 id="award-network-title">One initiative. Eleven district projects.</h3>
        </div>
        <p>Select a district to see its award and project focus.</p>
      </div>

      <div className="network-stage">
        <svg className="network-lines" viewBox="0 0 1000 620" aria-hidden="true">
          <circle cx="500" cy="310" r="175" />
          <circle cx="500" cy="310" r="235" />
          {positions.map(([x, y], index) => (
            <line key={districts[index].id} x1="500" y1="310" x2={x * 10} y2={y * 6.2} />
          ))}
        </svg>

        <button className="network-hub" onClick={onEnterFilm} aria-label="Play the current district award chapter">
          <span>Current cycle</span>
          <strong>$1.4M</strong>
          <small>11 districts · 2026–28</small>
          <ArrowUpRight size={16} />
        </button>

        {districts.map((item, index) => (
          <button
            className="network-node"
            key={item.id}
            style={{ "--x": `${positions[index][0]}%`, "--y": `${positions[index][1]}%` } as CSSProperties}
            aria-pressed={selected === index}
            aria-controls="district-award-detail"
            onClick={() => setSelected(index)}
          >
            <span>{item.shortName}</span>
            <strong>{money.format(item.award)}</strong>
          </button>
        ))}
      </div>

      <div className="network-detail" id="district-award-detail" aria-live="polite">
        <div>
          <span>{district.city} · {district.focus}</span>
          <h4>{district.name}</h4>
          <p>{district.description}</p>
        </div>
        <strong>{money.format(district.award)}</strong>
      </div>
      <p className="network-summary">Six $150,000 awards + five $100,000 awards = <strong>$1.4 million</strong></p>
    </section>
  );
}
