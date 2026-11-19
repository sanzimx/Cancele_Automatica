"""Interface desktop. Execute: python app.py"""
import csv
import json
import queue
import threading
import time
from datetime import datetime
from pathlib import Path
from dataclasses import asdict
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from src.vision import Engine, Params, normalize, valid_plate
from src.devices import Camera, SerialLink, camera_url

ROOT = Path(__file__).resolve().parent
HISTORY = ROOT/"outputs"/"historico.csv"

def load_image(path):
    data = np.fromfile(str(path),dtype=np.uint8)
    frame = cv2.imdecode(data,cv2.IMREAD_COLOR)
    if frame is None or frame.shape[0]*frame.shape[1] > 40_000_000:
        raise ValueError("Imagem inválida ou maior que 40 megapixels.")
    return frame

class App:
    def __init__(self, window):
        self.window = window
        window.title("Cancela inteligente • Computação Gráfica")
        window.geometry("1240x820")
        window.minsize(980,680)
        self.events = queue.Queue()
        self.engine = Engine()
        self.camera = self.serial = None
        self.source_image = None
        self.result = None
        self.busy = False
        self.current_request = None
        self.closed = False
        self.session = 0
        self.preview_photo = None
        self.state = tk.StringVar(value="Modo de teste: relé não acionado por fotos.")
        self.preview_choice = tk.StringVar(value="Resultado")
        self.mode = tk.StringVar(value="Veicular")
        self.confidence = tk.DoubleVar(value=.60)
        self.width = tk.IntVar(value=640)
        self.clip = tk.DoubleVar(value=2)
        self.osd = tk.BooleanVar(value=False)
        self.detect_enabled = tk.BooleanVar(value=True)
        self.detect_confidence = tk.DoubleVar(value=.35)
        self.detect_detail = tk.BooleanVar(value=False)
        self.auto = tk.BooleanVar(value=False)
        self.host = tk.StringVar(value="192.168.1.73")
        self.user = tk.StringVar(value="admin")
        self.password = tk.StringVar()
        self.channel = tk.StringVar(value="101")
        self.port = tk.StringVar(value="COM3")
        self.roi = [tk.DoubleVar(value=n) for n in (0,0,100,100)]
        self.build()
        window.protocol("WM_DELETE_WINDOW",self.close)
        window.after(100,self.poll)

    def build(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton",padding=6)
        outer = ttk.Frame(self.window,padding=12)
        outer.pack(fill="both",expand=True)
        ttk.Label(outer,text="Cancela inteligente",font=("Segoe UI",22,"bold")).pack(anchor="w")
        ttk.Label(outer,text="Azul: região de leitura • cinza: textos • verde: autorizado • vermelho: demais resultados").pack(anchor="w")
        body = ttk.Panedwindow(outer,orient="horizontal")
        body.pack(fill="both",expand=True,pady=10)
        left = ttk.Frame(body,width=330)
        right = ttk.Frame(body)
        body.add(left,weight=0)
        body.add(right,weight=1)
        connection = ttk.LabelFrame(left,text="Câmera e ESP32",padding=8)
        connection.pack(fill="x")
        for row,(label,var,secret) in enumerate([
            ("IP câmera",self.host,False),("Usuário",self.user,False),
            ("Senha",self.password,True),("Canal",self.channel,False),
            ("Porta serial",self.port,False)]):
            ttk.Label(connection,text=label).grid(row=row,column=0,sticky="w")
            ttk.Entry(connection,textvariable=var,width=21,show="*" if secret else "").grid(row=row,column=1,sticky="ew",pady=2)
        buttons=ttk.Frame(connection)
        buttons.grid(row=5,column=0,columnspan=2)
        for text,fn in [("Câmera IP",self.connect_ip),("Webcam",self.connect_webcam),
                        ("ESP32",self.connect_serial),("Parar",self.disconnect)]:
            ttk.Button(buttons,text=text,command=fn).pack(side="left")
        ttk.Checkbutton(connection,text="Autorizar pelo sensor (ESP32)",variable=self.auto).grid(row=6,column=0,columnspan=2,sticky="w")
        cfg=ttk.LabelFrame(left,text="Análise",padding=8)
        cfg.pack(fill="x",pady=8)
        ttk.Label(cfg,text="Modo").grid(row=0,column=0,sticky="w")
        ttk.Combobox(cfg,textvariable=self.mode,values=["Veicular","Identificadores"],state="readonly",width=18).grid(row=0,column=1)
        for row,(label,var,lo,hi,step) in enumerate([
            ("Confiança mínima",self.confidence,.1,.99,.05),
            ("Largura OCR (px)",self.width,320,2560,160),
            ("Contraste CLAHE",self.clip,.5,8,.5)],1):
            ttk.Label(cfg,text=label).grid(row=row,column=0,sticky="w")
            ttk.Spinbox(cfg,textvariable=var,from_=lo,to=hi,increment=step,width=18).grid(row=row,column=1)
        ttk.Checkbutton(cfg,text="Mascarar OSD HiLook",variable=self.osd).grid(row=4,column=0,columnspan=2,sticky="w")
        ttk.Label(cfg,text="Região (%): esquerda, topo, direita, base").grid(row=5,column=0,columnspan=2,sticky="w",pady=(8,2))
        region=ttk.Frame(cfg)
        region.grid(row=6,column=0,columnspan=2)
        for var in self.roi:
            ttk.Spinbox(region,textvariable=var,from_=0,to=100,width=6).pack(side="left")
        ttk.Button(cfg,text="Aplicar parâmetros",command=self.validate_params).grid(row=7,column=0,columnspan=2,sticky="ew",pady=6)
        auth=ttk.LabelFrame(left,text="Autorizados (um por linha)",padding=8)
        auth.pack(fill="both",expand=True)
        self.plates=tk.Text(auth,height=5,width=27)
        self.plates.pack(fill="both",expand=True)
        self.plates.insert("1.0","ABC1D23\n")
        ttk.Label(auth,text="ABC1D23 é um exemplo fictício.").pack(anchor="w")
        ttk.Button(auth,text="Salvar cadastro e parâmetros",command=self.save_config).pack(fill="x",pady=4)
        ttk.Button(auth,text="Usar cadastro livre",command=self.use_free_registration).pack(fill="x",pady=2)
        tools=ttk.Frame(right)
        tools.pack(fill="x")
        for text,fn in [("Abrir foto",self.open_photo),("Foto exemplo",self.open_demo),("Foto real",self.open_real),("Foto difícil",self.open_difficult),("Analisar",self.analyze),
                        ("Salvar evidência",self.export_result),("Avaliar conjunto",self.evaluate)]:
            ttk.Button(tools,text=text,command=fn).pack(side="left",padx=2)
        ttk.Combobox(tools,textvariable=self.preview_choice,state="readonly",
                     values=["Original","Processada","Resultado"],width=13).pack(side="right")
        detection_controls = ttk.Frame(right)
        detection_controls.pack(fill="x", pady=(6, 0))
        ttk.Checkbutton(detection_controls, text="Localizar placas automaticamente",
                        variable=self.detect_enabled, command=self.detection_changed).pack(side="left")
        ttk.Checkbutton(detection_controls, text="Busca distante (mais lenta)",
                        variable=self.detect_detail).pack(side="left", padx=8)
        ttk.Label(detection_controls, text="Confiança detector").pack(side="left")
        ttk.Spinbox(detection_controls, textvariable=self.detect_confidence,
                    from_=.1, to=.95, increment=.05, width=5).pack(side="left", padx=4)
        self.preview=ttk.Label(right,anchor="center",text="Abra uma foto ou conecte uma câmera.")
        self.preview.pack(fill="both",expand=True,pady=8)
        self.details=ttk.Label(right,text="Nenhuma análise realizada.",font=("Segoe UI",12))
        self.details.pack(anchor="w")
        self.log=tk.Text(right,height=7,state="disabled",font=("Consolas",9))
        self.log.pack(fill="x",pady=6)
        ttk.Label(outer,textvariable=self.state,wraplength=1120).pack(fill="x")
        self.restore_config()

    def note(self,text):
        self.state.set(text)
        self.log.configure(state="normal")
        self.log.insert("end",datetime.now().strftime("%H:%M:%S")+" "+text+"\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def params(self):
        return Params(confidence=float(self.confidence.get()),width=int(self.width.get()),
                      clip=float(self.clip.get()),roi=tuple(v.get()/100 for v in self.roi),
                      mode=self.mode.get(),mask_osd=self.osd.get(),
                      auto_detect=self.detect_enabled.get(),
                      detector_confidence=float(self.detect_confidence.get()),
                      detector_detail=self.detect_detail.get())

    def authorized(self):
        values={normalize(s) for s in self.plates.get("1.0","end").splitlines() if normalize(s)}
        if self.mode.get()=="Veicular" and any(not valid_plate(s) for s in values):
            invalid=sorted(s for s in values if not valid_plate(s))
            raise ValueError("O modo Veicular não aceita este formato: " + ", ".join(invalid) +
                             ". Para preservar o texto informado, selecione Modo: Identificadores ou clique Usar cadastro livre.")
        if self.mode.get()=="Identificadores" and any(not 3<=len(s)<=10 for s in values):
            raise ValueError("O cadastro livre aceita de 3 a 10 letras ou números por linha.")
        return values

    def use_free_registration(self):
        self.mode.set("Identificadores")
        self.note("Cadastro livre ativado. O detector continua disponível e a comparação usa o texto exato, sem trocar letras por números.")

    def validate_params(self):
        try:
            from src.vision import roi_pixels
            p=self.params()
            roi_pixels((1080,1920,3),p.roi)
            if not .1 <= p.confidence <= .99 or not 320 <= p.width <=2560 or not .5<=p.clip<=8:
                raise ValueError("Confira confiança, largura e contraste.")
            self.authorized()
            if not .1 <= p.detector_confidence <= .95:
                raise ValueError("Confiança do detector deve estar entre 0,10 e 0,95.")
            self.note("Parâmetros válidos.")
            return True
        except Exception as e:
            messagebox.showerror("Configuração",str(e))
            return False

    def save_config(self):
        if not self.validate_params():
            return
        try:
            config=dict(params=asdict(self.params()),authorized=sorted(self.authorized()))
            (ROOT/"config.local.json").write_text(json.dumps(config,indent=2),encoding="utf-8")
            self.note("Cadastro salvo. Senha e endereço da câmera não são gravados.")
        except OSError:
            messagebox.showerror("Salvar","Não foi possível gravar configuração.")

    def restore_config(self):
        path=ROOT/"config.local.json"
        if not path.exists():
            return
        try:
            config=json.loads(path.read_text(encoding="utf-8"))
            p=config["params"]
            self.confidence.set(p["confidence"]); self.width.set(p["width"])
            self.clip.set(p["clip"]); self.mode.set(p["mode"]); self.osd.set(p["mask_osd"])
            self.detect_enabled.set(p.get("auto_detect", True))
            self.detect_confidence.set(p.get("detector_confidence", .35))
            self.detect_detail.set(p.get("detector_detail", False))
            for var,value in zip(self.roi,p["roi"]):
                var.set(100*value)
            self.plates.delete("1.0","end")
            self.plates.insert("1.0","\n".join(config["authorized"]))
        except Exception:
            self.note("Configuração anterior inválida. Confira os campos.")

    def disconnect(self):
        self.auto.set(False)
        self.session+=1
        self.current_request=None
        if self.camera:
            self.camera.close()
        if self.serial:
            self.serial.close()
        self.camera=self.serial=None
        self.note("Conexões encerradas. Respostas de análises antigas serão descartadas.")

    def connect_ip(self):
        try:
            url=camera_url(self.host.get().strip(),self.user.get(),self.password.get(),self.channel.get())
            if self.camera:
                self.camera.close()
            self.camera=Camera(url,self.events)
            self.source_image=None; self.result=None
            self.note("Conectando à câmera IP...")
        except ValueError as e:
            messagebox.showerror("Câmera",str(e))

    def connect_webcam(self):
        if self.camera:
            self.camera.close()
        self.camera=Camera(0,self.events)
        self.source_image=None; self.result=None
        self.note("Conectando à webcam de índice 0.")

    def connect_serial(self):
        if self.serial and self.serial.thread.is_alive():
            self.note("Encerre as conexões antes de reconectar o ESP32.")
            return
        self.session+=1
        self.current_request=None
        self.serial=SerialLink(self.port.get().strip(),self.events)

    def detection_changed(self):
        if self.detect_enabled.get():
            for var, value in zip(self.roi, (0, 0, 100, 100)):
                var.set(value)
            self.note("Detector automático: busca na imagem inteira. Cada placa terá seu próprio recorte e leitura.")

    def open_photo(self):
        if self.busy:
            self.note("Aguarde o término da análise.")
            return
        path=filedialog.askopenfilename(filetypes=[("Imagens","*.jpg *.jpeg *.png *.bmp *.pgm"),("Todos","*.*")])
        if not path:
            return
        try:
            frame=load_image(path)
            self.detect_enabled.set(True)
            self.detection_changed()
            # A análise por foto nunca responde a uma solicitação física.
            self.auto.set(False)
            if self.camera:
                self.camera.close(); self.camera=None
            self.source_image=frame
            self.result=None
            self.note("Foto carregada. Modo de teste, sem acionamento.")
        except Exception as e:
            messagebox.showerror("Arquivo",str(e))

    def open_difficult(self):
        if self.busy:
            self.note("Aguarde o término da operação atual.")
            return
        self.auto.set(False)
        self.detect_enabled.set(True)
        self.detection_changed()
        if self.camera:
            self.camera.close()
            self.camera = None
        self.busy = True
        self.note("Preparando casos escuro, turvo e combinado da mesma foto real...")
        def work():
            try:
                from tools.gerar_casos_dificeis import generate
                path = generate()
                self.events.put(("real_photo", (load_image(path), str(path))))
                self.events.put(("notice", "Caso escuro e turvo carregado. Clique Analisar. As versões separadas estão na mesma pasta."))
            except Exception as error:
                self.events.put(("error", ("Falha ao preparar caso difícil: " + str(error), None, self.session)))
        threading.Thread(target=work, daemon=True).start()

    def open_real(self):
        if self.busy:
            self.note("Aguarde o término da operação atual.")
            return
        self.auto.set(False)
        self.detect_enabled.set(True)
        self.detection_changed()
        if self.camera:
            self.camera.close()
            self.camera = None
        self.busy = True
        self.note("Baixando foto real do Wikimedia Commons para data_samples/foto_real...")
        def work():
            try:
                from tools.baixar_foto_real import download
                path = download()
                image = load_image(path)
                self.events.put(("real_photo", (image, str(path))))
            except Exception as error:
                self.events.put(("error", ("Download da foto falhou: " + str(error), None, self.session)))
        threading.Thread(target=work, daemon=True).start()

    def open_demo(self):
        if self.busy:
            self.note("Aguarde o término da análise.")
            return
        try:
            from PIL import ImageDraw, ImageFont
            font_path = Path("C:/Windows/Fonts/arialbd.ttf")
            if not font_path.exists():
                font_path = Path("C:/Windows/Fonts/arial.ttf")
            font = ImageFont.truetype(str(font_path), 100)
            demo = Image.new("RGB", (900, 400), (80, 80, 80))
            draw = ImageDraw.Draw(demo)
            draw.rectangle((100, 100, 800, 300), fill="white", outline="black", width=3)
            text = "ABC1D23"
            box = draw.textbbox((0, 0), text, font=font)
            draw.text(((900-(box[2]-box[0]))/2, (400-(box[3]-box[1]))/2-box[1]),
                      text, font=font, fill="black")
            self.auto.set(False)
            if self.camera:
                self.camera.close()
                self.camera = None
            self.source_image = cv2.cvtColor(np.array(demo), cv2.COLOR_RGB2BGR)
            self.detect_enabled.set(False)
            self.result = None
            self.note("Exemplo sintético ABC1D23 carregado. Clique Analisar. O acerto precisa ser verificado.")
        except Exception as error:
            messagebox.showerror("Foto exemplo", str(error))

    def analyze(self, request=None):
        if self.busy:
            self.note("OCR ocupado. Nova solicitação será negada.")
            if request and self.serial:
                self.serial.send("NEGADO:"+request)
            return
        if request and (not self.auto.get() or self.mode.get()!="Veicular" or not self.camera):
            self.serial.send("NEGADO:"+request)
            self.note("Solicitação negada: habilite câmera, modo veicular e autorização pelo sensor.")
            return
        if not self.validate_params():
            if request and self.serial:
                self.serial.send("NEGADO:"+request)
            return
        if self.source_image is None and not self.camera:
            messagebox.showinfo("Entrada","Abra uma foto ou conecte uma câmera.")
            return
        params=self.params(); allowed=self.authorized()
        camera=self.camera
        original=self.source_image.copy() if camera is None and self.source_image is not None else None
        session=self.session
        self.busy=True
        self.current_request=request
        # Importações pesadas e inferência ficam fora da thread da interface.
        self.note("Preparando OCR e analisando. Na primeira execução os pesos podem ser baixados.")
        def work():
            try:
                image=original if original is not None else camera.snapshot(timeout=8,after=time.monotonic())
                result=self.engine.analyze(image,params,allowed)
                self.events.put(("result",(image,result,request,session,asdict(params))))
            except Exception as error:
                import traceback
                diagnostic = ROOT / "outputs" / "erro_interface.log"
                try:
                    diagnostic.parent.mkdir(exist_ok=True)
                    with diagnostic.open("a", encoding="utf-8") as stream:
                        traceback.print_exc(file=stream)
                except OSError:
                    pass
                self.events.put(("error",(str(error),request,session)))
        threading.Thread(target=work,daemon=True).start()

    def record(self,result,request,params):
        HISTORY.parent.mkdir(exist_ok=True)
        exists=HISTORY.exists()
        row=dict(timestamp=datetime.now().isoformat(timespec="seconds"),
                 plate=result["plate"],status=result["status"],
                 confidence=round(result["confidence"],4),
                 elapsed_ms=round(result["elapsed_ms"],2),
                 request_id=request or "FOTO_OU_MANUAL",
                 parameters=json.dumps(params))
        with HISTORY.open("a",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=list(row))
            if not exists:
                writer.writeheader()
            writer.writerow(row)

    def evaluate(self):
        if self.busy:
            self.note("Aguarde a análise atual.")
            return
        if not self.validate_params():
            return
        path=filedialog.askopenfilename(title="Manifesto CSV",filetypes=[("CSV","*.csv")])
        if not path:
            return
        self.auto.set(False)
        params=self.params(); allowed=self.authorized()
        self.busy=True
        self.note("Avaliando conjunto. O relé permanece sem comandos de autorização.")
        def work():
            try:
                from evaluate import run_evaluation
                output=run_evaluation(Path(path),params,allowed,self.engine)
                self.events.put(("evaluation",output))
            except Exception:
                self.events.put(("error",("Falha na avaliação. Confira CSV e caminhos das imagens.",None,self.session)))
        threading.Thread(target=work,daemon=True).start()

    def poll(self):
        if self.closed:
            return
        try:
            while True:
                kind,data=self.events.get_nowait()
                if kind=="notice":
                    self.note(data)
                elif kind=="real_photo":
                    self.busy = False
                    self.source_image, path = data
                    self.result = None
                    self.note("Foto real salva em " + path)
                    self.note("Confira visualmente a placa, mantenha o sensor desmarcado e clique Analisar. Créditos ao lado da foto.")
                elif kind=="serial":
                    sender,data=data
                    if sender is not self.serial:
                        continue
                    self.note("ESP32: "+data)
                    if data.startswith("VEICULO_DETECTADO:"):
                        self.analyze(data.split(":",1)[1])
                    elif data.startswith(("TEMPO_ESGOTADO:","CANCELADO:")):
                        if data.split(":",1)[1]==self.current_request:
                            self.current_request=None
                elif kind=="result":
                    image,result,request,session,params=data
                    self.busy=False
                    self.source_image=image
                    self.result=result
                    self.details.configure(text=f'{result["status"]} • Placa: {result["plate"] or "não reconhecida"} • Confiança: {result["confidence"]:.0%} • {result["elapsed_ms"]:.0f} ms')
                    if not result["plate"] and result.get("raw_text"):
                        self.details.configure(text=result["status"] + " • Texto detectado: " +
                                               result["raw_text"] + " • Escore bruto: " +
                                               format(result["raw_confidence"], ".1%") +
                                               " • sem autorização • " + format(result["elapsed_ms"], ".0f") + " ms")
                    self.note("Análise concluída: " + result["status"])
                    if "detected_count" in result:
                        if result["detected_count"] > 1:
                            self.details.configure(text="MULTIPLAS_PLACAS • " + str(result["detected_count"]) +
                                                   " localizadas • resultados individuais abaixo • " +
                                                   format(result["elapsed_ms"], ".0f") + " ms")
                        self.note("Placas localizadas: " + str(result["detected_count"]) +
                                  " • tempo detector: " + format(result["detection_ms"], ".0f") + " ms")
                        for item in result["plates"]:
                            if not item["plate"] and item.get("raw_text"):
                                self.note("Texto bruto #" + str(item["index"]) + ": " + item["raw_text"] +
                                          " • escore: " + format(item["raw_confidence"], ".1%") +
                                          " • motivo: " + item["rejection_reason"])
                                for hypothesis in item.get("review_candidates", []):
                                    self.note("Hipótese para revisão: " + hypothesis["text"] +
                                              " • menor escore por caractere: " +
                                              format(hypothesis["minimum_score"], ".1%") +
                                              " • não usada para autorizar")
                                if item.get("review_error"):
                                    self.note("Não foi possível gerar hipóteses: " + item["review_error"])
                            self.note("Reconhecedor #" + str(item["index"]) + ": " +
                                      item.get("recognizer_model", "easyocr"))
                            self.note("Recorte original #" + str(item["index"]) + ": " +
                                      str(item.get("original_plate_width", "?")) + " x " +
                                      str(item.get("original_plate_height", "?")) + " pixels")
                            self.note("Placa #" + str(item["index"]) + ": " +
                                      (item["plate"] or "SEM_LEITURA") + " • " + item["status"] +
                                      " • OCR: " + format(item["confidence"], ".1%"))
                        if result.get("skipped_count"):
                            self.note("Limite de 8 leituras por análise. Há mais detecções sem OCR neste quadro.")
                        if result["status"] == "MULTIPLAS_PLACAS":
                            self.note("Várias placas na região: resultados individuais exibidos, sem autorização de abertura.")
                    self.note("Tempo total do pedido: " + format(result.get("request_ms", result["elapsed_ms"])/1000, ".2f") + " s. O modelo permanece carregado para a próxima análise.")
                    if result["tokens"]:
                        for token in result["tokens"]:
                            self.note("Texto OCR: " + token["text"] + " • escore: " +
                                      format(token["confidence"], ".1%"))
                    else:
                        self.note("O OCR não detectou textos nesta imagem.")
                    if result["status"] == "SEM_LEITURA":
                        self.note("Nenhum candidato passou pelos filtros de confiança e formato. O cadastro não determina a leitura.")
                    elif result["status"] == "SEM_PLACA":
                        self.note("Detector não localizou placas. Confira a resolução original ou ative Busca distante para testar janelas sobrepostas.")
                    elif result["status"] == "FORMATO_INVALIDO":
                        self.note("Texto detectado, mas incompatível com os formatos brasileiros aceitos. As hipóteses não alteram a leitura nem autorizam a cancela.")
                    elif result["status"] == "BAIXA_CONFIANCA":
                        self.note("Texto detectado, mas o escore não atingiu o limite exigido. Nenhuma autorização enviada.")
                    try:
                        self.record(result,request,params)
                    except OSError:
                        self.note("Análise concluída, mas histórico não pôde ser gravado.")
                    if request:
                        if session==self.session and request==self.current_request and self.auto.get() and self.serial:
                            command="AUTORIZADO" if result["status"]=="AUTORIZADO" else "NEGADO"
                            try:
                                self.serial.send(command+":"+request)
                            except RuntimeError as e:
                                self.note(str(e))
                        else:
                            self.note("Resultado tardio ou cancelado. Nenhuma autorização enviada.")
                    self.current_request=None
                elif kind=="error":
                    message,request,session=data
                    self.busy=False
                    if request and session==self.session and self.serial:
                        try:
                            self.serial.send("NEGADO:"+request)
                        except RuntimeError:
                            pass
                    self.current_request=None
                    self.note(message)
                elif kind=="evaluation":
                    self.busy=False
                    self.note("Avaliação salva em "+str(data))
                    messagebox.showinfo("Avaliação","Resultados, métricas e relatório salvos em:\n"+str(data))
        except queue.Empty:
            pass
        self.render()
        self.window.after(120,self.poll)

    def render(self):
        selected=self.preview_choice.get()
        frame=None
        if self.result:
            frame={"Original":self.source_image,"Processada":self.result["prepared"],
                   "Resultado":self.result["overlay"]}[selected]
        elif self.source_image is not None:
            frame=self.source_image
        elif self.camera:
            with self.camera.lock:
                if self.camera.frame is not None and time.monotonic()-self.camera.received<=2:
                    frame=self.camera.frame.copy()
        if frame is None:
            return
        if frame.ndim==3:
            frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        image=Image.fromarray(frame)
        image.thumbnail((max(200,self.preview.winfo_width()),max(150,self.preview.winfo_height())))
        self.preview_photo=ImageTk.PhotoImage(image)
        self.preview.configure(image=self.preview_photo,text="")

    def export_result(self):
        if not self.result:
            messagebox.showinfo("Evidência","Execute uma análise primeiro.")
            return
        path=filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG","*.png")])
        if not path:
            return
        try:
            cv2.imencode(".png",self.result["overlay"])[1].tofile(path)
            info={k:v for k,v in self.result.items() if k not in ("overlay","prepared")}
            Path(path).with_suffix(".json").write_text(json.dumps(info,indent=2),encoding="utf-8")
            self.note("Evidência e leitura salvas.")
        except OSError:
            messagebox.showerror("Salvar","Não foi possível salvar a evidência.")

    def close(self):
        self.closed=True
        self.disconnect()
        self.window.destroy()

if __name__=="__main__":
    root=tk.Tk()
    App(root)
    root.mainloop()
