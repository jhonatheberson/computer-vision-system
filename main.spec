# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import sys
import os
import cv2
import torch
import ultralytics
import pygame
from PyInstaller.utils.hooks import collect_data_files
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from pygame import mixer
from PIL import Image, ImageTk
from PIL import Image as Img
import tkinter as tk
from ttkbootstrap.constants import *
import ttkbootstrap as tb

datas = []
datas += collect_data_files('ultralytics')
datas += collect_data_files('pygame')
datas += collect_data_files('PIL')
datas += collect_data_files('tkinter')
datas += collect_data_files('ttkbootstrap')
datas +=  [('best.pt', '.')]
datas +=  [('alert.mp3', '.')]
datas +=  [('logo_crop.png', '.')]


block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['ultralytics', 'pygame', 'ultralytics.yolo', 'PIL', 'tkinter', 'ttkbootstrap'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
