import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  BarChart3,
  CalendarDays,
  Check,
  CirclePause,
  CirclePlay,
  Clock3,
  FolderKanban,
  House,
  UsersRound,
} from "lucide-react";
import { links } from "../config";

const accounts = ["District A", "District B", "District C"];
const scenes = ["Overview", "Projects", "Status", "Book an SME"];

export function MobileShowcase() {
  const [account, setAccount] = useState(0);
  const [scene, setScene] = useState(0);
  const [playing, setPlaying] = useState(true);

  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(
      () => setScene((current) => (current + 1) % scenes.length),
      3200,
    );
    return () => window.clearInterval(timer);
  }, [playing]);

  return (
    <section className="mobile-showcase" aria-labelledby="mobile-showcase-title">
      <div className="width mobile-showcase-grid">
        <div className="mobile-copy">
          <p className="eyebrow">The dashboard · On the go</p>
          <h2 id="mobile-showcase-title">One connected view of the work.</h2>
          <p>
            A mobile-ready workspace brings award progress, project files,
            status updates, account views, and SME scheduling together—wherever
            district teams are working.
          </p>
          <div className="mobile-capabilities">
            <span><Check size={15} /> Award and project status</span>
            <span><Check size={15} /> District account views</span>
            <span><Check size={15} /> SME appointment booking</span>
          </div>
          <a className="button mobile-cta" href={links.portal}>
            Open EEO Dashboard <ArrowUpRight size={17} />
          </a>
          <small>Interactive preview uses illustrative sample data.</small>
        </div>

        <div className="phone-demo">
          <div className="phone-glow" />
          <div className="phone" aria-label="Interactive mobile EEO Dashboard preview">
            <div className="phone-hardware"><span /></div>
            <div className="phone-screen">
              <div className="phone-status"><span>9:41</span><span>● ● ●</span></div>
              <div className="app-header">
                <img src="./brand/cccco-logo-stacked.svg" alt="" />
                <span>EEO Dashboard</span>
              </div>
              <div className="account-switcher" role="group" aria-label="Sample district account">
                {accounts.map((name, index) => (
                  <button key={name} aria-pressed={account === index} onClick={() => setAccount(index)}>
                    {name}
                  </button>
                ))}
              </div>
              <div className="demo-scene" key={`${account}-${scene}`}>
                {scene === 0 && <Overview account={accounts[account]} />}
                {scene === 1 && <Projects />}
                {scene === 2 && <StatusUpdate />}
                {scene === 3 && <ExpertBooking />}
              </div>
              <div className="app-nav" aria-hidden="true">
                <span className={scene === 0 ? "active" : ""}><House size={16} />Home</span>
                <span className={scene === 1 ? "active" : ""}><FolderKanban size={16} />Projects</span>
                <span className={scene === 3 ? "active" : ""}><UsersRound size={16} />Experts</span>
              </div>
            </div>
          </div>
          <div className="demo-controls">
            <button onClick={() => setPlaying(!playing)} aria-label={playing ? "Pause dashboard walkthrough" : "Play dashboard walkthrough"}>
              {playing ? <CirclePause size={21} /> : <CirclePlay size={21} />}
            </button>
            <div>
              {scenes.map((name, index) => (
                <button key={name} aria-label={`Show ${name}`} aria-pressed={scene === index} onClick={() => setScene(index)}>
                  <span />
                </button>
              ))}
            </div>
            <span>{scenes[scene]}</span>
          </div>
        </div>
      </div>
    </section>
  );
}

function Overview({ account }: { account: string }) {
  return <>
    <div className="app-greeting"><span>Sample account</span><h3>{account}</h3><p>2026–28 EEO IBP award</p></div>
    <div className="app-balance"><span>Grant overview</span><strong>$150,000</strong><small><i /> Active · On track</small></div>
    <div className="app-stats"><div><BarChart3 size={17} /><strong>64%</strong><span>Utilized</span></div><div><Check size={17} /><strong>4 / 6</strong><span>Milestones</span></div></div>
  </>;
}

function Projects() {
  return <>
    <div className="app-greeting"><span>Active work</span><h3>Projects</h3><p>Two initiatives in progress</p></div>
    <Project name="Inclusive Hiring Lab" status="72%" />
    <Project name="Mentor Network" status="58%" />
    <button className="app-action">View all project files <ArrowUpRight size={14} /></button>
  </>;
}

function Project({ name, status }: { name: string; status: string }) {
  return <div className="app-project"><div><FolderKanban size={18} /><span><strong>{name}</strong><small>Active project</small></span></div><b>{status}</b></div>;
}

function StatusUpdate() {
  return <>
    <div className="app-greeting"><span>Latest activity</span><h3>Status updates</h3><p>Everything important, in one timeline</p></div>
    <div className="app-timeline">
      <div><i /><span><strong>Quarterly update submitted</strong><small>District team · Today</small></span></div>
      <div><i /><span><strong>Milestone approved</strong><small>Project review · This week</small></span></div>
      <div><i /><span><strong>SME notes available</strong><small>Advisory session</small></span></div>
    </div>
  </>;
}

function ExpertBooking() {
  return <>
    <div className="app-greeting"><span>Expert support</span><h3>Book an SME</h3><p>Choose the support your project needs</p></div>
    <div className="expert-card"><UsersRound size={21} /><div><strong>Recruitment strategy</strong><span>Subject-matter expert</span></div><b>3 slots</b></div>
    <div className="expert-card"><BarChart3 size={21} /><div><strong>Data & evaluation</strong><span>Subject-matter expert</span></div><b>2 slots</b></div>
    <button className="book-button"><CalendarDays size={16} /> View availability <Clock3 size={14} /></button>
  </>;
}
