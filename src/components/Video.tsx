import { useEffect, useRef, useState } from "react";
import { ArrowUpRight, Pause, Play } from "lucide-react";
import film from "../film.json";
import funding from "../funding.json";
import { DistrictGraph } from "./DistrictGraph";

const media = "./media/eeo-initiative.mp4";
const chapters = [
  { label: "Purpose", time: 0 },
  { label: "Funding foundation", time: 8 },
  { label: "First awards", time: 20 },
  { label: "Current cycle", time: 32 },
  { label: "Combined impact", time: 44 },
  { label: "Districts", time: 54 },
  { label: "Sustainable impact", time: 70 },
];

export function Video({ showChapters = false }: { showChapters?: boolean }) {
  const video = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(true);
  const [time, setTime] = useState(0);
  const [duration, setDuration] = useState(88);
  const [selected, setSelected] = useState(0);

  useEffect(() => {
    if (!video.current) return;
    video.current.muted = true;
    video.current.defaultMuted = true;
    void video.current.play().catch(() => setPlaying(false));
  }, []);

  function seek(next: number) {
    if (!video.current) return;
    video.current.currentTime = next;
    void video.current.play().then(() => setPlaying(true));
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

  const item = funding[selected];

  return (
    <section className="width film" id="initiative-story" aria-labelledby="story-title">
      <div className="section-heading">
        <div>
          <span className="eyebrow">EEO IBP · Funding to possibility</span>
          <h2 id="story-title">The initiative in motion.</h2>
        </div>
        <span className="silent-label">Silent experience</span>
      </div>

      <div className="cinema">
        <video
          ref={video}
          autoPlay
          loop
          muted
          playsInline
          preload="auto"
          disablePictureInPicture
          controlsList="nodownload noplaybackrate noremoteplayback"
          poster="./media/eeo-poster.jpg"
          aria-label="EEO IBP initiative funding story"
          onLoadedMetadata={(event) => setDuration(event.currentTarget.duration)}
          onTimeUpdate={(event) => setTime(event.currentTarget.currentTime)}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
        >
          <source src="./media/eeo-initiative.webm" type="video/webm" />
          <source src={media} type="video/mp4" />
          <track kind="captions" src="./media/eeo-initiative.en.vtt" srcLang="en" label="English" />
        </video>

        <div className="cinema-controls">
          <button onClick={togglePlayback} aria-label={playing ? "Pause video" : "Play video"}>
            {playing ? <Pause size={17} /> : <Play size={17} fill="currentColor" />}
          </button>
          <input
            aria-label="Video progress"
            type="range"
            min="0"
            max={duration}
            step="0.1"
            value={time}
            onChange={(event) => seek(Number(event.target.value))}
          />
          <span>{Math.floor(time / 60)}:{String(Math.floor(time % 60)).padStart(2, "0")}</span>
        </div>
      </div>

      <div className="story-chapters" aria-label="Explore the initiative story">
        {chapters.map((chapter, index) => (
          <button key={chapter.label} onClick={() => seek(chapter.time)}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            {chapter.label}
          </button>
        ))}
      </div>

      <DistrictGraph onEnterFilm={() => seek(54)} />

      <section className="funding-story" aria-labelledby="funding-title">
        <div className="funding-intro">
          <p className="eyebrow">Verified funding history</p>
          <h3 id="funding-title">From statewide foundation to district innovation.</h3>
          <p>Explore the published CCCCO funding record. Competitive award totals are separated from the original statewide apportionment to prevent double counting.</p>
        </div>
        <div className="funding-explorer">
          <div className="funding-tabs" role="tablist" aria-label="Funding milestones">
            {funding.map((entry, index) => (
              <button
                key={entry.id}
                role="tab"
                aria-selected={selected === index}
                onClick={() => {
                  setSelected(index);
                  seek(entry.time);
                }}
              >
                <span>{entry.year}</span>
                <strong>{entry.amount}</strong>
              </button>
            ))}
          </div>
          <div className="funding-detail" role="tabpanel" key={item.id}>
            <p>{item.note}</p>
            <h4>{item.label}</h4>
            <strong>{item.amount}</strong>
            <p>{item.detail}</p>
            <a href={item.source}>Official CCCCO source <ArrowUpRight size={15} /></a>
          </div>
        </div>
      </section>

      {showChapters && (
        <details className="transcript">
          <summary>Read transcript</summary>
          {film.map((scene) => (
            <p key={scene.title + scene.description}>
              <strong>{scene.title}</strong>{" "}
              {"transcript" in scene ? scene.transcript : scene.description}
            </p>
          ))}
        </details>
      )}
    </section>
  );
}
