# Drilling Well Course - build entry points.
# Stage 1 only provides environment checks; later stages add preview / render /
# audio / subs / assemble targets.

SHELL := /bin/bash
PY    ?= python3
VENV  ?= .venv
VPY   := $(if $(wildcard $(VENV)/bin/python),$(VENV)/bin/python,$(PY))

.PHONY: help doctor venv

help:
	@echo "make doctor  report which required tools are installed / missing"
	@echo "make venv    create $(VENV) with bpy 4.5 LTS + plotting deps (~1 GB download)"

doctor:
	@echo "== binaries =="
	@for t in ffmpeg ffprobe xvfb-run espeak-ng blender; do \
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
	@echo "(blender binary is optional: the pip 'bpy' module renders headless)"

venv:
	$(PY) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
