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
        # self.rowconfigure(0, weight=1)
        # self.rowconfigure(1, weight=100)
        # self.columnconfigure(0, weight=1)
        self.layout_config(self, rows=[(0, 1), (1, 100)], columns=[(0, 1)])
        # -- Methods --
        self.ui()

    def ui(self):
        # -- Path Frame --
        path_frame = ttk.Frame(self, relief="solid", padding=(5, 5))
        path_frame.grid(row=0, column=0, sticky="wsen")

        # Layout :: path_frame
        # path_frame.rowconfigure(0, weight=1)
        # path_frame.rowconfigure(1, weight=1)
        # path_frame.columnconfigure(0, weight=1)
        # path_frame.columnconfigure(1, weight=10)
        # path_frame.columnconfigure(2, weight=1)
        self.layout_config(
            path_frame, rows=[(0, 1), (1, 1)], columns=[(0, 1), (1, 10), (2, 1)]
        )

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
        # for child in path_frame.winfo_children():
        #     child.grid_configure(sticky="wesn", padx=5, pady=5)
        self.apply_childs(path_frame, sticky="wsen", padx=5, pady=5)

        ## -- Plot Frame --
        plot_frame = ttk.Frame(self, relief="solid", padding=(5, 5))
        plot_frame.grid(row=1, column=0, sticky="wsen")
        # Layout config
        # plot_frame.rowconfigure(0, weight=1)
        # plot_frame.columnconfigure(0, weight=1)
        # plot_frame.columnconfigure(1, weight=20)
        # plot_frame.columnconfigure(2, weight=1)
        self.layout_config(plot_frame, rows=[(0, 1)], columns=[(0, 1), (0, 20), (2, 1)])

        # Frames
        plot_left_frame = ttk.Frame(plot_frame, relief="sunken")
        plot_middle_frame = ttk.Frame(plot_frame, relief="solid")
        plot_right_frame = ttk.Frame(plot_frame, relief="solid")
        plot_left_frame.grid(row=0, column=0, sticky="wsen")
        plot_middle_frame.grid(row=0, column=1, sticky="wsen")
        plot_right_frame.grid(row=0, column=2, sticky="wsen")

        ## Plot Left Frame
        # Layout config
        # plot_left_frame.rowconfigure(0, weight=1)
        # plot_left_frame.rowconfigure(1, weight=1)
        # plot_left_frame.rowconfigure(2, weight=10)
        # plot_left_frame.rowconfigure(3, weight=10)
        # plot_left_frame.rowconfigure(4, weight=10)
        # plot_left_frame.columnconfigure(0, weight=1)
        self.layout_config(
            self, rows=[(0, 1), (1, 1), (2, 10), (3, 10), (4, 10)], columns=[(0, 1)]
        )
        # Widgets
        ttk.Label(
            plot_left_frame, text="CVM/Simulation DATA", font=("Arial", 14, "bold")
        ).grid(row=0, column=0)
        ttk.Label(plot_left_frame, text="DAQ complete: None").grid(row=1, column=0)
        # Left List Boxes
        listbox_grid = tk.Listbox(plot_left_frame, exportselection=False)
        listbox_direction = tk.Listbox(plot_left_frame, exportselection=False)
        listbox_event = tk.Listbox(
            plot_left_frame, exportselection=False, selectmode=tk.MULTIPLE
        )
        listbox_grid.grid(row=2, column=0)
        listbox_direction.grid(row=3, column=0)
        listbox_event.grid(row=4, column=0)

        # Apply to all childs
        # for child in plot_left_frame.winfo_children():
        #     child.grid_configure(sticky="wesn", padx=5, pady=5)
        self.apply_childs(plot_left_frame, sticky="wsen", padx=5, pady=5)

    def select_folder(self):
        pass

    def layout_config(self, parent, rows=[], columns=[]):
        for row in rows:
            parent.rowconfigure(row[0], weight=row[1])

        for col in columns:
            parent.columnconfigure(col[0], weight=col[1])

    def apply_childs(self, parent, **kwargs):
        for child in parent.winfo_children():
            child.grid_configure(**kwargs)


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
