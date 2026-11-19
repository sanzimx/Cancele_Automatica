"""Aquisição e serial em threads. Nunca inclui senha/URL completa em mensagens."""
import queue
import threading
import time
from urllib.parse import quote
import os
os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", "rtsp_transport;tcp")
import cv2

def camera_url(host, user, password, channel="101"):
    if not host or any(c in host for c in "/@ \n"):
        raise ValueError("Informe apenas IP ou nome da câmera, sem protocolo.")
    if not channel.isdigit():
        raise ValueError("Canal RTSP deve ser numérico.")
    return (f"rtsp://{quote(user,safe='')}:{quote(password,safe='')}@"
            f"{host}:554/Streaming/Channels/{channel}")

class Camera:
    def __init__(self, source, events):
        self.source, self.events = source, events
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.frame, self.received = None, 0
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        while not self.stop.is_set():
            cap = None
            try:
                if isinstance(self.source, int):
                    cap = cv2.VideoCapture(self.source)
                else:
                    cap = cv2.VideoCapture(self.source, cv2.CAP_FFMPEG, [
                        cv2.CAP_PROP_OPEN_TIMEOUT_MSEC,5000,
                        cv2.CAP_PROP_READ_TIMEOUT_MSEC,5000])
                if not cap.isOpened():
                    raise RuntimeError()
                self.events.put(("notice","Câmera conectada."))
                while not self.stop.is_set():
                    ok, frame = cap.read()
                    if not ok:
                        break
                    with self.lock:
                        self.frame, self.received = frame, time.monotonic()
            except Exception:
                self.events.put(("notice","Câmera indisponível. Confira rede, senha e canal."))
            finally:
                if cap is not None:
                    cap.release()
                with self.lock:
                    self.frame, self.received = None, 0
            self.stop.wait(2)

    def snapshot(self, timeout=2, after=0):
        end = time.monotonic()+timeout
        while time.monotonic() < end:
            with self.lock:
                if (self.frame is not None and self.received >= after
                        and time.monotonic()-self.received <= 2):
                    return self.frame.copy()
            self.stop.wait(.04)
        raise RuntimeError("Nenhum quadro recente da câmera.")

    def close(self):
        self.stop.set()

class SerialLink:
    def __init__(self, port, events):
        self.port, self.events = port, events
        self.stop = threading.Event()
        self.outgoing = queue.Queue()
        self.connected = False
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        device = None
        try:
            import serial
            device = serial.Serial(self.port,115200,timeout=.1,write_timeout=1)
            self.stop.wait(2)
            device.reset_input_buffer()
            self.connected = True
            self.events.put(("notice","Serial conectada. Use o firmware novo deste pacote."))
            while not self.stop.is_set():
                try:
                    command = self.outgoing.get_nowait()
                    device.write((command+"\n").encode("ascii"))
                except queue.Empty:
                    pass
                raw = device.readline()
                if raw:
                    message = raw.decode("ascii",errors="ignore").strip()
                    self.events.put(("serial",(self,message)))
        except Exception:
            self.events.put(("notice","Serial desconectada ou indisponível. Modo de análise continua disponível."))
        finally:
            self.connected = False
            if device:
                device.close()

    def send(self, command):
        if not self.connected:
            raise RuntimeError("ESP32 não está conectado.")
        self.outgoing.put(command)

    def close(self):
        self.stop.set()
