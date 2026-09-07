from __future__ import annotations
import socket,threading,tkinter as tk
from tkinter import ttk,messagebox
from bitstream import bytes_to_bits
from huffman import decode
from protocol import receive_frame,parse_frame
from waveform import plot_nrz
PORT=5000
BG="#08111f"; PANEL="#101c2d"; PANEL2="#0b1626"; BORDER="#26384f"; TEXT="#e8eef7"; MUTED="#8ea1b8"; GREEN="#39d98a"; BLUE="#43b5f5"; AMBER="#f3c969"
class App:
    def __init__(self,root):
        self.root=root; root.title("Huffman Link Analyzer | RX"); root.geometry("1180x760"); root.configure(bg=BG)
        self.bits=""; self.state=tk.StringVar(value="STARTING"); self.link=tk.StringVar(value="LINK: LISTENING"); self.framev=tk.StringVar(value="FRAME: --"); self.verify=tk.StringVar(value="VERIFY: --")
        self.style(); self.ui(); threading.Thread(target=self.server,daemon=True).start()
    def style(self):
        s=ttk.Style(); s.theme_use("clam"); s.configure("TButton",background="#1b2c44",foreground=TEXT,borderwidth=0,padding=(12,7),font=("Segoe UI",9,"bold")); s.map("TButton",background=[("active","#29415f")])
    def panel(self,p): return tk.Frame(p,bg=PANEL,highlightbackground=BORDER,highlightthickness=1)
    def title(self,p,t): tk.Label(p,text=t,bg=PANEL,fg=TEXT,font=("Consolas",10,"bold")).pack(anchor="w",padx=12,pady=(10,5))
    def ui(self):
        o=tk.Frame(self.root,bg=BG); o.pack(fill="both",expand=True,padx=18,pady=15)
        h=tk.Frame(o,bg=BG); h.pack(fill="x")
        tk.Label(h,text="HUFFMAN LINK ANALYZER",bg=BG,fg=TEXT,font=("Segoe UI Semibold",20)).pack(side="left")
        tk.Label(h,text="  RX / DESTINATION NODE",bg=BG,fg=GREEN,font=("Consolas",10,"bold")).pack(side="left",pady=(7,0))
        tk.Label(h,text="DIGITAL COMMUNICATION LAB",bg=BG,fg=MUTED,font=("Consolas",9)).pack(side="right",pady=(7,0))
        bar=tk.Frame(o,bg=PANEL2,highlightbackground=BORDER,highlightthickness=1); bar.pack(fill="x",pady=10)
        for v,c in [(self.state,GREEN),(self.link,BLUE),(self.framev,TEXT),(self.verify,AMBER)]:
            tk.Label(bar,textvariable=v,bg=PANEL2,fg=c,font=("Consolas",9,"bold")).pack(side="left",padx=13,pady=8)
        body=tk.Frame(o,bg=BG); body.pack(fill="both",expand=True)
        L=tk.Frame(body,bg=BG); L.pack(side="left",fill="both",expand=True,padx=(0,5)); R=tk.Frame(body,bg=BG); R.pack(side="left",fill="both",expand=True,padx=(5,0))
        p=self.panel(L); p.pack(fill="x",pady=(0,8)); self.title(p,"01  RECEIVER")
        tk.Label(p,text="TCP LISTENER",bg=PANEL,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=12)
        tk.Label(p,text="0.0.0.0 : 5000",bg=PANEL,fg=BLUE,font=("Consolas",14,"bold")).pack(anchor="w",padx=12,pady=(0,12))
        p=self.panel(L); p.pack(fill="both",expand=True); self.title(p,"02  RECOVERED PAYLOAD / BITS")
        self.bitsbox=tk.Text(p,bg=PANEL2,fg=BLUE,relief="flat",font=("Consolas",9),wrap="word"); self.bitsbox.pack(fill="both",expand=True,padx=12,pady=(0,12))
        p=self.panel(R); p.pack(fill="both",expand=True,pady=(0,8)); self.title(p,"03  RECOVERED CODEBOOK")
        self.table=tk.Text(p,bg=PANEL2,fg=TEXT,relief="flat",font=("Consolas",9)); self.table.pack(fill="both",expand=True,padx=12,pady=(0,12))
        p=self.panel(R); p.pack(fill="x",pady=(0,8)); self.title(p,"04  DECODED MESSAGE")
        self.dec=tk.Text(p,height=6,bg=PANEL2,fg=TEXT,relief="flat",font=("Segoe UI",11),wrap="word"); self.dec.pack(fill="x",padx=12,pady=(0,12))
        p=self.panel(R); p.pack(fill="x"); self.title(p,"05  LINK ANALYSIS")
        self.stats=tk.Text(p,height=7,bg=PANEL2,fg=TEXT,relief="flat",font=("Consolas",9)); self.stats.pack(fill="x",padx=12,pady=(0,7))
        ttk.Button(p,text="VIEW NRZ WAVEFORM",command=self.wave).pack(anchor="w",padx=12,pady=(0,12))
    def server(self):
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); s.bind(("0.0.0.0",PORT)); s.listen(5)
            self.root.after(0,lambda:self.state.set("LISTENING"))
            while True:
                c,a=s.accept(); threading.Thread(target=self.handle,args=(c,a),daemon=True).start()
        except Exception as e:self.root.after(0,lambda:messagebox.showerror("Receiver error",str(e)))
    def handle(self,c,a):
        try:
            with c:
                self.root.after(0,lambda:self.link.set(f"LINK: {a[0]}:{a[1]}"))
                frame=receive_frame(c); info=parse_frame(frame); self.bits=bytes_to_bits(info["compressed_data"],info["valid_bits"]); text=decode(self.bits,info["codebook"])
                if len(text)!=info["original_chars"]: raise ValueError("Decoded length mismatch.")
                stats=f"Source chars         {info['original_chars']:>8}\nPayload bits         {len(self.bits):>8}\nFrame bytes          {len(frame):>8}\nCodebook symbols     {len(info['codebook']):>8}\nCRC-32                PASSED ✓\nHuffman decode        PASSED ✓\nMessage verify        PASSED ✓"
                self.root.after(0,lambda:self.update(info["codebook"],text,stats,len(frame)))
        except Exception as e:
            self.root.after(0,lambda:messagebox.showerror("RX error",str(e))); self.root.after(0,lambda:self.state.set("RX ERROR"))
    def update(self,codes,text,stats,n):
        self.stats.delete("1.0","end"); self.stats.insert("1.0",stats); self.table.delete("1.0","end")
        for s,c in sorted(codes.items(),key=lambda x:(len(x[1]),x[1])): self.table.insert("end",f"{'[SPACE]' if s==' ' else repr(s):<12} {c}\n")
        self.bitsbox.delete("1.0","end"); self.bitsbox.insert("1.0",self.bits); self.dec.delete("1.0","end"); self.dec.insert("1.0",text)
        self.state.set("RECEIVED ✓"); self.framev.set(f"FRAME: {n} B"); self.verify.set("VERIFY: CRC + DECODE PASSED")
    def wave(self):
        if self.bits: plot_nrz(self.bits,title="RX | Recovered Huffman Payload | NRZ-L")
        else: messagebox.showinfo("Waveform","No message received yet.")
if __name__=="__main__":
    root=tk.Tk(); App(root); root.mainloop()
