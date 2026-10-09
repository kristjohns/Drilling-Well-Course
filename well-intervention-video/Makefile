# Into the Live Well - build entry points.
#
#   make doctor        which tools are installed / missing
#   make venv          create .venv (skia-python, kokoro-onnx, onnxruntime, numpy, Pillow, PyYAML)
#   make script        lint + regenerate script/NARRATION.md, FLAGS.md, timeline.json (budget timing)
#   make voice-model   download the Kokoro-82M voice (npm registry) and verify its SHA-256
#   make audio         neural narration + voice-first timeline (beats follow the speech)
#   make mix           music bed + sound design + narration -> audio/mix.wav
#   make qa            3 stills per beat for every chapter -> renders/qa/chNN/*.png
#   make preview CH=1  one chapter at 960x540 -> renders/preview/chNN.mp4
#   make render        every chapter at 1080p30 -> renders/video/chNN.mp4
#   make assemble      chapters + mix + subtitles -> build/*.mp4 + .srt (+ 720p parts for sharing)
#   make web           HLS web player page (needs make assemble first) -> build/web/
#   make final         script -> audio -> mix -> render -> assemble -> web
#
# `make script` rewrites timeline.json from the script budgets; `make audio` then re-times it from the real speech
# (cached sentences are not re-synthesised), so always run them in that order (`make audio` does it for you).

SHELL    := /bin/bash
PY       ?= python3
VENV     ?= .venv
VPY      := $(if $(wildcard $(VENV)/bin/python),$(VENV)/bin/python,$(PY))
JOBS     ?= 2
CHAPTERS ?= 5 4 2 3 7 1 6 8 0
CH       ?= 1

.PHONY: help doctor venv script lint-script voice-model audio mix qa preview render assemble web final clean

help:
	@sed -n '3,15p' Makefile

doctor:
	@echo "== binaries =="
	@for t in ffmpeg ffprobe; do \
	  if p=$$(command -v $$t 2>/dev/null); then printf "  %-11s OK       %s\n" $$t "$$p"; \
	  else printf "  %-11s MISSING\n" $$t; fi; done
	@echo "== ffmpeg capabilities =="
	@for f in libx264 libass loudnorm; do \
	  if { ffmpeg -hide_banner -encoders; ffmpeg -hide_banner -filters; ffmpeg -hide_banner -buildconf; } 2>/dev/null | grep -qw "$$f"; \
	  then printf "  %-11s OK\n" $$f; else printf "  %-11s MISSING\n" $$f; fi; done
	@echo "== python modules (using $(VPY)) =="
	@for m in skia kokoro_onnx onnxruntime numpy PIL yaml; do \
	  if $(VPY) -c "import $$m" 2>/dev/null; then printf "  %-11s OK\n" $$m; \
	  else printf "  %-11s MISSING\n" $$m; fi; done
	@echo "== fonts =="
	@for f in "Inter" "JetBrains Mono"; do if fc-list | grep -q "$$f"; then printf "  %-15s OK\n" "$$f"; else printf "  %-15s MISSING (apt install fonts-inter fonts-jetbrains-mono)\n" "$$f"; fi; done
	@test -f audio/models/kokoro-v1.0.fp32.onnx && echo "  voice model    OK" || echo "  voice model    MISSING (make voice-model)"

venv:
	$(PY) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

script:
	$(PY) script/scriptlib.py build

lint-script:
	$(PY) script/scriptlib.py lint

voice-model:
	$(VPY) audio/build_audio.py --fetch

audio: script
	$(VPY) audio/build_audio.py
	$(PY) script/scriptlib.py narration

mix:
	$(VPY) audio/mix.py

qa:
	@rm -rf renders/qa
	@printf "%s\n" 0 1 2 3 4 5 6 7 8 | xargs -P$(JOBS) -I{} sh -c '$(VPY) scenes/render.py --chapter {} --qa --fracs 0.3,0.62,0.93 --res 960x540 > /dev/null 2>&1'
	@echo "stills: renders/qa/chNN/*.png"

preview:
	$(VPY) scenes/render.py --chapter $(CH) --res 960x540 --out renders/preview/ch$$(printf %02d $(CH)).mp4

render:
	@mkdir -p renders/video renders/logs
	@printf "%s\n" $(CHAPTERS) | xargs -P$(JOBS) -I{} sh -c '$(VPY) scenes/render.py --chapter {} --threads 2 > renders/logs/render_{}.txt 2>&1 || echo "chapter {} FAILED (renders/logs/render_{}.txt)"'
	@grep -h "rendered" renders/logs/render_*.txt

assemble:
	$(VPY) scenes/assemble.py --small

web:
	$(VPY) scenes/package_web.py

final: script audio mix render assemble web

clean:
	rm -rf renders/preview renders/qa build
