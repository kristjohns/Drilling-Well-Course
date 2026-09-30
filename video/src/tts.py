"""Generate the voice-over with Kokoro TTS and build the beat timeline.

Outputs (in build/):
  audio/<beat>.wav     trimmed clip per beat (24 kHz mono)
  narration.wav        all clips placed on the master timeline
  timeline.json        scene and beat timings in seconds and frames
"""
import json
import os
import sys

import numpy as np
import soundfile as sf

import config as C
import script

SR = 24000

# extra hold time (s) after specific beats, to let visuals breathe
EXTRA_AFTER = {
    'hook4': 0.6, 'hook6': 3.0,
    'set1': 0.3, 'set3': 0.5, 'set6': 0.8,
    'pr1': 0.4, 'pr3': 0.6, 'pr5': 0.8, 'pr6': 0.6, 'pr8': 2.0,
    'cs1': 0.8, 'cs3': 0.6, 'cs4': 0.4, 'cs5': 1.6, 'cs6': 1.2,
    'ba2': 0.4, 'ba3': 1.6,
    'rg1': 0.6, 'rg4': 1.2,
    'th2': 0.8, 'th3': 0.6, 'th4': 1.2,
    'bp2': 0.4, 'bp3': 0.6, 'bp4': 1.2, 'bp5': 1.0,
    'mc1': 0.3, 'mc4': 0.8, 'mc5': 0.8, 'mc6': 0.6, 'mc7': 1.5,
    'ce1': 0.6, 'ce2': 0.6, 'ce3': 0.8, 'ce4': 1.0,
    'wc1': 0.8, 'wc2': 1.0, 'wc3': 1.0,
    'co1': 0.4, 'co2': 0.6, 'co3': 1.2, 'co5': 0.8, 'co6': 1.0, 'co7': 0.8, 'co8': 0.8, 'co9': 1.6,
    'pd1': 0.6, 'pd2': 0.6, 'pd3': 1.0,
    'pa2': 0.8, 'pa3': 0.8, 'pa4': 0.8, 'pa5': 0.6, 'pa6': 1.0, 'pa7': 1.0, 'pa8': 0.8,
    'pa9': 0.8, 'pa10': 1.2, 'pa11': 2.5,
    'ou1': 0.5, 'ou2': 0.6, 'ou3': 0.6, 'ou4': 0.6, 'ou5': 0.8, 'ou6': 3.5,
}
# lead-in (s) before the first beat of each scene
LEAD_IN = {'s01_intro': 3.0, 's06_rig': 1.0, 's13_production': 0.8, 's14_pa': 0.8}
GAP = 0.42          # pause between beats
SCENE_TAIL = 0.5    # extra pause at the end of each scene
DEFAULT_LEAD = 0.6


def trim(x, thresh=0.004, pad=0.04):
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(pad * SR))
    b = min(len(x), idx[-1] + int(pad * SR))
    return x[a:b]


def main(force=False):
    from kokoro_onnx import Kokoro
    os.makedirs(C.AUDIO_DIR, exist_ok=True)
    k = None
    timeline = {'fps': C.FPS, 'scenes': []}
    t = 0.0
    clips = []
    for sc in script.SCENES:
        s_start = t
        t += LEAD_IN.get(sc['id'], DEFAULT_LEAD)
        beats = []
        for bid, say, text in script.beats(sc):
            path = os.path.join(C.AUDIO_DIR, bid + '.wav')
            meta = path + '.txt'
            cached = (os.path.exists(path) and os.path.exists(meta)
                      and open(meta).read() == f'{C.VOICE}|{C.SPEED}|{say}')
            if force or not cached:
                if k is None:
                    k = Kokoro(C.KOKORO_MODEL, C.KOKORO_VOICES)
                samples, sr = k.create(say, voice=C.VOICE, speed=C.SPEED, lang='en-us')
                assert sr == SR
                samples = trim(np.asarray(samples, dtype=np.float32))
                sf.write(path, samples, SR)
                open(meta, 'w').write(f'{C.VOICE}|{C.SPEED}|{say}')
                print('tts', bid, round(len(samples) / SR, 2), 's', flush=True)
            x, _ = sf.read(path, dtype='float32')
            dur = len(x) / SR
            beats.append(dict(id=bid, start=round(t, 3), end=round(t + dur, 3),
                              text=script.display_text(text)))
            clips.append((t, x))
            t += dur + GAP + EXTRA_AFTER.get(bid, 0.0)
        t += SCENE_TAIL
        # snap scene end to a whole frame
        f0 = int(round(s_start * C.FPS))
        f1 = int(round(t * C.FPS))
        t = f1 / C.FPS
        timeline['scenes'].append(dict(id=sc['id'], title=sc['title'], start=round(s_start, 3),
                                       end=round(t, 3), frame_start=f0, frame_end=f1,
                                       beats=beats))
    total = t
    timeline['duration'] = round(total, 3)
    audio = np.zeros(int(total * SR) + SR, dtype=np.float32)
    for st, x in clips:
        i = int(st * SR)
        audio[i:i + len(x)] += x
    sf.write(os.path.join(C.BUILD, 'narration.wav'), audio, SR)
    with open(C.TIMELINE, 'w') as fh:
        json.dump(timeline, fh, indent=1)
    words = sum(len(b[1].split()) for s in script.SCENES for b in s['beats'])
    print(f'total {total:.1f}s = {total/60:.2f} min, {words} words, '
          f'{words/(total/60):.0f} wpm effective')
    for s in timeline['scenes']:
        print(f"  {s['id']:18s} {s['start']:7.1f} -> {s['end']:7.1f}  ({s['end']-s['start']:5.1f}s)")


if __name__ == '__main__':
    main(force='--force' in sys.argv)
