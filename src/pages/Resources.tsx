import { useState } from "react";
import { ArrowUpRight, Search } from "lucide-react";
import { Link } from "react-router-dom";
import { resources } from "../config";
export function Resources() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const shown = resources.filter(
    (r) =>
      (category === "All" || r.category === category) &&
      `${r.title} ${r.description}`.toLowerCase().includes(query.toLowerCase()),
  );
  return (
    <section className="width section resource-page">
      <p className="eyebrow">EEO IBP · Resource workspace</p>
      <h1>
        Everything starts
        <br />
        <span>with a next step.</span>
      </h1>
      <p className="intro">
        A practical starting point for initiative guidance, reporting systems,
        training, and district coordination.
      </p>
      <div className="search">
        <Search size={20} />
        <label className="sr-only" htmlFor="search">
          Search resources
        </label>
        <input
          id="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search resources…"
          type="search"
        />
      </div>
      <div className="filters" aria-label="Resource categories">
        {["All", ...new Set(resources.map((r) => r.category))].map((c) => (
          <button
            key={c}
            aria-pressed={category === c}
            onClick={() => setCategory(c)}
          >
            {c}
          </button>
        ))}
      </div>
      <p className="caption" role="status">
        {shown.length} {shown.length === 1 ? "resource" : "resources"} found
      </p>
      <div className="resource-grid">
        {shown.map((r) => (
          <article key={r.title}>
            <p className="eyebrow">{r.category}</p>
            <h2>{r.title}</h2>
            <p>{r.description}</p>
            {r.category === "Training" ? (
              <Link className="text-link" to="/video">
                {r.label}
                <ArrowUpRight size={17} />
              </Link>
            ) : (
              <a className="text-link" href={r.href}>
                {r.label}
                <ArrowUpRight size={17} />
              </a>
            )}
          </article>
        ))}
      </div>
      {!shown.length && (
        <div className="empty">
          <h2>No matching resources.</h2>
          <p>Try another search or select a different category.</p>
          <button
            className="button"
            onClick={() => {
              setQuery("");
              setCategory("All");
            }}
          >
            Clear filters
          </button>
        </div>
      )}
      <p className="resource-note">
        Use the guidance and reporting requirements applicable to your
        district’s award. Official program materials are maintained by the
        Chancellor’s Office.
      </p>
    </section>
  );
}
