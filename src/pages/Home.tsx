import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";
import { Video } from "../components/Video";
import { MobileShowcase } from "../components/MobileShowcase";
import { links } from "../config";

const priorities = [
  {
    name: "Recruitment",
    text: "Explore innovative approaches to equitable recruitment and inclusive hiring.",
  },
  {
    name: "Growth",
    text: "Support mentorship, professional learning, and opportunities for faculty and staff to thrive.",
  },
  {
    name: "Belonging",
    text: "Strengthen workplace cultures where people feel connected, valued, and able to contribute.",
  },
];
export function Home() {
  const [priority, setPriority] = useState(0);
  return (
    <>
      <section className="hero width">
        <div className="hero-copy">
          <p className="eyebrow">EEO Innovative Best Practices Grant Initiative</p>
          <h1>
            Opportunity for everyone.
            <br />
            <span>Progress we build together.</span>
          </h1>
          <p className="intro">
            Advancing equal employment opportunity through innovative approaches
            to recruitment, professional growth, and belonging.
          </p>
          <div className="actions">
            <Link className="button" to="/resources">
              Explore resources <ArrowUpRight size={16} />
            </Link>
          </div>
        </div>
        <div className="hero-system" aria-label="EEO IBP funding overview">
          <div className="hero-system-core">
            <span>Statewide foundation</span>
            <strong>$20M</strong>
            <small>Established through AB 132</small>
          </div>
          <div className="hero-signal signal-one"><span>✓</span>$15.5M apportioned</div>
          <div className="hero-signal signal-two"><span>✓</span>32 award selections</div>
          <div className="hero-signal signal-three"><span>✓</span>11 current districts</div>
        </div>
      </section>
      <div className="initiative-facts width" aria-label="Initiative overview">
        <span>Statewide EEO investment</span>
        <strong>$20M foundation</strong>
        <strong>$7.05M competitive awards</strong>
        <strong>32 award selections</strong>
        <strong>11 current districts</strong>
      </div>
      <section className="initiative-note width" aria-labelledby="purpose-heading">
        <div className="initiative-note-heading">
          <p className="eyebrow">The initiative</p>
          <h2 id="purpose-heading">Better practices create broader opportunity.</h2>
        </div>
        <div className="initiative-feature-grid" role="group" aria-label="Explore initiative priorities">
          {priorities.map((item, i) => (
            <article key={item.name} className={priority === i ? "active" : ""}>
              <div className={`priority-visual priority-visual-${i + 1}`} aria-hidden="true">
                <i /><i /><i /><i />
              </div>
              <button
                aria-pressed={priority === i}
                aria-controls="priority-description"
                onClick={() => setPriority(i)}
              >
                {item.name}
              </button>
              <p>{item.text}</p>
            </article>
          ))}
        </div>
        <p id="priority-description" className="sr-only" aria-live="polite">
          {priorities[priority].text}
        </p>
        <div className="initiative-action">
          <a className="button" href={links.initiative}>
            Explore the initiative <ArrowUpRight size={16} />
          </a>
        </div>
      </section>
      <Video />
      <MobileShowcase />
      <section className="closing width">
        <div>
          <p className="eyebrow">For participating district teams</p>
          <h2>Your next step, connected.</h2>
        </div>
        <a className="button" href={links.portal}>
          Open EEO Dashboard <ArrowUpRight size={18} />
        </a>
      </section>
    </>
  );
}
