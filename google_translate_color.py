import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def ru(text):
    return text.encode("ascii").decode("unicode_escape")


AUTO = ru("\\u0410\\u0432\\u0442\\u043e\\u043e\\u043f\\u0440\\u0435\\u0434\\u0435\\u043b\\u0435\\u043d\\u0438\\u0435")

LANGUAGES = {
    AUTO: "auto",
    ru("\\u0420\\u0443\\u0441\\u0441\\u043a\\u0438\\u0439"): "ru",
    ru("\\u0410\\u043d\\u0433\\u043b\\u0438\\u0439\\u0441\\u043a\\u0438\\u0439"): "en",
    ru("\\u0418\\u0441\\u043f\\u0430\\u043d\\u0441\\u043a\\u0438\\u0439"): "es",
    ru("\\u0424\\u0440\\u0430\\u043d\\u0446\\u0443\\u0437\\u0441\\u043a\\u0438\\u0439"): "fr",
    ru("\\u041d\\u0435\\u043c\\u0435\\u0446\\u043a\\u0438\\u0439"): "de",
    ru("\\u0418\\u0442\\u0430\\u043b\\u044c\\u044f\\u043d\\u0441\\u043a\\u0438\\u0439"): "it",
    ru("\\u041f\\u043e\\u0440\\u0442\\u0443\\u0433\\u0430\\u043b\\u044c\\u0441\\u043a\\u0438\\u0439"): "pt",
    ru("\\u0423\\u043a\\u0440\\u0430\\u0438\\u043d\\u0441\\u043a\\u0438\\u0439"): "uk",
    ru("\\u041f\\u043e\\u043b\\u044c\\u0441\\u043a\\u0438\\u0439"): "pl",
    ru("\\u0422\\u0443\\u0440\\u0435\\u0446\\u043a\\u0438\\u0439"): "tr",
    ru("\\u041a\\u0438\\u0442\\u0430\\u0439\\u0441\\u043a\\u0438\\u0439"): "zh-CN",
    ru("\\u042f\\u043f\\u043e\\u043d\\u0441\\u043a\\u0438\\u0439"): "ja",
    ru("\\u041a\\u043e\\u0440\\u0435\\u0439\\u0441\\u043a\\u0438\\u0439"): "ko",
    ru("\\u0410\\u0440\\u0430\\u0431\\u0441\\u043a\\u0438\\u0439"): "ar",
    ru("\\u0425\\u0438\\u043d\\u0434\\u0438"): "hi",
    ru("\\u041a\\u0430\\u0437\\u0430\\u0445\\u0441\\u043a\\u0438\\u0439"): "kk",
    ru("\\u0423\\u0437\\u0431\\u0435\\u043a\\u0441\\u043a\\u0438\\u0439"): "uz",
}


class PlaceholderText(tk.Text):
    def __init__(self, parent, placeholder, **kwargs):
        super().__init__(parent, **kwargs)
        self.placeholder = placeholder
        self.placeholder_visible = False
        self.normal_fg = kwargs.get("fg", "#202124")
        self.placeholder_fg = "#80868b"
        self.bind("<FocusIn>", self._hide_placeholder)
        self.bind("<FocusOut>", self._show_placeholder_if_empty)
        self.bind("<Button-1>", self._hide_placeholder)
        self.show_placeholder()

    def show_placeholder(self):
        self.placeholder_visible = True
        self.configure(fg=self.placeholder_fg)
        self.delete("1.0", "end")
        self.insert("1.0", self.placeholder)

    def _hide_placeholder(self, _event=None):
        if self.placeholder_visible:
            self.placeholder_visible = False
            self.configure(fg=self.normal_fg)
            self.delete("1.0", "end")

    def _show_placeholder_if_empty(self, _event=None):
        if not self.get_plain_text().strip():
            self.show_placeholder()

    def get_plain_text(self):
        if self.placeholder_visible:
            return ""
        return self.get("1.0", "end-1c")

    def set_plain_text(self, text):
        self.placeholder_visible = False
        self.configure(fg=self.normal_fg)
        self.delete("1.0", "end")
        self.insert("1.0", text)
        self._show_placeholder_if_empty()


class ColorGoogleTranslator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Color Translate")
        self.geometry("980x640")
        self.minsize(760, 500)
        self.configure(bg="#f6f8fc")

        self.source_language = tk.StringVar(value=AUTO)
        self.target_language = tk.StringVar(value=ru("\\u0410\\u043d\\u0433\\u043b\\u0438\\u0439\\u0441\\u043a\\u0438\\u0439"))
        self.status = tk.StringVar(value=ru("\\u0413\\u043e\\u0442\\u043e\\u0432\\u043e"))

        self._build_styles()
        self._build_ui()
        self.after(250, self.focus_input)

    def _build_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("App.TFrame", background="#f6f8fc")
        self.style.configure("Lang.TCombobox", padding=8)

    def _build_ui(self):
        header = tk.Frame(self, bg="#1a73e8")
        header.pack(fill="x")

        title_line = tk.Frame(header, bg="#1a73e8")
        title_line.pack(fill="x", padx=22, pady=(18, 4))
        tk.Label(
            title_line,
            text="Google Translate",
            bg="#1a73e8",
            fg="white",
            font=("Segoe UI", 24, "bold"),
        ).pack(side="left")
        tk.Label(
            title_line,
            text=ru("\\u0446\\u0432\\u0435\\u0442\\u043d\\u043e\\u0439 Python-\\u043f\\u0435\\u0440\\u0435\\u0432\\u043e\\u0434\\u0447\\u0438\\u043a"),
            bg="#1a73e8",
            fg="#dbe7ff",
            font=("Segoe UI", 11),
        ).pack(side="left", padx=(14, 0), pady=(8, 0))

        accent = tk.Frame(header, bg="#1a73e8")
        accent.pack(fill="x", padx=22, pady=(0, 18))
        for color in ("#4285f4", "#34a853", "#fbbc04", "#ea4335"):
            tk.Frame(accent, bg=color, height=5).pack(side="left", fill="x", expand=True)

        root = ttk.Frame(self, style="App.TFrame")
        root.pack(fill="both", expand=True, padx=22, pady=18)

        controls = ttk.Frame(root, style="App.TFrame")
        controls.pack(fill="x", pady=(0, 12))

        self.source_box = self._language_box(controls, self.source_language)
        self.source_box.pack(side="left", fill="x", expand=True)

        tk.Button(
            controls,
            text="<->",
            command=self.swap_languages,
            bg="#ffffff",
            fg="#1a73e8",
            activebackground="#e8f0fe",
            activeforeground="#174ea6",
            relief="flat",
            font=("Segoe UI", 15, "bold"),
            width=4,
            cursor="hand2",
        ).pack(side="left", padx=12)

        self.target_box = self._language_box(controls, self.target_language)
        self.target_box.pack(side="left", fill="x", expand=True)

        panels = ttk.Frame(root, style="App.TFrame")
        panels.pack(fill="both", expand=True)
        panels.columnconfigure(0, weight=1, uniform="translate")
        panels.columnconfigure(1, weight=1, uniform="translate")
        panels.rowconfigure(0, weight=1)

        left = self._panel(panels, ru("\\u0418\\u0441\\u0445\\u043e\\u0434\\u043d\\u044b\\u0439 \\u0442\\u0435\\u043a\\u0441\\u0442"), "#4285f4")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = self._panel(panels, ru("\\u041f\\u0435\\u0440\\u0435\\u0432\\u043e\\u0434"), "#34a853")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.input_text = PlaceholderText(
            left,
            ru("\\u0412\\u0432\\u0435\\u0434\\u0438\\u0442\\u0435 \\u0442\\u0435\\u043a\\u0441\\u0442 \\u0434\\u043b\\u044f \\u043f\\u0435\\u0440\\u0435\\u0432\\u043e\\u0434\\u0430"),
            wrap="word",
            relief="flat",
            bg="#ffffff",
            fg="#202124",
            insertbackground="#1a73e8",
            selectbackground="#d2e3fc",
            selectforeground="#202124",
            font=("Segoe UI", 15),
            padx=12,
            pady=12,
            undo=True,
        )
        self.input_text.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        self.input_text.bind("<Control-Return>", lambda _event: self.translate())

        self.output_text = self._text_box(right)
        self.output_text.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        self.output_text.configure(state="disabled", bg="#fbfffb")

        footer = ttk.Frame(root, style="App.TFrame")
        footer.pack(fill="x", pady=(14, 0))

        tk.Button(
            footer,
            text=ru("\\u041e\\u0447\\u0438\\u0441\\u0442\\u0438\\u0442\\u044c"),
            command=self.clear_text,
            bg="#ffffff",
            fg="#5f6368",
            activebackground="#f1f3f4",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=18,
            pady=10,
            cursor="hand2",
        ).pack(side="left")

        tk.Button(
            footer,
            text=ru("\\u0412\\u0441\\u0442\\u0430\\u0432\\u0438\\u0442\\u044c"),
            command=self.paste_from_clipboard,
            bg="#ffffff",
            fg="#1a73e8",
            activebackground="#e8f0fe",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=18,
            pady=10,
            cursor="hand2",
        ).pack(side="left", padx=(10, 0))

        tk.Label(
            footer,
            textvariable=self.status,
            bg="#f6f8fc",
            fg="#5f6368",
            font=("Segoe UI", 10),
        ).pack(side="left", padx=16)

        tk.Button(
            footer,
            text=ru("\\u041f\\u0435\\u0440\\u0435\\u0432\\u0435\\u0441\\u0442\\u0438"),
            command=self.translate,
            bg="#1a73e8",
            fg="#ffffff",
            activebackground="#174ea6",
            activeforeground="#ffffff",
            relief="flat",
            font=("Segoe UI", 12, "bold"),
            padx=28,
            pady=11,
            cursor="hand2",
        ).pack(side="right")

    def _language_box(self, parent, variable):
        return ttk.Combobox(
            parent,
            textvariable=variable,
            values=list(LANGUAGES.keys()),
            state="readonly",
            style="Lang.TCombobox",
            font=("Segoe UI", 11),
        )

    def _panel(self, parent, title, color):
        panel = tk.Frame(parent, bg="#ffffff", highlightbackground="#dadce0", highlightthickness=1)
        tk.Frame(panel, bg=color, height=5).pack(fill="x")
        tk.Label(
            panel,
            text=title,
            bg="#ffffff",
            fg="#202124",
            font=("Segoe UI", 12, "bold"),
            anchor="w",
            padx=16,
            pady=12,
        ).pack(fill="x")
        return panel

    def _text_box(self, parent):
        return tk.Text(
            parent,
            wrap="word",
            relief="flat",
            bg="#ffffff",
            fg="#202124",
            insertbackground="#1a73e8",
            selectbackground="#d2e3fc",
            selectforeground="#202124",
            font=("Segoe UI", 15),
            padx=12,
            pady=12,
        )

    def focus_input(self):
        self.input_text.focus_set()
        self.input_text.mark_set("insert", "1.0")

    def paste_from_clipboard(self):
        try:
            text = self.clipboard_get()
        except tk.TclError:
            self.status.set(ru("\\u0411\\u0443\\u0444\\u0435\\u0440 \\u043e\\u0431\\u043c\\u0435\\u043d\\u0430 \\u043f\\u0443\\u0441\\u0442"))
            return
        self.input_text._hide_placeholder()
        self.input_text.insert("insert", text)
        self.focus_input()

    def clear_text(self):
        self.input_text.set_plain_text("")
        self._set_output("")
        self.status.set(ru("\\u0413\\u043e\\u0442\\u043e\\u0432\\u043e"))
        self.focus_input()

    def swap_languages(self):
        source = self.source_language.get()
        target = self.target_language.get()
        if source == AUTO:
            self.status.set(ru("\\u0414\\u043b\\u044f \\u043e\\u0431\\u043c\\u0435\\u043d\\u0430 \\u0432\\u044b\\u0431\\u0435\\u0440\\u0438\\u0442\\u0435 \\u043a\\u043e\\u043d\\u043a\\u0440\\u0435\\u0442\\u043d\\u044b\\u0439 \\u0438\\u0441\\u0445\\u043e\\u0434\\u043d\\u044b\\u0439 \\u044f\\u0437\\u044b\\u043a"))
            return
        self.source_language.set(target)
        self.target_language.set(source)

        original = self.input_text.get_plain_text()
        translated = self.output_text.get("1.0", "end-1c")
        self.input_text.set_plain_text(translated)
        self._set_output(original)
        self.focus_input()

    def translate(self):
        text = self.input_text.get_plain_text().strip()
        if not text:
            self.status.set(ru("\\u0412\\u0432\\u0435\\u0434\\u0438\\u0442\\u0435 \\u0442\\u0435\\u043a\\u0441\\u0442 \\u0434\\u043b\\u044f \\u043f\\u0435\\u0440\\u0435\\u0432\\u043e\\u0434\\u0430"))
            self.focus_input()
            return

        source = LANGUAGES[self.source_language.get()]
        target = LANGUAGES[self.target_language.get()]
        if source == target:
            self._set_output(text)
            self.status.set(ru("\\u042f\\u0437\\u044b\\u043a\\u0438 \\u0441\\u043e\\u0432\\u043f\\u0430\\u0434\\u0430\\u044e\\u0442"))
            return

        self.status.set(ru("\\u041f\\u0435\\u0440\\u0435\\u0432\\u043e\\u0436\\u0443..."))
        threading.Thread(target=self._translate_worker, args=(text, source, target), daemon=True).start()

    def _translate_worker(self, text, source, target):
        try:
            result = google_translate(text, source, target)
        except Exception as error:
            self.after(0, self._show_error, error)
            return
        self.after(0, self._finish_translation, result)

    def _finish_translation(self, result):
        self._set_output(result)
        self.status.set(ru("\\u0413\\u043e\\u0442\\u043e\\u0432\\u043e"))

    def _show_error(self, error):
        self.status.set(ru("\\u041e\\u0448\\u0438\\u0431\\u043a\\u0430 \\u043f\\u0435\\u0440\\u0435\\u0432\\u043e\\u0434\\u0430"))
        messagebox.showerror(
            ru("\\u041d\\u0435 \\u0443\\u0434\\u0430\\u043b\\u043e\\u0441\\u044c \\u043f\\u0435\\u0440\\u0435\\u0432\\u0435\\u0441\\u0442\\u0438"),
            ru("\\u041f\\u0440\\u043e\\u0432\\u0435\\u0440\\u044c\\u0442\\u0435 \\u0438\\u043d\\u0442\\u0435\\u0440\\u043d\\u0435\\u0442 \\u0438 \\u043f\\u043e\\u043f\\u0440\\u043e\\u0431\\u0443\\u0439\\u0442\\u0435 \\u0435\\u0449\\u0435 \\u0440\\u0430\\u0437.\\n\\n") + str(error),
        )

    def _set_output(self, text):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.configure(state="disabled")


def google_translate(text, source, target):
    params = urlencode(
        {
            "client": "gtx",
            "sl": source,
            "tl": target,
            "dt": "t",
            "q": text,
        }
    )
    url = "https://translate.googleapis.com/translate_a/single?" + params
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    with urlopen(request, timeout=15) as response:
        payload = response.read().decode("utf-8")

    data = json.loads(payload)
    chunks = data[0] if data and data[0] else []
    return "".join(part[0] for part in chunks if part and part[0])


if __name__ == "__main__":
    app = ColorGoogleTranslator()
    app.mainloop()
