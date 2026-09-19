import { useEffect } from "react";
import { HashRouter, Route, Routes, useLocation, Link } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Home } from "./pages/Home";
import { Resources } from "./pages/Resources";
import { Support } from "./pages/Support";
import { Video } from "./components/Video";
function RouteFocus() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
    document.getElementById("main")?.focus();
    const titles: Record<string, string> = {
      "/": "EEO IBP Grant Initiative",
      "/resources": "Resources",
      "/video": "Video Guide",
      "/support": "Support",
    };
    document.title = `${titles[pathname] ?? "Page not found"} | EEO Dashboard`;
  }, [pathname]);
  return null;
}
export default function App() {
  return (
    <HashRouter>
      <RouteFocus />
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/resources" element={<Resources />} />
          <Route
            path="/video"
            element={
              <>
                <section className="width video-intro">
                  <p className="eyebrow">Learn & share</p>
                  <h1>EEO IBP Initiative</h1>
                  <p>Innovative Best Practices Grant Initiative</p>
                </section>
                <Video chapters />
              </>
            }
          />
          <Route path="/support" element={<Support />} />
          <Route
            path="*"
            element={
              <section className="section width">
                <h1>Page not found.</h1>
                <Link className="button" to="/">
                  Return to the initiative
                </Link>
              </section>
            }
          />
        </Route>
      </Routes>
    </HashRouter>
  );
}
