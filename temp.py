import os
import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import SpanSelector

import matplotlib.pyplot as plt
import read_signal_csv  # Assuming this is the class where you handle the CSV logic
from decimal import Decimal
import glob
import shutil
import threading
import matplotlib.gridspec as gridspec
import numpy as np

class CSVSignal:
    """Handles operations related to CSV signals."""
    
    def __init__(self, csv_loc, csv_dict, f_name):
        self.csv_loc = csv_loc
        self.csv_dict = csv_dict
        self.f_name = f_name
    
    def convert_g(self):
        """Convert amplitude values to 'g'."""
        amp = self.csv_dict[self.f_name][self.csv_loc]['amp']
        amp_g = [i / 9 for i in amp if i != 0]
        self.csv_dict[self.f_name][self.csv_loc]['amp'] = amp_g
        return self.csv_dict
    
    def extract_val(self):
        """Extract time and amplitude values from the CSV."""
        t = self.csv_dict[self.f_name][self.csv_loc].get('time')
        amp = self.csv_dict[self.f_name][self.csv_loc].get('amp')
        return t, amp
    
    def reorder_time(self, time_list, start_t):
        """Reorder time values starting from a given time."""
        t_delta = Decimal(str(time_list[1])) - Decimal(str(time_list[0]))
        start_t = Decimal(str(start_t))
        # start_t = float(str(start_t))
        # t_delta = float(str(t_delta))
        new_time = [start_t + i * t_delta for i in range(len(time_list))]
        return new_time


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
        t = self.grid_dict[self.grid_id][dirs][ev].get('time')
        amp = self.grid_dict[self.grid_id][dirs][ev].get('amp')
        return t, amp


class Utils:
    """Utility functions for handling file operations."""
    def __init__(self):
        self.complete = 0
        
        
    @staticmethod
    def check_file_creation(f_name):
        """Check file creation time."""
        return os.path.getctime(f_name)
    
    @staticmethod
    def compare_file_current_time(file_create_time, current_time):
        """Compare file creation time with the current time."""
        return file_create_time > current_time
    
    def create_csv_from_s3t_rsp(self, folder_name, file_type):
        """Convert RSP/S3T files to CSV format."""
        rsp_list = self.find_all_rsps(folder_name, file_type)
        return rsp_list
        
    
    @staticmethod
    def find_all_rsps(dirname, file_type):
        """Find all RSP/S3T files in a directory."""
        os.chdir(dirname)
        return glob.glob(file_type)

    @staticmethod
    def process_rsp_file(rsp, flo_path):
        """Process an individual RSP file for conversion."""
        extra_files = []
        rsp_base = os.path.basename(rsp)[:-4]
        sh_rsp, script_rsp, log_rsp = (f"{rsp_base}_{suffix}" for suffix in ["sh_file.sh", "script_file.script", "log_file.log"])
        rsp_full_path = os.path.abspath(rsp)
        extra_files.extend([sh_rsp, script_rsp, log_rsp])
        
        for f in extra_files:
            os.system(f"touch {f}")
        
        shutil.copy("/nobackup/vol01/a504696/rsp_to_csv/rsp_2_csv.sh", sh_rsp)
        shutil.copy("/nobackup/vol01/a504696/rsp_to_csv/rsp_2_csv.script", script_rsp)
        
        # Update and execute shell and script files
        Utils.update_file(sh_rsp, {"script_name": os.path.abspath(script_rsp), "log_file": os.path.abspath(log_rsp), "flo_file": flo_path})
        Utils.update_file(script_rsp, {"rsp_file": rsp_full_path})
        
        os.system(f"./{sh_rsp}")
        
        # Clean up extra files
        for file in extra_files:
            os.remove(file)
        
        
    @staticmethod
    def update_file(file_path, replacements):
        """Update content in a file based on given replacements."""
        with open(file_path) as f:
            content = f.read()
        for key, value in replacements.items():
            content = content.replace(key, value)
        with open(file_path, "w") as f:
            f.write(content)
            
            
            
            




class DataSingelton:
    _instance = None
    
    cvm_data = {}
    test_data = {}
    sim_combine ={}
    selected_sim_comb = ''
    

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataSingelton, cls).__new__(cls)
        return cls._instance






class ReadSignalFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.flag_daq = None
        self.ev_not_exist = None
        self.flag_csv_file = dict()
        self.csv_dict = dict()
        self.csv_old_time = dict()
        self.csv_file = list()
        self.utils = Utils()
        self.file_type = None # This is used for the s3t or rsp conversion
       # global cvm_data
        #global test_data
        # Store grid data with attributes
        self.grid_data = []
        self.csv_point = []
        self.color_dict = {i: color for i, color in enumerate(plt.get_cmap('tab10', 10).colors)}
        # Initialize R_file with the script directory
        initial_path = os.path.dirname(os.path.abspath(__file__))
        self.r_f = read_signal_csv.R_file(initial_path)        
        self.ui()
        # bigger weight means more space
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=10)
       
        self.columnconfigure(0,weight=1)
        
        self.shared_data = DataSingelton()
        print(self.shared_data.cvm_data)
        print(self.shared_data.test_data)
        
        
        
    def ui(self):
        
        # Main frames
        self.top_frame = tk.Frame(self)
        self.top_frame_csv = tk.Frame(self)
        self.middle_frame = tk.Frame(self)        

        # grid all frames
        self.top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.top_frame_csv.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.middle_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Top frame widgets
        self.label = tk.Label(self.top_frame, text="Selected R files Folder Path:")
        self.line_edit = tk.Entry(self.top_frame, width=70)
        self.button = tk.Button(self.top_frame, text="Select R files Folder",  command=self.select_folder)

        # pack the top frame widgets
        self.label.pack(side=tk.LEFT, padx=5)
        self.line_edit.pack(side=tk.LEFT, padx=5, expand=True, fill='both')
        self.button.pack(side=tk.LEFT, padx=5, expand=False, fill='y')
    
        
        # CSV Frame widgets
        self.label_csv = tk.Label(self.top_frame_csv, text="Selected test csv Path:")
        self.line_edit_csv = tk.Entry(self.top_frame_csv, width=74)
        self.button_csv = tk.Button(self.top_frame_csv, text="Select csv file(s)", command=self.select_csv_file)
        
        # Pack CSV frame widgets
        self.label_csv.pack(side=tk.LEFT, padx=5)
        self.line_edit_csv.pack(side=tk.LEFT, padx=5, expand=True, fill='both')                
        self.button_csv.pack(side=tk.LEFT, padx=5, expand=False, fill='y')        
        
        ### Middle Frame
        self.left_frame = tk.Frame(self.middle_frame)
        self.plot_frame = tk.Frame(self.middle_frame)
        self.right_frame_csv = tk.Frame(self.middle_frame)

        # Config the row and column
        self.middle_frame.columnconfigure(0, weight=1)
        self.middle_frame.columnconfigure(1, weight=10)
        self.middle_frame.columnconfigure(2, weight=1)
        self.middle_frame.rowconfigure(0, weight=10)        

        # grid Middle frame frames
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.right_frame_csv.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.plot_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
   
        # Left frame widgest
        
        label_title_r = tk.Label(self.left_frame, text="CVM/Simulation DATA", font=("Arial", 14, "bold"))
        self.label_daq = tk.Label(self.left_frame, text="DAQ complete : None")
        self.listbox_grid = tk.Listbox(self.left_frame, exportselection=False)
        self.listbox_direction = tk.Listbox(self.left_frame, exportselection=False)
        self.listbox_event = tk.Listbox(self.left_frame, exportselection=False, selectmode=tk.MULTIPLE)
        
        # checkbox variable
        self.chck_all_var = tk.BooleanVar() 
        self.checkbox_sl_all = tk.Checkbutton(self.left_frame, text="Check All", variable=self.chck_all_var, 
                               command=self.func_check_all_sig)        
        ## pack left frame widgets
        label_title_r.pack(side="top", pady=5)
        self.label_daq.pack(pady=5)

        # pack all Left frame listboxes
        self.listbox_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox_direction.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  
        self.listbox_event.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.checkbox_sl_all.pack(side=tk.LEFT, padx=5)
        
        # Bind all listboxes for simulation / cvm data
        self.listbox_grid.bind('<<ListboxSelect>>', self.on_listbox_grid_select)
        self.listbox_direction.bind('<<ListboxSelect>>', self.on_listbox_select_dir)
        self.listbox_event.bind('<<ListboxSelect>>', self.on_listbox_event)

        # Plot frame canvas and widgets
        self.fig, self.ax = plt.subplots(2,1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Right_frame_csv widgets
        label_title_csv = tk.Label(self.right_frame_csv, text="CSV/Test DATA", font=("Arial", 14, "bold"))
        self.label_csv_ok = tk.Label(self.right_frame_csv, text="CSV File : None")
        
        self.listbox_csv = tk.Listbox(self.right_frame_csv, exportselection=False, selectmode=tk.MULTIPLE, width=50)
        self.listbox_csv_file = tk.Listbox(self.right_frame_csv, exportselection=False, selectmode=tk.SINGLE, width=50)
        
        # check box variable and widget
        self.reorder_var = tk.BooleanVar()
        self.checkbox_reorder = tk.Checkbutton(self.right_frame_csv, text="Reorder Time", variable=self.reorder_var, 
                               command=self.reorder_csv_time)
        
        # packing all right csv frame widgets
        label_title_csv.pack(side="top", pady=5)
        self.label_csv_ok.pack(pady=5)
        
        self.listbox_csv_file.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox_csv.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.checkbox_reorder.pack(side=tk.LEFT, padx=5)


        # Listbox bind
        self.listbox_csv.bind('<<ListboxSelect>>', self.on_listbox_csv_select)
        self.listbox_csv_file.bind('<<ListboxSelect>>', self.on_listbox_csv_file_select)


    def func_check_all_sig(self):
        
        if self.chck_all_var.get():
            self.listbox_event.select_set(0, tk.END)
            try:
                selected_grid_index = self.listbox_grid.curselection()[0]
                selected_direction_index = self.listbox_direction.curselection()[0]
                selected_event_index = self.listbox_event.curselection()
                selected_grid = self.grid_data[selected_grid_index]
                selected_direction = selected_grid.get_grid_dir()[selected_direction_index]
                selected_events = [selected_grid.get_grid_event(selected_direction)[i] for i in selected_event_index]
                ev_dict = {i: selected_grid.extract_val(selected_direction, i) for i in selected_events}
                #cvm_data = {'grid': {selected_grid.grid_id:{selected_direction:ev_dict}}}
                self.shared_data.cvm_data = {'grid': {selected_grid.grid_id:{selected_direction:ev_dict}}}
                self.plot_data(ev_dict)
            except IndexError:
                pass
        else:
            self.listbox_event.select_clear(0, tk.END)
            ev_dict = {}
            self.shared_data.cvm_data = {}
            self.plot_data(ev_dict)
                



    def reorder_csv_time(self):
        selected_index = self.listbox_csv_file.curselection()[0]
        selected_csv = self.csv_file[selected_index][0] # self.csv_fie contain (file_name complete, basename file_name)
        if self.reorder_var.get():
            if self.csv_point:
                for i in self.csv_point:
                    t, _ = i.extract_val()
                    t_new = i.reorder_time(t, 0)
                    self.csv_dict[selected_csv][i.csv_loc]['time'] = t_new
                    
                self.listbox_csv.selection_clear(0, tk.END)
                self.listbox_csv.selection_anchor(tk.END)
                self.plot_data_csv({})
        else:
            
            if len(self.csv_point) > 0 and len(self.csv_old_time) > 0:
                for i in self.csv_point:
                    t, _ = i.extract_val()
                    
                    t_new = i.reorder_time(t, self.csv_old_time[selected_csv][0])
                    self.csv_dict[selected_csv][i.csv_loc]['time'] = t_new
                self.listbox_csv.selection_clear(0, tk.END) 
                self.listbox_csv.selection_anchor(tk.END)
                self.plot_data_csv({})

                
    def get_all_elements(self, listbox):
        # Get all elements in the Listbox
        all_elements = listbox.get(0, tk.END)
        return all_elements        


        
                    
    def on_listbox_csv_file_select(self, event):
        #global test_data
        
        self.listbox_csv.delete(0, tk.END)
        self.csv_point.clear()
        
        selected_index = self.listbox_csv_file.curselection()[0]
        
        selected_csv = self.csv_file[selected_index][0] # self.csv_fie contain (file_name complete, basename file_name)
        text = "CSV File : Ok!" if self.flag_csv_file[selected_csv] else "CSV file wrong!"
        self.change_label_text(self.label_csv_ok, text)
        if self.flag_csv_file[selected_csv]:
            all_gs = list(self.csv_dict[selected_csv].keys())
            for grid_id in all_gs:
                self.csv_point.append(CSVSignal(grid_id, self.csv_dict, selected_csv))
                display_text = f"Signal Loc: {grid_id}"
                self.listbox_csv.insert(tk.END, display_text)
            
            
            #test_data = {'csv':{}}
            self.shared_data.test_data = {'csv':{}}
        

    def change_label_text(self, label, text):
        label.config(text=text)


    
    def select_folder(self):
        
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.line_edit.delete(0, tk.END)
            self.line_edit.insert(0, folder_path)
            self.r_f = read_signal_csv.R_file(folder_path)
            self.flag_daq, ev = self.r_f.check_all_dir()
            if self.flag_daq != True:
                self.ev_not_exist = ev
            self.display_data()



    def select_csv_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=[("CSV files", "*.csv")], multiple=False) 
        if file_path:
            self.line_edit_csv.delete(0, tk.END)
            self.line_edit_csv.insert(0, file_path)
            flag, text = read_signal_csv.check_csv_format(file_path)
            if file_path not in self.csv_file:
                
                f_ = os.path.basename(file_path)
                v = file_path, f_
                if v not in self.csv_file:
                    if len(self.csv_file) == 0:
                        self.csv_file.append(v)
                    else:
                        self.csv_file.insert(0,v)
                        
            if flag: 
                self.flag_csv_file[file_path] = True
                a_dict = read_signal_csv.pull_csv_data(file_path)
                first_item = list(a_dict.keys())[0]
                one_time = a_dict[first_item].get('time')
                if file_path not in self.csv_old_time:
                    self.csv_old_time[file_path] = one_time
                if file_path not in self.csv_dict:
                    self.csv_dict[file_path] = a_dict
                    self.display_data_csv(file_path)
                else:
                    messagebox.showerror('Error', "This CSV  already exists!")
                    return 0
                    
            else:
                self.flag_csv_file[file_path] = False
                messagebox.showerror('Error incompatible CSV', text)
                return 0
                
                
          


    def display_data(self):
        self.listbox_grid.delete(0, tk.END)
        self.listbox_direction.delete(0, tk.END)
        self.listbox_event.delete(0, tk.END)
        self.grid_data.clear()

        text = "DAQ complete : Yes!" if self.flag_daq else f"DAQ complete : No!\nEvent {self.ev_not_exist} missing!"
        self.change_label_text(self.label_daq, text)
        
        all_gs = self.r_f.find_all_grid()
        g_dict_ = self.r_f.grid_track_dict(all_gs)
        g_dict = self.r_f.convert_to_g(g_dict_)

        for grid_id in all_gs:
            self.grid_data.append(Grid(grid_id, g_dict))
            display_text = f"Grid ID: {grid_id}"
            self.listbox_grid.insert(tk.END, display_text)


    def display_data_csv(self, file_path):
        all_elements = self.get_all_elements(self.listbox_csv_file)
        a_file = os.path.basename(file_path)
        if a_file not in all_elements:
            self.listbox_csv_file.insert(0, a_file)



    def on_listbox_csv_select(self, event):
        #global test_data
        selected_csv_point_index = self.listbox_csv.curselection()
        selected_csv = [self.csv_point[i] for i in selected_csv_point_index]
        csv_sel_dict = {}
        for csv_loc in selected_csv:
            t,amp = csv_loc.extract_val()
            csv_sel_dict[csv_loc.csv_loc] = t,amp
        

        
        
        #test_data = {'csv':csv_sel_dict}
        self.shared_data.test_data = {'csv':csv_sel_dict}
        
        self.plot_data_csv(csv_sel_dict)

    
    def display_any_list_box(self, listbox, item_list):
        listbox.delete(0, tk.END)
        for item in item_list:
            listbox.insert(tk.END, item)
    
    def on_listbox_grid_select(self, event):
        try:
            selected_index = self.listbox_grid.curselection()[0]
            selected_grid = self.grid_data[selected_index]
            
            
            dirs = selected_grid.get_grid_dir()
            self.display_any_list_box(self.listbox_direction, dirs)
        except IndexError:
            pass

    def on_listbox_select_dir(self, event):
        try:
            selected_grid_index = self.listbox_grid.curselection()[0]
            selected_direction_index = self.listbox_direction.curselection()[0]
            selected_grid = self.grid_data[selected_grid_index]
            selected_direction = selected_grid.get_grid_dir()[selected_direction_index]
            
            event_info = selected_grid.get_grid_event(selected_direction)
            self.display_any_list_box(self.listbox_event, event_info)
        except IndexError:
            pass
    
    def on_listbox_event(self, event):
        #global cvm_data
        try:
            selected_grid_index = self.listbox_grid.curselection()[0]
            selected_direction_index = self.listbox_direction.curselection()[0]
            selected_event_index = self.listbox_event.curselection()
            selected_grid = self.grid_data[selected_grid_index]
            selected_direction = selected_grid.get_grid_dir()[selected_direction_index]
            selected_events = [selected_grid.get_grid_event(selected_direction)[i] for i in selected_event_index]
            ev_dict = {i: selected_grid.extract_val(selected_direction, i) for i in selected_events}
            #cvm_data = {'grid': {selected_grid.grid_id:{selected_direction:ev_dict}}}
            self.shared_data.cvm_data = {'grid': {selected_grid.grid_id:{selected_direction:ev_dict}}}
            self.plot_data(ev_dict)
        except IndexError:
            pass


    def plot_data_csv(self, data_dict):
        self.ax[1].cla()  # Clear previous plot
        if not data_dict:
            self.canvas.draw()
            return 0
    
        for i, (k, value) in enumerate(data_dict.items()):
            if i >= 11:
                messagebox.showinfo('Information', 'Maximum number of 9 plots reached!')
                break
    
            t_, amplitude = value
            self.ax[1].plot(t_, amplitude, label=k, color=self.color_dict[i])
    
        # Set the labels and legends
        self.ax[1].set_xlabel("Time")
        self.ax[1].set_ylabel("Amplitude")
        self.ax[1].legend()
    
        # Draw the new plot
        self.canvas.draw()
    
    
    def plot_data(self, data_dict):
        self.ax[0].cla()  # Clear previous plot
        
    
        if not data_dict:
            self.canvas.draw()
            return 0
    
        for i, (k, value) in enumerate(data_dict.items()):
            if i >= 11:
                messagebox.showinfo('Information', 'Maximum number of 9 plots reached!')
                break
    
            t_, amplitude = value
            self.ax[0].plot(t_, amplitude, label=k, color=self.color_dict[i])
    
        # Set the labels and legends
        self.ax[0].set_xlabel("Time")
        self.ax[0].set_ylabel("Amplitude")
        self.ax[0].legend()
    
        # Draw the new plot
        self.canvas.draw()
    
        
class Event_Org():
    def __init__(self):
        pass

    def event_names(self, val):
        event_dict = {'outer_ccw': ['EAST-STRAIGHT', 'NORTH-STRAIGHT', 'CORNER-BUMPS', 'WEST-STRAIGHT'],
                      "Corrugation":['CORRUGATIONS'],
                    'inner_loop':['BELGIAN-BLOCK', 'NORTH-TURN', 'BROKEN-CONCRETE', 'CROSS-DITCHES', 'POTHOLES'],
                    'outer_cw':['WEST-STRAIGHT', 'CORNER-BUMPS',  'NORTH-STRAIGHT', 'EAST-STRAIGHT'], 
                    'Full_DAQ': ['EAST-STRAIGHT', 'NORTH-STRAIGHT', 'CORNER-BUMPS', 'WEST-STRAIGHT', 'CORRUGATIONS', 
                                 'BELGIAN-BLOCK', 'NORTH-TURN', 'BROKEN-CONCRETE', 'CROSS-DITCHES', 'POTHOLES', 
                                 'WEST-STRAIGHT2', 'CORNER-BUMPS2',  'NORTH-STRAIGHT2', 'EAST-STRAIGHT2'],
                    'None':None}
        if val == "Single":
            return "Single"
        elif val not in event_dict:
            return None
        return event_dict.get(val)


    def reorder_time_cvm(self, time_list, start_t):
        #print('time_list', time_list)
        #print('start_t', start_t)
        t2 = str(time_list[1])
        t1 = str(time_list[0])
 
        t_delta = Decimal(t2) - Decimal(t1)
        t_delta = float(t_delta)
        
        
        new_time = list()
        start_t = start_t + t_delta
        for i in time_list:
            new_time.append(start_t)
            start_t += t_delta
        
        return new_time
    
    
    def event_seq_creator(self, event_data, event_seq, grid_id, grid_dir):
    
 
        if event_seq == "Single":
           evt_names= list(event_data.keys())
        else:
            evt_names = self.event_names(event_seq)
      
        new_data = {grid_id:{}}
        new_data[grid_id] = {grid_dir:{}}
        new_data[grid_id][grid_dir] = {event_seq:{'time':[], 'amp':[]}}

        t_list = list()
        amp_list = list()        

        for ev_count, evt in enumerate(evt_names):
            t_ = event_data.get(evt)[0]
            amp_ = event_data.get(evt)[1]

            t,amp = t_, amp_
            if ev_count == 0:
                t_list.extend(t)
                amp_list.extend(amp)
            if ev_count > 0:
                t = self.reorder_time_cvm(t, t_list[-1])
                t_list.extend(t)
                amp_list.extend(amp)
                

        new_data[grid_id][grid_dir][event_seq].get('time').extend(t_list)
        new_data[grid_id][grid_dir][event_seq].get('amp').extend(amp_list)
        return t_list, amp_list


    def reorder_one_event(self, xdata, ydata, xmin,xmax, flag_first_event):
        min_x, max_x = min(xdata), max(xdata)
        if xmin <= 0:
            xmin = 0
        elif xmin>=max_x:
            index = np.where(xdata == max_x)[0][0]
            xmin = xdata[index-20]
        else:
            xmin = xmin
        
        if xmax >= max_x:
            xmax = max_x
        elif xmax <= 0:
            xmax = xdata[20]
        else:
            xmax = xmax
        
        condition = np.logical_and(xmin < xdata, xdata < xmax)
        # Crop array1 based on the condition
        cropped_array1 = xdata[condition]
        # Apply the same cropping to array2
        cropped_array2 = ydata[condition]
        
        if flag_first_event:
            cropped_array1 = self.reorder_time_cvm(cropped_array1, 0)
        
        return cropped_array1 , cropped_array2
            
        



    def event_seq_creator_on_select(self, event_data, event_seq, grid_id, grid_dir, event_title_time):
        all_changed_event = list(event_title_time.keys())
        
        if event_seq == "Single":
           evt_names= list(event_data.keys())
        else:
            evt_names = self.event_names(event_seq)
      
        new_data = {grid_id:{}}
        new_data[grid_id] = {grid_dir:{}}
        new_data[grid_id][grid_dir] = {event_seq:{'time':[], 'amp':[]}}

        t_list = list()
        amp_list = list()        

        for ev_count, evt in enumerate(evt_names):
            if evt in all_changed_event:
                if ev_count == 0:
                    flag_first_event = True
                else:
                    flag_first_event = False
                t_ = event_data.get(evt)[0]
                amp_ = event_data.get(evt)[1]
                xmin,xmax  = event_title_time.get(evt)
                t_, amp_ = self.reorder_one_event(t_, amp_, xmin,xmax, flag_first_event)
            else:
                t_ = event_data.get(evt)[0]
                amp_ = event_data.get(evt)[1]
            
            
            t,amp = t_, amp_
            if ev_count == 0:
                t_list.extend(t)
                amp_list.extend(amp)
            if ev_count > 0:
                t = self.reorder_time_cvm(t, t_list[-1])
                t_list.extend(t)
                amp_list.extend(amp)
                

        new_data[grid_id][grid_dir][event_seq].get('time').extend(t_list)
        new_data[grid_id][grid_dir][event_seq].get('amp').extend(amp_list)
        return t_list, amp_list


class CvmData():
    def __init__(self, data):
        
        self.grid_id = None
        self.grid_dir = None
        self.num_of_evnts = None
        self.event_dict = dict()
        self.ev_names = list()
        self.data = data
        self.get_grid_id()
        
        
    def get_grid_id(self):
        
       if self.data:
            self.grid_id = list(self.data.get('grid').keys())[0]
            self.grid_dir = list(self.data['grid'].get(self.grid_id).keys())[0]
            self.num_of_evnts = len(self.data['grid'][self.grid_id][self.grid_dir])
            self.event_dict = self.data['grid'][self.grid_id][self.grid_dir]
            self.ev_names = list(self.event_dict.keys())

        
    # def run(self):
    #     self.root.mainloop()
class ProcessSignalFrame(ttk.Frame):
    
    def __init__(self, master, notebook):
        super().__init__(master)
        self.master = master
        self.create_signal_process_tab()
        self.event_org = Event_Org()
        self.reset_buttons = []
        self.test_plot = None
        self.test_sim_plot_data = {}
        
        self.shared_data = DataSingelton()
        
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)
        self.rowconfigure(2, weight=10)
        self.columnconfigure(0, weight=10)
        
    def create_signal_process_tab(self):
        # Process frame create frames
        self.help_frame = tk.Frame(self)
        self.event_comb_frame = tk.Frame(self)
        self.event_single_frame = tk.Frame(self)
        
        # Process frame grid all frames 
        self.help_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.event_comb_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.event_single_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
                
       
        # Create help frame widgets
        self.help_button = tk.Button(self.help_frame, text="Help signal", command=self.help_toplevel)
        self.var = tk.StringVar(value='None')
        self.checkbox_outer_ccw = tk.Radiobutton(self.help_frame, text="outer ccw", value="outer_ccw", variable=self.var, command=self.check_one_chbox)
        self.checkbox_corrugation = tk.Radiobutton(self.help_frame, text="Corrugation", value="Corrugation",variable=self.var, command=self.check_one_chbox)
        self.checkbox_inner_loop = tk.Radiobutton(self.help_frame, text="inner loop", value="inner_loop",variable=self.var, command=self.check_one_chbox)
        self.checkbox_outer_cw = tk.Radiobutton(self.help_frame, text="outer cw", value="outer_cw",variable=self.var, command=self.check_one_chbox)
        self.checkbox_full_daq = tk.Radiobutton(self.help_frame, text="full_DAQ", value="Full_DAQ",variable=self.var, command=self.check_one_chbox)
        self.checkbox_single = tk.Radiobutton(self.help_frame, text="Single", value="Single",variable=self.var, command=self.check_one_chbox)
        self.checkbox_none = tk.Radiobutton(self.help_frame, text="None", value="None",variable=self.var, command=self.check_one_chbox)
        
        
        self.help_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.checkbox_outer_ccw.grid(row=0, column=1, padx=10, pady=10, sticky="ew")  
        self.checkbox_corrugation.grid(row=0, column=2, padx=10, pady=10, sticky="ew") 
        self.checkbox_inner_loop.grid(row=0, column=3, padx=10, pady=10, sticky="ew") 
        self.checkbox_outer_cw.grid(row=0, column=4, padx=10, pady=10, sticky="ew")        
        self.checkbox_full_daq.grid(row=0, column=5, padx=10, pady=10, sticky="ew") 
        self.checkbox_single.grid(row=0, column=6, padx=10, pady=10, sticky="ew")
        self.checkbox_none.grid(row=0, column=7, padx=10, pady=10, sticky="ew")

        # set configure 
        self.event_comb_frame.rowconfigure(0,weight=1)
        self.event_comb_frame.rowconfigure(1,weight=1)
        self.event_comb_frame.columnconfigure(0,weight=1)

        # simulation event in single plot 
        self.fig_event = plt.figure(figsize=(10, 3))
        #self.fig_event = plt.figure()
        self.canvas = FigureCanvasTkAgg(self.fig_event, master=self.event_comb_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="snew")
        
        # set configure 
        self.event_single_frame.rowconfigure(0,weight=1)
        self.event_single_frame.columnconfigure(0,weight=1)        
        
        
        #### figure to combine all signals
        self.fig_combine, self.ax_sim_test = plt.subplots(figsize=(10,3))
        self.canvas_combine = FigureCanvasTkAgg(self.fig_combine, master=self.event_single_frame)
        self.canvas_combine.get_tk_widget().grid(row=0, column=0, sticky="snew")



        self.sim_line, = self.ax_sim_test.plot([], [], label='Combine simulation', color='b')
        self.test_line, = self.ax_sim_test.plot([], [], label='Test', color='r')
        self.ax_sim_test.set_title('Combine simulation versus Test')
        self.ax_sim_test.legend()
        # Create a checkbox
        self.var_test_plot =  tk.BooleanVar()
        self.checkbox_csv_show = tk.Checkbutton(self.event_single_frame, text="Show/Hide test curve",variable=self.var_test_plot, command=self.plot_test_curve)
        self.checkbox_csv_show.grid(row=1, column=0, padx=1, pady=1, sticky="w")         
        self.var_sim_plot =  tk.BooleanVar()
        self.checkbox_sim_hide = tk.Checkbutton(self.event_single_frame, text="Hide Simulation plot",variable=self.var_sim_plot, command=self.hide_sim_plot)
        self.checkbox_sim_hide.grid(row=1, column=0, padx=1, pady=1, sticky="e")
       
        # Create a SpanSelector for sim test plot widget
        self.span_sim_test = SpanSelector(self.ax_sim_test, lambda xmin, xmax, ax=self.ax_sim_test: self.onselect_sim_plot(ax, xmin, xmax), 'horizontal', useblit=True)
               
        # Create a reset button for this plot and position it in the second row
        self.reset_button_sim_test = tk.Button(self.event_single_frame, text="Reset View", command=lambda ax=self.ax_sim_test: self.reset_view_sim_test(ax))
        self.reset_button_sim_test.grid(row=1, column=0, padx=5, pady=5, sticky="n")  # Use grid for positioning
        self.sim_test_original_limit= [((0,0),(0,0)),((0,0),(0,0))]
       


    def hide_sim_plot(self):
        if self.var_sim_plot.get():
            self.sim_test_original_limit.pop(0)
            self.sim_test_original_limit.insert(0, ((0,0), (0,0)))
            self.sim_line.set_visible(False)
            self.canvas_combine.draw()
        else:
            
            x_data = self.sim_line.get_xdata()
            y_data = self.sim_line.get_ydata()            
            min_x,max_x = min(x_data), max(x_data)
            min_y,max_y = min(y_data), max(y_data)

            self.sim_line.set_visible(True)
            self.sim_test_original_limit.pop(0)
            self.sim_test_original_limit.insert(0, ((min_x,max_x), (min_y, max_y)))
            self.canvas_combine.draw()


    def plot_test_curve(self):
        #global test_data
      
    
        selected_csv = {}
        #self.sim_test_original_limit.insert(1, ((0,0), (0,0)))
        if self.var_test_plot.get():
            if self.shared_data.test_data:
                if self.shared_data.test_data['csv']:
                    plot_num = len(self.shared_data.test_data.get('csv'))
                    if plot_num != 1:
                        messagebox.showerror("Warning", "Select only one plot")
                        return
                    selected_csv = self.shared_data.test_data.get('csv')
                else:
                    messagebox.showerror("Warning", "Select a curve")
                    return      
            else:
                messagebox.showerror("Warning", "No test data available")
                return

            csv_title = list(selected_csv.keys())[0]
            time_csv = list(selected_csv.values())[0][0]
            amp_csv =  list(selected_csv.values())[0][1]
            
            if time_csv[0] == 0:
                self.test_line.set_visible(True)

                    
                #self.test_plot = self.ax_row2_evt.plot(time_csv, amp_csv, color='r')
                self.test_line.set_data(time_csv, amp_csv)
                
                x_test_lim = (min(time_csv), max(time_csv))
                y_test_lim = (min(amp_csv), max(amp_csv))
                self.sim_test_original_limit.pop(1)
                self.sim_test_original_limit.insert(1, (x_test_lim, y_test_lim))
                
                self.ax_sim_test.relim()               # Recalculate limits
                self.ax_sim_test.autoscale_view() 
                
                self.canvas_combine.draw()
                
            else:
                messagebox.showerror("Warning", "Use reorder time to start from 0")
            
        else:
            self.sim_test_original_limit.pop(1)
            self.sim_test_original_limit.insert(1, ((0,0), (0,0)))
            self.test_line.set_visible(False)
            self.canvas_combine.draw()

            

            
        

    def check_one_chbox(self):
        print('self.shared_data.cvm_data', self.shared_data.cvm_data)
        #global cvm_data
        val = self.var.get()
        self.shared_data.selected_sim_comb = val
        self.val_cvm_plot =val
        #self.fig_event.clf()
      
        self.event_names = self.event_org.event_names(val)
   
        if val == 'None':
            self.fig_event.clf()
            
            self.sim_line.set_visible(False)
            self.canvas_combine.draw()
            self.canvas.draw()
            if len(self.reset_buttons) > 0:
                for bn in self.reset_buttons:
                    bn.destroy()
            self.sim_test_original_limit.pop(0)
            self.sim_test_original_limit.insert(0, ((0,0), (0,0)))
            return
        
        cvm_data_obj = CvmData(self.shared_data.cvm_data)
        event_dict = cvm_data_obj.event_dict
        grid_id = cvm_data_obj.grid_id
        grid_dir = cvm_data_obj.grid_dir
        self.ev_names = cvm_data_obj.ev_names # list of event names from cvm_data
        ev_not_exists = list()
        

        if val == "Full_DAQ":
            temp_dict = {'EAST-STRAIGHT':'EAST-STRAIGHT2', 'NORTH-STRAIGHT':'NORTH-STRAIGHT2', 
                         'CORNER-BUMPS':'CORNER-BUMPS2', 'WEST-STRAIGHT': 'WEST-STRAIGHT2'}
            for i in temp_dict:
                if i in event_dict:
                   event_dict[temp_dict[i]] = event_dict[i]
                    
            
            
        if val == 'Single':
            if len(event_dict) == 1:
                self.event_names = list(event_dict.keys())
                self.seq_t, self.seq_amp = self.event_org.event_seq_creator(event_dict, val, grid_id, grid_dir)
                x_test_lim = (min(self.seq_t), max(self.seq_t))
                y_test_lim = (min(self.seq_amp), max(self.seq_amp))
                self.sim_test_original_limit.pop(0)
                self.sim_test_original_limit.insert(0, (x_test_lim, y_test_lim))
                self.plot_evnt_comb(event_dict, val, grid_id, grid_dir)
            else:
                messagebox.showerror('Error', f'Select One event\n{len(event_dict)} selected!')
                return
                
                
            
        for i in self.event_names:
            if i not in self.ev_names:
                if not i.endswith("2"):
                    ev_not_exists.append(i)
                
        if len(ev_not_exists) > 0:
            ev_not_found = ','.join(ev_not_exists)
            messagebox.showerror('Error', f'{ev_not_found}')
            return
            
        self.event_dict_com_org =   {k: event_dict[k] for k in event_dict}
        

        self.shared_data.sim_combine = {}
        for i in event_dict:
            max_t,min_t = min(event_dict[i][0]) , max(event_dict[i][0])
            self.shared_data.sim_combine[i] = max_t,min_t
            

        self.seq_t, self.seq_amp = self.event_org.event_seq_creator(event_dict, val, grid_id, grid_dir)
        x_test_lim = (min(self.seq_t), max(self.seq_t))
        y_test_lim = (min(self.seq_amp), max(self.seq_amp))
        self.sim_test_original_limit.pop(0)
        self.sim_test_original_limit.insert(0, (x_test_lim, y_test_lim))        
        self.plot_evnt_comb(event_dict, val, grid_id, grid_dir)


    def clear_first_row(self, ax_plot):
        # Clear each subplot in the first row
        for ax in ax_plot:
            ax.cla()  # Clears the content of the axes



    def plot_evnt_comb(self, event_data, val, grid_id, grid_dir):
        
        
        if not self.shared_data.cvm_data:
            self.canvas.draw()
            self.canvas_combine.draw()
            return 
    
        cvm_data_obj = CvmData(self.shared_data.cvm_data)
        event_dict = cvm_data_obj.event_dict
        to_plot = [i for i in list(event_dict.keys()) if i in self.event_names]
        event_dict2 = {k: event_dict[k] for k in to_plot}

        
        first_row_plots = len(self.event_names)
        if len(self.reset_buttons) > 0:
            for bn in self.reset_buttons:
                bn.destroy()
        
        # Clear the previous figure
        self.fig_event.clf()
        self.ax_row1_evt = []  # Clear previous axes
        self.reset_buttons = []  # Clear previous buttons
        self.span_selectors = []  # Clear previous selectors
        self.original_limits = []  # Clear previous limits
        
        # Create a grid for the plots and buttons
        self.gs_evnt = gridspec.GridSpec(1, first_row_plots)  # Two rows: one for plots, one for buttons
        
        ii = 10
        
        frame_btn = ttk.Frame(self.event_comb_frame)
        frame_btn.grid(row=1, column=0, sticky="ew")
        
        
        for index, ev_ in enumerate(self.event_names):
            value = event_dict2.get(ev_)
            key = ev_
            x = value[0]
            y = value[1]
    
            ax = self.fig_event.add_subplot(self.gs_evnt[0, index])  # First row for plots
            ax.plot(x, y)
            ax.set_title(f"{key}", fontsize=8)
            ax.tick_params(axis='both', which='major', labelsize=8)
    
            # Store the axis for resetting later
            self.ax_row1_evt.append(ax)
            self.original_limits.append((ax.get_xlim(), ax.get_ylim()))
    
            # Create a SpanSelector widget
            span = SpanSelector(ax, lambda xmin, xmax, ax=ax: self.onselect(ax, xmin, xmax, val, grid_id, 
                                                                            grid_dir, event_data), 'horizontal', useblit=True)
            self.span_selectors.append(span)
            
            # Create a reset button for this plot and position it in the second row
            reset_button = tk.Button(frame_btn, text="Reset View", 
                                     command=lambda ax=ax: self.reset_view(ax, val, grid_id, grid_dir, event_data))


            if len(self.event_names) <=5:
                reset_button.pack(side='left', expand=True, padx=100)
            else:
                reset_button.pack(side='left', expand=True, padx=10)

            self.reset_buttons.append(reset_button)
        
        self.fig_event.tight_layout()
        self.sim_line.set_visible(True)
        self.sim_line.set_data(self.seq_t, self.seq_amp)
        self.ax_sim_test.relim()               # Recalculate limits
        self.ax_sim_test.autoscale_view()        
        self.fig_combine.tight_layout()
        self.canvas.draw()
        self.canvas_combine.draw()



    def onselect_sim_plot(self, ax, xmin, xmax):
        """Callback function to handle the range selection."""
 
        ax.set_xlim(xmin, xmax)
        title = ax.get_title()

        ax.figure.canvas.draw()        


    def onselect(self, ax, xmin, xmax, val, grid_id, grid_dir, event_data):
        """Callback function to handle the range selection."""

        ax.set_xlim(xmin, xmax)
        title = ax.get_title()

        ax.figure.canvas.draw()
        if title in self.shared_data.sim_combine:
            self.shared_data.sim_combine[title]= xmin, xmax

        
  
        self.seq_t_onselect, self.seq_amp_onselect = self.event_org.event_seq_creator_on_select(event_data, val, 
                                                                                  grid_id, grid_dir, self.shared_data.sim_combine)
        x_test_lim = (min(self.seq_t_onselect), max(self.seq_t_onselect))
        y_test_lim = (min(self.seq_amp_onselect), max(self.seq_amp_onselect))
        self.sim_test_original_limit.pop(0)
        self.sim_test_original_limit.insert(0, (x_test_lim, y_test_lim))   
        
        self.sim_line.set_visible(True)
        self.sim_line.set_data(self.seq_t_onselect, self.seq_amp_onselect)
        self.ax_sim_test.relim()               # Recalculate limits
        self.ax_sim_test.autoscale_view()        

        self.canvas_combine.draw()
        


    def reset_view(self, ax, val, grid_id, grid_dir, event_data):
        """Reset the plot to the original view."""
        original_xlim, original_ylim = self.original_limits[self.ax_row1_evt.index(ax)]
        
        ax.set_xlim(original_xlim)
        ax.set_ylim(original_ylim)
        title = ax.get_title()
        xmin,xmax = original_xlim
        ax.figure.canvas.draw()
        
        if title in self.shared_data.sim_combine:
            self.shared_data.sim_combine[title]= xmin, xmax
        
        

        
        self.seq_t_onselect, self.seq_amp_onselect = self.event_org.event_seq_creator_on_select(event_data, val, 
                                                                                  grid_id, grid_dir, self.shared_data.sim_combine)
        x_test_lim = (min(self.seq_t_onselect), max(self.seq_t_onselect))
        y_test_lim = (min(self.seq_amp_onselect), max(self.seq_amp_onselect))
        self.sim_test_original_limit.pop(0)
        self.sim_test_original_limit.insert(0, (x_test_lim, y_test_lim))   
        
        self.sim_line.set_visible(True)
        self.sim_line.set_data(self.seq_t_onselect, self.seq_amp_onselect)
        self.ax_sim_test.relim()               # Recalculate limits
        self.ax_sim_test.autoscale_view()        

        self.canvas_combine.draw()

    @classmethod
    def return_sim_test_plot(cls):
        return cls.sim_line, cls.test_line 
        

    def reset_view_sim_test(self, ax):

        limits = self.find_max_min_lim(self.sim_test_original_limit)
        original_xlim, original_ylim = limits
        ax.set_xlim(original_xlim)
        ax.set_ylim(original_ylim) 
        ax.figure.canvas.draw()

    def find_max_min_lim(self, list_max_min):
        max_t=0
        min_t =0
        max_amp =0
        min_amp=0
    
        
        for i in list_max_min:
            for number, j in enumerate(i):
                if number == 0:
                    min_, max_ = j
                    if min_ <= min_t:
                        min_t = min_
                    if max_ >= max_t:
                        max_t = max_
                elif number % 2 == 0:
                    min_, max_ = j
                    if min_ <= min_t:
                        min_t = min_
                    if max_ >= max_t:
                        max_t = max_
                else:
                    min_, max_ = j
                    if min_ <= min_amp:
                        min_amp = min_
                    if max_ >= max_amp:
                        max_amp = max_
        lim = (min_t,max_t), (min_amp, max_amp)
        
        
        return lim
                
        
    
    def help_toplevel(self): 
        text = """
outer_ccw":
    'EAST-STRAIGHT', 'NORTH-STRAIGHT', 'CORNER-BUMPS', 'WEST-STRAIGHT'\n
"Corrugation":
    'CORRUGATIONS'\n
'inner_loop':
    'BELGIAN-BLOCK', 'NORTH-TURN', 'BROKEN-CONCRETE', 'CROSS-DITCHES', 'POTHOLES'\n
'outer_cw':
    'WEST-STRAIGHT', 'CORNER-BUMPS',  'NORTH-STRAIGHT', 'EAST-STRAIGHT'"""
        
        top_level = tk.Toplevel(self.master)
        label = ttk.Label(top_level, text=text)
        label.pack(expand=True, fill='both')


        
class ConvertSignalFrame(ttk.Frame):
    def __init__(self, master, notebook):
        super().__init__(master)     
        self.master = master
        self.utils = Utils()
        
        self.rsp_frame = tk.Frame(self)
        self.rsp_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")  

        # Folder Selection (Top Frame CSV)
        self.label_rsp = tk.Label(self.rsp_frame, text="Selected Folder path:")
        self.label_rsp.pack(side=tk.LEFT, padx=5)

        #### For R files
        self.line_edit_rsp = tk.Entry(self.rsp_frame, width=70)
        self.line_edit_rsp.pack(side=tk.LEFT, padx=5)
        self.button_rsp = tk.Button(self.rsp_frame, text="Select RSP or S3T to convert to CSV", command=self.select_folder)
        self.button_rsp.pack(side=tk.LEFT, padx=5)
        
        self.s3t_var = tk.BooleanVar()
        # Create a checkbox
        self.checkbox_s3t = tk.Checkbutton(self.rsp_frame, text="s3t (rsp if not selected)", variable=self.s3t_var)
        self.checkbox_s3t.pack(side=tk.LEFT, padx=5)         
    
    # Function that runs the task and updates the progress bar

    def select_folder(self):
        
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.line_edit_rsp.delete(0, tk.END)
            self.line_edit_rsp.insert(0, folder_path) 
            if self.s3t_var.get():
                file_type = '*.s3t'
            else:
                file_type = '*.rsp'

            self.file_type = file_type
            self.start_progress_window(file_type, folder_path)

    def run_task(self, progress_var, progress_window, file_type, folder_path, label):
        # Simulating a task with a loop, updating the progress bar
        rsp_files = self.utils.create_csv_from_s3t_rsp(folder_path, file_type)
        """Convert RSP files to CSV format."""
        if not rsp_files:
            messagebox.showerror('Error', 'No such file type found!')
            return None
        
        
        shutil.copy("/nobackup/vol01/a504696/rsp_to_csv/rsp_2_csv.flo", folder_path)
        flo_path = os.path.abspath("rsp_2_csv.flo")
        cc_com = 0
        for n, rsp in enumerate(rsp_files):
            label.config(text= f"{n+1} file of {len(rsp_files)}")
            self.utils.process_rsp_file(rsp, flo_path)
            cc_com += (100 / len(rsp_files)) - 1
            

        
            #progress_var.set(1)
            progress_var.set(cc_com)  # Update progress bar value
            progress_window.update_idletasks()  # Force the GUI to update
    
        # Close the progress window after task is completed
        #progress_window.destroy()
        label.config(text= f"All {len(rsp_files)} files are converted!")
        time.sleep(0.5)
        progress_var.set(100)
        progress_window.after(1000, progress_window.destroy)


    # Function to open a new window with the progress bar
    def start_progress_window(self, file_type, folder_path):
        # Create a new window for the progress bar
        progress_window = tk.Toplevel(self.master.root)
        #progress_window.title("Task in Progress")
        
        # Create a label to show progress text
        label = ttk.Label(progress_window, text="Task is in progress, please wait...")
        label.pack(pady=10)
    
        # Create a variable to store the progress value
        progress_var = tk.IntVar()
    
        # Create the progress bar widget
        progress_bar = ttk.Progressbar(progress_window, length=300, variable=progress_var, maximum=100)
        progress_bar.pack(pady=10)
    
        # Run the task in a separate thread to avoid freezing the UI
        threading.Thread(target=self.run_task, args=(progress_var, progress_window, file_type, folder_path, label), daemon=True).start()
        #task_thread.start()    


class TestVsSim(ttk.Frame):
    def __init__(self, master, notebook):
        super().__init__(master)
        self.master = master
        self.notebook = notebook
        
        # print(prosee_obj.sim_line)
        # print(prosee_obj.test_line)
        self.ui()
        self.master = master

        self.event_org = Event_Org()
        self.reset_buttons = []
        self.test_plot = None
        self.shared_data = DataSingelton()

    def ui(self):

        self.plot_frame = tk.Frame(self)
        self.plot_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.analysis_frame = tk.Frame(self)
        self.analysis_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")        
       
        
        #### figure to combine all signals
        self.fig_combine, self.ax_sim_test = plt.subplots(figsize=(10,3))
        self.canvas_combine = FigureCanvasTkAgg(self.fig_combine, master=self.plot_frame)
        self.canvas_combine.get_tk_widget().grid(row=0, column=0)
        
        #self.ax_row2_evt = self.fig_combine.add_subplot(2, 1, 1)

        self.sim_line, = self.ax_sim_test.plot([], [], label='Combine simulation', color='b')
        self.test_line, = self.ax_sim_test.plot([], [], label='Test', color='r')
        self.ax_sim_test.set_title('Combine simulation versus Test')
        self.ax_sim_test.legend()

       
        # Create a SpanSelector for sim test plot widget
        self.span_sim_test = SpanSelector(self.ax_sim_test, lambda xmin, xmax, ax=self.ax_sim_test: self.onselect_sim_plot(ax, xmin, xmax), 'horizontal', useblit=True)
               
        # Create a reset button for this plot and position it in the second row
        self.reset_button_sim_test = tk.Button(self.plot_frame, text="Update", command=self.update_plot)
        self.reset_button_sim_test.grid(row=1, column=0, padx=5, pady=5, sticky="n")  # Use grid for positioning
        # self.sim_test_original_limit= [((0,0),(0,0)),((0,0),(0,0))]

    def update_plot(self):
        cvm_data_obj = CvmData(self.shared_data.cvm_data)
        event_dict = cvm_data_obj.event_dict
        grid_id = cvm_data_obj.grid_id
        grid_dir = cvm_data_obj.grid_dir
        
        seq_t, seq_amp = self.event_org.event_seq_creator_on_select(event_dict, self.shared_data.selected_sim_comb, 
                                                                                  grid_id, grid_dir, self.shared_data.sim_combine)
        self.sim_line.set_data(seq_t, seq_amp)
        self.sim_line.set_visible(True)
        
        min_x_sim,max_x_sim = min(seq_t), max(seq_t)
        min_y_sim,max_y_sim = min(seq_amp), max(seq_amp)
        
        self.ax_sim_test.set_xlim( min_x_sim,max_x_sim)
        self.ax_sim_test.set_ylim(min_y_sim,max_y_sim)
        # print(self.sim_line)
        # sim_xdata = self.sim_line.get_xdata()
        # sim_ydata = self.sim_line.get_ydata()
        # print(sim_xdata, sim_ydata)
        
        # self.test_line.set_visible(True)
        
        self.canvas_combine.draw()



    def onselect(self, ax, xmin, xmax, val, grid_id, grid_dir, event_data):
        """Callback function to handle the range selection."""

        ax.set_xlim(xmin, xmax)
        title = ax.get_title()

        ax.figure.canvas.draw()
        if title in self.shared_data.sim_combine:
            self.shared_data.sim_combine[title]= xmin, xmax

        
  
        self.seq_t_onselect, self.seq_amp_onselect = self.event_org.event_seq_creator_on_select(event_data, val, 
                                                                                  grid_id, grid_dir, self.shared_data.sim_combine)
        x_test_lim = (min(self.seq_t_onselect), max(self.seq_t_onselect))
        y_test_lim = (min(self.seq_amp_onselect), max(self.seq_amp_onselect))
        self.sim_test_original_limit.pop(0)
        self.sim_test_original_limit.insert(0, (x_test_lim, y_test_lim))   
        
        self.sim_line.set_visible(True)
        self.sim_line.set_data(self.seq_t_onselect, self.seq_amp_onselect)
        self.ax_sim_test.relim()               # Recalculate limits
        self.ax_sim_test.autoscale_view()        

        self.canvas_combine.draw()



class MainFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Create Notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.root = master
        
        # Create Frames for each Tab
        self.read_signal_frame = ReadSignalFrame(self)
        self.signal_processing_frame = ProcessSignalFrame(self, self.notebook)
        self.test_vs_sim_frame = TestVsSim(self, self.notebook)
        self.signal_convert_frame = ConvertSignalFrame(self, self.notebook)   
        
        self.notebook.add(self.read_signal_frame, text="Read Signal")
        self.notebook.add(self.signal_processing_frame, text="Signal Processing")
        self.notebook.add(self.test_vs_sim_frame, text="Test versus Simulation")
        self.notebook.add(self.signal_convert_frame, text="Signal Conversion")    
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0,weight=1)        



        self.signal_processing_frame.rowconfigure(0, weight=1)
        self.signal_processing_frame.columnconfigure(0,weight=1)

        self.test_vs_sim_frame.rowconfigure(0, weight=1)
        self.test_vs_sim_frame.columnconfigure(0,weight=1)

        self.signal_convert_frame.rowconfigure(0, weight=1)
        self.signal_convert_frame.columnconfigure(0,weight=1)
        
        
        
        
        
        
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Signal Processing App")
        #self.geometry("1400x900")
        self.main_frame = MainFrame(self)
        self.main_frame.pack(expand=True, fill='both')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0,weight=1)
        self.minsize(1200, 800)
        

    
if __name__ == "__main__":
    root = App()
    root.mainloop()
