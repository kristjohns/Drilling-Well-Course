#!/usr/bin/env python3
"""Package the finished film for a web player page: 1080p HLS (fMP4 segments under 15 MB each), WebVTT subtitles,
a poster frame and the player page itself.

    python scenes/package_web.py            # needs build/<name>_1080p_nosubs.mp4 (scenes/assemble.py) -> build/web/

The page plays the segments with hls.js (or natively on Safari), has a chapter menu, switchable subtitles and a
speed control. Publish build/web/index.html with every other file in build/web/ beside it."""
from __future__ import annotations
import argparse
import glob
import html
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NAME = "into_the_live_well"
sys.path.insert(0, os.path.join(ROOT, "audio"))
import subtitles  # noqa: E402


def run(cmd):
    print("+", " ".join(cmd[:6]), "...", flush=True)
    subprocess.run(cmd, check=True)


def vtt_time(t):
    t = max(t, 0.0)
    h, rem = divmod(int(t), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}.{int(round((t - int(t)) * 1000)):03d}"


def clock(t):
    m, s = divmod(int(round(t)), 60)
    return f"{m}:{s:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(ROOT, "build", f"{NAME}_1080p_nosubs.mp4"))
    ap.add_argument("--out", default=os.path.join(ROOT, "build", "web"))
    ap.add_argument("--crf", type=int, default=22)
    ap.add_argument("--seg", type=float, default=6.0)
    ap.add_argument("--page-only", action="store_true", help="rewrite index.html from an existing encode")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tl = json.load(open(os.path.join(ROOT, "script", "timeline.json")))
    total = tl["total"]
    if not a.page_only:
        for f in glob.glob(os.path.join(a.out, "seg_*.mp4")) + glob.glob(os.path.join(a.out, "init.mp4")):
            os.remove(f)
        fps = 30
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.src,
             "-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf), "-tune", "animation", "-pix_fmt", "yuv420p",
             "-profile:v", "high", "-level", "4.1", "-g", str(int(a.seg * fps)), "-keyint_min", str(int(a.seg * fps)),
             "-sc_threshold", "0", "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
             "-f", "hls", "-hls_time", str(a.seg), "-hls_playlist_type", "vod", "-hls_segment_type", "fmp4",
             "-hls_fmp4_init_filename", "init.mp4", "-hls_segment_filename", os.path.join(a.out, "seg_%03d.mp4"),
             os.path.join(a.out, "film.m3u8")])
        # poster: the film's title card at the end of the cold open
        b02 = [b for b in tl["chapters"][0]["beats"] if b["id"] == "0.02"][0]
        t_title = b02["start"] + 0.93 * b02["dur"]
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t_title:.2f}", "-i", a.src, "-frames:v", "1",
             "-vf", "scale=1280:720:flags=lanczos", "-q:v", "3", os.path.join(a.out, "poster.jpg")])
    # subtitles
    cues = json.load(open(os.path.join(ROOT, "audio", "cues.json")))
    lines = ["WEBVTT", ""]
    for i, (s, e, txt) in enumerate(subtitles.expand(cues, 0.0, total)):
        lines += [str(i + 1), f"{vtt_time(s)} --> {vtt_time(e)}", txt, ""]
    vtt = "\n".join(lines)
    open(os.path.join(a.out, "subtitles.vtt"), "w").write(vtt)       # kept for reference; the page embeds it
    # page
    playlist = open(os.path.join(a.out, "film.m3u8")).read()
    segs = sorted(glob.glob(os.path.join(a.out, "seg_*.mp4")))
    big = max(os.path.getsize(p) for p in segs) / 2**20
    size = sum(os.path.getsize(p) for p in segs + [os.path.join(a.out, "init.mp4")]) / 2**20
    chapters = [{"n": c["num"], "title": c["title"], "t": round(c["start"], 2)} for c in tl["chapters"]]
    page = TEMPLATE
    for k, v in {"__PLAYLIST__": json.dumps(playlist), "__CHAPTERS__": json.dumps(chapters), "__VTT__": json.dumps(vtt),
                 "__RUNTIME__": html.escape(f"{int(total // 60)} min"),
                 "__CHAPTER_LIST__": "\n".join(
                     f'<li><button type="button" class="ch" data-t="{c["t"]}" data-n="{c["n"]}">'
                     f'<span class="num">{c["n"]:02d}</span><span class="ttl">{html.escape(c["title"])}</span>'
                     f'<span class="tc">{clock(c["t"])}</span></button></li>' for c in chapters)}.items():
        page = page.replace(k, v)
    open(os.path.join(a.out, "index.html"), "w").write(page)
    print(f"web: {len(segs)} segments, {size:.0f} MiB (largest {big:.1f} MiB), {len(cues)} cues -> {a.out}")


TEMPLATE = r"""<title>Into the Live Well</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Screening room: the film first, then a chapter rail (operable) beside the viewing notes; one column on phones. */
:root {
  --bg: #0a111c; --surface: #111a2a; --line: #233350; --fg: #e8eef6; --muted: #97a6c0;
  --accent: #4cc9f0; --amber: #ffb703; --screen: #05080f;
  --display: "Barlow Condensed", "Arial Narrow", "Helvetica Neue", Arial, sans-serif;
  --body: "IBM Plex Sans", "Segoe UI", Helvetica, Arial, sans-serif;
  --mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  /* the film's own colour key */
  --k-oil: #4caf50; --k-gas: #e5446d; --k-wire: #d6dde8; --k-copper: #d98c5f; --k-coil: #4cc9f0; --k-snub: #ffd166;
  --k-scale: #e8e4d8; --k-ok: #2a9d8f;
  color-scheme: dark;
}
@media (prefers-color-scheme: light) {
  :root:not([data-theme="dark"]) { --bg: #eef2f7; --surface: #ffffff; --line: #cdd6e4; --fg: #0e1828; --muted: #4c5b75;
    --accent: #0a7aa3; --amber: #a86400; --screen: #05080f; color-scheme: light; }
}
:root[data-theme="light"] { --bg: #eef2f7; --surface: #ffffff; --line: #cdd6e4; --fg: #0e1828; --muted: #4c5b75;
  --accent: #0a7aa3; --amber: #a86400; --screen: #05080f; color-scheme: light; }
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--fg); font: 400 16px/1.55 var(--body); margin: 0; }
.wrap { max-width: 1180px; margin: 0 auto; padding-inline: 16px; padding-block: 28px 56px; display: grid; gap: 22px; }
.masthead { display: grid; gap: 6px; }
.eyebrow { font: 500 12px/1.4 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--accent); margin: 0; }
h1 { font: 700 clamp(40px, 7vw, 76px)/0.95 var(--display); letter-spacing: .01em; text-transform: uppercase; margin: 0;
  text-wrap: balance; }
.dek { color: var(--muted); max-width: 62ch; margin: 4px 0 0; }
.frame { position: relative; background: var(--screen); border-radius: 6px; overflow: hidden; aspect-ratio: 16 / 9;
  max-width: 100%; box-shadow: 0 18px 50px -24px rgba(0, 0, 0, .7); }
video { display: block; width: 100%; height: 100%; background: var(--screen); }
video::cue { font-family: var(--body); font-size: 0.9em; background: rgba(5, 8, 15, .72); color: #fff; }
.err { position: absolute; inset: auto 12px 12px 12px; background: rgba(5, 8, 15, .9); color: #fff; padding: 10px 12px;
  border-radius: 4px; font-size: 14px; }
.bar { display: flex; flex-wrap: wrap; align-items: center; gap: 10px 16px; }
.now { flex: 1 1 260px; min-width: 0; font: 600 15px/1.3 var(--body); }
.now .label { font: 500 11px/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted);
  display: block; margin-bottom: 4px; }
.controls { display: flex; flex-wrap: wrap; gap: 8px; }
.btn { font: 500 13px/1 var(--body); color: var(--fg); background: var(--surface); border: 1px solid var(--line);
  border-radius: 999px; padding: 9px 14px; cursor: pointer; }
.btn[aria-pressed="true"] { border-color: var(--accent); color: var(--accent); }
.btn:focus-visible, .ch:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.below { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 28px; align-items: start; }
@media (max-width: 820px) { .below { grid-template-columns: minmax(0, 1fr); } }
h2 { font: 700 22px/1.1 var(--display); letter-spacing: .03em; text-transform: uppercase; margin: 0 0 10px; }
.chapters ol { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--line); }
.ch { width: 100%; display: grid; grid-template-columns: 2.6em minmax(0, 1fr) auto; gap: 12px; align-items: baseline;
  padding: 11px 6px; background: none; border: 0; border-bottom: 1px solid var(--line); color: var(--fg);
  font: 400 15px/1.35 var(--body); text-align: left; cursor: pointer; }
.ch:hover .ttl { color: var(--accent); }
.ch .num, .ch .tc { font: 500 13px/1.35 var(--mono); color: var(--muted); font-variant-numeric: tabular-nums; }
.ch[aria-current="true"] { box-shadow: inset 3px 0 0 var(--amber); }
.ch[aria-current="true"] .num, .ch[aria-current="true"] .ttl { color: var(--amber); }
.notes { display: grid; gap: 22px; min-width: 0; }
.notes p { margin: 0; color: var(--muted); max-width: 62ch; }
.notes p strong { color: var(--fg); font-weight: 600; }
.badge { display: inline-block; font: 600 11px/1 var(--body); letter-spacing: .04em; color: #fff; background: #d62839;
  border-radius: 999px; padding: 4px 8px; vertical-align: 1px; }
.key { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px 14px; margin: 0; padding: 0;
  list-style: none; }
.key li { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.key i { width: 22px; height: 10px; border-radius: 2px; flex: none; }
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; } }
</style>

<div class="wrap">
  <header class="masthead">
    <p class="eyebrow">A producing well, Norwegian Continental Shelf &middot; 9 chapters &middot; __RUNTIME__</p>
    <h1>Into the Live Well</h1>
    <p class="dek">Why we go back into a producing well, and how: wireline, coiled tubing, snubbing, rigs and vessels, explained
      for a mechanical engineer who is new to wells. Every term is defined the first time it is spoken.</p>
  </header>

  <section aria-label="Film">
    <div class="frame">
      <video id="film" controls playsinline preload="metadata" poster="poster.jpg">
      </video>
      <p class="err" id="err" hidden>This browser cannot play the stream here. Try a current Chrome, Edge, Firefox or Safari.</p>
    </div>
  </section>

  <div class="bar">
    <p class="now"><span class="label">Now playing</span><span id="now">00 &middot; Cold open</span></p>
    <div class="controls">
      <button class="btn" id="cc" type="button" aria-pressed="true">Subtitles on</button>
      <button class="btn rate" type="button" data-rate="1" aria-pressed="true">1&times;</button>
      <button class="btn rate" type="button" data-rate="1.25" aria-pressed="false">1.25&times;</button>
      <button class="btn rate" type="button" data-rate="1.5" aria-pressed="false">1.5&times;</button>
    </div>
  </div>

  <main class="below">
    <nav class="chapters" aria-label="Chapters">
      <h2>Chapters</h2>
      <ol>
__CHAPTER_LIST__
      </ol>
    </nav>
    <aside class="notes">
      <div>
        <h2>Read this first</h2>
        <p><strong>An illustrative composite well: invented numbers, real physics.</strong> Material specific to Norway carries
          a <span class="badge">NORWAY / NORSOK-SPECIFIC</span> badge on screen. The Norwegian regulations and NORSOK D-010 were
          not available in their primary form: check any requirement against them before relying on it. Simplifications are
          badged <strong>SIMPLIFIED</strong>; <code>script/FLAGS.md</code> lists every flagged claim.</p>
      </div>
      <div>
        <h2>Colour key</h2>
        <ul class="key">
          <li><i style="background: var(--k-oil)"></i>Oil</li>
          <li><i style="background: var(--k-gas)"></i>Gas, failed or faulty parts</li>
          <li><i style="background: var(--k-wire)"></i>Slickline and braided line</li>
          <li><i style="background: var(--k-copper)"></i>Electric line (conductor)</li>
          <li><i style="background: var(--k-coil)"></i>Coiled tubing</li>
          <li><i style="background: var(--k-snub)"></i>Snubbing, warnings</li>
          <li><i style="background: var(--k-scale)"></i>Scale</li>
          <li><i style="background: var(--k-ok)"></i>Verified, safe</li>
        </ul>
      </div>
      <div>
        <h2>How it was made</h2>
        <p>One well model drives every number on screen. Narration by the Kokoro-82M neural voice, animation drawn by a 2-D
          motion-graphics engine, music and sound synthesised in code. Built on the same pipeline as <em>The Hole That Fights Back</em>.</p>
      </div>
    </aside>
  </main>
</div>

<script src="https://cdn.jsdelivr.net/npm/hls.js@1.5.13/dist/hls.min.js"></script>
<script>
(function () {
  var PLAYLIST = __PLAYLIST__;
  var VTT = __VTT__;
  var CHAPTERS = __CHAPTERS__;
  var video = document.getElementById("film");
  // subtitles: embedded WebVTT, attached as a track through a blob URL (the host serves no .vtt files)
  var track = document.createElement("track");
  track.kind = "subtitles"; track.srclang = "en"; track.label = "English"; track.default = true;
  track.src = URL.createObjectURL(new Blob([VTT], { type: "text/vtt" }));
  video.appendChild(track);
  var abs = function (name) { return new URL(name, location.href).href; };
  var text = PLAYLIST.replace(/URI="([^"]+)"/g, function (_, n) { return 'URI="' + abs(n) + '"'; })
                     .replace(/^(seg_\d+\.mp4)$/gm, function (n) { return abs(n); });
  if (window.Hls && window.Hls.isSupported()) {
    var hls = new window.Hls({ maxBufferLength: 40 });
    hls.loadSource(URL.createObjectURL(new Blob([text], { type: "application/vnd.apple.mpegurl" })));
    hls.attachMedia(video);
    hls.on(window.Hls.Events.ERROR, function (_, d) { if (d && d.fatal) document.getElementById("err").hidden = false; });
  } else {
    document.getElementById("err").hidden = false;
  }

  // subtitles toggle (remembered per viewer when storage is available)
  var cc = document.getElementById("cc");
  var setCC = function (on) {
    for (var i = 0; i < video.textTracks.length; i++) video.textTracks[i].mode = on ? "showing" : "hidden";
    track.track && (track.track.mode = on ? "showing" : "hidden");
    cc.setAttribute("aria-pressed", on ? "true" : "false");
    cc.textContent = on ? "Subtitles on" : "Subtitles off";
    try { localStorage.setItem("itlw-cc", on ? "1" : "0"); } catch (e) {}
  };
  var ccOn = true;
  try { ccOn = localStorage.getItem("itlw-cc") !== "0"; } catch (e) {}
  setCC(ccOn);
  video.textTracks.addEventListener && video.textTracks.addEventListener("addtrack", function () { setCC(cc.getAttribute("aria-pressed") === "true"); });
  cc.addEventListener("click", function () { setCC(cc.getAttribute("aria-pressed") !== "true"); });

  // playback speed
  var rates = document.querySelectorAll(".rate");
  rates.forEach(function (b) {
    b.addEventListener("click", function () {
      video.playbackRate = parseFloat(b.dataset.rate);
      rates.forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); });
    });
  });

  // chapters: seek, highlight the current one, deep links (#ch7)
  var buttons = document.querySelectorAll(".ch");
  var now = document.getElementById("now");
  var seek = function (t) { video.currentTime = t + 0.05; var p = video.play(); if (p && p.catch) p.catch(function () {}); };
  buttons.forEach(function (b) { b.addEventListener("click", function () { seek(parseFloat(b.dataset.t)); }); });
  var current = -1;
  var mark = function () {
    var t = video.currentTime, k = 0;
    for (var i = 0; i < CHAPTERS.length; i++) if (t >= CHAPTERS[i].t - 0.01) k = i;
    if (k === current) return;
    current = k;
    buttons.forEach(function (b, i) { b.setAttribute("aria-current", i === k ? "true" : "false"); });
    var c = CHAPTERS[k];
    now.textContent = String(c.n).padStart(2, "0") + " · " + c.title;
  };
  video.addEventListener("timeupdate", mark);
  mark();
  var m = /^#ch(\d+)$/.exec(location.hash || "");
  if (m) {
    var c = CHAPTERS.filter(function (x) { return x.n === parseInt(m[1], 10); })[0];
    if (c) video.addEventListener("loadedmetadata", function () { video.currentTime = c.t + 0.05; }, { once: true });
  }
})();
</script>
"""

if __name__ == "__main__":
    main()
