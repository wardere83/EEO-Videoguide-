import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowUpRight, Play } from "lucide-react";
import { Video } from "../components/Video";
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
        <p className="eyebrow">
          EEO Innovative Best Practices Grant Initiative
        </p>
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
          <Link className="button" to="/video">
            Watch the initiative film <Play size={16} />
          </Link>
          <Link className="text-link" to="/resources">
            Explore resources <ArrowUpRight size={18} />
          </Link>
        </div>
      </section>
      <Video />
      <section
        className="initiative-note width"
        aria-labelledby="purpose-heading"
      >
        <div>
          <p className="eyebrow">The initiative</p>
          <h2 id="purpose-heading">
            Better practices.
            <br />
            Broader opportunity.
          </h2>
        </div>
        <div>
          <p>
            Guided by diversity, equity, inclusion, and accessibility, the
            Chancellor’s Office EEO Innovative Best Practices Grant Initiative
            supports new and expanded approaches to equal employment opportunity
            and faculty and staff diversity.
          </p>
          <div
            className="priority-controls"
            role="group"
            aria-label="Explore initiative priorities"
          >
            {priorities.map((item, i) => (
              <button
                key={item.name}
                aria-pressed={priority === i}
                aria-controls="priority-description"
                onClick={() => setPriority(i)}
              >
                {item.name}
              </button>
            ))}
          </div>
          <p
            id="priority-description"
            className="priority-description"
            aria-live="polite"
          >
            {priorities[priority].text}
          </p>
          <a className="text-link" href={links.initiative}>
            Explore the initiative <ArrowUpRight size={16} />
          </a>
        </div>
      </section>
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
