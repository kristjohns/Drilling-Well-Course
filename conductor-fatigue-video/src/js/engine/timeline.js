// Access to the voice-timed timeline (src/data/timeline.json, written by tools/tts.py).
export class Timeline {
  constructor(j) {
    this.j = j;
    this.duration = j.duration;
    this.beats = {};
    this.chapters = {};
    for (const c of j.chapters) {
      this.chapters[c.no] = c;
      for (const b of c.beats) { b.chapter = c; this.beats[b.id] = b; }
    }
  }
  ch(no) { return this.chapters[no]; }
  b(id) {
    const b = this.beats[id];
    if (!b) throw new Error('unknown beat ' + id);
    return b;
  }
  // time of a {cue}; falls back to the beat start (with a console warning) so a missing cue never breaks a build
  c(id, name) {
    const b = this.b(id);
    if (b.cues[name] === undefined) { console.warn(`missing cue ${id}:${name}`); return b.start + 0.6; }
    return b.cues[name];
  }
  s(id, i = 0) { const b = this.b(id); return (b.sentences[i] || b.sentences[b.sentences.length - 1]).start; }
  se(id, i = 0) { const b = this.b(id); return (b.sentences[i] || b.sentences[b.sentences.length - 1]).end; }
  // first time a word (case-insensitive, punctuation ignored) is spoken in a beat, nth occurrence
  w(id, word, nth = 0) {
    const b = this.b(id);
    const want = word.toLowerCase();
    let k = 0;
    for (const s of b.sentences) for (const w of s.words) {
      if (w.w.toLowerCase().replace(/[^a-z0-9'-]/g, '') === want) { if (k === nth) return w.s; k++; }
    }
    console.warn(`missing word ${id}:${word}`);
    return b.start + 0.6;
  }
  start(id) { return this.b(id).start; }
  end(id) { return this.b(id).end; }
}
