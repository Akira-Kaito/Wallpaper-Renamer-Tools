import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from wallpaper_renamer.ui.ui_display import WallpaperRenamerApp, set_window_icon
import customtkinter as ctk

if __name__ == '__main__':
    root = ctk.CTk()
    set_window_icon(root)
    app = WallpaperRenamerApp(root)
    root.mainloop()