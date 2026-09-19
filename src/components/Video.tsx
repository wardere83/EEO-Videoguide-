import { useEffect, useRef, useState } from "react";
import { Copy, Download, Pause, Play } from "lucide-react";
import film from "../film.json";
const media = "./media/eeo-initiative.mp4";
export function Video({
  chapters = false,
}: {
  chapters?: boolean;
}) {
  const video = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(true);
  const [status, setStatus] = useState("");

  useEffect(() => {
    if (!video.current) return;
    video.current.muted = true;
    video.current.defaultMuted = true;
    void video.current.play().catch(() => setPlaying(false));
  }, []);

  function seek(time: number) {
    if (video.current) {
      video.current.currentTime = time;
      video.current.focus();
      void video.current
        .play()
        .then(() => setPlaying(true))
        .catch(() => setStatus("Select play to begin the video."));
    }
  }

  function togglePlayback() {
    if (!video.current) return;
    if (video.current.paused) {
      void video.current.play().then(() => setPlaying(true));
    } else {
      video.current.pause();
      setPlaying(false);
    }
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(
        new URL("#/video", window.location.href).href,
      );
      setStatus("Initiative video link copied.");
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
          autoPlay
          loop
          muted
          playsInline
          preload="auto"
          poster="./media/eeo-poster.jpg"
          aria-label="EEO IBP Initiative video"
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
        >
          <source src="./media/eeo-initiative.webm" type="video/webm" />
          <source src={media} type="video/mp4" />
          <track
            kind="captions"
            src="./media/eeo-initiative.en.vtt"
            srcLang="en"
            label="English"
          />
          Your browser does not support embedded video. Download the video below.
        </video>
        <button
          className="video-toggle"
          onClick={togglePlayback}
          aria-label={playing ? "Pause video" : "Play video"}
        >
          {playing ? <Pause size={18} /> : <Play size={18} fill="currentColor" />}
        </button>
      </div>
      <div className="video-actions">
        <a href={media} download="EEO_IBP_Initiative_Film.mp4">
          <Download size={15} /> Download video
        </a>
        <button onClick={copy}>
          <Copy size={14} /> Share video
        </button>
      </div>
      <p className="status" role="status">
        {status}
      </p>
      {chapters && (
        <div className="film-chapters">
          <h3>Explore chapters</h3>
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
            <summary>Read transcript</summary>
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
