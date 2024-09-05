from time import time

import cv2
import torch
import os
import sys

from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from pygame import mixer

from PIL import Image, ImageTk
from PIL import Image as Img


Image.CUBIC = Image.BICUBIC
if sys.version_info[0] == 3:
    import tkinter as tk
    from tkinter import *
else:
    import Tkinter as tk

from ttkbootstrap.constants import *

import ttkbootstrap as tb


global CONFIDENCE


def send_sound(object_detected=1):
    """Sends an email notification indicating the number of objects detected; defaults to 1 object."""
    mixer.init()
    model_path = resource_path("alert.mp3")
    mixer.music.load(model_path)
    mixer.music.play()
    print("alarm")


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class ObjectDetection:
    def __init__(self, capture_index):
        """Initializes an ObjectDetection instance with a given camera index."""
        self.capture_index = capture_index
        self.sond_send = False

        # model information
        model_path = resource_path("best.pt")
        self.model = YOLO(model_path)

        # visual information
        self.annotator = None
        self.start_time = 0
        self.end_time = 0

        # device information
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.logo_path = resource_path("logo-final-com-nome-250x250.png")
        self.ico_path = resource_path("icon-48x48.bmp")

        self.size_y = 1920
        self.size_x = 1080

        self.logo_position_x = 0.2
        self.logo_position_y = 0.1

        self.compright_position_y = 0.86
        self.compright_position_x = 0.23

        self.button_position_x = 0.36
        self.button_position_y = 0.55
        self.button_width = 13

        self.metter_position_x = 0.25
        self.metter_position_y = 0.4

    def predict(self, im0):
        """Run prediction using a YOLO model for the input image `im0`."""
        global CONFIDENCE
        results = self.model(im0, conf=float(CONFIDENCE / 100))
        return results

    def display_fps(self, im0):
        """Displays the FPS on an image `im0` by calculating and overlaying as white text on a black rectangle."""
        self.end_time = time()
        fps = 1 / round(self.end_time - self.start_time, 2)
        text = f"FPS: {int(fps)}"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
        gap = 10
        cv2.rectangle(
            im0,
            (20 - gap, 70 - text_size[1] - gap),
            (20 + text_size[0] + gap, 70 + gap),
            (255, 255, 255),
            -1,
        )
        cv2.putText(im0, text, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

    def plot_bboxes(self, results, im0):
        """Plots bounding boxes on an image given detection results; returns annotated image and class IDs."""
        class_ids = []
        self.annotator = Annotator(im0, 3, results[0].names)
        boxes = results[0].boxes.xyxy.cpu()
        clss = results[0].boxes.cls.cpu().tolist()
        names = results[0].names
        for box, cls in zip(boxes, clss):
            if cls in [5, 0]:
                class_ids.append(cls)
                self.annotator.box_label(
                    box, label=names[int(cls)], color=colors(int(cls), True)
                )
        return im0, class_ids

    def __call__(self):
        root = tb.Window(themename="solar")
        root.title("Sentinela")
        root.iconbitmap(self.ico_path)
        root.bind("<Escape>", lambda e: root.quit())
        # root.attributes("-fullscreen", True)
        root.geometry(f"{self.size_y}x{self.size_x}")

        def start():
            """Run object detection on video frames from a camera stream, plotting and showing the results."""
            cap = cv2.VideoCapture(self.capture_index)
            # resolve problem the webcam logitech bellow
            # cap = cv2.VideoCapture(self.capture_index, cv2.CAP_DSHOW)
            assert cap.isOpened()
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            global frame_count
            frame_count = 0

            # ---------------------------
            # Init created button Stop
            def stop():
                cap.release()
                frame_inference.place_forget()
                button_stop.place_forget()
                button_start = tb.Button(
                    frame_config,
                    text="Start",
                    bootstyle="primary",
                    width=self.button_width,
                    command=start,
                )
                button_start.place(
                    relx=self.button_position_x, rely=self.button_position_y
                )

            # End created button Stop
            # ---------------------------

            # Drop button Start
            button_start.place_forget()

            # ---------------------------
            # Init create Button stop
            button_stop = tb.Button(
                frame_config,
                text="Stop",
                bootstyle="primary",
                width=self.button_width,
                command=stop,
            )
            button_stop.place(relx=self.button_position_x, rely=self.button_position_y)
            # End create Button stop
            # ---------------------------

            global CONFIDENCE
            CONFIDENCE = metter_confidence.amountusedvar.get()

            # =========================
            # init Frame inference
            frame_inference = tb.Frame(root)
            frame_inference.place(
                relx=0.6, rely=0.5, width=1020, height=1080, anchor=tk.CENTER
            )
            lmain = tb.Label(frame_inference)
            lmain.place(x=5, y=5, width=1510, height=1070)

            def show_frame():
                global frame_count
                self.start_time = time()
                ret, im0 = cap.read()
                assert ret
                results = self.predict(im0)
                im0, class_ids = self.plot_bboxes(results, im0)

                if (5 in class_ids) and (0 in class_ids):
                    if not self.sond_send:
                        send_sound(len(class_ids))
                        self.sond_send = True
                else:
                    self.sond_send = False

                self.display_fps(im0)
                stretch_near = cv2.resize(
                    im0, (1510, 1070), interpolation=cv2.INTER_LINEAR
                )
                frame_rgb = cv2.cvtColor(stretch_near, cv2.COLOR_BGR2RGB)
                img = Img.fromarray(frame_rgb)
                frame_tk = ImageTk.PhotoImage(img)
                lmain.imgtk = frame_tk
                lmain.configure(image=frame_tk)

                lmain.after(10, show_frame)
                frame_count += 1

            show_frame()

        # ---------------------------
        # init Frame configuration
        frame_config = tb.Labelframe(root, bootstyle="primary")
        frame_config.place(relx=0.1, rely=0.5, width=400, height=1200, anchor=tk.CENTER)

        metter_confidence = tb.Meter(
            frame_config,
            bootstyle="success",
            subtext="Confidence",
            interactive=True,
            textright="%",
            metertype="semi",  # full
            stripethickness=5,
            metersize=300,
            subtextstyle="light",
        )

        metter_confidence.place(
            relx=self.metter_position_x, rely=self.metter_position_y
        )

        label_logo = tb.Label(frame_config, bootstyle="primary")
        label_logo.place(relx=self.logo_position_x, rely=self.logo_position_y)
        company_logo = ImageTk.PhotoImage(file=self.logo_path)
        label_logo.imgtk = company_logo
        label_logo.configure(image=company_logo)

        # Create Button
        button_start = tb.Button(
            frame_config,
            text="Start",
            bootstyle="primary",
            width=self.button_width,
            command=start,
        )
        button_start.place(relx=self.button_position_x, rely=self.button_position_y)

        label_compright = tb.Label(
            frame_config,
            bootstyle="dark inverse",
            text="© 2024 NeuAI U.S., LLC. All Rights",
        )
        label_compright.place(
            relx=self.compright_position_x, rely=self.compright_position_y
        )
        # End Frame configuration
        # ---------------------------

        root.mainloop()


if __name__ == "__main__":
    detector = ObjectDetection(capture_index=0)
    detector()
