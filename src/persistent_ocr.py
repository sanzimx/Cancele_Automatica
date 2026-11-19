"""Processo OCR reutilizável, isolado da interface e reiniciado após falhas."""
import atexit
from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
from time import perf_counter
import numpy as np

class Engine:
    def __init__(self):
        self.process = None
        self.messages = None
        self.log_stream = None
        self.log_path = None
        self.lock = threading.Lock()
        self.counter = 0
        atexit.register(self.close)

    @staticmethod
    def _read_output(process, messages):
        try:
            for line in process.stdout:
                try:
                    messages.put(json.loads(line))
                except (ValueError, TypeError):
                    pass
        finally:
            messages.put({"type": "exit"})

    def _wait(self, expected, timeout=180):
        try:
            message = self.messages.get(timeout=timeout)
        except queue.Empty:
            raise RuntimeError("OCR excedeu o prazo. Registro: " + str(self.log_path))
        if message.get("type") != expected:
            raise RuntimeError("Falha no OCR: " + message.get("message", "processo encerrado") + ". Registro: " + str(self.log_path))
        return message

    def _stop(self):
        process, self.process = self.process, None
        if process:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=2)
            for stream in (process.stdin, process.stdout):
                if stream:
                    stream.close()
        if self.log_stream:
            self.log_stream.close()
            self.log_stream = None

    def _ensure(self):
        if self.process is not None and self.process.poll() is None:
            return
        self._stop()
        root = Path(__file__).resolve().parents[1]
        (root / "outputs").mkdir(exist_ok=True)
        self.log_path = root / "outputs" / ("ocr_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".log")
        self.log_stream = self.log_path.open("w", encoding="utf-8")
        self.messages = queue.Queue()
        self.process = subprocess.Popen(
            [sys.executable, "-u", "-X", "faulthandler", str(root / "ocr_service.py")],
            cwd=str(root), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=self.log_stream, text=True, encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        threading.Thread(target=self._read_output,
                         args=(self.process,self.messages),daemon=True).start()
        try:
            self._wait("ready")
        except Exception:
            self._stop()
            raise

    def load(self):
        with self.lock:
            self._ensure()

    def analyze(self,image,params,authorized):
        with self.lock:
            try:
                start = perf_counter()
                self._ensure()
                startup_ms = (perf_counter()-start)*1000
                with tempfile.TemporaryDirectory(prefix="cancela_ocr_") as folder:
                    work = Path(folder)
                    np.save(work/"entrada.npy",image,allow_pickle=False)
                    (work/"config.json").write_text(json.dumps({
                        "params":asdict(params),"authorized":sorted(authorized)}),encoding="utf-8")
                    self.counter += 1
                    self.process.stdin.write(json.dumps({"folder":str(work),"id":self.counter})+"\n")
                    self.process.stdin.flush()
                    message = self._wait("result")
                    if message.get("id") != self.counter:
                        raise RuntimeError("Resposta OCR fora de sequência.")
                    result = json.loads((work/"resultado.json").read_text(encoding="utf-8"))
                    with np.load(work/"imagens.npz",allow_pickle=False) as images:
                        result["prepared"]=images["prepared"].copy()
                        result["overlay"]=images["overlay"].copy()
                    result["worker_startup_ms"]=startup_ms
                    result["request_ms"]=(perf_counter()-start)*1000
                    return result
            except Exception:
                self._stop()
                raise

    def close(self):
        with self.lock:
            self._stop()
