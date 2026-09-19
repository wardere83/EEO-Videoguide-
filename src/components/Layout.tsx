import { useState } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { ArrowUpRight, Menu, X } from "lucide-react";
import { links } from "../config";
export function Layout() {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  return (
    <>
      <a className="skip" href="#main">
        Skip to content
      </a>
      <div className="topline">
        California Community Colleges Chancellor’s Office
      </div>
      <header>
        <div className="width header-inner">
          <Link
            to="/"
            aria-label="EEO initiative home"
            onClick={() => setOpen(false)}
          >
            <img
              className="logo"
              src="./brand/cccco-logo-stacked.svg"
              alt="California Community Colleges"
            />
          </Link>
          <button
            className="menu-toggle"
            aria-label={open ? "Close navigation" : "Open navigation"}
            aria-expanded={open}
            aria-controls="navigation"
            onClick={() => setOpen(!open)}
          >
            {open ? <X /> : <Menu />}
          </button>
          <nav
            id="navigation"
            aria-label="Main navigation"
            className={open ? "open" : ""}
            onClick={() => setOpen(false)}
          >
            <NavLink to="/" end>
              Initiative
            </NavLink>
            <NavLink to="/resources">Resources</NavLink>
            <a className="button small outline" href={links.portal}>
              Open dashboard <ArrowUpRight size={16} />
            </a>
          </nav>
        </div>
      </header>
      <main id="main" tabIndex={-1} key={location.pathname}>
        <Outlet />
      </main>
      <footer className="width">
        <div className="footer-top">
          <img
            className="logo"
            src="./brand/cccco-logo-stacked.svg"
            alt="California Community Colleges"
          />
          <div>
            <Link to="/resources">Resources</Link>
            <Link to="/support">Support</Link>
            <a href={links.initiative}>
              CCCCO initiative <ArrowUpRight size={14} />
            </a>
          </div>
        </div>
        <div className="footer-bottom">
          <span>EEO Innovative Best Practices Grant Initiative</span>
          <span>
            Platform support by{" "}
            <a href="https://bulleconsulting.com">Bulle Consulting</a>
          </span>
        </div>
      </footer>
    </>
  );
}
