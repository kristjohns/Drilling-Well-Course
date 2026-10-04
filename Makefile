# Drilling Well Course - build entry points.
#
#   make doctor        which tools are installed / missing
#   make venv          create .venv (bpy 4.5 LTS, numpy, matplotlib, Pillow, PyYAML)
#   make script        fit durations, lint, regenerate script/NARRATION.md, FLAGS.md, timeline.json   (Stage 2)
#   make audio         placeholder TTS narration fitted to the timeline + real sentence timings       (Stage 5)
#   make subs          SRT + ASS subtitles from the TTS timings
#   make qa            fast style check: two settled frames per beat, all chapters + contact sheets    (Stage 4)
#   make preview CH=1  full-chapter low-res render (854x480) into renders/preview
#   make render        full 1080p render of every chapter into renders/final (long: ~1.5-2 h on 4 cores)
#   make assemble      ffmpeg: chapters + narration + subtitles -> build/*.mp4 + .srt
#   make final         script -> audio -> subs -> render -> assemble
#
# Rendering uses Blender's Workbench engine through the pip `bpy` module, under xvfb (software GL, no GPU needed).

SHELL    := /bin/bash
PY       ?= python3
VENV     ?= .venv
VPY      := $(if $(wildcard $(VENV)/bin/python),$(VENV)/bin/python,$(PY))
XVFB     := xvfb-run -a -s "-screen 0 1920x1080x24"
RES      ?= 1920x1080
JOBS     ?= 3
# Workbench anti-aliasing samples: 5 is visually identical to 8 for this flat artwork and ~40 % faster
SAMPLES  ?= 5
CHAPTERS ?= 8 1 4 2 7 6 9 0 3 5 10
CH       ?= 1

.PHONY: help doctor venv script lint-script audio subs qa preview render assemble final clean

help:
	@sed -n '3,14p' Makefile

doctor:
	@echo "== binaries =="
	@for t in ffmpeg ffprobe xvfb-run pico2wave espeak-ng blender; do \
	  if p=$$(command -v $$t 2>/dev/null); then printf "  %-11s OK       %s\n" $$t "$$p"; \
	  else printf "  %-11s MISSING\n" $$t; fi; done
	@echo "== ffmpeg capabilities =="
	@for f in libx264 libass drawtext loudnorm xfade; do \
	  if { ffmpeg -hide_banner -encoders; ffmpeg -hide_banner -filters; ffmpeg -hide_banner -buildconf; } 2>/dev/null | grep -qw "$$f"; \
	  then printf "  %-11s OK\n" $$f; else printf "  %-11s MISSING\n" $$f; fi; done
	@echo "== python modules (using $(VPY)) =="
	@for m in bpy numpy matplotlib PIL yaml; do \
	  if $(VPY) -c "import $$m" 2>/dev/null; then printf "  %-11s OK\n" $$m; \
	  else printf "  %-11s MISSING\n" $$m; fi; done
	@echo "(blender binary is optional: the pip 'bpy' module renders headless; pico2wave: apt install libttspico-utils)"

venv:
	$(PY) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

script:
	$(PY) script/scriptlib.py build

lint-script:
	$(PY) script/scriptlib.py lint

audio: script
	$(VPY) audio/build_audio.py

subs: audio
	$(VPY) audio/subtitles.py

qa:
	@rm -rf renders/qa && mkdir -p renders/qa
	@printf "%s\n" 0 1 2 3 4 5 6 7 8 9 10 | xargs -P$(JOBS) -I{} sh -c '$(XVFB) $(VPY) scenes/render.py --chapter {} --res 854x480 --qa --out renders/qa > renders/qa/log_{}.txt 2>&1'
	@for n in 0 1 2 3 4 5 6 7 8 9 10; do $(VPY) scenes/contact_sheet.py --chapter $$n --renders renders/qa --frac 0.92 --cols 3 --thumb 560 > /dev/null; done
	@echo "contact sheets: renders/qa/sheet_chNN.png"

preview:
	$(XVFB) $(VPY) scenes/render.py --chapter $(CH) --res 854x480 --out renders/preview

render:
	@mkdir -p renders/final
	@printf "%s\n" $(CHAPTERS) | xargs -P$(JOBS) -I{} sh -c '$(XVFB) $(VPY) scenes/render.py --chapter {} --res $(RES) --samples $(SAMPLES) --out renders/final > renders/final/log_{}.txt 2>&1'
	@grep -h "rendered in" renders/final/log_*.txt

assemble:
	$(VPY) scenes/assemble.py

final: script audio subs render assemble

clean:
	rm -rf renders/preview renders/qa build
