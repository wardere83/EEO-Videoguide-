import { useState } from "react";
import type { CSSProperties } from "react";
import { ArrowUpRight } from "lucide-react";
import districts from "../grantees.json";

const positions = [[12, 22], [31, 10], [51, 16], [72, 9], [89, 25], [90, 55], [78, 82], [57, 91], [37, 82], [16, 76], [8, 49]];
const logos = ["ahc.png", "avc.svg", "citrus.svg", "kern.png", "mtsac.svg", "nocccd.svg", "peralta-seal.png", "sdccd.svg", "smc.svg", "scccd-mark.png", "wvm.svg"];
const connections = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 9], [9, 10], [10, 0], [1, 8], [2, 5], [4, 7], [0, 6]];

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
          <h3 id="award-network-title">One initiative. Multi-District projects,</h3>
        </div>
        <p>Select a district to see its award and project focus.</p>
      </div>

      <div className="network-stage">
        <svg className="network-lines" viewBox="0 0 1000 620" aria-hidden="true">
          <circle className="network-orbit" cx="500" cy="310" r="166" />
          <circle className="network-orbit outer" cx="500" cy="310" r="238" />
          {positions.map(([x, y], index) => (
            <line className={selected === index ? "selected" : ""} key={districts[index].id} x1="500" y1="310" x2={x * 10} y2={y * 6.2} />
          ))}
          {connections.map(([from, to]) => (
            <line
              className={selected === from || selected === to ? "mesh selected" : "mesh"}
              key={`${from}-${to}`}
              x1={positions[from][0] * 10}
              y1={positions[from][1] * 6.2}
              x2={positions[to][0] * 10}
              y2={positions[to][1] * 6.2}
            />
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
            style={{ "--x": `${positions[index][0]}%`, "--y": `${positions[index][1]}%`, "--delay": `${-index * .22}s` } as CSSProperties}
            aria-pressed={selected === index}
            aria-controls="district-award-detail"
            aria-label={`${item.name}, ${money.format(item.award)}`}
            onClick={() => setSelected(index)}
          >
            <img src={`./district-logos/${logos[index]}`} alt="" />
            <strong>{money.format(item.award)}</strong>
          </button>
        ))}
      </div>

      <div className="network-detail" id="district-award-detail" aria-live="polite">
        <div className="network-detail-title">
          <span>{district.city} · {district.focus}</span>
          <h4>{district.name}</h4>
          <strong>{money.format(district.award)}</strong>
        </div>
        <div><span>Project</span><p>{district.description}</p></div>
        <div><span>Intended impact</span><p>{district.impact}</p></div>
      </div>
      <p className="network-summary">Six $150,000 awards + five $100,000 awards = <strong>$1.4 million</strong></p>
    </section>
  );
}
