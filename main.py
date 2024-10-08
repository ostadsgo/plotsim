import os
import tkinter as tk
from tkinter import filedialog, ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import read_signal_csv


class Grid:
    """Handles operations related to grids in the data."""

    def __init__(self, grid_id, grid_dict):
        self.grid_id = grid_id
        self.grid_dict = grid_dict

    def get_grid_dir(self):
        """Get all directories related to the grid."""
        return list(self.grid_dict.get(self.grid_id).keys())

    def get_grid_event(self, dirs):
        """Get all events in a directory."""
        return list(self.grid_dict[self.grid_id][dirs].keys())

    def extract_val(self, dirs, ev):
        """Extract time and amplitude values for a specific event."""
        t = self.grid_dict[self.grid_id][dirs][ev].get("time")
        amp = self.grid_dict[self.grid_id][dirs][ev].get("amp")
        return t, amp


class Plot:
    def __init__(self, master):
        self.fig, self.ax = plt.subplots(2, 1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.colors = {
            i: color for i, color in enumerate(plt.get_cmap("tab10", 10).colors)
        }

    def grid(self):
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="wsen")
        self.canvas.draw()

    def clear(self):
        self.ax[0].cla()

    def draw(self, data, x_label, y_label):
        has_label = False
        self.clear()
        for i, (label, value) in enumerate(data.items()):
            time, amplitude = value
            if label and not label.startswith('_'):
                self.ax[0].plot(time, amplitude, label=label, color=self.colors[i])
                has_label = True
            else:
                self.ax[0].plot(time, amplitude, color=self.colors[i])

        self.ax[0].set_xlabel(x_label)
        self.ax[0].set_xlabel(y_label)
        if has_label:
            self.ax[0].legend()
        self.canvas.draw()


class DataSingelton:
    _instance = None

    cvm_data = {}
    test_data = {}
    sim_combine = {}
    selected_sim_comb = ""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataSingelton, cls).__new__(cls)
        return cls._instance


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
        self.shared_data = DataSingelton()

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
        ttk.Button(path_frame, text="Select R Files Folder", command=self.on_select_folder).grid(
            row=0, column=2
        )

        self.test_path_var = tk.StringVar()
        ttk.Label(path_frame, text="Test CSV path:").grid(row=1, column=0)
        self.test_path_entry = ttk.Entry(path_frame, textvariable=self.test_path_var)
        self.test_path_entry.grid(row=1, column=1)
        ttk.Button(path_frame, text="Select Test File", command=self.on_select_test_file).grid(
            row=1, column=2
        )
        # Applay to all childs
        self.apply_childs(path_frame, sticky="wsen", padx=5, pady=5)

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

        ## -- Plot Frame --
        self.plot = Plot(plot_middle_frame)
        self.plot.grid()

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

    def on_select_folder(self):
        path = filedialog.askdirectory()
        if not path:
            return

        self.r_path_var.set("")
        self.r_path_var.set(path)
        rf = read_signal_csv.R_file(path)
        rf.check_all_dir()
        daq, ev = rf.check_all_dir()
        if not daq:
            self.daq_text_var.set(f"DAQ complete : No\nEvent {ev} missed")
        else:
            self.daq_text_var.set("DAQ complete : Yes")

        # Display Grid
        self.clear_listbox(
            self.grid_listbox, self.direction_listbox, self.event_listbox
        )
        self.grid_data = []

        initial_path = os.path.dirname(os.path.abspath(__file__))
        rf = read_signal_csv.R_file(initial_path)
        grids = rf.find_all_grid()
        grid_tracks = rf.grid_track_dict(grids)
        grid_dict = rf.convert_to_g(grid_tracks)

        for grid_id in grids:
            self.grid_data.append(Grid(grid_id, grid_dict))
            self.grid_listbox.insert(tk.END, f"Grid ID: {grid_id}")

    def on_select_test_file(self):
        filepath = self.ask_open_csv()
        if filepath:
            self.test_path_var.set("")
            self.test_path_var.set(filepath)

    def on_grid_select(self, event):
        grid = self.get_selected_grid()
        if grid:
            directions = grid.get_grid_dir()
            self.clear_insert_listbox(self.direction_listbox, directions)

    def on_direction_select(self, event):
        grid = self.get_selected_grid()
        direction = self.get_selected_direction()
        if grid and direction is not None:
            events = grid.get_grid_event(direction)
            self.clear_insert_listbox(self.event_listbox, events)

    def on_event_select(self, event):
        grid = self.get_selected_grid()
        direction = self.get_selected_direction()
        if grid and direction is not None:
            indices = self.event_listbox.curselection()
            events = self.get_selected_events(indices, grid, direction)
            self.modify_cvm_data(grid, direction, events)
            self.plot.draw(events, "Time", "Amplitude")
        self.select_all_events_var.set(False)

    def on_select_all_events(self):
        if self.select_all_events_var.get():
            self.event_listbox.select_set(0, tk.END)
            grid = self.get_selected_grid()
            direction = self.get_selected_direction()
            if grid and direction is not None:
                indices = self.event_listbox.curselection()
                events = self.get_selected_events(indices, grid, direction)
                self.modify_cvm_data(grid, direction, events)
                self.plot.draw(events, "Time", "Amplitude")
        else:
            self.event_listbox.select_clear(0, tk.END)
            self.shared_data.cvm_data = {}
            self.plot.draw({}, "", "")

    def on_test_select(self, event):
        pass

    def on_testfile_select(self, event):
        pass

    def on_reorder_test_time(self):
        pass

    def layout_config(self, parent, rows=[], columns=[]):
        for row in rows:
            parent.rowconfigure(row[0], weight=row[1])

        for col in columns:
            parent.columnconfigure(col[0], weight=col[1])

    def apply_childs(self, parent, **kwargs):
        for child in parent.winfo_children():
            child.grid_configure(**kwargs)

    def insert_listbox(self, listbox, items):
        for item in items:
            listbox.insert(tk.END, item)

    def clear_listbox(self, *listboxes):
        for listbox in listboxes:
            listbox.delete(0, tk.END)

    def clear_insert_listbox(self, listbox, data):
        self.clear_listbox(listbox)
        self.insert_listbox(listbox, data)
    
    def ask_open_csv(self):
        filepath = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=[("CSV files", "*.csv")],
            multiple=False,
        )
        return filepath

    def get_selected_grid(self):
        selection = self.grid_listbox.curselection()
        if selection:
            return self.grid_data[selection[0]]
    
    def get_selected_direction(self):
        selection = self.direction_listbox.curselection()
        if selection:
            grid = self.get_selected_grid()
            direction = grid.get_grid_dir()[selection[0]]
            return direction

    def get_selected_events(self, indices, grid, direction):
        selected_events = [grid.get_grid_event(direction)[i] for i in indices]
        events = {i: grid.extract_val(direction, i) for i in selected_events}
        return events
    
    def modify_cvm_data(self, grid, direction, events):
        self.shared_data.cvm_data = {"grid": {grid.grid_id: {direction: events}}}
    
   
    




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
