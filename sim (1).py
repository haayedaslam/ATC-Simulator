from tkinter import *
#import tkinter.font
import math
import datetime
import winsound
from numpy import random

# Global variables
level_1_radius = 150	# Radius of the inner holding pattern circle. Stored in pixel units.
level_2_radius = 240	# Radius of the outer holding pattern circle. Stored in pixel units.
canvas_center_x = 0		# X coordinate of the centre of the canvas.
canvas_center_y = 0		# Y coordinate of the centre of the canvas.
unique_msg_id = 1		# The incremental id of the messages.
plane_ids = 1			# The incremental id of the planes.
plane_counter = 3		# Counter to keep track of how many planes have spawned during the simulation.
emergency_limit = 3		# to limit the total number of simultaneous emergencies.

class Message:
	def __init__(self):
		global unique_msg_id
		self.messageID = unique_msg_id				# Assign the unique message id when the class is instantiated. 
		unique_msg_id = unique_msg_id + 1			# incrementing the global variable so the next instiated Message class can use it
		now = datetime.datetime.now()				# Store the curren time stamp.
		self.time_stamp = now.strftime('%H:%M:%S')	# Format the time stamp.
		self.message_string = ""

	# This function adds the newly created message into the Message window
	def store_message(self, sim):
		sim.messages_list.append(self.message_string)
		sim.msg_stringvar.set(sim.messages_list)

	# Create "Plane spawned" message
	def create_Plane_spawned_message(self, sim, plane_id):
		self.message_string = "{m_id} - {m_time} - Plane {p_id} has spawned".format(
			m_id=self.messageID, m_time=self.time_stamp, p_id=plane_id)
		self.store_message(sim)

	# Create "prepare for landing" message
	def create_prepare_for_landing_message(self, sim, plane_id):
		self.message_string = "{m_id} - {m_time} - ATC »» Plane {p_id} prepare for landing".format(
			m_id=self.messageID, m_time=self.time_stamp, p_id=plane_id)
		self.store_message(sim)

	# Create "plane has landed" message
	def create_plane_landed_message(self, sim, plane_id):
		self.message_string = "{m_id} - {m_time} - Plane {p_id} has landed".format(
			m_id=self.messageID, m_time=self.time_stamp, p_id=plane_id)
		self.store_message(sim)

	# Create "Simulation ends!" message
	def create_end_of_simulation_message(self, sim):
		self.message_string = "{m_id} - {m_time} - All planes have landed - Simulation ends!".format(
			m_id=self.messageID, m_time=self.time_stamp)
		self.store_message(sim)
		
	# Create "Plane level is changed" message
	def create_level_changed_message(self, sim, plane_id, new_level):
		self.message_string = "{m_id} - {m_time} - Plane {p_id} moved to holding pattern {p_level}".format(
			m_id=self.messageID, m_time=self.time_stamp, p_id=plane_id, p_level = new_level)
		self.store_message(sim)

	# Create "plane has an emergency" message
	def create_Plane_emergency_message(self, sim, plane_id)	:
		self.message_string = "{m_id} - {m_time} - Plane {p_id} has declared an EMERGENCY".format(
			m_id=self.messageID, m_time=self.time_stamp, p_id=plane_id)
		self.store_message(sim)


class Plane:
	def __init__(self, sim, fuel, altitude, waiting_time, level, holding_slot, angle):
		global plane_ids
		self.flightID ="BA "+str(plane_ids)	# storing the flight ID locally
		plane_ids = plane_ids + 1			# incrementing the global variable so the next initiated plane class can use it
		self.canvas = sim.canvas			# storing the canvas object locally
		self.remaining_fuel = fuel			# storing the remaining fuel value locally
		self.altitude = altitude			# storing the altitude value locally
		self.waiting_time = waiting_time	# storing the waiting time value locally
		self.current_level = level			# storing the current value of the holding pattern locally
		self.holding_slot = holding_slot	# storing the current value of the holding slot  locally
		self.x = 0							# storing the x coordinate value
		self.y = 0							# storing the y coordidate value
		self.emergency_status = False		# storing the emergency status
		self.landing_priority = 0			# storing the landing priority value 
		self.visible = True					# storing the plane visibility value 
		self.angle = angle					# Storing the angle in degree 
		self.rad_angle = math.radians(self.angle)	# Storing the angle in radian 
		msg = Message()						# Create the message class object
		msg.create_Plane_spawned_message(sim, self.flightID)	 # send the message that the plane is spawned.

	# Function to store the current degrees and radian angle values locally
	def set_angles(self, angle):
		self.angle = angle
		self.rad_angle = math.radians(self.angle)
	
	# Function to calculate plane's current location. 
	def calculate_position(self):
		global level_1_radius, level_2_radius, canvas_center_x, canvas_center_y
		radius = level_1_radius
		if self.current_level == 2:
			radius = level_2_radius
		self.x = canvas_center_x + (radius * math.cos(self.rad_angle))	# calculating x coordinate of center of the plane's position on the radar
		self.y = canvas_center_y + (radius * math.sin(self.rad_angle))	# calculating y coordinate of center of the plane's position on the radar

	# draw plane's graphics
	def draw_plane_graphics(self, sim):
		# creating the plane marker on the canvas
		self.tk_oval = sim.canvas.create_oval(self.x - 10, self.y - 10, self.x + 10, self.y + 10, outline="lime", fill="lime") 
		# creating the rectangle on the canvas which will enclose the flight strip information.
		self.tk_rectangle = sim.canvas.create_rectangle(self.x + 20, self.y - 20, self.x + 90, self.y + 25, outline="lime") 
		# creating and formatting the text object on canvas that will display the flight strip information.
		txt = "{id}\nFuel: {fuel}\nWaiting: {wait}".format(id = self.flightID, fuel=round(self.remaining_fuel), wait=round(self.waiting_time))
		self.tk_text = sim.canvas.create_text(self.x + 25, self.y - 18, text=txt, anchor='nw', font=("Arial", 8), fill="lime", ) 
		# creating the line on the canvas that will connect the self.tk_oval (plane) and the self.tk_rectangle (flight strip)
		self.tk_line = sim.canvas.create_line(self.x , self.y, self.x + 20, self.y - 20, fill="lime")

	# Function to move the plane's and its flight strip's canvas drawing to the plane's x and y coordinates. 
	def move_plane_graphics(self):
		self.canvas.moveto(self.tk_oval, self.x-11, self.y-11)		# Move the blue circle indicating the plane
		self.canvas.moveto(self.tk_rectangle, self.x+20, self.y-20)	# Move the flight strip inforation rectangle
		self.canvas.moveto(self.tk_text, self.x+25, self.y-18)		# Move the text enclosed inside the rectangle
		self.canvas.moveto(self.tk_line, self.x, self.y-20)			# Move the line joining the flight strip and plane's circle
		txt = "{id}\nFuel: {fuel}\nWaiting: {wait}".format(id = self.flightID, fuel=round(self.remaining_fuel), wait=round(self.waiting_time))
		self.canvas.itemconfigure(self.tk_text, text=txt)			# Update the flight strip with the latest fuel, waiting information. 

	# Function to show the animation of landing the plane.
	def land_plane(self):
		self.x = self.x + 20	# Calculate new position of the landing plane
		self.move_plane_graphics()		# Call the update_plane_graphics() to move the plane towards and then on the runway

	# Function to declare emergency on the plane by chaning the plane's colour to red.
	def declare_emergency(self, sim):
		self.emergency_status = True
		winsound.Beep(8000, 100)								# Play the sound. frequency is set to 500Hz. Duration is set to 100 milliseconds
		#winsound.PlaySound("*", winsound.SND_ASYNC)				# Play the default windows sound asynchronously.
		self.canvas.itemconfigure(self.tk_oval, outline="limegreen", fill="red")	# Turn the plane colour to red
		self.canvas.itemconfigure(self.tk_line, fill="red")		# Turn the line joining the plane and the flight stripplane to red
		msg = Message()											# Create the message class object
		msg.create_Plane_emergency_message(sim, self.flightID)	# send the message that the plane is spawned.


class StartupScreen:

	def start_simulation(self, *args):
		for child_widget in self.startup_frame.winfo_children():
			child_widget.destroy()
		self.startup_frame.destroy()
		self.sim.draw_interface()

	# Function to create the main frame and set the parameters for the main frame
	def create_main_frame(self):
		self.ln=150
		self.bg='peachpuff'
		self.abg='red'
		self.hbg="chocolate"
		self.pad_margin = 20

		# create title_frame
		self.startup_frame = Frame(root, padx=10, pady=10, background=self.bg)
		self.startup_frame.grid(column=1, row=1, sticky=(N, W, E, S))

	# Function to create the text at the top of the start-up screen
	def create_title_labels(self):
		# Create top level title label
		self.atc_label=Label(self.startup_frame, padx=10, pady=10, text="ATC SIMULATOR", background=self.bg, font=("Arial", 18),)
		self.atc_label.grid(column=2, row=1, sticky=NSEW)

		# Create the label to show the text "Start up screen"
		self.startup_label=Label(self.startup_frame,  text="Start up screen\n", background=self.bg, font=("Arial", 12))
		self.startup_label.grid(column=2, row=2, sticky=(N, W, E, S), padx=self.pad_margin, pady=15)

	# Function to create the 'Total Aeroplanes' slider
	def create_total_planes_scaler(self):
		self.total_planes_scaler = Scale(self.startup_frame, orient=HORIZONTAL, length=self.ln, from_=5, to=20, background=self.bg, activebackground=self.abg, label="Total Aeroplanes",
									   highlightbackground=self.hbg, variable=self.sim.total_planes)
		self.total_planes_scaler.set(20)
		self.total_planes_scaler.grid(column=1, row=3, sticky=NSEW, padx=self.pad_margin, pady=2)
		
		# Legends for the scalers
		self.total_planes_scaler_label=Label(self.startup_frame, text="5 ---- 10 ---- 15 ---- 20\n\n\n", background=self.bg, font=("Verdana", 8),)
		self.total_planes_scaler_label.grid(column=1, row=4, sticky=(N),)

	# Function to create the 'Aeroplane Spawn Rate' slider
	def create_plane_spawn_rate_scaler(self):
		self.plane_spawn_rate_scaler = Scale(self.startup_frame, orient=HORIZONTAL, length=self.ln, from_=1, to=3, background=self.bg, activebackground=self.abg, 
										   label="Aeroplane Spawn Rate", highlightbackground=self.hbg, variable=self.sim.plane_spawn_rate)
		self.plane_spawn_rate_scaler.grid(column=2, row=3, sticky=NSEW, padx=self.pad_margin, pady=2)
        
		# Legends for the 'Aeroplane Spawn Rate' slider
		self.spawn_rate_scaler_label=Label(self.startup_frame, text="Slow ----- Medium ----- Fast\n\n\n", background=self.bg, font=("Verdana", 8),)
		self.spawn_rate_scaler_label.grid(column=2, row=4, sticky=(N),)

	# Function to create the 'Simulation Speed' slider
	def create_simulation_speed_scaler(self):
		self.simulation_speed_scaler = Scale(self.startup_frame, orient=HORIZONTAL, length=self.ln, from_=1, to=4, background=self.bg, activebackground=self.abg, label="Simulation Speed",
									   highlightbackground=self.hbg, variable=self.sim.simulation_speed)
		self.simulation_speed_scaler.grid(column=3, row=3, sticky=NSEW, padx=self.pad_margin, pady=2)

		# Legends for the 'Simulation Speed' slider
		self.simulation_speed_scaler_label=Label(self.startup_frame, text="Slow - Medium - Fast - Max\n\n\n", background=self.bg, font=("Verdana", 8),)
		self.simulation_speed_scaler_label.grid(column=3, row=4, sticky=(N),)

	# Function to create the 'Emergency Probability' slider
	def create_emergency_probability_scaler(self):
		self.emergency_probability_scaler = Scale(self.startup_frame, orient=HORIZONTAL, length=self.ln, from_=1, to=3, background=self.bg, activebackground=self.abg, 
											label="Emergency Probability", highlightbackground=self.hbg, variable=self.sim.emergency_probability)
		self.emergency_probability_scaler.grid(column=1, row=5, sticky=NSEW, padx=self.pad_margin, pady=2)

		# Legends for the 'Emergency Probability' slider
		self.emergency_scaler_label=Label(self.startup_frame, text="Low ---- Medium ---- High\n\n\n", background=self.bg, font=("Verdana", 8),)
		self.emergency_scaler_label.grid(column=1, row=6, sticky=(N),)

	# Function to create the 'Weather Conditions' slider
	def create_weather_scaler(self):
		self.weather_scaler = Scale(self.startup_frame, orient=HORIZONTAL, length=self.ln, from_=1, to=3, background=self.bg, activebackground=self.abg, 
							  label="Weather Conditions", highlightbackground=self.hbg, variable=self.sim.weather_probability)
		self.weather_scaler.grid(column=2, row=5, sticky=NSEW, padx=self.pad_margin, pady=2)

		# Legends for the 'Weather Conditions' slider
		self.weather_scaler_label=Label(self.startup_frame, text="Normal ---- Bad ---- Adverse\n\n\n", background=self.bg, font=("Verdana", 8),)
		self.weather_scaler_label.grid(column=2, row=6, sticky=(N),)

	# Function to create the clickable 'Start Simulation' button
	def create_start_simulation_button(self):
		self.start_simulation_button = Button(self.startup_frame, height=3, width=15, text="Start Simulation", background='cornflowerblue', foreground='white', 
										font=("Arial", 12), command=self.start_simulation)
		self.start_simulation_button.grid(column=3, row=5, padx=0, pady=0, rowspan=1)

	def __init__(self, simulator):
		self.sim = simulator		# Store simulator object as a class object for easier references. 
		self.create_main_frame()	# create main frame to hold the widgets.
		self.create_title_labels()	# create the title lables with the main frame
		self.create_total_planes_scaler()	# create the total plane scaler widget
		self.create_plane_spawn_rate_scaler()	# create the plane spawn rate scaler widget
		self.create_simulation_speed_scaler()	# create the scaler widget to control the simulation speed
		self.create_emergency_probability_scaler()	# create the emergency control scaler widget
		self.create_weather_scaler()	# create the weather control scaler widget
		self.create_start_simulation_button()	# create the start simulation button


class Simulation:
	def __init__(self):
		self.Load_and_initiate_simulator()	# Call this function to load all the variables required to run the simulation

	# This function loads the variables required to run the simulation
	def Load_and_initiate_simulator(self):
		self.canvas = 0			# Canvas object
		self.ln = 130			# used to create all the scalers with the same fixed width
		self.bg='peachpuff'		# used to set up the same background colour across all widgets. 
		self.abg='red'			# used to set up the same active background colour across all widgets.
		self.hbg="chocolate"	# used to set up the same highlight background colour across all widgets.
		self.pad_margin = 10	# used to set up the same padding margin of widgets. 
		self.total_planes_spawned = 0	# to keep the count of total plans spawn during the simulation. 
		self.total_planes_landed = 0	# to keep the count of total plans landed during the simulation. 
		self.total_planes = StringVar(value="0")			# String var variable to store the value of the total planes widgets. 
		self.plane_spawn_rate = StringVar(value="0")		# String var variable to store the value of the planes spawn rate widgets. 
		self.simulation_speed = StringVar(value="0")		# String var variable to store the value of the simulation speed widgets. 
		self.emergency_probability = StringVar(value="0")	# String var variable to store the value of the emergency probability widgets. 
		self.weather_probability = StringVar(value="0")	# String var variable to store the value of the weather probability widgets. 
		self.sim_interval = 500		# The milli second delay between every simulation cycle. 500 Ms is the default delay value.
		self.sim_speed_dict = {100: "5x", 300: "4x", 500: "3x", 700: "2x", 900: "1x"}	# This stores the fixed simulation delay intervals. 
		self.angle_increment = 5			# The increase in angle each time a simulation cycle is run
		self.simulator_pause = False		# if True, the simulation is paused, otherwise will keep running
		self.new_planes_list: list[Plane] = []			# The list containing newly spawned planes which have not been assigned any holding patterns.
		self.landed_planes_list: list[Plane] = []		# The list containing landed planes
		self.holding_pattern_1_list: list[Plane] = []	# The list containing planes assigned to the holding patter 1.
		self.holding_pattern_2_list: list[Plane] = []	# The list containing planes assigned to the holding patter 2.
		self.messages_list: list[str] = ["       Air Traffic Controller Simulator Messages", ""] # Keeps all the simulation messages.
		self.msg_stringvar = StringVar(value=self.messages_list)	# String var to store the list of all the simulation messages.
		# Variables to support the landing procedure
		self.is_plane_landing = False	# if True, then don't instruct any other plane to land
		self.landing_plane = 0			# the reference to the landing plane. 
		self.root_after_id = 0			# The identifier returned by the root.after(). This is used to cancel scheduling with after_cancel.
		self.active_emergencies = 0 	# this variable will keep count of how many planes are currently declared emergency
		self.default_emergency_ratio = 0.002	# default initial probability value of emergency taking place
		
	# Function to create the top main frame	
	def create_main_frame(self):
		self.main_frame = Frame(root, padx=10, pady=10, background=self.bg, borderwidth=2, relief="raised")
		self.main_frame.grid(column=1, row=1, sticky=(N, W, E, S))
		
	# Function to create the top left radar planel within the main frame	
	def create_radar_panel(self):
		# create the canvas that will be used to draw the radar and moving planes.
		self.canvas = Canvas(self.main_frame, height=540, width=800,  background='black')
		self.canvas.grid(column=1, row=1, padx = 10, rowspan=2, sticky=(N, W, E, S))
		global canvas_center_x, canvas_center_y	# The global variables to holds the value of the center of the canvas.
		canvas_center_x = int(self.canvas['width']) / 2
		canvas_center_y = int(self.canvas['height']) / 2

		# Outer holding pattern
		self.canvas.create_oval(canvas_center_x - 240, canvas_center_y - 240, canvas_center_x + 240, canvas_center_y + 240, outline='gray')
		self.canvas.create_text(canvas_center_x - 15, 45, text='Level 2', anchor='nw', font=('Helvetica', 8, 'bold'), fill='white')
		self.canvas.create_text(canvas_center_x + 230, canvas_center_y + 100, text='2000 ft', anchor='nw', font=('Helvetica', 8, 'bold', 'underline'), fill='white')
		# Inner holding pattern
		self.canvas.create_oval(canvas_center_x - 150, canvas_center_y - 150, canvas_center_x + 150, canvas_center_y + 150, outline='gray')
		self.canvas.create_text(canvas_center_x - 15, 135, text='Level 1', anchor='nw', font=('Helvetica', 8, 'bold'), fill='white')
		self.canvas.create_text(canvas_center_x + 145, canvas_center_y + 60, text='1000 ft', anchor='nw', font=('Helvetica', 8, 'bold', 'underline'), fill='white')
		# Runway 
		self.canvas.create_rectangle(canvas_center_x - 50, canvas_center_y - 10, canvas_center_x + 50, canvas_center_y + 10, outline='gray')
		self.canvas.create_text(canvas_center_x - 38, canvas_center_y + 15, text='Airport runway', anchor='nw', font=('Helvetica', 8,), fill='dimgray')
		# Runway dash line
		self.canvas.create_line(canvas_center_x - 45, canvas_center_y , canvas_center_x + 45, canvas_center_y, dash=(3,2), fill="gray")
		# Arrow to the left of the Runway
		self.canvas.create_line(canvas_center_x - 80, canvas_center_y , canvas_center_x - 55, canvas_center_y, width=7, arrow='last', arrowshape=(10,10,4),  fill="silver")
		# Create label for showing the simulation statistics
		self.canvas.create_rectangle(10, int(self.canvas['height']) - 62, 162, int(self.canvas['height']) - 5, outline='black', fill='dimgray')
		self.tk_radar_stats_label = self.canvas.create_text(18, int(self.canvas['height']) - 57, text="", anchor='nw', font=("Helvetica", 10), fill='lime', ) 
		# Draw horizontal and vertical guides.
		self.canvas.create_line(1, canvas_center_y, self.canvas['width'], canvas_center_y, fill="gray")
		self.canvas.create_line(canvas_center_x, 1, canvas_center_x, self.canvas['height'], fill="gray")	
		
	# Function to create the top left radar planel within the main frame	
	def create_messages_panel(self):
		# Create the message Listbox widget. 
		self.messages_listbox = Listbox(self.main_frame, listvariable=self.msg_stringvar, height=32, width=50)
		self.messages_listbox.grid(column=2, row=1, sticky=(N, S), )

		# Create the message Listbox horizontal scroll widget. 
		self.messages_v_scrollbar = Scrollbar(self.main_frame, orient=VERTICAL, command=self.messages_listbox.yview)
		self.messages_v_scrollbar.grid(column=3, row=1, sticky=(W,N,S), padx=2, )
		self.messages_listbox['yscrollcommand'] = self.messages_v_scrollbar.set

		# Create the message Listbox vertical scroll widget. 
		self.messages_h_scrollbar = Scrollbar(self.main_frame, orient=HORIZONTAL, command=self.messages_listbox.xview)
		self.messages_h_scrollbar.grid(column=2, row=2, pady = 0, sticky=(E,W), )
		self.messages_listbox['xscrollcommand'] = self.messages_h_scrollbar.set

	# Function to create the bottm frame that will host all the widgets to control the simulation.
	def create_widgets_frame(self):
		# bottom widgets frame
		self.widgets_frame = Frame(root, padx=10, pady=10, background=self.bg, borderwidth=2, relief="raised")
		self.widgets_frame.grid(column=1, row=2, sticky=(N, W, E, S))

    # Function to update the simulation information on the bottom left of the radar window
	def update_radar_screen_stats(self, val):
		txt = "Planes spwned: " + str(plane_counter) + " / " + val  
		txt += "\nPlanes landed: " + str(len(self.landed_planes_list)) 
		txt += "\nSimulation Speed: " + self.sim_speed_dict[self.sim_interval] 
		self.canvas.itemconfigure(self.tk_radar_stats_label, text=txt)
		
	# Function to slow down the simulation speed.
	def slow_down(self):
		if self.sim_interval < 900:
			self.sim_interval += 200	# each time add 200 Ms. 
			self.update_radar_screen_stats(str(self.total_planes.get()))
		else:
			print("Reached slowest speed")
	
	# Function to increase the simulation speed.
	def speed_up(self):
		if self.sim_interval > 100:
			self.sim_interval -= 200	# each time minus 200 Ms. 
			self.update_radar_screen_stats(str(self.total_planes.get()))
		else:
			print("Maximum speed")

	# Function to pause/play the simulation.
	def play_pause(self):
		if self.simulator_pause == True:
			self.simulator_pause = False
		else:
			self.simulator_pause = True
	
	# Function to create the panel that will host all the widgets to control the simulation.
	def create_control_box_panel(self):
		# Create the Simulation Control Box Label
		self.widgets_label=Label(self.widgets_frame, text="Simulation Control Box", background=self.bg, font=("Verdana", 12),)
		self.widgets_label.grid(column=4, row=1, sticky=N, columnspan=4)

		# Create Slow Down button
		self.slow_down_image = PhotoImage(file="res\\SlowDown.png")
		self.slow_down_button = Button(self.widgets_frame, image=self.slow_down_image, command=self.slow_down)
		self.slow_down_button.grid(column=1, row=1, rowspan=3, padx=10, pady=10)

		# Create Play / Pause button
		self.play_pause_image = PhotoImage(file="res\\PlayPause.png")
		self.play_puase_button = Button(self.widgets_frame, image=self.play_pause_image, command=self.play_pause)
		self.play_puase_button.grid(column=2, row=1, rowspan=3, padx=10, pady=10)

		# Create Speed Up button
		self.speed_up_image = PhotoImage(file="res\\SpeedUp.png")
		self.speed_up_button = Button(self.widgets_frame, image=self.speed_up_image, command=self.speed_up)
		self.speed_up_button.grid(column=3, row=1, rowspan=3, padx=10, pady=10)

        # Create total aeroplane scaler
		self.total_planes_scaler = Scale(self.widgets_frame, orient=HORIZONTAL, length=self.ln, from_=5, to=20, background=self.bg, activebackground=self.abg, label="Total Aeroplanes",
									   highlightbackground=self.hbg, variable=self.total_planes, command=self.update_radar_screen_stats)
		self.total_planes_scaler.grid(column=4, row=2, sticky=S, padx=self.pad_margin, pady=3)
		
        # Create Aeroplane Spawn Rate scaler
		self.plane_spawn_rate_scaler = Scale(self.widgets_frame, orient=HORIZONTAL, length=self.ln, from_=1, to=3, background=self.bg, activebackground=self.abg, label="Aeroplane Spawn Rate",
										   highlightbackground=self.hbg, variable=self.plane_spawn_rate)
		self.plane_spawn_rate_scaler.grid(column=5, row=2, sticky=S, padx=self.pad_margin, pady=3)

        # Create Emergency Probability scaler
		self.emergency_probability_scaler = Scale(self.widgets_frame, orient=HORIZONTAL, length=self.ln, from_=1, to=3, background=self.bg, activebackground=self.abg, label="Emergency Probability",
											highlightbackground=self.hbg, variable=self.emergency_probability)
		self.emergency_probability_scaler.grid(column=6, row=2, sticky=S, padx=self.pad_margin, pady=3)

        # Create Weather Conditions scaler
		self.weather_scaler = Scale(self.widgets_frame, orient=HORIZONTAL, length=self.ln, from_=1, to=3, background=self.bg, activebackground=self.abg, label="Weather Conditions",
							  highlightbackground=self.hbg, variable=self.weather_probability)
		self.weather_scaler.grid(column=7, row=2, sticky=S, padx=self.pad_margin, pady=3)
		
        # Create the label frame around the compass image
		self.compass_label_frame = LabelFrame(self.widgets_frame, background=self.bg, border=True, borderwidth=2)
		self.compass_label_frame.grid(column=8, row=1, rowspan=3, padx=15, pady=0, )
		
		# Create the compas image
		self.compass_image = PhotoImage(file='res\\Compass.png')
		self.compass_label = Label(self.compass_label_frame, background=self.bg, image=self.compass_image, border=True, borderwidth=2)
		self.compass_label.grid(column=1, row=1, )
		
        # Legends for all the scalers widgets.
		self.total_planes_scaler_label=Label(self.widgets_frame, text="5 --- 10 --- 15 --- 20", background=self.bg, font=("Verdana", 8),)
		self.total_planes_scaler_label.grid(column=4, row=3, sticky=(N),)
		
		self.spawn_rate_scaler_label=Label(self.widgets_frame, text="Slow - Medium - Fast", background=self.bg, font=("Verdana", 8),)
		self.spawn_rate_scaler_label.grid(column=5, row=3, sticky=(N),)
		
		self.emergency_scaler_label=Label(self.widgets_frame, text="Low - Medium - High", background=self.bg, font=("Verdana", 8),)
		self.emergency_scaler_label.grid(column=6, row=3, sticky=(N),)
		
		self.weather_scaler_label=Label(self.widgets_frame, text="Normal - Bad - Adverse", background=self.bg, font=("Verdana", 8),)
		self.weather_scaler_label.grid(column=7, row=3, sticky=(N),)
        
	# Function to create and draw all the user interface of the simulation.
	def draw_interface(self):
		self.create_main_frame()		# Create the main top level frame
		self.create_radar_panel()		# Create the radar panel within the top level frame
		self.create_messages_panel()	# Create the message frame to the right hand side
		self.create_widgets_frame()		# Create the frame that will contain all the control widgets.
		self.create_control_box_panel()	# Create teh panel that will holds all the control widgets. 
		# 	Create initial planes
		self.holding_pattern_1_list.append(Plane(self, fuel=278, altitude=2000, waiting_time=40, level=1, holding_slot=1, angle=0))
		self.holding_pattern_1_list.append(Plane(self, fuel=480, altitude=2000, waiting_time=30, level=1, holding_slot=2, angle=270))
		self.holding_pattern_1_list.append(Plane(self, fuel=350, altitude=2000, waiting_time=20, level=1, holding_slot=3, angle=180))
		self.update_radar_screen_stats(str(self.total_planes.get()))
		for pl in self.holding_pattern_1_list:
			pl.draw_plane_graphics(self)
		self.run_engine()

	# Function to run the procedure of landing a plane. 
	def process_landed_plane(self):
		if self.landing_plane.emergency_status == True:
			self.active_emergencies -= 1			# counting how many simultanous emergicies have occured
		self.holding_pattern_1_list.remove(self.landing_plane)	# Remove the landing plane from the holding_pattern_1 list
		self.landed_planes_list.append(self.landing_plane)		# Append the landing plane to the landed_planes list
		self.canvas.delete(self.landing_plane.tk_oval)		# Delete the canvas object showing the plane 
		self.canvas.delete(self.landing_plane.tk_rectangle)	# Delete the canvas object showing the plane information
		self.canvas.delete(self.landing_plane.tk_text)		# Delete the canvas object showing the plane information
		self.canvas.delete(self.landing_plane.tk_line)		# Delete the canvas object showing the plane  information
		msg = Message()
		msg.create_plane_landed_message(self, self.landing_plane.flightID)	# Create the message that the plane has landed.
		self.is_plane_landing = False	# Reset it to False, so that the next plane can be instructucted to land
		self.landing_plane = 0			# Reset to the landing plane object to null.
		self.update_radar_screen_stats(str(self.total_planes.get()))

	# Function to check the probability of spawning a new plane. If True then spawn the plane. 
	def spawn_new_plane(self):
		global plane_counter
		if int(self.total_planes.get()) <= plane_counter:
			return False
		
		# Stringvar values: Slow = 1, Medium = 2, Fast = 3
		rate = int(self.plane_spawn_rate.get())
		x = 0
		if rate == 1: 	# 1 = Slow 
			x = random.choice([0, 1], p=[0.980, 0.020], size=(1))
		elif rate == 2:	# 2 = Medium
			x = random.choice([0, 1], p=[0.960, 0.040], size=(1))
		elif rate == 3:	# 3 = Fast
			#x = random.choice([0, 1], p=[0.940, 0.060], size=(1))
			x = random.choice([0, 1], p=[0.8, 0.2], size=(1))
		
		if x == 1:
			# spawn new plane
			rem_fuel = random.randint(150, 500, size=(1))	# creating a random value for fuel remaining field.
			new_plane = Plane(self, fuel=rem_fuel[0], altitude=2000, waiting_time=0, level=3, holding_slot=1, angle=300)	# spawn the plane
			self.new_planes_list.append(new_plane)
			new_plane.x = int(self.canvas['width']) - 100	# determine the x coordinate of the new plane
			new_plane.y = len(self.new_planes_list) * 60	# determine the y coordinate of the new plane
			new_plane.draw_plane_graphics(self)				# Draw the graphical elements of the planes
			plane_counter += 1 								# increment the counter of total planes spawned
			self.update_radar_screen_stats(str(self.total_planes.get()))
			return True
		return False

	# Function is executed when all the planes have landed. To end the siumation. 
	def end_simulator(self):
		msg = Message()
		msg.create_end_of_simulation_message(self)	# Create message that all the planes have landed and the simulation ends.
		root.after_cancel(self.root_after_id)

	# This function increase the waiting time and decrease the fuel for all planes except the landed planes
	def process_fuel_and_wait(self):
		# The list containing all the plane lists.
		all_planes_lists = [self.new_planes_list, self.holding_pattern_1_list, self.holding_pattern_2_list]	
		for pl_lists in all_planes_lists:
			for p in pl_lists:
				p.waiting_time += 1
				p.remaining_fuel -= 0.25
				if p.remaining_fuel < 50 and p.emergency_status == False:	# declare emergency on this plane
					p.declare_emergency(self)
		
	# This function checks the weather conditions and process them
	def process_weather_conditions(self):
		# Stringvar values: Normal = 1, Bad = 2, Adverse = 3
		weather = int(self.weather_probability.get())
		if weather == 1:	# Normal weather
			self.default_emergency_ratio = 0.002	# reset the emergency probability
		elif weather == 2:	# Bad weather. 
			self.default_emergency_ratio = 0.012	# increase the default emergency probability 
		elif weather == 3:	# Adverse weather. 
			self.default_emergency_ratio = 0.022	# Further increase the default emergency probability 

	# This function generate random emergency on the basis of a fixed probability, it then process the plane with the emergency.
	def check_and_generate_emergency(self):
		# Stringvar values: Low = 1, Medium = 2, High = 3
		# create a list of all the flying planes lists.
		all_flying_planes_list = [self.holding_pattern_1_list, self.holding_pattern_2_list]
		low = 	self.default_emergency_ratio	# 0.995 and 0.005, 1 out of 1000
		med = 	low + 0.010	# 0.990 and 0.015, 10 out of 1000
		high = 	med + 0.010	# 0.980 and 0.025, 20 out of 1000
		emergency = int(self.emergency_probability.get())

		for pl_lists in all_flying_planes_list:
			for p in pl_lists:
				if p.emergency_status == False:
					x = [0]
					if emergency == 1:
						x = random.choice([0, 1], p=[1-low, low], size=(1))
					elif emergency == 2:
						x = random.choice([0, 1], p=[1-med, med], size=(1))
					elif emergency == 3:
						x = random.choice([0, 1], p=[1-high, high], size=(1))
						
					if x[0] == 1:	# this plane has emergency
						print("YES, Low = ", low, "x = ", x[0], ", prob = " + self.emergency_probability.get())
						self.active_emergencies += 1	# counting how many simultanous emergicies have occured
						p.declare_emergency(self)

	# This function sort the list by priority
	def sort_criteria(self, plane):
		return plane.remaining_fuel

	# This function finds the first empty slot on the 2nd holding pattern and returns its angle
	def find_empty_slot(self, holding_pattern_list):
		angle = int(holding_pattern_list[0].angle % 90)	# find the lowest angle among all planes
		if angle < 0:
			angle = angle * -1	# if angle is negative, turn it to positive
		angles_list = [angle, angle + 90, angle + 180, angle + 270]	# Create a list of all four angles of the four holding slots
		
		# Find the first empty slot on the 2nd holding pattern and returns its angle
		found = False
		for angle in angles_list:
			found = False
			for plane in holding_pattern_list:
				if plane.angle == angle:
					found = True
					break
			if found == False:
				return angle

	# This function checks and process if a new plane can be transit to the lower level 2 
	def transit_to_level_2(self):
		if len(self.new_planes_list) == 0 or len(self.holding_pattern_2_list) == 4: # Check if plane can be moved down to level 2
			return
		self.new_planes_list.sort(key=self.sort_criteria)	# sort the list with respect to the fuel 
		moving_plane = self.new_planes_list[0]				# moving _plane now holds the reference to the plane with the lowest fuel level
		# set the angle of the plane
		if len(self.holding_pattern_2_list) == 0:			# if there are not planes on level 2, then move the plane to any location
			if len(self.holding_pattern_1_list) == 0:
				moving_plane.set_angles(0)
			else:
				moving_plane.set_angles(self.holding_pattern_1_list[0].angle)
		else:
			moving_plane.set_angles(self.find_empty_slot(self.holding_pattern_2_list))
		moving_plane.current_level = 2						# set the new level of the plane
		moving_plane.calculate_position()					# calculate the new position of the plane on the new level
		self.new_planes_list.remove(moving_plane)			# Remove the plane from the new_planes_list list
		self.holding_pattern_2_list.append(moving_plane)	# Then append this plane to the holding_pattern_2_list list
		msg = Message()										# create the message to show that the plane has moved to the level 2.
		msg.create_level_changed_message(self, moving_plane.flightID, 2)

	# This function identify the most suitable candidate plane to be taken to the lower level, based emergency status and remaining fuel.
	def find_plane_to_move_to_lower_level(self, holding_pattern_list):
		# Find the plane with the highest priority to move to the lower level
		emergency = False
		rem_fuel = 10000				# this variable will be used in the loop below to find the plane with the least fuel remaining.
		for p in holding_pattern_list:
			if p.emergency_status == True:
				emergency = True		# this flag will indicate that a plane has been identified with the ememergency status.
				if p.remaining_fuel < rem_fuel:
					moving_plane = p	# the emergency plane with the least fuel will be picked up to move it down to the lower level.
					rem_fuel = p.remaining_fuel
		if emergency == False:	# if no emergency is found in any of the planes then use the method below to identify the plane with the lowest fuel.
			holding_pattern_list.sort(key=self.sort_criteria)	# sort the list with respect to the fuel 
			moving_plane = holding_pattern_list[0]				# moving _plane now holds the reference to the plane with the lowest fuel level
		return moving_plane
	
	# This function moves planes from outer level 2 to the inner level 1.
	def transit_to_level_1(self):
		if len(self.holding_pattern_2_list) == 0 or len(self.holding_pattern_1_list) == 4: # Check if plane can be moved down to the lower level
			return
		# Find the plane with the highest priority to move to the lower level
		moving_plane = self.find_plane_to_move_to_lower_level(self.holding_pattern_2_list)
        # set the angle of the plane
		if len(self.holding_pattern_1_list) > 0:			# if there are not planes on the lower level, then don't change the angle of the plane.
			moving_plane.set_angles(self.find_empty_slot(self.holding_pattern_1_list))	# Otherwise find an empty slot and assign its angle to the plane.
		moving_plane.current_level = 1						# set the new level of the plane
		moving_plane.calculate_position()					# calculate the new position of the plane on the new level
		self.holding_pattern_2_list.remove(moving_plane)			# Remove the plane from the holding_pattern_2_list list
		self.holding_pattern_1_list.append(moving_plane)	# Then append this plane to the holding_pattern_1_list list
		msg = Message()										# create the message to show that the plane has moved to the level 2.
		msg.create_level_changed_message(self, moving_plane.flightID, 1)

	# This function moves the planes on level 1
	def move_level_1_planes(self):
		if self.is_plane_landing == False:	# find out if a plane has been picked up previously for landing.
			self.is_plane_landing = True
			self.landing_plane = self.find_plane_to_move_to_lower_level(self.holding_pattern_1_list)
			# change the colour of landing plane to blue to indicate that it has been authorised to land next. 
			self.canvas.itemconfigure(self.landing_plane.tk_rectangle, outline="blue", fill="lightgray")	# Turn the flight strip colour to blue
			self.canvas.itemconfigure(self.landing_plane.tk_text, fill="blue")								# Turn the flight strip text colour to blue
			msg = Message()
			msg.create_prepare_for_landing_message(self, self.landing_plane.flightID)
		
		ready_to_remove = False
		for p in self.holding_pattern_1_list:
			if p.angle == 180 and p == self.landing_plane:
				p.land_plane() # Take this plane to the runway and make it land. 
				if p.x > 440:
					ready_to_remove = True
			else:	
				if p.angle <= 0:
					p.set_angles(360 - self.angle_increment)
				else:
					p.set_angles(p.angle - self.angle_increment)
				p.calculate_position()
				p.move_plane_graphics()

		if ready_to_remove:
			ready_to_remove = False
			self.process_landed_plane() # The plane has landed.
			if len(self.holding_pattern_1_list) == 0:
				self.end_simulator()
				return False	# return false to stop calling back run_engine()
			else:
				return True		# return true to continue calling back run_engine()
		else:
			return True			# return true to continue calling back run_engine()

	# This function moves the planes on level 2
	def move_level_2_planes(self):
		for p in self.holding_pattern_2_list:
			if p.angle <= 0:
				p.set_angles(360 - self.angle_increment)
			else:
				p.set_angles(p.angle - self.angle_increment)
			p.calculate_position()
			p.move_plane_graphics()

	# The main loop of the simulation. This function is executed as a loop to move the simulation forward.
	def run_engine(self):
		if self.simulator_pause == True:
			self.root_after_id = root.after(self.sim_interval, self.run_engine) # If simulation is paused then don't take any action. 
			return
		
		# Load variables 
		self.process_fuel_and_wait()

		# Check for bad weather 
		self.process_weather_conditions()
		
		# Spawn new planes and transit planes to lower levels if slot available.
		if self.spawn_new_plane() == False:
			self.transit_to_level_2()
			# Check for emergencies
			if self.active_emergencies < emergency_limit:	# cannot exceed total emergencies at any given time from the set limit.
				self.check_and_generate_emergency()
		self.transit_to_level_1()

		# Move planes and update their flight information
		for n in self.new_planes_list:
			n.move_plane_graphics()
		self.move_level_2_planes()
		continue_loop = self.move_level_1_planes()
		# call root.after with time interval if continue_loop is true (meaning there are still planes that needs simulation)
		if continue_loop:
			self.root_after_id = root.after(self.sim_interval, self.run_engine)


root = Tk()
simulator = Simulation()
root.start_up_screen = StartupScreen(simulator) # To view the start up screen, uncomment this line and comment the following line. 
#simulator.draw_interface() 

root.mainloop()
