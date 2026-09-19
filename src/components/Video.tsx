import { useRef, useState } from "react";
import { Copy, Play, Download } from "lucide-react";
import film from "../film.json";
const media = "./media/eeo-initiative.mp4";
export function Video({
  immediate = false,
  chapters = false,
}: {
  immediate?: boolean;
  chapters?: boolean;
}) {
  const video = useRef<HTMLVideoElement>(null);
  const [started, setStarted] = useState(immediate);
  const [status, setStatus] = useState("");
  function seek(time: number) {
    if (video.current) {
      setStarted(true);
      video.current.currentTime = time;
      video.current.focus();
      void video.current
        .play()
        .catch(() => setStatus("Press play to begin the film."));
    }
  }
  async function copy() {
    try {
      await navigator.clipboard.writeText(
        new URL("#/video", window.location.href).href,
      );
      setStatus("Initiative film link copied.");
    } catch {
      setStatus("Copy the video guide address from your browser to share it.");
    }
  }
  return (
    <section
      className="width film"
      id="grant-film"
      aria-labelledby="film-title"
    >
      <div className="section-heading">
        <h2 id="film-title">The initiative in focus.</h2>
        <span className="eyebrow">EEO IBP · Shared possibility</span>
      </div>
      <div className="cinema">
        <video
          ref={video}
          controls={started}
          playsInline
          preload={immediate ? "metadata" : "none"}
          poster="./media/eeo-poster.jpg"
          aria-label="EEO IBP Initiative Film"
          onPlay={() => setStarted(true)}
        >
          <source src="./media/eeo-initiative.webm" type="video/webm" />
          <source src={media} type="video/mp4" />
          <track
            kind="captions"
            src="./media/eeo-initiative.en.vtt"
            srcLang="en"
            label="English"
          />
          Your browser does not support embedded video. Download the film below.
        </video>
        {!started && (
          <button className="film-start" onClick={() => seek(0)}>
            <Play size={20} fill="currentColor" /> Watch the initiative film
          </button>
        )}
      </div>
      <div className="video-actions">
        <a href={media} download="EEO_IBP_Initiative_Film.mp4">
          <Download size={15} /> Download the film
        </a>
        <button onClick={copy}>
          <Copy size={14} /> Share initiative film
        </button>
      </div>
      <p className="status" role="status">
        {status}
      </p>
      {chapters && (
        <div className="film-chapters">
          <h3>Explore the film</h3>
          <div>
            {[
              { label: "The initiative", time: 0 },
              { label: "Opportunity in practice", time: 12 },
              { label: "Ideas in action", time: 30 },
              { label: "A shared future", time: 70 },
            ].map((chapter) => (
              <button key={chapter.label} onClick={() => seek(chapter.time)}>
                <Play size={13} />
                {chapter.label}
              </button>
            ))}
          </div>
          <details>
            <summary>Read the film transcript</summary>
            {film.map((scene) => (
              <p key={scene.title + scene.description}>
                <strong>{scene.title}</strong> {scene.description}
              </p>
            ))}
          </details>
        </div>
      )}
    </section>
  );
}
