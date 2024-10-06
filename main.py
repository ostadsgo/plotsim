import tkinter as tk
from tkinter import ttk


class ConvertSignalFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)


class TestVsSimFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)


class ProcessSignalFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)


class ReadSignalFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # -- Fields --

        # Layout Config
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=100)
        self.columnconfigure(0, weight=1)
        # -- Methods --
        self.ui()

    def ui(self):
        # Frames
        path_frame = ttk.Frame(self, relief="solid", padding=(5, 5))
        plot_frame = ttk.Frame(self, relief="solid", padding=(5, 5))
        path_frame.grid(row=0, column=0, sticky="wsen")
        plot_frame.grid(row=1, column=0, sticky="wsen")

        # Layout :: path_frame
        path_frame.rowconfigure(0, weight=1)
        path_frame.rowconfigure(1, weight=1)
        path_frame.columnconfigure(0, weight=1)
        path_frame.columnconfigure(1, weight=10)
        path_frame.columnconfigure(2, weight=1)

        # Widgets :: path_frame
        ttk.Label(path_frame, text="R files folder path:").grid(row=0, column=0)
        self.r_path_entry = ttk.Entry(path_frame)
        self.r_path_entry.grid(row=0, column=1)
        ttk.Button(path_frame, text="Select Folder", command=self.select_folder).grid(
            row=0, column=2
        )
        
        ttk.Label(path_frame, text="Test CSV path:").grid(row=1, column=0)
        self.test_path_entry = ttk.Entry(path_frame)
        self.test_path_entry.grid(row=1, column=1)
        ttk.Button(path_frame, text="Select Folder", command=self.select_folder).grid(
            row=1, column=2
        )
        # Applay to all childs
        for child in path_frame.winfo_children():
            child.grid_configure(sticky="wesn", padx=5, pady=5)

    def select_folder(self):
        pass


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # -- Tabs --
        notebook.add(ReadSignalFrame(notebook), text="Read Signal")
        notebook.add(ProcessSignalFrame(notebook), text="Signal Processing")
        notebook.add(TestVsSimFrame(notebook), text="Test VS Simulation")
        notebook.add(ConvertSignalFrame(notebook), text="Signal Conversion")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Signal Processing App")
        self.minsize(1200, 800)

        # MainFrame
        self.main_frame = MainFrame(self, padding=(5, 5))
        self.main_frame.pack(expand=True, fill="both")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


if __name__ == "__main__":
    root = App()
    root.mainloop()
