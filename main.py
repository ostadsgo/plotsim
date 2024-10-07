import tkinter as tk
from tkinter import filedialog, ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import read_signal_csv


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
        self.grid_data = []


        # Layout Config
        self.layout_config(self, rows=[(0, 1), (1, 100)], columns=[(0, 1)])
        # -- Methods --
        self.ui()

    def ui(self):
        ## -- Main Frames --
        path_frame = ttk.Frame(self, relief="solid", padding=(5, 5))
        plot_frame = ttk.Frame(self, relief="solid", padding=(5, 5))
        path_frame.grid(row=0, column=0, sticky="wsen")
        plot_frame.grid(row=1, column=0, sticky="wsen")

        ## -- Path Frame --
        # Layout
        self.layout_config(
            path_frame, rows=[(0, 1), (1, 1)], columns=[(0, 1), (1, 100), (2, 1)]
        )
        self.layout_config(plot_frame, rows=[(0, 1)], columns=[(0, 1), (1, 20), (2, 1)])

        # Widgets
        self.r_path_var = tk.StringVar()
        ttk.Label(path_frame, text="R files folder path:").grid(row=0, column=0)
        self.r_path_entry = ttk.Entry(path_frame, textvariable=self.r_path_var)
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
        self.apply_childs(path_frame, sticky="wsen", padx=5, pady=5)

        ## -- Plot Frame --

        # Frames
        plot_left_frame = ttk.Frame(plot_frame, relief="sunken")
        plot_middle_frame = ttk.Frame(plot_frame, relief="solid")
        plot_right_frame = ttk.Frame(plot_frame, relief="solid")
        # Grid
        plot_left_frame.grid(row=0, column=0, sticky="wsen")
        plot_middle_frame.grid(row=0, column=1, sticky="wsen")
        plot_right_frame.grid(row=0, column=2, sticky="wsen")
        # Layout

        ## Plot Left Frame
        # Layout config
        self.layout_config(
            plot_left_frame,
            rows=[(0, 1), (1, 1), (2, 10), (3, 10), (4, 10), (5, 1)],
            columns=[(0, 1)],
        )
        self.layout_config(plot_middle_frame, rows=[(0, 1)], columns=[(0, 1)])
        self.layout_config(
            plot_right_frame,
            rows=[(0, 1), (1, 1), (2, 10), (3, 10), (4, 1)],
            columns=[(0, 1)],
        )
        # Widgets
        self.daq_text_var = tk.StringVar(value=f"DAQ complete : Unknown")
        ttk.Label(
            plot_left_frame, text="CVM/Simulation DATA", font=("Arial", 14, "bold")
        ).grid(row=0, column=0)
        ttk.Label(plot_left_frame, textvariable=self.daq_text_var).grid(row=1, column=0)
        # Left List Boxes
        self.grid_listbox = tk.Listbox(plot_left_frame, exportselection=False)
        self.direction_listbox = tk.Listbox(plot_left_frame, exportselection=False)
        self.event_listbox = tk.Listbox(
            plot_left_frame, exportselection=False, selectmode=tk.MULTIPLE
        )
        self.grid_listbox.grid(row=2, column=0)
        self.direction_listbox.grid(row=3, column=0)
        self.event_listbox.grid(row=4, column=0)
        # Binds
        self.grid_listbox.bind("<<ListboxSelect>>", self.on_grid_select)
        self.direction_listbox.bind("<<ListboxSelect>>", self.on_direction_select)
        self.event_listbox.bind("<<ListboxSelect>>", self.on_event_select)

        self.apply_childs(plot_left_frame, sticky="wsen", padx=5, pady=5)

        # check button
        self.select_all_events_var = tk.BooleanVar()
        ttk.Checkbutton(
            plot_left_frame,
            text="Select All",
            variable=self.select_all_events_var,
            command=self.on_select_all_events,
        ).grid(row=5, column=0)

        ### Plot Middle Frame
        self.fig, self.ax = plt.subplots(2, 1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_middle_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="wsen")
        self.canvas.draw()

        ### Plot Right Frame
        # Widgets
        ttk.Label(
            plot_right_frame, text="CSV/Test DATA", font=("Arial", 14, "bold")
        ).grid(row=0, column=0)
        ttk.Label(plot_right_frame, text="CSV File : None").grid(row=1, column=0)
        csv_listbox = tk.Listbox(
            plot_right_frame, exportselection=False, selectmode=tk.MULTIPLE
        )
        csvfile_listbox = tk.Listbox(
            plot_right_frame, exportselection=False, selectmode=tk.SINGLE
        )
        # Grid
        csv_listbox.grid(row=2, column=0)
        csvfile_listbox.grid(row=3, column=0)
        # Binds
        csv_listbox.bind("<<ListboxSelect>>", self.on_test_select)
        csvfile_listbox.bind("<<ListboxSelect>>", self.on_testfile_select)

        self.apply_childs(plot_right_frame, sticky="wsen", padx=5, pady=5)

        # Checkbutton
        self.reorder_test_time_var = tk.BooleanVar()
        ttk.Checkbutton(
            plot_right_frame,
            text="Reorder Time",
            variable=self.reorder_test_time_var,
            command=self.on_reorder_test_time,
        ).grid(row=4, column=0)

    def select_folder(self):
        path = filedialog.askdirectory()
        if not path:
            return

        self.r_path_var.set("")
        self.r_path_var.set(path)
        rf = read_signal_csv.R_file(path)
        rf.check_all_dir()
        daq, ev =rf.check_all_dir()
        if not daq:
            self.daq_text_var.set(f"DAQ complete : No\nEvent {ev} missed")
        else:
            self.daq_text_var.set("DAQ complete : Yes")

        # Display Data
        # Clear Listboxes
        self.grid_listbox.delete(0, tk.END)
        self.direction_listbox.delete(0, tk.END)
        self.event_listbox.delete(0, tk.END)
        self.grid_data = []

    

    def on_grid_select(self, event):
        pass

    def on_direction_select(self, event):
        pass

    def on_event_select(self, event):
        pass

    def on_select_all_events(self):
        pass

    def on_reorder_test_time(self):
        pass

    def on_test_select(self, event):
        pass

    def on_testfile_select(self, event):
        pass

    def layout_config(self, parent, rows=[], columns=[]):
        for row in rows:
            parent.rowconfigure(row[0], weight=row[1])

        for col in columns:
            parent.columnconfigure(col[0], weight=col[1])

    def apply_childs(self, parent, **kwargs):
        for child in parent.winfo_children():
            child.grid_configure(**kwargs)

    def get_directory(self):
        path = filedialog.askdirectory()
        return path if path else ""


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

        # In my linux closing would'nt terminate python.
        # Properly close the root window.
        master.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.master.quit()
        self.master.destroy()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Signal Processing App")
        self.minsize(1200, 800)

        # MainFrame
        self.main_frame = MainFrame(self, padding=(5, 5))
        self.main_frame.grid(row=0, column=0, sticky="wsen")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


if __name__ == "__main__":
    root = App()
    root.mainloop()
