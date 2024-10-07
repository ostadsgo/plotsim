
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to create the plot and embed it in the Tkinter frame
def create_plot(frame):
    # Create a Figure for the plot
    fig = Figure(figsize=(5, 4), dpi=100)

    # Add a subplot (1x1 grid, first plot)
    ax = fig.add_subplot(111)
    
    # Sample data
    x = [1, 2, 3, 4, 5]
    y = [1, 4, 9, 16, 25]
    
    # Plot data on the axes
    ax.plot(x, y)
    
    # Set title and labels
    ax.set_title("Sample Plot")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    
    # Embed the plot into the Tkinter frame using FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=frame)  # A tk.DrawingArea.
    
    # Place the canvas in the frame
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Draw the canvas (show the plot)
    canvas.draw()

# Tkinter App
root = tk.Tk()
root.title("Matplotlib Plot in Tkinter")

# Create a frame to hold the plot
plot_frame = ttk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=True)

# Create the plot in the plot_frame
create_plot(plot_frame)

# Start the Tkinter event loop
root.mainloop()
