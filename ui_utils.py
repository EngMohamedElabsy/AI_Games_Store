import customtkinter as ctk
import winsound
import threading
import time

try:
    import pygame
    pygame.mixer.init()
except Exception:
    pass

def play_win_sound(is_ai, stop_event, on_finish):
    import os
    import sys
    
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
        user_dir = os.path.dirname(sys.executable)
    else:
        bundle_dir = os.path.dirname(__file__)
        user_dir = bundle_dir
        
    bundle_sound_dir = os.path.join(bundle_dir, "assets", "sounds")
    user_sound_dir = os.path.join(user_dir, "assets", "sounds")
    
    
    user_mp3 = os.path.join(user_sound_dir, "AI Win.mp3" if is_ai else "Human Win.mp3")
    bundle_mp3 = os.path.join(bundle_sound_dir, "AI Win.mp3" if is_ai else "Human Win.mp3")
    wav_file = os.path.join(bundle_sound_dir, "ai_win.wav" if is_ai else "win.wav")
    meme_wav = os.path.join(user_sound_dir, "meme.wav")
    
    target_file = None
    if os.path.exists(user_mp3): target_file = user_mp3
    elif os.path.exists(bundle_mp3): target_file = bundle_mp3
    elif not is_ai and os.path.exists(meme_wav): target_file = meme_wav
    elif os.path.exists(wav_file): target_file = wav_file
    
    played_with_pygame = False
    try:
        if target_file and pygame.mixer.get_init():
            pygame.mixer.music.load(target_file)
            pygame.mixer.music.play()
            played_with_pygame = True
            while pygame.mixer.music.get_busy() and not stop_event.is_set():
                time.sleep(0.1)
            if stop_event.is_set():
                pygame.mixer.music.stop()
    except Exception:
        pass
        
    if not played_with_pygame:
        if target_file:
            winsound.PlaySound(target_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            for _ in range(50):
                if stop_event.is_set():
                    try: winsound.PlaySound(None, winsound.SND_PURGE)
                    except: pass
                    break
                time.sleep(0.1)
        else:
            if is_ai:
                beeps = [(400, 100), (600, 100), (800, 100), (1000, 100), (1200, 300)]
            else:
                try: winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
                except: pass
                beeps = [(523, 150), (659, 150), (784, 150), (1046, 400)]
                
            for freq, dur in beeps:
                if stop_event.is_set(): break
                try: winsound.Beep(freq, dur)
                except: pass
                
    if not stop_event.is_set():
        on_finish()

import random
import os
from PIL import Image
import math

def show_congratulations(parent, message=None, callback=None, is_ai=False):
    stop_event = threading.Event()
    
    def auto_close():
        if overlay.winfo_exists():
            close_overlay()
            
    threading.Thread(target=play_win_sound, args=(is_ai, stop_event, lambda: parent.after(0, auto_close)), daemon=True).start()
    
    if not message:
        if is_ai:
            quotes = [
                "🤖 AI Computed the Perfect Solution!",
                "⚡ Silicon Brain Triumphs!",
                "🧠 Machine Logic Unmatched!",
                "🤖 Algorithm Completed Flawlessly!"
            ]
        else:
            quotes = [
                "🧠 Mastermind Level Unlocked!",
                "🔥 Unstoppable Logic!",
                "✨ Absolute Perfection!",
                "🚀 Cosmic Brainpower Detected!",
                "💎 Brilliant Move, Champion!"
            ]
        message = random.choice(quotes)
    
    overlay = ctk.CTkFrame(parent, fg_color=("#F9F9FB", "#2C2C2E"), corner_radius=20, border_width=1, border_color=("#D1D1D6", "#38383A"))
    overlay.place(relx=0.5, rely=0.5, anchor="center")
    
    icon_name = "ai_win.png" if is_ai else "trophy.png"
    
    import sys
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(__file__)
        
    trophy_path = os.path.join(bundle_dir, "assets", "ui", icon_name)
    if os.path.exists(trophy_path):
        img = Image.open(trophy_path)
        trophy_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
        trophy_container = ctk.CTkFrame(overlay, fg_color="transparent", width=120, height=120)
        trophy_container.pack(pady=(20, 0))
        trophy_container.pack_propagate(False)
        trophy_lbl = ctk.CTkLabel(trophy_container, text="", image=trophy_img)
        trophy_lbl.place(relx=0.5, rely=0.5, anchor="center")
        
        def animate_trophy(step=0):
            if not overlay.winfo_exists(): return
            y_offset = math.sin(step * 0.1) * 0.1
            trophy_lbl.place_configure(rely=0.5 + y_offset)
            parent.after(30, lambda: animate_trophy(step+1))
            
        animate_trophy()
    
    title_text = "AI Wins!" if is_ai else "You Win!"
    title_color = ("#E74C3C", "#E74C3C") if is_ai else ("#000000", "#FFFFFF")
    title_lbl = ctk.CTkLabel(overlay, text=title_text, font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"), text_color=title_color)
    title_lbl.pack(pady=(10, 10))
    
    msg_lbl = ctk.CTkLabel(overlay, text=message, font=ctk.CTkFont(family="Helvetica", size=18), text_color=("#3A3A3C", "#EBEBF5"), wraplength=350)
    msg_lbl.pack(pady=(5, 20), padx=30, expand=True)
    
    sep = ctk.CTkFrame(overlay, height=1, fg_color=("#D1D1D6", "#38383A"))
    sep.pack(fill="x", padx=0, pady=0)
    
    def close_overlay():
        stop_event.set()
        try: winsound.PlaySound(None, winsound.SND_PURGE)
        except: pass
        
        if overlay.winfo_exists():
            overlay.place_forget()
            overlay.destroy()
        if callback:
            callback()
        
    btn = ctk.CTkButton(overlay, text="Play Again", height=50, font=("Helvetica", 20, "bold"), 
                        fg_color="transparent", hover_color=("#E5E5EA", "#3A3A3C"), text_color="#007AFF", corner_radius=0,
                        command=close_overlay)
    btn.pack(fill="x")
    
    def animate_popup(step=0):
        progress = step / 20.0
        ease = 1 - (1 - progress) ** 3
        
        # Avoid strictly limiting relheight so the button isn't clipped
        # We can just slide it up from rely=0.6 to rely=0.5 and fade in if opacity was supported
        # But for scaling, we scale relwidth and let height be automatic (by not setting relheight)
        w = 0.2 + ease * 0.25
        
        if step <= 20:
            overlay.place_configure(relwidth=w, rely=0.6 - (ease * 0.1))
            parent.after(16, lambda: animate_popup(step+1))
            
    animate_popup()
    
    # Drag functionality
    def start_move(event):
        overlay._drag_start_x = event.x_root
        overlay._drag_start_y = event.y_root
        overlay._start_relx = float(overlay.place_info().get('relx', 0.5))
        overlay._start_rely = float(overlay.place_info().get('rely', 0.5))

    def on_motion(event):
        if getattr(overlay, '_drag_start_x', None) is not None:
            dx = event.x_root - overlay._drag_start_x
            dy = event.y_root - overlay._drag_start_y
            
            parent_w = parent.winfo_width()
            parent_h = parent.winfo_height()
            if parent_w == 0 or parent_h == 0: return
            
            new_relx = overlay._start_relx + (dx / parent_w)
            new_rely = overlay._start_rely + (dy / parent_h)
            
            overlay.place_configure(relx=new_relx, rely=new_rely)

    # Bind to overlay and its non-interactive children
    widgets_to_bind = [overlay, title_lbl, msg_lbl]
    if os.path.exists(trophy_path):
        widgets_to_bind.extend([trophy_container, trophy_lbl])
        
    for w in widgets_to_bind:
        w.bind("<ButtonPress-1>", start_move)
        w.bind("<B1-Motion>", on_motion)
