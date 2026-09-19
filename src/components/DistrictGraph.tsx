import { useState } from "react";
import type { CSSProperties } from "react";
import { ArrowUpRight } from "lucide-react";
import districts from "../grantees.json";

const logos = ["ahc.png", "avc.svg", "citrus.svg", "kern.png", "mtsac.svg", "nocccd.svg", "peralta-seal.png", "sdccd.svg", "smc.svg", "scccd-mark.png", "wvm.svg"];
const maxAward = 150000;

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
          <p className="eyebrow">2026–28 district award graph</p>
          <h3 id="award-network-title">One initiative. Multi-District projects,</h3>
        </div>
        <button className="chart-total" onClick={onEnterFilm} aria-label="View the current district award chapter">
          <span>Current cycle</span>
          <strong>$1.4M</strong>
          <small>11 district awards</small>
          <ArrowUpRight size={16} />
        </button>
      </div>

      <p className="chart-instruction">Award amount by district. Select a logo marker to view its project and intended impact.</p>
      <div className="award-chart-scroll">
        <div className="award-chart-layout">
          <div className="award-chart-scale" aria-hidden="true">
            <span>$150K</span>
            <span>$100K</span>
            <span>$50K</span>
            <span>$0</span>
          </div>
          <div className="award-chart-plot" role="group" aria-label="District grant awards from zero to one hundred fifty thousand dollars">
            <div className="award-chart-grid" aria-hidden="true"><i /><i /><i /><i /></div>
            <div className="award-chart-columns">
              {districts.map((item, index) => (
                <button
                  className="award-column"
                  key={item.id}
                  style={{ "--award-height": `${(item.award / maxAward) * 100}%`, "--delay": `${index * 45}ms` } as CSSProperties}
                  aria-pressed={selected === index}
                  aria-controls="district-award-detail"
                  aria-label={`${item.name}, ${money.format(item.award)}`}
                  onClick={() => setSelected(index)}
                >
                  <span className="award-bar">
                    <span className="award-logo"><img src={`./district-logos/${logos[index]}`} alt="" /></span>
                    <strong>{money.format(item.award)}</strong>
                  </span>
                  <span className="award-label">{item.shortName}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
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
