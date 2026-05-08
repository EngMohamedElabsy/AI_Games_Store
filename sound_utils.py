import threading
import os

_pygame_initialized = False
try:
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    import pygame
    pygame.mixer.init()
    _pygame_initialized = True
except:
    import winsound

def _play_sound(sound_type):
    if _pygame_initialized:
        try:
            import sys
            if getattr(sys, 'frozen', False):
                bundle_dir = sys._MEIPASS
            else:
                bundle_dir = os.path.dirname(__file__)
            assets_dir = os.path.join(bundle_dir, "assets", "sounds")
            path = os.path.join(assets_dir, f"{sound_type}.mp3")
            if os.path.exists(path):
                pygame.mixer.Sound(path).play()
                return
        except:
            pass
            
    # Fallback to winsound
    try:
        import winsound
        if sound_type == "move":
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        elif sound_type == "error":
            winsound.MessageBeep(winsound.MB_ICONHAND)
        elif sound_type == "slide":
            winsound.MessageBeep(winsound.MB_OK)
    except:
        pass

def play_move_sound():
    threading.Thread(target=_play_sound, args=("move",), daemon=True).start()

def play_error_sound():
    threading.Thread(target=_play_sound, args=("error",), daemon=True).start()

def play_slide_sound():
    threading.Thread(target=_play_sound, args=("slide",), daemon=True).start()
