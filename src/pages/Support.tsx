import { links } from "../config";
export function Support() {
  return (
    <section className="section width support">
      <p className="eyebrow">Here to help</p>
      <h1>Support for your next step.</h1>
      <p className="intro">
        Choose the right starting point for your question.
      </p>
      <div className="resource-grid">
        <article>
          <h2>District workspace access</h2>
          <p>
            Open the EEO Dashboard and use the sign-in or password recovery
            options. For assignment or access questions, contact your district
            coordinator or Bulle Consulting project manager.
          </p>
          <a className="text-link" href={links.portal}>
            Open EEO Dashboard ↗
          </a>
        </article>
        <article>
          <h2>Grant requirements</h2>
          <p>
            Consult the official initiative page for program guidance and the
            materials applicable to your award.
          </p>
          <a className="text-link" href={links.initiative}>
            View CCCCO resources ↗
          </a>
        </article>
        <article>
          <h2>Platform assistance</h2>
          <p>
            Contact Bulle Consulting through its website for platform
            assistance. Include your district name and a brief description of
            the issue.
          </p>
          <a className="text-link" href="https://bulleconsulting.com">
            Contact Bulle Consulting ↗
          </a>
        </article>
      </div>
    </section>
  );
}
