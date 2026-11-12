"""A true wallpaper-backed transcript: the entire viewport remains visible between bubbles."""
import tkinter as tk
from tkinter import font as tkfont, messagebox, ttk

import room_style as style
from room_core import data_dir
from room_identity import avatar_path, avatar_photo, display_author
from room_locale import tr
from room_preferences import wallpaper_photo


class WallpaperTimeline(tk.Frame):
    def __init__(self, parent, suggest, *, options, own_name, describe_call, on_wallpaper=None):
        super().__init__(parent, bg=style.BACKGROUND)
        self.options, self.own_name, self.describe_call = options, own_name, describe_call
        self.suggest, self.on_wallpaper = suggest, on_wallpaper
        self.view = tk.Canvas(self, bg=style.BACKGROUND, width=1, height=1,
                              highlightthickness=0, bd=0, yscrollincrement=24)
        self.scroll = ttk.Scrollbar(self, orient="vertical", command=self.view.yview)
        self.scroll.pack(side="right", fill="y")
        self.view.pack(side="left", fill="both", expand=True)
        self.view.configure(yscrollcommand=self._scrolled)
        self.view.bind("<Configure>", self._resize)
        self.view.tag_bind("detail-link","<Enter>",lambda _:self.view.configure(cursor="hand2"))
        self.view.tag_bind("detail-link","<Leave>",lambda _:self.view.configure(cursor="arrow"))
        self.wheel_bindings = [(key, self.winfo_toplevel().bind(key, self._wheel, add="+"))
                               for key in ("<MouseWheel>", "<Button-4>", "<Button-5>")]
        self.messages, self.rows, self.avatars = [], [], {}
        self.resize_job = self.scroll_job = None
        self.photo = None
        self.background_size = None
        self.background_item = None
        self.font = tkfont.Font(self, family=style.FONT, size=options["message_font_size"])
        self.meta_font = tkfont.Font(self, family=style.FONT, size=9)
        self.copy_menu = tk.Menu(self, tearoff=False)
        self.copy_menu.add_command(label=tr("复制消息"))
        self.copy_menu.add_command(label=tr("复制调用详情"))

    def _scrolled(self, first, last):
        self.scroll.set(first, last)
        if self.background_item:
            # Pin the image to the viewport, rather than the full transcript height.
            self.view.coords(self.background_item, 0, self.view.canvasy(0))

    def _wheel(self, event):
        if not str(event.widget).startswith(str(self)):
            return
        if event.num in (4, 5):
            units = -1 if event.num == 4 else 1
        else:
            units = -max(1,abs(event.delta)//120) if event.delta>0 else max(1,abs(event.delta)//120)
        self.view.yview_scroll(units, "units")
        return "break"

    def _resize(self, _event=None):
        if self.resize_job:
            self.after_cancel(self.resize_job)
        self.resize_job = self.after(60, self._fit_all)

    def _fit_all(self):
        self.resize_job = None
        old = self.view.yview()
        old_y = max(0,self.view.canvasy(0))
        follow = old[1] >= .98 and self.options["auto_scroll"]
        width, height = max(200,self.view.winfo_width()), max(100,self.view.winfo_height())
        size = (width,height)
        if self.background_size != size:
            self.photo = wallpaper_photo(self, self.options, width, height, style.BACKGROUND)
            self.background_size = size
            if self.on_wallpaper:
                self.on_wallpaper(self.photo)
        self.view.delete("all")
        self.rows.clear()
        self.background_item = self.view.create_image(0,0,image=self.photo,anchor="nw",tags="wallpaper") if self.photo else None
        y = 22
        for index,message in enumerate(self.messages):
            y = self._draw_message(message,index,width,y)+20
        if not self.messages:
            self._draw_empty(width,height)
        document_height = max(height,y+12)
        self.view.configure(scrollregion=(0,0,width,document_height))
        if follow:
            self.view.yview_moveto(1)
        else:
            self.view.yview_moveto(old_y/document_height)
        self._scrolled(*self.view.yview())

    def _capsule(self, left, top, right, bottom, fill, outline):
        r = min(12, (bottom-top)/2)
        return self.view.create_polygon(left+r,top,right-r,top,right,top,right,top+r,
            right,bottom-r,right,bottom,right-r,bottom,left+r,bottom,left,bottom,left,bottom-r,
            left,top+r,left,top,fill=fill,outline=outline,smooth=True,splinesteps=24)

    def _draw_message(self, message, index, width, y):
        own = message.author == "你"
        tag = "message-"+str(index)
        limit = max(120,int((width-112)*.82))
        name = display_author(message, self.own_name()) if own else (tr(message.author) if message.author in {"系统","讨论","联网搜索"} else message.author)
        title = name
        if own and message.recipients:
            title += " → "+"、".join(message.details.get("audience",message.recipients))
        if message.details.get("round"):
            title += " · "+tr(f"第 {message.details['round']} 轮")
        if self.options["show_timestamps"]:
            title += "  "+message.time[11:16]
        anchor_x = width-72 if own else 72
        meta = self.view.create_text(anchor_x,y,text=title,anchor="ne" if own else "nw",
            justify="right" if own else "left",width=limit,font=self.meta_font,fill=style.INK,tags=tag)
        meta_box = self.view.bbox(meta)
        chip=self._capsule(meta_box[0]-4,meta_box[1]-2,meta_box[2]+4,meta_box[3]+2,style.SURFACE,"")
        self.view.addtag_withtag(tag,chip)
        self.view.tag_lower(chip,meta)
        top = meta_box[3]+5
        body = tr(message.body) if message.author in {"系统","讨论"} else message.body
        text = self.view.create_text(0,0,text=body,anchor="nw",justify="left",width=limit,
            font=self.font,fill=style.INK,tags=tag)
        bounds = self.view.bbox(text)
        bubble_width, bubble_height = bounds[2]-bounds[0]+32, bounds[3]-bounds[1]+24
        left = width-72-bubble_width if own else 72
        self.view.coords(text,left+16,top+12)
        rect = self._capsule(left,top,left+bubble_width,top+bubble_height,
                             style.ACCENT_PALE if own else style.SURFACE,
                             style.ACCENT_PALE if own else style.LINE)
        self.view.addtag_withtag(tag,rect)
        self.view.tag_lower(rect,text)
        center = width-41 if own else 41
        path = avatar_path(data_dir(),message.details.get("avatar_asset")) if own else None
        if own and "avatar_asset" not in message.details:
            path = self.options["avatar"]
        photo = None
        if path:
            cache_key = str(path)
            if cache_key not in self.avatars:
                self.avatars[cache_key] = avatar_photo(self,path,34)
            photo = self.avatars[cache_key]
        if photo:
            self.view.create_image(center,y+17,image=photo,tags=tag)
        else:
            self.view.create_oval(center-17,y,center+17,y+34,fill=style.ACCENT if own else "#087e97",outline="",tags=tag)
            letter = name[:1].upper() if name else "?"
            self.view.create_text(center,y+17,text=letter,font=(style.FONT,11,"bold"),fill="#ffffff",tags=tag)
        bottom = top+bubble_height
        if "endpoint" in message.details:
            details = message.details
            summary = tr(f"API · {details.get('model') or '模型未返回'} · {details['elapsed']:.2f} 秒 · 详情")
            link = self.view.create_text(left,bottom+5,text=summary,anchor="nw",width=limit,
                                        font=(style.FONT,8),fill=style.ACCENT,tags=(tag,"detail-link"))
            box=self.view.bbox(link)
            link_bg=self._capsule(box[0]-3,box[1]-1,box[2]+3,box[3]+1,style.SURFACE,"")
            self.view.tag_lower(link_bg,link)
            self.view.tag_bind(link,"<Button-1>",lambda _,d=details: messagebox.showinfo(
                tr("模型调用详情"),tr(self.describe_call(d)),parent=self.winfo_toplevel()))
            bottom = self.view.bbox(link)[3]
        self.view.tag_bind(tag,"<Button-3>",lambda event,m=message:self._message_menu(event,m))
        self.rows.append((rect,text))
        return bottom

    def _draw_empty(self,width,height):
        left,right = max(16,width/2-200),min(width-16,width/2+200)
        y = max(25,height/2-70)
        self._capsule(left,y,right,y+140,style.SURFACE,style.LINE)
        self.view.create_text(width/2,y+35,text=tr("开始一次讨论"),font=(style.FONT,18,"bold"),fill=style.INK)
        self.view.create_text(width/2,y+77,text=tr("点名成员发送消息，或让全体分轮讨论。"),width=right-left-32,
                              font=(style.FONT,10),fill=style.MUTED,justify="center")
        action = self.view.create_text(width/2,y+115,text=tr("填入讨论示例"),fill=style.ACCENT,font=(style.FONT,10))
        self.view.tag_bind(action,"<Button-1>",lambda _:self.suggest("@全体 小团队应该先自动化测试，还是先做代码评审？"))

    def _message_menu(self,event,message):
        def copy(value):
            self.clipboard_clear(); self.clipboard_append(value)
        self.copy_menu.entryconfigure(0,command=lambda:copy(message.body))
        self.copy_menu.entryconfigure(1,state="normal" if "endpoint" in message.details else "disabled",
                                     command=lambda:copy(self.describe_call(message.details)))
        self.copy_menu.tk_popup(event.x_root,event.y_root)

    def load(self,messages):
        self.messages = list(messages)
        self._resize()
        self.schedule_scroll(100)

    def add(self,message,*,auto_fit=True):
        follow = self.options["auto_scroll"] and (message.author=="你" or self.view.yview()[1]>=.98)
        self.messages.append(message)
        self._resize()
        if auto_fit and follow:
            self.schedule_scroll(90)

    def schedule_scroll(self,delay=0):
        if self.scroll_job:
            self.after_cancel(self.scroll_job)
        self.scroll_job = self.after(delay,self.scroll_to_end)

    def scroll_to_end(self):
        self.scroll_job = None
        self.view.yview_moveto(1)

    def destroy(self):
        for event,token in self.wheel_bindings:
            self.winfo_toplevel().unbind(event,token)
        for job in (self.resize_job,self.scroll_job):
            if job:
                self.after_cancel(job)
        super().destroy()
