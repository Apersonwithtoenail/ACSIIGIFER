#!/usr/bin/env python3
"""asciigif — chafa + original view inside a GTK window."""

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gtk, Gdk, GLib, Vte, Pango

import os, glob, random, configparser, signal

import platform

IS_MAC = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"

if IS_MAC:
    MONO_FONT = "Menlo"
elif IS_WINDOWS:
    MONO_FONT = "Consolas"
else:
    MONO_FONT = "DejaVu Sans Mono"

if IS_MAC or IS_WINDOWS:
    _default_dir = os.path.expanduser("~/Pictures/gifs")
else:
    _default_dir = os.path.expanduser("~/Videos/GIF")

APP = "asciigif"
VER = "5.3"
GIF_DIR = os.environ.get("ASCIIGIF_DIR", _default_dir)
CONF = os.path.expanduser("~/.config/asciigif.conf")

SYMBOLS = ["all", "block", "braille", "ascii", "space", "technical", "geometric"]

CSS = b"""
window { background: #1e1e2e; }
.sidebar { background: #181825; }
label.title { color: #89b4fa; font-size: 18pt; font-weight: bold; }
label.sub   { color: #a6adc8; font-size: 9pt; }
label.info  { color: #6c7086; font-size: 8pt; }
label.section { color: #f9e2af; font-size: 10pt; font-weight: bold; margin-top: 8px; }
button.menu {
    background: #313244; color: #cdd6f4;
    border: none; border-radius: 8px;
    padding: 10px 14px; font-size: 11pt; margin: 3px 0;
}
button.menu:hover  { background: #45475a; }
button.menu:active { background: #89b4fa; color: #1e1e2e; }
combobox button { background: #313244; color: #cdd6f4; border: none; border-radius: 6px; }
scale trough { background: #313244; border-radius: 4px; min-height: 6px; }
scale highlight { background: #89b4fa; border-radius: 4px; }
"""


def media_files():
    out = []
    for ext in ("*.gif", "*.mp4", "*.webm", "*.mkv", "*.mov"):
        out += glob.glob(os.path.join(GIF_DIR, ext))
    return sorted(out)


class Settings:
    def __init__(self):
        self.symbols = "all"
        self.font_size = 11
        self.load()

    def save(self):
        c = configparser.ConfigParser()
        c["main"] = {"symbols": self.symbols, "font_size": str(self.font_size)}
        try:
            os.makedirs(os.path.dirname(CONF), exist_ok=True)
            with open(CONF, "w") as f:
                c.write(f)
        except Exception:
            pass

    def load(self):
        if not os.path.exists(CONF):
            return
        c = configparser.ConfigParser()
        try:
            c.read(CONF)
            if "main" in c:
                self.symbols = c["main"].get("symbols", self.symbols)
                self.font_size = c["main"].getint("font_size", self.font_size)
        except Exception:
            pass


class OriginalView(Gtk.DrawingArea):
    """Plays a GIF with GdkPixbuf — pixel-perfect, no ASCII."""

    def __init__(self):
        super().__init__()
        self.set_can_focus(True)
        self.anim = None
        self.iter = None
        self.timer = None
        self._static = False

    def load(self, path):
        self.stop()
        try:
            from gi.repository import GdkPixbuf
            self.anim = GdkPixbuf.PixbufAnimation.new_from_file(path)
            try:
                self._static = self.anim.is_static_image()
            except Exception:
                self._static = False
            self.iter = self.anim.get_iter(None)
        except Exception as e:
            print("anim err:", e)
            self.anim = None
            self.iter = None
            return False
        self.queue_draw()
        self._schedule()
        return True

    def stop(self):
        if self.timer:
            GLib.source_remove(self.timer)
            self.timer = None

    def _schedule(self):
        if not self.iter or self._static:
            return
        try:
            d = self.iter.get_delay_time()
        except Exception:
            d = 100
        if not d or d <= 0:
            d = 100
        self.timer = GLib.timeout_add(max(d, 33), self._next)

    def _next(self):
        if not self.iter:
            return False
        try:
            self.iter.advance(None)
        except Exception:
            pass
        self.queue_draw()
        self._schedule()
        return False

    def do_draw(self, cr):
        from gi.repository import Gdk, GdkPixbuf
        w = self.get_allocated_width()
        h = self.get_allocated_height()
        cr.set_source_rgb(0.04, 0.04, 0.07)
        cr.paint()

        if not self.iter:
            cr.set_source_rgb(0.65, 0.68, 0.78)
            cr.select_font_face("Sans")
            cr.set_font_size(14)
            t = "Pick a GIF to start"
            e = cr.text_extents(t)
            cr.move_to((w - e.width) / 2, h / 2)
            cr.show_text(t)
            return

        try:
            pb = self.iter.get_pixbuf()
        except Exception:
            return
        if not pb:
            return

        pw, ph = pb.get_width(), pb.get_height()
        if pw <= 0 or ph <= 0:
            return

        scale = min(w / pw, h / ph)
        dw = max(1, int(pw * scale))
        dh = max(1, int(ph * scale))
        x = (w - dw) // 2
        y = (h - dh) // 2

        scaled = pb.scale_simple(dw, dh, GdkPixbuf.InterpType.BILINEAR)
        Gdk.cairo_set_source_pixbuf(cr, scaled, x, y)
        cr.paint()


class App(Gtk.Window):
    def __init__(self):
        super().__init__(title=f"{APP} v{VER}")
        self.set_default_size(1200, 720)
        self.s = Settings()
        self.pid = None
        self.file = None
        self.view_mode = "ascii"
        self._alloc_timer = None

        p = Gtk.CssProvider()
        p.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), p,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(root)

        # ---------- Sidebar ----------
        side = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.sidebar = side
        side.get_style_context().add_class("sidebar")
        side.set_size_request(240, -1)
        side.set_margin_start(12); side.set_margin_end(12)
        side.set_margin_top(12); side.set_margin_bottom(12)
        root.pack_start(side, False, False, 0)

        t = Gtk.Label(label="🎬  asciigif")
        t.get_style_context().add_class("title")
        t.set_xalign(0)
        side.pack_start(t, False, False, 4)

        s = Gtk.Label(label="chafa in a real window")
        s.get_style_context().add_class("sub")
        s.set_xalign(0)
        side.pack_start(s, False, False, 12)

        self.mkbtn(side, "🎲   Random GIF",   self.random_gif)
        self.mkbtn(side, "📁   Browse GIFs",  self.browse_gif)
        self.mkbtn(side, "⏹   Stop",           self.stop)

        self.view_btn = Gtk.Button(label="🎨   View: ASCII")
        self.view_btn.get_style_context().add_class("menu")
        self.view_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.view_btn.set_can_focus(False)
        self.view_btn.connect("clicked", lambda *_: self.toggle_view())
        side.pack_start(self.view_btn, False, False, 0)

        self.mkbtn(side, "⛶    Fullscreen",   self.fullscreen_toggle)

        lbl = Gtk.Label(label="🎨  Symbols")
        lbl.get_style_context().add_class("section")
        lbl.set_xalign(0)
        side.pack_start(lbl, False, False, 0)

        self.combo = Gtk.ComboBoxText()
        for n in SYMBOLS:
            self.combo.append_text(n)
        self.combo.set_active(SYMBOLS.index(self.s.symbols))
        self.combo.connect("changed", self.on_symbols)
        side.pack_start(self.combo, False, False, 2)

        side.pack_start(Gtk.Label(), False, False, 6)
        self.mkbtn(side, "❌   Quit", Gtk.main_quit)

        self.info = Gtk.Label(label=f"📂  {GIF_DIR}")
        self.info.get_style_context().add_class("info")
        self.info.set_xalign(0)
        self.info.set_line_wrap(True)
        side.pack_end(self.info, False, False, 0)

        # ---------- Terminal + Original (Stacked) ----------
        self.term = Vte.Terminal()
        self.term.set_scroll_on_output(False)
        self.term.set_scroll_on_keystroke(False)
        self.term.set_scrollback_lines(0)
        self.term.set_font(Pango.FontDescription.from_string(
            f"DejaVu Sans Mono {self.s.font_size}"))

        bg = Gdk.RGBA(); bg.parse("#0a0a12")
        fg = Gdk.RGBA(); fg.parse("#cdd6f4")
        palette = ["#45475a","#f38ba8","#a6e3a1","#f9e2af",
                   "#89b4fa","#f5c2e7","#94e2d5","#bac2de",
                   "#585b70","#f38ba8","#a6e3a1","#f9e2af",
                   "#89b4fa","#f5c2e7","#94e2d5","#a6adc8"]
        colors = []
        for h in palette:
            c = Gdk.RGBA(); c.parse(h)
            colors.append(c)
        self.term.set_colors(fg, bg, colors)
        self.term.set_color_background(bg)
        self.term.set_color_foreground(fg)
        self.term.connect("child-exited", self._child_exit)
        self.term.connect("size-allocate", self._on_term_alloc)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.add_named(self.term, "ascii")
        self.original = OriginalView()
        self.stack.add_named(self.original, "original")
        root.pack_start(self.stack, True, True, 0)

        self.connect("key-press-event", self._key)
        self.connect("destroy", Gtk.main_quit)
        self.show_all()

        GLib.idle_add(self._idle_banner)

    def mkbtn(self, parent, text, cb):
        b = Gtk.Button(label=text)
        b.get_style_context().add_class("menu")
        b.set_relief(Gtk.ReliefStyle.NONE)
        b.set_can_focus(False)
        b.connect("clicked", lambda *_: cb())
        parent.pack_start(b, False, False, 0)

    # ---------- Process mgmt ----------
    def _run(self, argv):
        self._kill()
        GLib.timeout_add(60, self._try_spawn, argv)

    def _try_spawn(self, argv, tries=0):
        if self.pid:
            if tries < 25:
                GLib.timeout_add(60, self._try_spawn, argv, tries + 1)
            return False
        try:
            r = self.term.spawn_async(
                Vte.PtyFlags.DEFAULT, None, argv,
                None, GLib.SpawnFlags.DEFAULT, None, None, -1, None, None)
        except Exception as e:
            print("spawn err:", e)
            return False
        if r is None:
            if tries < 25:
                GLib.timeout_add(60, self._try_spawn, argv, tries + 1)
            return False
        self.pid, _ = r
        return False

    def _kill(self):
        if self.pid:
            try:
                os.kill(self.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            except Exception as e:
                print("kill err:", e)
            self.pid = None

    def _child_exit(self, term, status):
        self.pid = None

    # ---------- Playback ----------
    def _cell_size(self):
        """Approx pixel size of one mono cell."""
        fs = self.s.font_size
        try:
            m = self.term.create_pango_context().get_metrics(
                Pango.FontDescription.from_string(
                    f"DejaVu Sans Mono {fs}"), None)
            cw = max(4, int(m.get_approximate_char_width() / Pango.SCALE))
            ch = max(8, int(m.get_height() / Pango.SCALE))
        except Exception:
            cw, ch = fs // 2 + 1, fs + 3
        return cw, ch

    def _grid_size(self, path=None):
        """Return cols/rows that FIT path inside the widget, preserving aspect."""
        try:
            alloc = self.stack.get_allocation()
            if not alloc or alloc.width < 50:
                alloc = self.term.get_allocation()
        except Exception:
            alloc = None
        W = (alloc.width if alloc else 0) or (self.get_allocated_width() - 260)
        H = (alloc.height if alloc else 0) or self.get_allocated_height()

        cw, ch = self._cell_size()
        cols_max = max(20, W // cw)
        rows_max = max(10, H // ch)

        # image aspect
        iw, ih = 16, 9
        if path:
            try:
                from PIL import Image
                with Image.open(path) as im:
                    iw, ih = im.size
            except Exception:
                pass

        if iw <= 0 or ih <= 0:
            iw, ih = 16, 9

        # aspect in *cell* units (chars are ~2x taller than wide)
        target = (iw / ih) * (ch / cw)

        if cols_max / rows_max > target:
            rows = rows_max
            cols = max(20, int(rows * target))
        else:
            cols = cols_max
            rows = max(10, int(cols / target))

        return cols, rows

    def play(self, path):
        if not path or not os.path.exists(path):
            return
        self.file = path
        ext = os.path.splitext(path)[1].lower()

        if self.view_mode == "original" and ext == ".gif":
            self._kill()
            self.stack.set_visible_child_name("original")
            self.original.load(path)
            self.info.set_text(f"🖼️  {os.path.basename(path)} (original)")
            return

        # ASCII mode — aspect-correct sizing
        self.original.stop()
        self.stack.set_visible_child_name("ascii")
        cols, rows = self._grid_size(path)
        self._run(["/bin/bash", "-c",
            f"chafa -f symbols --symbols={self.s.symbols} "
            f"--dither=none --color-space=din99d "
            f"--align=center --animate=on --clear "
            f"--size={cols}x{rows} "
            f"'{path}'"])
        self.info.set_text(f"▶  {os.path.basename(path)}  ({cols}x{rows})")


    def toggle_view(self):
        if self.view_mode == "ascii":
            self.view_mode = "original"
            self.view_btn.set_label("🎨   View: Original")
        else:
            self.view_mode = "ascii"
            self.view_btn.set_label("🎨   View: ASCII")
        if self.file:
            self.play(self.file)

    def random_gif(self):
        g = media_files()
        if not g:
            self.info.set_text(f"No files in {GIF_DIR}")
            return
        self.play(random.choice(g))

    def browse_gif(self):
        d = Gtk.FileChooserDialog(title="Pick a file",
            transient_for=self, action=Gtk.FileChooserAction.OPEN)
        d.add_buttons("Cancel", Gtk.ResponseType.CANCEL,
                      "Open", Gtk.ResponseType.OK)
        if os.path.isdir(GIF_DIR):
            d.set_current_folder(GIF_DIR)
        ff = Gtk.FileFilter(); ff.set_name("GIF / Video")
        for e in ("*.gif", "*.mp4", "*.webm", "*.mkv", "*.mov"):
            ff.add_pattern(e)
        d.add_filter(ff)
        if d.run() == Gtk.ResponseType.OK:
            self.play(d.get_filename())
        d.destroy()

    def stop(self):
        self._kill()
        self.original.stop()
        self.stack.set_visible_child_name("ascii")
        self._idle_banner()
        self.info.set_text("⏹  stopped")

    def _idle_banner(self):
        self._run(["/bin/bash", "-c",
            "printf '\\033[2J\\033[H'; "
            "echo; echo '   🎬  asciigif'; echo; "
            "echo '   Click Random GIF or Browse'; echo; "
            "echo '   F11 fullscreen · ESC exit'; echo; "
            "echo '   Space  ASCII / original'; "
            "sleep 999999"])
        return False

    # ---------- Keys ----------
    def fullscreen_toggle(self):
        win = self.get_window()
        if not win:
            return
        if win.get_state() & Gdk.WindowState.FULLSCREEN:
            self.unfullscreen()
            self.sidebar.show()
        else:
            self.fullscreen()
            self.sidebar.hide()
        # Give GTK time to re-layout, then force pty resize + replay
        GLib.timeout_add(250, self._after_fs)

    def _on_term_alloc(self, widget, alloc):
        """Terminal resize -> debounce re-render."""
        if self._alloc_timer:
            GLib.source_remove(self._alloc_timer)
        self._alloc_timer = GLib.timeout_add(450, self._reflow)

    def _reflow(self):
        self._alloc_timer = None
        if self.file and self.view_mode == "ascii":
            self.play(self.file)
        return False

    def _after_fs(self):
        # Wait a bit longer for GTK layout to settle
        GLib.timeout_add(500, self._reflow)
        return False


    def _key(self, w, e):
        if e.keyval == Gdk.KEY_F11:
            self.fullscreen_toggle(); return True
        if e.keyval == Gdk.KEY_Escape:
            self.unfullscreen()
            self.sidebar.show()
            return True
        if e.keyval == Gdk.KEY_F5:
            self.random_gif(); return True
        if e.keyval == Gdk.KEY_space:
            self.toggle_view(); return True
        return False

    def on_symbols(self, combo):
        name = combo.get_active_text()
        if not name:
            return
        self.s.symbols = name
        self.s.save()
        # Re-render current file with new symbols
        if self.file and self.view_mode == "ascii":
            self.play(self.file)
            self.info.set_text(f"🎨  {name}")


if __name__ == "__main__":
    win = App()
    Gtk.main()
