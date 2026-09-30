"""Paths and global settings for the video build."""
import os

SRC = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.dirname(SRC)
ROOT = os.path.dirname(VIDEO)
BUILD = os.environ.get('WELL_BUILD', os.path.join(VIDEO, 'build'))
AUDIO_DIR = os.path.join(BUILD, 'audio')
FRAMES = os.path.join(BUILD, 'frames')      # blender renders per scene
ANCHORS = os.path.join(BUILD, 'anchors')    # projected label anchors per scene
SEGMENTS = os.path.join(BUILD, 'segments')  # composited per-scene video
TIMELINE = os.path.join(BUILD, 'timeline.json')
FONTS = os.path.join(VIDEO, 'assets', 'fonts')
OUTPUT = os.path.join(VIDEO, 'output')

FPS = 24
W, H = 1920, 1080
HANDLE = 12  # extra frames rendered past each scene end for cross-fades

# Text-to-speech (Kokoro-82M, Apache-2.0, run locally via onnxruntime)
MODELS = os.environ.get('KOKORO_DIR', '/tmp/claude-0/models')
KOKORO_MODEL = os.path.join(MODELS, 'kokoro-v1.0.onnx')
KOKORO_VOICES = os.path.join(MODELS, 'voices-v1.0.bin')
VOICE = os.environ.get('WELL_VOICE', 'af_heart')
SPEED = float(os.environ.get('WELL_SPEED', '0.9'))
