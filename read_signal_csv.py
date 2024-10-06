#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 11:29:27 2024

@author: a420192
"""
import csv
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import glob
import copy
from scipy.signal import welch
from scipy.signal import butter, filtfilt, find_peaks
import pandas as pd
from decimal import Decimal




class Signal_process:
    def __init__(self, signal_t, signal_amp):
        self.signal_t = signal_t
        self.signal_amp = signal_amp

    # Function for Level Crossing Analysis
    def level_crossings(self, num_levels=500, reference_level_type='mean', gate=0, count_on_level=False):
        
        reference_level = np.mean(self.signal_amp) if reference_level_type == 'mean' else 0
        levels = np.linspace(np.min(self.signal_amp), np.max(self.signal_amp), num_levels)
        
        # Initialize crossing counts
        crossings = {level: 0 for level in levels}
        
        # Count crossings
        for i in range(1, len(self.signal_amp)):
            for level in levels:
                if (self.signal_amp[i-1] < level and self.signal_amp[i] >= level) or (self.signal_amp[i-1] > level and self.signal_amp[i] <= level):
                    crossings[level] += 1
                    
                    
                    
        test_crossing_counts = {level: count for level, count in crossings.items()}
        test_crossing_counts_df = pd.DataFrame(list(test_crossing_counts.items()), columns=['Level', 'CrossingCount'])
        cross_x, level_y = test_crossing_counts_df['CrossingCount'], test_crossing_counts_df['Level']
        
        return cross_x, level_y





############################################################




    def psd(self):

        fs = int(1 / np.mean(np.diff(self.signal_t )))  # Sample frequency
        print(fs)
        #frequencies_test, psd_test = welch(self.signal_amp, fs=fs, nperseg=1024)
        frequencies_test, psd_test = welch(self.signal_amp, fs=fs, nperseg=1024)
        
        return frequencies_test, psd_test
        







class R_file:
    def __init__(self, r_path_folder):
        self.r_path_folder = r_path_folder
        self.node_list=list()
        self.r_folder = str 
        self.track = Track_Event()
    
    

    def read_file(self,f_n):
        with open(f_n) as f:
            cnt = f.read().split('\n')
        return cnt
    
    
    
    def grab_t_amp(self,f_n):
        cnt = self.read_file(f_n)
        time = list()
        amplitude = list()
        for l in cnt:
            if len(l.strip()) >1:
                ll = l.split()
                time.append(float(ll[0]))
                amplitude.append(float(ll[-1]))
        
        time = np.array(time)
        amplitude = np.array(amplitude)
        return time , amplitude


    
    def check_all_dir(self):
        os.chdir(self.r_path_folder) 
        cur_dir = os.getcwd()
        flag = True
        for i in self.track.full_daq:
            sch_path = os.path.join(cur_dir, i)
            if os.path.exists(sch_path):
                flag = True
            else:
                flag = False
                break
        return flag, i
    
    
    
    def find_all_grid(self):
        cur_dir = os.getcwd()
        cor_dir = 'CORRUGATIONS'
        cor_dir_p = os.path.join(cur_dir, cor_dir)
        #./CORRUGATIONS/ACCE20720001_R3.R
        all_gs = list()
        if os.path.exists(cor_dir_p):
            os.chdir(cor_dir_p)
            r_files = glob.glob("*.R")
            for r_f in r_files:
                if r_f.startswith("ACCE"):
                    grid_id = r_f[:-2].split('ACCE')[-1].split('_')[0]
                    if grid_id not in all_gs:
                        all_gs.append(grid_id)
        os.chdir("../")
        return all_gs
                        
            
    def grid_track_dict(self,all_gs):
        cur_dir = os.getcwd()
        dirs = ["T1", "T2", "T3"]
        all_f = list(set(self.track.full_daq))
        g_dict = {}
        
        for g_num in all_gs:
            g_dict[g_num] = {}
            for d in dirs:
                g_dict[g_num][d] = {}
                for folder in all_f:
                    path = os.path.join(cur_dir, folder)
                    if os.path.exists(path):
                        g_dict[g_num][d][folder] = {'time':[], 'amp':[]}
                        os.chdir(path)
                        g_path = f"ACCE{g_num}_{d}.R"
                        if os.path.exists(g_path):
                            t,amp = self.grab_t_amp(g_path)
                            a_list = [t,amp]
                            g_dict[g_num][d][folder]['time']=a_list[0]
                            g_dict[g_num][d][folder]['amp']=a_list[1]
                            os.chdir('../')
        return g_dict    

    

    def reorder_time(self, time_list, start_t):
        t2 = str(time_list[1])
        t1 = str(time_list[0])
 
        t_delta = Decimal(t2) - Decimal(t1)

        
        
        new_time = list()
        start_t = start_t + t_delta
        for i in time_list:
            new_time.append(start_t)
            start_t += t_delta
        
        return new_time
    
    def time_gap(self, time_in_sec, start_t, time_delta):
        number_of_step = int(time_in_sec / time_delta)
  
        new_time = list()
        start_t = start_t + time_delta
        for i in range(number_of_step):
            new_time.append(start_t)
            start_t += time_delta
        
        return new_time    
            
        


    def event_name_func(self,event_name):
        event_list = None
        if event_name == "outer_ccw":
            event_list = ['EAST-STRAIGHT', 'NORTH-STRAIGHT', 'CORNER-BUMPS', 'WEST-STRAIGHT']
        elif event_name == "Corrugation":
            event_list = ['CORRUGATIONS']
        elif event_name == 'inner_loop':
            event_list = ['BELGIAN-BLOCK', 'NORTH-TURN', 'BROKEN-CONCRETE', 'CROSS-DITCHES', 'POTHOLES']
        elif event_name == 'outer_cw':
            event_list = ['WEST-STRAIGHT', 'CORNER-BUMPS',  'NORTH-STRAIGHT', 'EAST-STRAIGHT']
        
        return event_list

    def event_sorter(self, dict_data, event_list):
        # key: 20720001 --> next key : T1, T2,T3  --> next key : 'BROKEN-CONCRETE', 'WEST-STRAIGHT', ... and value time:[] and amp :[] 
        #evnt_list:['EAST-STRAIGHT', 'NORTH-STRAIGHT', 'CORNER-BUMPS', 'WEST-STRAIGHT']
        for g in dict_data:
            for dirs in dict_data.get(g):
                a_dict = dict_data[g][dirs]
                sorted_keys = sorted(a_dict.keys(), key=lambda x: event_list.index(x) if x in event_list else float('inf'))
                sorted_dict = {key: a_dict[key] for key in sorted_keys}
                dict_data[g][dirs] = sorted_dict
        return dict_data
                
    
    def convert_to_g(self, data_dict):
        
        new_dict= copy.deepcopy(data_dict)
        for g in data_dict:
            for dirs in data_dict[g]:
                for ev in data_dict[g][dirs]:
                    amp = data_dict[g][dirs][ev].get('amp')
                    amp_max = max(amp)
                    if amp_max > 100:
                        new_amp = amp / 9810
                        new_dict[g][dirs][ev]['amp'] = new_amp
                        
        

        return new_dict
                    
                    
    def shorten_evnt(self, ev, t, amp):
        shorten_dict = {'EAST-STRAIGHT':[0, 17], 'NORTH-STRAIGHT':[0,12], 
                        'CORNER-BUMPS':[0.1,6], 'WEST-STRAIGHT':[1,22],'CORRUGATIONS':[0.5,14.0],
                        'BELGIAN-BLOCK':[1.2,8], 'NORTH-TURN':[2, 10.2], 
                        'BROKEN-CONCRETE':[0.1, 6.0], 'CROSS-DITCHES':[0.5, 4.8], 'POTHOLES':[0.75, 3.2]}
        
        upper_limit = shorten_dict.get(ev)[1]
        lower_limit = shorten_dict.get(ev)[0]
        new_t = list()
        new_amp = list()

        for value, amp_val in zip(t, amp):
            if value < lower_limit:
                continue
            if value > upper_limit:
                break
            new_t.append(value)
            new_amp.append(amp_val)
            
        
        
        
        new_t2 = self.reorder_time(new_t, 0)
        print(new_t2)
        
        return new_t2, new_amp
                    
                        
        
    
    
    def event_seq_creator(self, dict_data, event_list):
        a_name = "outer_ccw"
        new_data = {k:{'T1':{}, 'T2':{}, 'T3':{}} for k in dict_data}
 
        
        for g in dict_data:
            for dirs in dict_data[g]:
                new_data[g][dirs] = {a_name:{'time':[], 'amp':[]}}
                
   

                t_list = list()
                amp_list = list()

                for ev_count, ev in enumerate(event_list):
                    t_ = dict_data[g][dirs][ev].get('time')
                    print(t_)
                    
                    amp_ = dict_data[g][dirs][ev].get('amp')
                    t,amp = self.shorten_evnt(ev, t_, amp_)
            
                    if ev_count == 0:
                        t_list.extend(t)
                        amp_list.extend(amp)
                    if ev_count > 0:
                        t = self.reorder_time(t, t_list[-1])
                        
                        
                        
                        t_list.extend(t)
                        amp_list.extend(amp)
                    

                new_data[g][dirs][a_name].get('time').extend(t_list)
                new_data[g][dirs][a_name].get('amp').extend(amp_list)
        
        return new_data
                    
                    
            
            




    def create_s3t_fron_r(self):
        
        temp_t = "cmulti *20720001*_T* *20720003*_T* *20720004*_T* *20720005*_T* *20720006*_T* *20720002*_T* "
        all_folder_name = [name for name in os.listdir(".") if os.path.isdir(name)]
        for name in  all_folder_name:
            path = f"./{name}"
            if os.path.exists(path):
                os.chdir(path)
                r_files = glob.glob("*.R")
                if len(r_files) == 0:
                    os.chdir("../")
                    continue
                else:
                    if len(r_files) > 0:
                        os.system(temp_t)
                        os.chdir("../")
        return 0





class Track_Event:
    def __init__(self):
        self.outer_ccw = ['EAST-STRAIGHT', 'NORTH-STRAIGHT', 'CORNER-BUMPS', 'WEST-STRAIGHT']
        self.corrugation = ['CORRUGATIONS']
        self.Inner_loop = ['BELGIAN-BLOCK', 'NORTH-TURN', 'BROKEN-CONCRETE', 'CROSS-DITCHES', 'POTHOLES']
        self.outer_cw = ['WEST-STRAIGHT', 'CORNER-BUMPS',  'NORTH-STRAIGHT', 'EAST-STRAIGHT']
        self.full_daq = self.outer_ccw + self.corrugation + self.Inner_loop + self.outer_cw




def check_csv_format(f_csv):
    flag = True
    with open(f_csv, 'r') as file:
        cnt = file.read().split('\n')
    
    text = """#HEADER
#TITLES
 , ,1_Grillesbar_Drv_Ax,all point name
#UNITS
 , ,g,g,g,g,
#DATATYPES
Huge,Double,
#DATA
1,90.855000,-0.006422924,actual data,
"""
    for n,l in enumerate(cnt):
        if n == 9 :
            break
        if cnt[0].strip() == '#HEADER':
            flag = True
        else:
            flag = False
        
        if cnt[1].strip() == '#TITLES':
            flag = True
        else:
            flag = False
        if ',' in cnt[2]:
            flag = True
        else:
            flag = False
        if cnt[3].strip() == '#UNITS':
            flag = True
        else:
            flag = False
        if ',' in cnt[4]:
            flag = True
        else:
            flag = False            
        if cnt[5].strip() == '#DATATYPES':
            flag = True
        else:
            flag = False
            
        if ',' in cnt[6]:
            flag = True
        else:
            flag = False   
        if cnt[7].strip() == '#DATA':
            flag = True
        else:
            flag = False
            
            
            
        
            
            
        
            
    
        
    return flag, text

        
        
    

       

def pull_csv_data(f_n):

    with open(f_n, 'r') as file:
    # Create a CSV reader object
        reader = csv.reader(file)

        # Skip the first two rows
        next(reader)
        next(reader)
    
        # Extract the headers from the third row
        header_name = next(reader)
    
        # Check if the second column header is empty
        if header_name[1] == '':
            # Rename the second column header
            header_name[1] = 'Time'
    
        # Skip the rows until the ninth row
        for _ in range(5):
            next(reader)
        data_dict = {key: {'time':[], 'amp':[]} for key in header_name[2:]}  
        
        #Iterate over the remaining rows
        for row in reader:
            # Get the time column
            time_column = float(row[1])
    
            # Iterate over the data columns
            for i, data in enumerate(row[2:], start=2):
                header = header_name[i]
                data_column = float(data)
                data_dict[header]['time'].append(time_column)
                data_dict[header]['amp'].append(data_column)
            
    data_dict2 = {}            
    for k, v in data_dict.items():
        t = np.array(v.get('time'))
        amp =np.array(v.get('amp')) 
        data_dict2[k] = {'time':t, 'amp':amp}
        
        
    return data_dict2
    
           
# Function to split dictionary into chunks
def split_dict(input_dict, chunk_size):
    keys = list(input_dict.keys())
    return [{key: input_dict[key] for key in keys[i:i + chunk_size]} for i in range(0, len(keys), chunk_size)]            



def generate_plot_images(data_dict):
    num_plots = len(data_dict)
    num_plot_f = math.ceil(num_plots / 20 )
    
    split_d = split_dict(data_dict, 20)

    f_time = 0
    
    for i in range(num_plot_f):
        the_data = split_d[i]
        fig, axes = plt.subplots(5, 4, figsize=(15, 10))
        cnt_x = 0
        cnt_y = 0
        for counter, (key, value) in enumerate(the_data.items()):
            sig_n = key # Removing file extension
            #dir_n = os.path.basename(os.path.dirname(key))
            title_name = f"{sig_n}"
            t = value.get('time')
            f_time = t[-1]
            amp = value.get('amp')
            ax = axes[cnt_x,cnt_y]
            ax.plot(t,amp)
            ax.set_title(f"{title_name}",fontsize=8)
            cnt_y +=1
            
            if cnt_y % 4 == 0:
                cnt_x +=1
                cnt_y = 0
            
    
        plt.tight_layout()
        plt.show()
        # plot_filename = f"output_subplots_{i}.png"
        # plt.savefig(plot_filename, dpi=300)
        # plt.close(fig)  # Close the figure to free memory
  


def map_signal():
    {"Outer Loop Counter-clockwise" : "CCH",
    "Corrugations" : "CG",
    "Outer Loop Clockwise" : "CWH",
    "Inner Loop" : "IL"}
    outer_ccw = ['EAST-STRAIGHT', 'NORTH-STRAIGHT', 'CORNER-BUMPS', 'WEST-STRAIGHT']
    corrugation = ['CORRUGATIONS']
    Inner_loop = ['BELGIAN-BLOCK', 'NORTH-TURN', 'BROKEN-CONCRETE', 'CROSS-DITCHES', 'POTHOLES']
    outer_cw = ['WEST-STRAIGHT', 'CORNER-BUMPS',  'NORTH-STRAIGHT', 'EAST-STRAIGHT']


if __name__ == "__main__":

    #f_n = '/nobackup/vol01/a420192/GSO/CNA_10476_V1_Bolt_grille/test_result/test_loaded/VHB-11_DAQ_GrilleLoad_HCCH_5-50Hz_rsp_to_csv_out.csv'
    #f_n = '/nobackup/vol01/a420192/GSO/CNA_10476_V1_Bolt_grille/cvm_accel/it3/Loaded/test_data/Loaded/VHB-11_DAQ_GrilleLoad_HCCH_5-50Hz_rsp_to_csv_out.csv'
    #f_n = '/nobackup/vol01/a420192/GSO/CNA_10476_V1_Bolt_grille/cvm_accel/it3/Loaded/test_data/Loaded/VHB-11_DAQ_GrilleLoad_HIL_5-50Hz_rsp_to_csv_out.csv'
    #f_n = '/nobackup/vol01/a420192/GSO/CNA_10476_V1_Bolt_grille/cvm_accel/it3/Loaded/test_data/Loaded/VHB-11_DAQ_GrilleLoad_HCG_5-50Hz_rsp_to_csv_out.csv'
    f_n = '/nobackup/vol01/a420192/GSO/CNA_10476_V1_Bolt_grille/cvm_accel/it3/Loaded/test_data/Loaded/VHB-11_DAQ_GrilleLoad_HCWH_5-50Hz_rsp_to_csv_out.csv'
    data_dict_csv = pull_csv_data(f_n)
    check_csv_format(f_n)
    d
    #generate_plot_images(data_dict)
    r_f = R_file('/nobackup/vol01/a420192/GSO/CNA_10476_V1_Bolt_grille/cvm_accel/it3/Loaded/')
    all_gs = r_f.find_all_grid()
    g_dict_ = r_f.grid_track_dict(all_gs)
    g_dict = r_f.convert_to_g(g_dict_)
    gg = '20720001'
    print(all_gs)
    map_dict = {'20720001':['16_HoodCrossbar_Psg_Ax', '17_HoodCrossbar_Psg_Ay', '18_HoodCrossbar_Psg_Az'], 
                '20720002': ['13_HoodCrossbar_Drv_Ax', '14_HoodCrossbar_Drv_Ay', '15_HoodCrossbar_Drv_Az'], 
                '20720003': ['7_Grille_Drv_UpperMount_Ax', '8_Grille_Drv_UpperMount_Ay', '9_Grille_Drv_UpperMount_Az'], 
                '20720004': ['10_Grille_Psg_UpperMount_Ax', '11_Grille_Psg_UpperMount_Ay', '12_Grille_Psg_UpperMount_Az'], 
                '20720005': ['1_Grille_Drv_LowerMount_Ax', '2_Grille_Drv_LowerMount_Ay', '3_Grille_Drv_LowerMount_Az'], 
                '20720006': ['4_Grille_Psg_LowerMount_Ax', '5_Grille_Psg_LowerMount_Ay','6_Grille_Psg_LowerMount_Az']}




    
    #seq_dict = r_f.event_seq_creator(g_dict, ['EAST-STRAIGHT', 'NORTH-STRAIGHT', 'CORNER-BUMPS', 'WEST-STRAIGHT'])
    #seq_dict = r_f.event_seq_creator(g_dict, ['BELGIAN-BLOCK', 'NORTH-TURN', 'BROKEN-CONCRETE', 'CROSS-DITCHES', 'POTHOLES'])
    #seq_dict = r_f.event_seq_creator(g_dict, ['CORRUGATIONS'])
    seq_dict = r_f.event_seq_creator(g_dict, ['WEST-STRAIGHT', 'CORNER-BUMPS',  'NORTH-STRAIGHT', 'EAST-STRAIGHT'])
    
    fig, axes = plt.subplots(5, 5, figsize=(15, 10),  sharey='row')
    cnt_x = 0
    cnt_y = 0
    for num, ev in enumerate(['WEST-STRAIGHT', 'CORNER-BUMPS',  'NORTH-STRAIGHT', 'EAST-STRAIGHT']):
        x = g_dict.get(gg).get('T3').get(ev).get('time')
        y = g_dict.get(gg).get('T3').get(ev).get('amp')

        titl = ev
        ax = axes[0,num]
        ax.plot(x,y)
        ax.set_title(f"{titl}",fontsize=8)      

    a_name = "outer_ccw"
    t_seq = seq_dict[gg].get('T3').get(a_name).get('time')
    amp_seq = seq_dict[gg].get('T3').get(a_name).get('amp')

    axes[1, 0].remove()
    axes[1, 1].remove()
    axes[1, 2].remove()   
    axes[1, 3].remove()
    axes[1, 4].remove()
    
    big_ax = fig.add_subplot(5, 1, 2)
    big_ax.plot(t_seq, amp_seq, color='red')
    big_ax.set_title('sequence')
    # for k,v in seq_dict.items():
    #     for dirs in v:
    #         t =  seq_dict[k][dirs].get('time')
    #         amp = seq_dict[k][dirs].get('amp')
    #         break
    
    # for x,y in zip(t,amp):
    #     print(x,y)
    
    # plt.plot(t,amp)

    #     # Add labels and title
    # plt.xlabel('X-axis')
    # plt.ylabel('Y-axis')
    # plt.title('Line Plot')

    # # Display the plot
    # plt.show()
    x1 = data_dict_csv.get('1_Grille_Drv_LowerMount_Ax').get('time')
    y1 = data_dict_csv.get('1_Grille_Drv_LowerMount_Ax').get('amp')
    x1_reorder = r_f.reorder_time(x1, 0)
    print(data_dict_csv.keys())
    
    
    axes[2, 0].remove()
    axes[2, 1].remove()
    axes[2, 2].remove()   
    axes[2, 3].remove()
    axes[2, 4].remove()
    
    big_ax = fig.add_subplot(5, 1, 3) # grid arrangment 3 row 1 column position 3 
    big_ax.plot(x1_reorder, y1)
    big_ax.set_title('test data')    
    
    
    # plt.tight_layout()
    # plt.show()

    axes[3, 0].remove()
    axes[3, 1].remove()
    axes[3, 2].remove()   
    axes[3, 3].remove()
    axes[3, 4].remove()


    # Perform Level Crossing Analysis on original signals
    num_levels = 500
    reference_level_type = 'mean'
    gate = 0
    count_on_level = False
    
    
    seq_signal_obj = Signal_process(t_seq, amp_seq)
    seq_crossings, seq_levels = seq_signal_obj.level_crossings(num_levels, reference_level_type, gate, count_on_level)
    se_freq, seq_psd = seq_signal_obj.psd()
    
    
    # Test data LCR
    signal_object_test = Signal_process(x1_reorder, y1)
    test_crossings, test_levels = signal_object_test.level_crossings(num_levels, reference_level_type, gate, count_on_level)
    test_freq,test_psd = signal_object_test.psd()
    
    
    level_cross_fig = fig.add_subplot(5, 1, 4) # grid arrangment 3 row 1 column position 3 
    # Plot the LCR for test data
    #plt.figure(figsize=(10, 6))
    level_cross_fig.plot(test_crossings, test_levels, color='red', label='Test Data')
    level_cross_fig.plot(seq_crossings, seq_levels, color='blue', label='sequence Data')
    # plt.xscale('log')
    # plt.title('Level Crossing Rate - Test Data')
    # plt.xlabel('Level Crossing Count')
    # plt.xlim(1, 1e4)
    # plt.xticks([1, 10, 100, 1000, 10000, 100000], ['1', '10', '100', '1000', '1E4', '1E5'])
    # plt.yticks(np.arange(-3.5, 3.0, 0.5))
    # plt.ylabel('Level')
    # plt.grid()
    # plt.legend()


    axes[4, 0].remove()
    axes[4, 1].remove()
    axes[4, 2].remove()   
    axes[4, 3].remove()
    axes[4, 4].remove()

    psd_fig = fig.add_subplot(5, 1, 5)
    psd_fig.plot(test_freq,test_psd, color='red', label='Test Data')
    psd_fig.plot(se_freq, seq_psd, color='blue', label='sequence Data')    
    psd_fig.set_xlim(0, 70)
    
    plt.tight_layout()    
    
    plt.show()

    # # Plot the PSD
    # plt.figure(figsize=(10,6))
    # plt.semilogy(frequencies_test, psd_test)
    # plt.xlabel('Frequency(Hz)')
    # plt.ylabel('Power Spectrum Density(V^2/Hz)')
    # plt.title('Power Spectrum Density (PSD)')
    # plt.grid(True)
    # plt.show()








































































