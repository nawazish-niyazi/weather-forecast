def main():
    try:
        import tkinter as tk
        from ui import WeatherUI
        import config
        
        root = tk.Tk()
        app = WeatherUI(root)
        
        # Centers the window (Optional, but looks better)
        window_width = 500
        window_height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        root.mainloop()
    except Exception as e:
        import sys
        import traceback
        error_msg = f"CRITICAL STARTUP ERROR:\n\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        try:
            import tkinter.messagebox as mb
            temp_root = tk.Tk()
            temp_root.withdraw()
            mb.showerror("Application Error", error_msg)
            temp_root.destroy()
        except:
            pass # If tkinter fails, we already printed to console

if __name__ == "__main__":
    main()
