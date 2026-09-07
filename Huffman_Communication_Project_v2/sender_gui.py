from __future__ import annotations
import socket, threading, tkinter as tk
from tkinter import ttk, messagebox
from huffman import build_tree, generate_codes, encode
from bitstream import bits_to_bytes
from protocol import build_frame, send_all
from waveform import plot_nrz

PORT=5000
BG="#08111f"; PANEL="#101c2d"; PANEL2="#0b1626"; BORDER="#26384f"
TEXT="#e8eef7"; MUTED="#8ea1b8"; GREEN="#39d98a"; BLUE="#43b5f5"; AMBER="#f3c969"

class App:
    def __init__(self,root):
        self.root=root; self.root.title("Huffman Link Analyzer | TX"); self.root.geometry("1180x760")
        self.root.configure(bg=BG); self.codes={}; self.bits=""; self.frame=b""
        self.ip=tk.StringVar(value="127.0.0.1"); self.state=tk.StringVar(value="IDLE")
        self.link=tk.StringVar(value="LINK: OFFLINE"); self.framev=tk.StringVar(value="FRAME: --")
        self.comp=tk.StringVar(value="RAW SAVING: --"); self.style(); self.ui()
    def style(self):
        s=ttk.Style(); s.theme_use("clam")
        s.configure("TButton",background="#1b2c44",foreground=TEXT,borderwidth=0,padding=(12,7),font=("Segoe UI",9,"bold"))
        s.map("TButton",background=[("active","#29415f")])
        s.configure("Accent.TButton",background=GREEN,foreground="#06120b",padding=(14,7),font=("Segoe UI",9,"bold"))
    def panel(self,p): return tk.Frame(p,bg=PANEL,highlightbackground=BORDER,highlightthickness=1)
    def title(self,p,t): tk.Label(p,text=t,bg=PANEL,fg=TEXT,font=("Consolas",10,"bold")).pack(anchor="w",padx=12,pady=(10,5))
    def ui(self):
        o=tk.Frame(self.root,bg=BG); o.pack(fill="both",expand=True,padx=18,pady=15)
        h=tk.Frame(o,bg=BG); h.pack(fill="x")
        tk.Label(h,text="HUFFMAN LINK ANALYZER",bg=BG,fg=TEXT,font=("Segoe UI Semibold",20)).pack(side="left")
        tk.Label(h,text="  TX / SOURCE NODE",bg=BG,fg=BLUE,font=("Consolas",10,"bold")).pack(side="left",pady=(7,0))
        tk.Label(h,text="DIGITAL COMMUNICATION LAB",bg=BG,fg=MUTED,font=("Consolas",9)).pack(side="right",pady=(7,0))
        bar=tk.Frame(o,bg=PANEL2,highlightbackground=BORDER,highlightthickness=1); bar.pack(fill="x",pady=10)
        for v,c in [(self.state,GREEN),(self.link,BLUE),(self.framev,TEXT),(self.comp,AMBER)]:
            tk.Label(bar,textvariable=v,bg=PANEL2,fg=c,font=("Consolas",9,"bold")).pack(side="left",padx=13,pady=8)
        top=tk.Frame(o,bg=BG); top.pack(fill="x")
        p=self.panel(top); p.pack(side="left",fill="x",expand=True,padx=(0,5)); self.title(p,"01  LINK")
        r=tk.Frame(p,bg=PANEL); r.pack(fill="x",padx=12,pady=(0,11))
        tk.Label(r,text="Receiver IPv4",bg=PANEL,fg=MUTED).pack(side="left")
        tk.Entry(r,textvariable=self.ip,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",font=("Consolas",10),width=20).pack(side="left",padx=10,ipady=5)
        tk.Label(r,text="TCP 5000",bg=PANEL,fg=BLUE,font=("Consolas",9)).pack(side="left")
        p=self.panel(top); p.pack(side="left",fill="x",padx=(5,0)); self.title(p,"02  CONTROL")
        r=tk.Frame(p,bg=PANEL); r.pack(padx=12,pady=(0,11))
        ttk.Button(r,text="BUILD FRAME",command=self.compress).pack(side="left",padx=3)
        ttk.Button(r,text="NRZ",command=self.wave).pack(side="left",padx=3)
        ttk.Button(r,text="TRANSMIT",style="Accent.TButton",command=self.send).pack(side="left",padx=3)
        body=tk.Frame(o,bg=BG); body.pack(fill="both",expand=True,pady=(10,0))
        L=tk.Frame(body,bg=BG); L.pack(side="left",fill="both",expand=True,padx=(0,5))
        R=tk.Frame(body,bg=BG); R.pack(side="left",fill="both",expand=True,padx=(5,0))
        p=self.panel(L); p.pack(fill="x",pady=(0,8)); self.title(p,"03  SOURCE MESSAGE")
        self.msg=tk.Text(p,height=6,bg=PANEL2,fg=TEXT,insertbackground=GREEN,relief="flat",font=("Consolas",11),wrap="word")
        self.msg.pack(fill="x",padx=12,pady=(0,12)); self.msg.insert("1.0","Huffman coding provides lossless compression for digital communication.")
        p=self.panel(L); p.pack(fill="both",expand=True); self.title(p,"04  HUFFMAN PAYLOAD / BITS")
        self.bitsbox=tk.Text(p,bg=PANEL2,fg=BLUE,relief="flat",font=("Consolas",9),wrap="word"); self.bitsbox.pack(fill="both",expand=True,padx=12,pady=(0,12))
        p=self.panel(R); p.pack(fill="both",expand=True,pady=(0,8)); self.title(p,"05  CODEBOOK")
        self.table=tk.Text(p,bg=PANEL2,fg=TEXT,relief="flat",font=("Consolas",9)); self.table.pack(fill="both",expand=True,padx=12,pady=(0,12))
        p=self.panel(R); p.pack(fill="x"); self.title(p,"06  METRICS")
        self.stats=tk.Text(p,height=8,bg=PANEL2,fg=TEXT,relief="flat",font=("Consolas",9)); self.stats.pack(fill="x",padx=12,pady=(0,12))
    def compress(self):
        text=self.msg.get("1.0","end-1c")
        if not text: messagebox.showwarning("Input","Enter a message first."); return
        try:
            tree=build_tree(text); self.codes=generate_codes(tree); self.bits=encode(text,self.codes)
            packed,n=bits_to_bytes(self.bits); self.frame=build_frame(self.codes,len(text),packed,n)
            ob=len(text.encode())*8; cb=len(self.bits); fb=len(self.frame)*8
            raw=(1-cb/ob)*100; actual=(1-fb/ob)*100
            self.stats.delete("1.0","end"); self.stats.insert("1.0",f"Source bits          {ob:>8}\nHuffman payload      {cb:>8}\nFull frame bits      {fb:>8}\nRaw saving           {raw:>7.2f}%\nFrame saving         {actual:>7.2f}%\nSymbols              {len(self.codes):>8}\nPadding              {(8-cb%8)%8:>8}\nCRC                   ENABLED")
            self.table.delete("1.0","end")
            for s,c in sorted(self.codes.items(),key=lambda x:(len(x[1]),x[1])):
                self.table.insert("end",f"{'[SPACE]' if s==' ' else repr(s):<12} {c}\n")
            self.bitsbox.delete("1.0","end"); self.bitsbox.insert("1.0",self.bits)
            self.state.set("READY"); self.framev.set(f"FRAME: {len(self.frame)} B"); self.comp.set(f"RAW SAVING: {raw:.2f}%")
        except Exception as e: messagebox.showerror("Compression error",str(e))
    def wave(self):
        if not self.bits:self.compress()
        if self.bits: plot_nrz(self.bits,title="TX | Huffman Payload | NRZ-L")
    def send(self):
        if not self.frame:self.compress()
        if not self.frame:return
        ip=self.ip.get().strip(); self.state.set("CONNECTING"); self.link.set(f"LINK: {ip}:5000")
        def work():
            try:
                with socket.create_connection((ip,PORT),timeout=10) as s: send_all(s,self.frame)
                self.root.after(0,lambda:self.state.set("TRANSMITTED ✓"))
            except Exception as e:
                self.root.after(0,lambda:messagebox.showerror("Transmission error",str(e)))
                self.root.after(0,lambda:self.state.set("TX ERROR"))
        threading.Thread(target=work,daemon=True).start()
if __name__=="__main__":
    root=tk.Tk(); App(root); root.mainloop()
