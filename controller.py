import tkinter
import sys
import serial
import time
import os
import threading
import subprocess
import pyglet
from PIL import ImageTk, Image
from functools import partial

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
img_path = "images/"
img_files_path = os.path.join(script_dir, img_path)

#font_path = "font/UAV-OSD-Sans-Mono.ttf"
#font_file_path = os.path.join(script_dir, font_path)

arduino = serial.Serial(port='/dev/ttyS0', baudrate=115200, timeout=0.1) 

#pyglet.font.add_file(font_path)
b_font = "UAV OSD Sans Mono"
#b_font = "arial"
b_font_size = 12
b_font_type = "normal"
b_width=144 #144
b_height=148 #148
b_c_text = "#FFFFFF"
b_c_bg = "#000000"
b_b =0
b_hl_t = 0
colour_background = "#000000"
colour4 = "#AAAAAA"
colour5 = "#FFFFFF"

i_width = 126 #126
i_height = 126 #126

class KEYB:
  KEY_LEFT_CTRL = 1001
  KEY_LEFT_SHIFT = 1002
  KEY_LEFT_ALT = 1003
  KEY_RIGHT_CTRL = 1004
  KEY_RIGHT_SHIFT = 1005
  KEY_RIGHT_ALT = 1006
  KEY_TAB = 1007
  KEY_F1 = 1011
  KEY_F2 = 1012
  KEY_F3 = 1013
  KEY_F4 = 1014
  KEY_F5 = 1015
  KEY_F6 = 1016
  KEY_F7 = 1017
  KEY_F8 = 1018
  KEY_F9 = 1019
  KEY_F10 = 1020
  KEY_F11 = 1021
  KEY_F12 = 1022
  KEY_UP_ARROW = 1023
  KEY_DOWN_ARROW = 1024
  KEY_LEFT_ARROW = 1025
  KEY_RIGHT_ARROW = 1026
  KEY_PAGE_UP = 1027
  KEY_PAGE_DOWN = 1028
  KEY_HOME = 1029
  KEY_END = 1030
  KEY_KP_1 = 1031
  KEY_KP_2 = 1032
  KEY_KP_3 = 1033
  KEY_KP_4 = 1034
  KEY_KP_5 = 1035
  KEY_KP_6 = 1036
  KEY_KP_7 = 1037
  KEY_KP_8 = 1038
  KEY_KP_9 = 1039
  KEY_KP_0 = 1040
  KEY_KP_MINUS = 1041
  KEY_KP_PLUS = 1042
  KEY_KP_ASTERISK = 1043

def resize_image(file):
  i_original = Image.open(os.path.join(img_files_path, file))
  i_resize = i_original.resize((i_width, i_height))
  i_finished = ImageTk.PhotoImage(i_resize)
  return i_finished

def create_button(frame, b_text, image_obj, event_int, event_char, type, target_frame, row, column):
  width_px=144 #144
  height_px=148
  container = tkinter.Frame(frame, width=width_px, height=height_px, background=b_c_bg)
  container.grid(row=row, column=column)
  container.grid_propagate(False)  # Prevent button from resizing the frame

  button=tkinter.Button(container, text=b_text, image=image_obj, compound="center", font=(b_font, b_font_size, b_font_type), foreground=b_c_text, activeforeground=b_c_text, background=b_c_bg, activebackground=b_c_bg, border=b_b, highlightthickness=b_hl_t, relief="raised")

  button.place(relx=0.5, rely=0.5, anchor="center", width=width_px, height=height_px)

  if type == "button":
    button.bind("<ButtonPress-1>", lambda event, i=str(event_int), s="J":  button_press(event, i, s))
    button.bind("<ButtonRelease-1>", lambda event, i=str(event_int*-1), s="J": button_press(event, i, s))
  elif type == "on":
    button.bind("<ButtonPress-1>", lambda event, i=str(event_int), s="J":  button_press(event, i, s))
  elif type == "off":
    button.bind("<ButtonPress-1>", lambda event, i=str(event_int*-1), s="J":  button_press(event, i, s))
  elif type == "key":
    button.bind("<ButtonPress-1>", lambda event, i=str(event_int), s=str(event_char): button_press(event, i, s))
    button.bind("<ButtonRelease-1>", lambda event, i=str(event_int*-1), s=str(event_char): button_press(event, i, s))
  elif type == "redir":
    button.bind("<ButtonRelease-1>", lambda event: raise_frame(target_frame))
  elif type == "redir+button":
    button.bind("<ButtonPress-1>", lambda event, i=str(event_int), s="J":  button_press(event, i, s))
    button.bind("<ButtonRelease-1>", lambda event, i=str(event_int*-1), s="J": button_press_frame(event, i, s, target_frame))
  elif type == "close":
    button.bind("<ButtonPress-1>", lambda event: close_gui())
  elif type == "shutdown":
    button.bind("<ButtonPress-1>", lambda event, tb=text_output: shutdown(tb))
  elif type == "update":
    button.bind("<ButtonPress-1>", lambda event, tb=text_output: update_rpi(tb))

  return button

def create_dummys(target_frame, image_obj):
  for row in [1,2,3,4]:
    for column in [1,2,3,4,5,6,7]:
      button_dummy=create_button(target_frame, "", image_obj, 0, "", "dummy", None, row, column)

def button_press(event, i, s):
  arduino.write(bytes(i, 'utf-8'))
  arduino.write(bytes("x", 'utf-8'))
  arduino.write(bytes(s, 'utf-8'))
  print(f"Integer: {i}, Char: {s}" )

def button_press_frame(event, i, s, frame):
  arduino.write(bytes(i, 'utf-8'))
  arduino.write(bytes("x", 'utf-8'))
  arduino.write(bytes(s, 'utf-8'))
  raise_frame(frame)
  print(f"Integer: {i}, Char: {s}" )

def close_gui():
  sys.exit()

def shutdown(textbox=None):
  arduino.close()
  time.sleep(5)
  threading.Thread(target=shutdown_thread, args=[textbox]).start()

def shutdown_thread(textbox=None):
  if textbox:
        textbox.insert(tkinter.END, "\n---- SHUTTING DOWN ----\n")
        textbox.see("end")
        textbox.update_idletasks()  # force immediate redraw

  time.sleep(1)
  arduino.close()
  time.sleep(5)
  process = subprocess.Popen("sudo shutdown -h now", shell=True, stdout=subprocess.PIPE, bufsize=1, text=True)
  while process.poll() is None:
    msg = process.stdout.readline().strip()  # read a line from the process output
    if msg:
      textbox.insert(tkinter.END,"\n"+"---- SHUTTING DOWN  ----"+"\n")
      textbox.insert(tkinter.END, msg + "\n")
      textbox.see("end")

  #c_shutdown = subprocess.run("sudo shutdown -h now",shell=True, stdout=subprocess.PIPE)
  #print(c_shutdown.stdout.decode())
  #call("sudo shutdown -h now", shell=True)


def update_rpi(textbox=None):
  threading.Thread(target=update_rpi_thread, args=[textbox]).start()

def update_rpi_thread(textbox=None):
  #c_update = subprocess.run("sudo apt-get update -y && sudo apt-get upgrade -y",shell=True, stdout=subprocess.PIPE)
  c_update = subprocess.Popen("sudo apt-get update -y && sudo apt-get upgrade -y", shell=True, stdout=subprocess.PIPE, bufsize=1, text=True)
  while c_update.poll() is None:
    msg = c_update.stdout.readline().strip()  # read a line from the process output
    if msg:
      textbox.insert(tkinter.END, msg + "\n")
      textbox.see("end")
  textbox.insert(tkinter.END,"\n"+"---- UPDATE FINISHED ----"+"\n")
  textbox.see("end")

#  print(c_update.stdout.decode())

def raise_frame(frame):
  frame.tkraise()

class Redirect():

    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.insert('end', text)
        self.widget.see('end') # autoscroll

    def flush(self):
        pass

master=tkinter.Tk()
master.title("Controller")
#master.geometry("350x275")
master.attributes('-fullscreen',True)
master.config(cursor="none")
master.configure(background=b_c_bg)

#Main
frame_Main= tkinter.Frame(master)
#frame_Main.configure(background=b_c_bg)
frame_Salvage= tkinter.Frame(master)
frame_Mining= tkinter.Frame(master)
frame_Emotes1= tkinter.Frame(master)
frame_Emotes2= tkinter.Frame(master)
frame_Turret= tkinter.Frame(master)
frame_Camera= tkinter.Frame(master)
frame_AdvancedCamera1= tkinter.Frame(master)
frame_AdvancedCamera2= tkinter.Frame(master)
frame_AdvancedCamera3= tkinter.Frame(master)
frame_Engineering= tkinter.Frame(master)
frame_Shield= tkinter.Frame(master)
frame_Flight= tkinter.Frame(master)
frame_Drive= tkinter.Frame(master)
frame_FPS= tkinter.Frame(master)
frame_Info= tkinter.Frame(master)
frame_Info2= tkinter.Frame(master)
frame_Debug= tkinter.Frame(master)
frame_Settings= tkinter.Frame(master)
frame_Setup= tkinter.Frame(master)
frame_Fight= tkinter.Frame(master)
frame_Target= tkinter.Frame(master)

for frame in (frame_Main, frame_Fight, frame_Target, frame_Salvage, frame_Mining, frame_Emotes1, frame_Emotes2, frame_Turret, frame_Camera, frame_Engineering, frame_AdvancedCamera1, frame_AdvancedCamera2, frame_AdvancedCamera3, frame_Info, frame_Info2, frame_Settings, frame_Flight, frame_Drive, frame_FPS, frame_Debug, frame_Setup, frame_Shield):
    frame.configure(background=b_c_bg)
    frame.grid(row=4, column=7, sticky='news')


i_general_ui_back = resize_image("general_ui_close_and_back.png")
i_general_ui_previous = resize_image("general_ui_previous.png")
i_general_ui_next = resize_image("general_ui_next.png")
i_general_ui_home = resize_image("general_ui_home.png")
i_general_ui_quit = resize_image("general_ui_quit.png")
i_general_ui_desktop = resize_image("general_ui_button_desktop.png")
i_general_ui_update = resize_image("general_ui_button_update.png")
i_general_ui_shutdown = resize_image("general_ui_button_shutdown.png")
i_general_ui_voice_attack = resize_image("general_ui_button_voice_attack.png")
i_general_ui_team_speak = resize_image("general_ui_button_team_speak.png")
i_general_increase = resize_image("vehicle_mining_increase_icon.png")
i_general_decrease = resize_image("vehicle_mining_decrease_icon.png")
i_empty = resize_image("head_tracking_voip_foip_empty.png")
i_general_dark = resize_image("general_ui_button_dark.png")
i_general_bright = resize_image("general_ui_button_bright.png")
i_social_general_accept = resize_image("social_general_accept.png")
i_social_general_reject = resize_image("social_general_reject.png")
i_general_ui_info = resize_image("misc_display_info_icon.png")
i_general_ui_setup = resize_image("general_ui_button_controller_setup.png")

i_flight_power_engine_icon = resize_image("flight_power_engine_icon.png")
i_flight_power_power_icon = resize_image("flight_power_power_icon.png")
i_LandingGearButton = resize_image("flight_movement_gear_icon.png")
i_vehicles_weapons_cycle_gimble_mode = resize_image("vehicles_weapons_cycle_gimble_mode.png")


#button_Test=create_button(current_frame, "Test", i_general_dark, trigger, "", "button", None, row=2, column=1)
#button_Test2=create_button(current_frame, "Test2\nTest3", i_general_dark, trigger, "", "button", None, row=2, column=2)


#############################################################################################################################################################
### Main Frame ##############################################################################################################################################
#############################################################################################################################################################
trigger = 20
current_frame=frame_Main
create_dummys(current_frame, i_empty)

#Images
i_general_ui_pilot = resize_image("general_ui_pilot.png")
i_general_ui_mode_drive_text = resize_image("general_ui_mode_drive_text.png")
i_general_ui_fpshoot = resize_image("general_ui_fpshoot.png")
i_general_ui_fight = resize_image("general_ui_fight.png")
i_general_ui_target = resize_image("general_ui_target.png")
i_general_ui_emote = resize_image("general_ui_emote.png")
i_general_ui_settings = resize_image("general_ui_settings.png")
i_advanced_camera_control_icon = resize_image("advanced_camera_control_icon.png")

button_Main_Flight=create_button(current_frame, "", i_general_ui_pilot, None, "", "redir", target_frame=frame_Flight, row=1, column=1)
button_Main_Drive=create_button(current_frame, "", i_general_ui_mode_drive_text, None, "", "redir", target_frame=frame_Drive, row=1, column=2)
button_Main_FPS=create_button(current_frame, "", i_general_ui_fpshoot, None, "", "redir", target_frame=frame_FPS, row=1, column=3)
button_Main_Fight=create_button(current_frame, "", i_general_ui_fight, None, "", "redir", target_frame=frame_Fight, row=1, column=4)
button_Main_Target=create_button(current_frame, "", i_general_ui_target, None, "", "redir", target_frame=frame_Target, row=1, column=5)
button_Main_Settings=create_button(current_frame, "", i_general_ui_settings, None, "", "redir", target_frame=frame_Settings, row=1, column=7)
button_Main_info=create_button(current_frame, "", i_general_ui_info, None, "", "redir", target_frame=frame_Info, row=3, column=7)
button_Main_camera=create_button(current_frame, "", i_advanced_camera_control_icon, None, "", "redir", target_frame=frame_Camera, row=4, column=6)
button_Main_Emote=create_button(current_frame, "", i_general_ui_emote, None, "", "redir", target_frame=frame_Emotes1, row=4, column=7)


trigger_accept = trigger
button_Main_41=create_button(current_frame, "", i_social_general_accept, trigger, "", "button", None, row=4, column=1)
trigger = trigger+1

trigger_decline= trigger
button_Main_42=create_button(current_frame, "", i_social_general_reject, trigger, "", "button", None, row=4, column=2)
trigger = trigger+1


#############################################################################################################################################################
### Flight Frame ############################################################################################################################################
#############################################################################################################################################################
trigger = 30
current_frame=frame_Flight
create_dummys(current_frame, i_empty)

#Images
i_flight_power_flightsysready = resize_image("flight_power_flightsysready.png")
i_flight_movement_request_landing_icon = resize_image("flight_movement_request_landing_icon.png")
i_flight_movement_gear_up_icon = resize_image("flight_movement_gear_up_icon.png")
i_flight_movement_gear_down_icon = resize_image("flight_movement_gear_down_icon.png")
i_vehicles_cockpit_open_doors_icon = resize_image("vehicles_cockpit_open_doors_icon.png")
i_vehicles_cockpit_close_doors_icon = resize_image("vehicles_cockpit_close_doors_icon.png")
i_lights_light_icon = resize_image("lights_light_icon.png")
i_flight_power_engine_icon = resize_image("flight_power_engine_icon.png")
i_vehicle_scanning_scan_icon = resize_image("vehicle_scanning_scan_icon.png")
i_flight_movement_scm_mode_icon = resize_image("flight_movement_scm_mode_icon.png")
i_flight_movement_nav_mode_icon = resize_image("flight_movement_nav_mode_icon.png")
i_mobiglass_sky_map = resize_image("mobiglass_sky_map.png")
i_vehicles_seat_operator_modes_salvage_mode_icon = resize_image("vehicles_seat_operator_modes_salvage_mode_icon.png")
i_vehicles_seat_operator_modes_mining_mode_icon = resize_image("vehicles_seat_operator_modes_mining_mode_icon.png")
i_vehicles_seat_operator_modes_enter_remote_turret_icon = resize_image("vehicles_seat_operator_modes_enter_remote_turret_icon.png")
i_engineering_icon = resize_image("general_ui_engineer.png")
i_vehicles_cockpit_lock_doors_icon = resize_image("vehicles_cockpit_lock_doors_icon.png")
i_vehicles_cockpit_lookbehind_on = resize_image("vehicles_cockpit_lookbehind_ON.png")
i_vehicles_cockpit_lookbehind_off = resize_image("vehicles_cockpit_lookbehind_OFF.png")
i_flight_movement_decoupled_mode_icon = resize_image("flight_movement_decoupled_mode_icon.png")
i_flight_movement_vtol_mode_icon = resize_image("flight_movement_vtol_mode_icon.png")

#button_Flight_11=create_button(current_frame, "", i_flight_power_flightsysready, trigger, "", "button", None, row=1, column=1)
button_Flight_11=create_button(current_frame, "", i_flight_power_flightsysready, KEYB.KEY_RIGHT_ALT, "r", "key", None, row=1, column=1)
trigger = trigger+1

#button_Flight_21=create_button(current_frame, "", i_flight_movement_request_landing_icon, trigger, "", "button", None, row=2, column=1)
button_Flight_21=create_button(current_frame, "", i_flight_movement_request_landing_icon, KEYB.KEY_LEFT_ALT, "n", "key", None, row=2, column=1)
trigger = trigger+1

button_Flight_12=create_button(current_frame, "", i_flight_movement_gear_up_icon, trigger, "", "button", None, row=1, column=2)
trigger = trigger+1

button_Flight_22=create_button(current_frame, "", i_flight_movement_gear_down_icon, trigger, "", "button", None, row=2, column=2)
trigger = trigger+1

button_Flight_13=create_button(current_frame, "", i_vehicles_cockpit_open_doors_icon, trigger, "", "button", None, row=2, column=3)
trigger = trigger+1

button_Flight_23=create_button(current_frame, "", i_vehicles_cockpit_close_doors_icon, trigger, "", "button", None, row=1, column=3)
trigger = trigger+1

trigger_Lights = trigger
button_Flight_15=create_button(current_frame, "", i_lights_light_icon, trigger_Lights, "", "button", None, row=1, column=5)
trigger = trigger+1

trigger_Toggle_Engine_Power = trigger
button_Flight_15=create_button(current_frame, "", i_flight_power_engine_icon, trigger_Toggle_Engine_Power, "", "button", None, row=1, column=4)
trigger = trigger+1

trigger_Scan = trigger
button_Flight_43=create_button(current_frame, "", i_vehicle_scanning_scan_icon, trigger_Scan, "", "button", None, row=4, column=3)
trigger = trigger+1

trigger_SCM_Mode = trigger
button_Flight_44=create_button(current_frame, "", i_flight_movement_scm_mode_icon, trigger_SCM_Mode, "", "button", None, row=4, column=4)
trigger = trigger+1

trigger_NAV_Mode = trigger
button_Flight_45=create_button(current_frame, "", i_flight_movement_nav_mode_icon, trigger_NAV_Mode, "", "button", None, row=4, column=5)
trigger = trigger+1

button_Flight_46=create_button(current_frame, "", i_mobiglass_sky_map, KEYB.KEY_F2, "", "key", None, row=4, column=6)
trigger = trigger+1

button_Flight_Salvage=create_button(current_frame, "", i_vehicles_seat_operator_modes_salvage_mode_icon, trigger, "", "redir+button", target_frame=frame_Salvage, row=3, column=1)
trigger = trigger+1

button_Flight_Mining=create_button(current_frame, "", i_vehicles_seat_operator_modes_mining_mode_icon, trigger, "", "redir+button", target_frame=frame_Mining, row=3, column=2)
trigger = trigger+1

button_Flight_Turret=create_button(current_frame, "", i_vehicles_seat_operator_modes_enter_remote_turret_icon, trigger, "", "redir+button", target_frame=frame_Turret, row=3, column=3)
trigger = trigger+1

button_Flight_engineering=create_button(current_frame, "", i_engineering_icon, None, "", "redir", target_frame=frame_Engineering, row=3, column=6)

button_Flight_24=create_button(current_frame, "", i_vehicles_cockpit_lock_doors_icon, trigger, "", "button", None, row=2, column=4)
trigger = trigger+1

button_Flight_41=create_button(current_frame, "", i_social_general_accept, trigger_accept, "", "button", None, row=4, column=1)

button_Flight_42=create_button(current_frame, "", i_social_general_reject, trigger_decline, "", "button", None, row=4, column=2)

#UNUSED
trigger = trigger+1
trigger = trigger+1

button_Flight_16=create_button(current_frame, "", i_vehicles_cockpit_lookbehind_on, trigger, "", "on", None, row=1, column=6)
button_Flight_26=create_button(current_frame, "", i_vehicles_cockpit_lookbehind_off, trigger, "", "off", None, row=2, column=6)
trigger = trigger+1

button_Flight_info=create_button(current_frame, "", i_general_ui_info, trigger, "", "redir", target_frame=frame_Info, row=2, column=7)

#UNUSED
trigger = trigger+1

button_Flight_35=create_button(current_frame, "", i_flight_movement_decoupled_mode_icon, trigger, "", "button", None, row=3, column=5)
trigger = trigger+1

button_Flight_34=create_button(current_frame, "", i_flight_movement_vtol_mode_icon, 1000, "k", "key", None, row=3, column=4)

button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Info Frame ##############################################################################################################################################
#############################################################################################################################################################
current_frame=frame_Info
create_dummys(current_frame, i_empty)

i_aaron_halo_info_original = Image.open(os.path.join(img_files_path,"Aaron_Halo.png"))
i_aaron_halo_info_resize = i_aaron_halo_info_original.resize((1020, 448))
i_aaron_halo_info = ImageTk.PhotoImage(i_aaron_halo_info_resize)

label_aaron_halo = tkinter.Label(current_frame, image = i_aaron_halo_info, bg=b_c_bg)
label_aaron_halo.grid(row=1, column=1, rowspan=3, columnspan=7)

#Activate SCM Mode
button_Info_44=create_button(current_frame, "", i_flight_movement_scm_mode_icon, trigger_SCM_Mode, "", "button", None, row=4, column=1)

#Activate NAV Mode
button_Info_45=create_button(current_frame, "", i_flight_movement_nav_mode_icon, trigger_NAV_Mode, "", "button", None, row=4, column=2)

#MAP
button_Info_46=create_button(current_frame, "", i_mobiglass_sky_map, KEYB.KEY_F2, "", "key", None, row=4, column=3)
#button_Info_46=create_button(current_frame, "", i_mobiglass_sky_map, trigger_Map, "", "button", None, row=4, column=3)

button_Info_frame_Info_Previous=create_button(current_frame, "", i_general_ui_previous, None, "", "redir", target_frame=frame_Info2, row=4, column=5)
button_Info_frame_Info_Next=create_button(current_frame, "", i_general_ui_next, None, "", "redir", target_frame=frame_Info2, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Info2 Frame #############################################################################################################################################
#############################################################################################################################################################
current_frame=frame_Info2
create_dummys(current_frame, i_empty)

i_components_original = Image.open(os.path.join(img_files_path,"components.png"))
i_components_resize = i_components_original.resize((1020, 448))
i_components_info = ImageTk.PhotoImage(i_components_resize)

label_aaron_halo2 = tkinter.Label(current_frame, image = i_components_info, bg=b_c_bg)
label_aaron_halo2.grid(row=1, column=1, rowspan=3, columnspan=7)

button_Info2_43=create_button(current_frame, "", i_vehicle_scanning_scan_icon, trigger_Scan, "", "button", None, row=4, column=3)
button_Info2_frame_Info_Previous=create_button(current_frame, "", i_general_ui_previous, None, "", "redir", target_frame=frame_Info, row=4, column=5)
button_Info2_frame_Info_Next=create_button(current_frame, "", i_general_ui_next, None, "", "redir", target_frame=frame_Info, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Salvage Frame ###########################################################################################################################################
#############################################################################################################################################################
trigger = 60
current_frame=frame_Salvage
create_dummys(current_frame, i_empty)

#Images
i_vehicles_salvage_salvage_mode_icon = resize_image("vehicles_salvage_salvage_mode_icon.png")
i_vehicles_salvage_tractor_beam_mode_icon = resize_image("vehicles_salvage_tractor_beam_mode_icon.png")
i_vehicles_salvage_cut_mode_icon = resize_image("vehicles_salvage_cut_mode_icon.png")
i_vehicles_salvage_fracture_mode_icon = resize_image("vehicles_salvage_fracture_mode_icon.png")
i_vehicles_salvage_disintegrate_mode_icon = resize_image("vehicles_salvage_disintegrate_mode_icon.png")
i_vehicles_salvage_increase_beam_spacing_icon = resize_image("vehicles_salvage_increase_beam_spacing_icon.png")
i_vehicles_salvage_toggle_fire_focused_icon = resize_image("vehicles_salvage_toggle_fire_focused_icon.png")
i_vehicles_salvage_toggle_fire_right_icon = resize_image("vehicles_salvage_toggle_fire_right_icon.png")
i_vehicles_salvage_toggle_fire_left_icon = resize_image("vehicles_salvage_toggle_fire_left_icon.png")
i_vehicles_salvage_toggle_fire_fracture_icon = resize_image("vehicles_salvage_toggle_fire_fracture_icon.png")
i_vehicles_salvage_toggle_fire_disintegrate_icon = resize_image("vehicles_salvage_toggle_fire_disintegrate_icon.png")
i_vehicles_salvage_decrease_beam_spacing_icon = resize_image("vehicles_salvage_decrease_beam_spacing_icon.png")
i_vehicles_salvage_cycle_focused_modifiers_icon = resize_image("vehicles_salvage_cycle_focused_modifiers_icon.png")
i_vehicles_salvage_cycle_right_modifiers_icon = resize_image("vehicles_salvage_cycle_right_modifiers_icon.png")
i_vehicles_salvage_cycle_left_modifiers_icon = resize_image("vehicles_salvage_cycle_left_modifiers_icon.png")
i_vehicles_salvage_gimball_icon = resize_image("vehicles_salvage_gimball_icon.png")
i_vehicles_salvage_free_gimball_icon = resize_image("vehicles_salvage_free_gimball_icon.png")
i_vehicles_salvage_cycle_structure_modifiers_icon = resize_image("vehicles_salvage_cycle_structure_modifiers_icon.png")
i_vehicles_salvage_focus_icon = resize_image("vehicles_salvage_focus_icon.png")
i_vehicles_salvage_salvage_beam_axis_toggle_icon = resize_image("vehicles_salvage_salvage_beam_axis_toggle_icon.png")
i_vehicles_cockpit_unlock_all_ports_icon = resize_image("vehicles_cockpit_unlock_all_ports_icon.png")

button_Salvage_11=create_button(current_frame, "", i_vehicles_salvage_salvage_mode_icon, trigger, "", "button", None, row=1, column=1)
trigger = trigger+1

button_Salvage_12=create_button(current_frame, "", i_vehicles_salvage_tractor_beam_mode_icon, trigger, "", "button", None, row=1, column=2)
trigger = trigger+1

button_Salvage_14=create_button(current_frame, "", i_lights_light_icon, trigger_Lights, "", "button", None, row=1, column=4)

button_Salvage_15=create_button(current_frame, "", i_vehicles_salvage_cut_mode_icon, trigger, "", "button", None, row=1, column=5)
trigger = trigger+1

button_Salvage_16=create_button(current_frame, "", i_vehicles_salvage_fracture_mode_icon, trigger, "", "button", None, row=1, column=6)
trigger = trigger+1

button_Salvage_17=create_button(current_frame, "", i_vehicles_salvage_disintegrate_mode_icon, trigger, "", "button", None, row=1, column=7)
trigger = trigger+1

button_Salvage_21=create_button(current_frame, "", i_vehicles_salvage_increase_beam_spacing_icon, trigger, "", "button", None, row=2, column=1)
trigger = trigger+1

button_Salvage_22=create_button(current_frame, "", i_vehicles_salvage_toggle_fire_focused_icon, trigger, "", "button", None, row=2, column=2)
trigger = trigger+1

#button_Salvage_24=create_button(current_frame, "", i_vehicles_salvage_toggle_fire_right_icon, trigger, "", "button", None, row=2, column=4)
button_Salvage_24=create_button(current_frame, "", i_vehicles_salvage_toggle_fire_right_icon, KEYB.KEY_RIGHT_ALT, "d", "key", None, row=2, column=4)
trigger = trigger+1

#button_Salvage_23=create_button(current_frame, "", i_vehicles_salvage_toggle_fire_left_icon, trigger, "", "button", None, row=2, column=3)
button_Salvage_23=create_button(current_frame, "", i_vehicles_salvage_toggle_fire_left_icon, KEYB.KEY_RIGHT_ALT, "a", "key", None, row=2, column=3)
trigger = trigger+1

#button_Salvage_26=create_button(current_frame, "", i_vehicles_salvage_toggle_fire_fracture_icon, trigger, "", "button", None, row=2, column=6)
button_Salvage_26=create_button(current_frame, "", i_vehicles_salvage_toggle_fire_fracture_icon, KEYB.KEY_RIGHT_ALT, "w", "key", None, row=2, column=6)
trigger = trigger+1

#button_Salvage_27=create_button(current_frame, "", i_vehicles_salvage_toggle_fire_disintegrate_icon, trigger, "", "button", None, row=2, column=7)
button_Salvage_27=create_button(current_frame, "", i_vehicles_salvage_toggle_fire_disintegrate_icon, KEYB.KEY_RIGHT_ALT, "s", "key", None, row=2, column=7)
trigger = trigger+1

button_Salvage_31=create_button(current_frame, "", i_vehicles_salvage_decrease_beam_spacing_icon, trigger, "", "button", None, row=3, column=1)
trigger = trigger+1

button_Salvage_32=create_button(current_frame, "", i_vehicles_salvage_cycle_focused_modifiers_icon, trigger, "", "button", None, row=3, column=2)
trigger = trigger+1

button_Salvage_34=create_button(current_frame, "", i_vehicles_salvage_cycle_right_modifiers_icon, trigger, "", "button", None, row=3, column=4)
trigger = trigger+1

button_Salvage_33=create_button(current_frame, "", i_vehicles_salvage_cycle_left_modifiers_icon, trigger, "", "button", None, row=3, column=3)
trigger = trigger+1

button_Salvage_41=create_button(current_frame, "", i_vehicles_salvage_gimball_icon, trigger, "", "button", None, row=4, column=4)
trigger = trigger+1

button_Salvage_42=create_button(current_frame, "", i_vehicles_salvage_free_gimball_icon, trigger, "", "button", None, row=4, column=2)
trigger = trigger+1

button_Salvage_35=create_button(current_frame, "", i_vehicles_salvage_cycle_structure_modifiers_icon, trigger, "", "button", None, row=3, column=5)
trigger = trigger+1

button_Salvage_44=create_button(current_frame, "", i_vehicles_salvage_focus_icon, trigger, "", "button", None, row=4, column=1)
trigger = trigger+1

button_Salvage_43=create_button(current_frame, "", i_vehicle_scanning_scan_icon, trigger_Scan, "", "button", None, row=4, column=3)

button_Salvage_45=create_button(current_frame, "", i_vehicles_salvage_salvage_beam_axis_toggle_icon, trigger, "", "button", None, row=4, column=5)
trigger = trigger+1

button_Salvage_37=create_button(current_frame, "", i_vehicles_cockpit_unlock_all_ports_icon, KEYB.KEY_RIGHT_ALT, "k", "key", None, row=3, column=7)

button_Salvage_13=create_button(current_frame, "", i_flight_power_engine_icon, trigger_Toggle_Engine_Power, "", "button", None, row=1, column=3)

button_Salvage_back=create_button(current_frame, "", i_general_ui_back, None, "", "redir", target_frame=frame_Flight, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Mining Frame ############################################################################################################################################
#############################################################################################################################################################
trigger = 90
current_frame=frame_Mining
create_dummys(current_frame, i_empty)

#Images
i_vehicle_mining_laser_fire_icon = resize_image("vehicle_mining_laser_fire_icon.png")
i_vehicle_mining_switch_laser_type_icon = resize_image("vehicle_mining_switch_laser_type_icon.png")
i_vehicle_mining_jettison_cargo_icon = resize_image("vehicle_mining_jettison_cargo_icon.png")
i_vehicle_mining_increase_icon = resize_image("vehicle_mining_increase_icon.png")
i_vehicle_mining_decrease_icon = resize_image("vehicle_mining_decrease_icon.png")
i_vehicle_mining_module01_text = resize_image("vehicle_mining_module01_text.png")
i_vehicle_mining_module02_text = resize_image("vehicle_mining_module02_text.png")
i_vehicle_mining_module03_text = resize_image("vehicle_mining_module03_text.png")

button_Mining_11=create_button(current_frame, "", i_vehicle_mining_laser_fire_icon, trigger, "", "button", None, row=1, column=1)
trigger = trigger+1

button_Mining_12=create_button(current_frame, "", i_vehicle_mining_switch_laser_type_icon, trigger, "", "button", None, row=1, column=2)
trigger = trigger+1

button_Mining_17=create_button(current_frame, "", i_vehicle_mining_jettison_cargo_icon, KEYB.KEY_LEFT_ALT, "j", "key", None, row=1, column=7)
trigger = trigger+1

button_Mining_21=create_button(current_frame, "", i_vehicle_mining_increase_icon, trigger, "", "button", None, row=2, column=1)
trigger = trigger+1

button_Mining_31=create_button(current_frame, "", i_vehicle_mining_decrease_icon, trigger, "", "button", None, row=3, column=1)
trigger = trigger+1

button_Mining_41=create_button(current_frame, "Modul\n-01-", i_general_dark, KEYB.KEY_LEFT_ALT, "1", "key", None, row=4, column=1)
trigger = trigger+1

button_Mining_42=create_button(current_frame, "Modul\n-02-", i_general_dark, KEYB.KEY_LEFT_ALT, "2", "key", None, row=4, column=2)
trigger = trigger+1

button_Mining_43=create_button(current_frame, "Modul\n-03-", i_general_dark, KEYB.KEY_LEFT_ALT, "3", "key", None, row=4, column=3)
trigger = trigger+1

button_Mining_44=create_button(current_frame, "Modul\n-04-", i_general_dark, KEYB.KEY_LEFT_ALT, "4", "key", None, row=4, column=4)
trigger = trigger+1

button_Mining_back=create_button(current_frame, "", i_general_ui_back, None, "", "redir", target_frame=frame_Flight, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Turret Frame ############################################################################################################################################
#############################################################################################################################################################
trigger = 120
current_frame=frame_Turret
create_dummys(current_frame, i_empty)

#Images
i_vehicles_seat_operator_modes_remote_turret1_icon = resize_image("vehicles_seat_operator_modes_remote_turret1_icon.png")
i_vehicles_seat_operator_modes_remote_turret2_icon = resize_image("vehicles_seat_operator_modes_remote_turret2_icon.png")
i_vehicles_seat_operator_modes_remote_turret3_icon = resize_image("vehicles_seat_operator_modes_remote_turret3_icon.png")
i_turret_movement_previous_remote_turret = resize_image("turret_movement_previous_remote_turret.png")
i_turret_advanced_turret_change_position_icon = resize_image("turret_advanced_turret_change_position_icon.png")
i_turret_movement_next_remote_turret = resize_image("turret_movement_next_remote_turret.png")
i_turret_movement_exit_remote_turret = resize_image("turret_movement_exit_remote_turret.png")
i_turret_advanced_instant_zoom_icon = resize_image("turret_advanced_instant_zoom_icon.png")
i_turret_movement_zoom_in_icon2 = resize_image("turret_movement_zoom_in_icon2.png")
i_turret_movement_zoom_out_icon2 = resize_image("turret_movement_zoom_out_icon2.png")
i_turret_advanced_turret_speed_limiter_text = resize_image("turret_advanced_turret_speed_limiter_text.png")
i_turret_advanced_turret_speed_limiter_increase_text = resize_image("turret_advanced_turret_speed_limiter_increase_text.png")
i_turret_advanced_turret_speed_limiter_decrease_text = resize_image("turret_advanced_turret_speed_limiter_decrease_text.png")
i_vehicles_weapons_set_auto_gimbal_icon = resize_image("vehicles_weapons_set_auto_gimbal_icon.png")
i_vehicles_weapons_set_manual_gimbal_icon = resize_image("vehicles_weapons_set_manual_gimbal_icon.png")
i_vehicles_weapons_set_fixed_gimbal_icon = resize_image("vehicles_weapons_set_fixed_gimbal_icon.png")
i_vehicles_weapons_cycle_gimbal_icon = resize_image("vehicles_weapons_cycle_gimbal_icon.png")
i_vehicles_weapons_lock_gimbal_icon = resize_image("vehicles_weapons_lock_gimbal_icon.png")
i_turret_movement_FPS_Vjoy = resize_image("turret_movement_FPS_Vjoy.png")
i_turret_movement_gyro_icon3 = resize_image("turret_movement_gyro_icon3.png")
i_turret_advanced_turret_esp_icon = resize_image("turret_advanced_turret_esp_icon.png")
i_turret_advanced_recenter_turret_icon = resize_image("turret_advanced_recenter_turret_icon.png")
i_turret_advanced_cycle_fire_mode_icon = resize_image("turret_advanced_cycle_fire_mode_icon.png")

button_Turret_11=create_button(current_frame, "", i_vehicles_seat_operator_modes_remote_turret1_icon, trigger, "", "button", None, row=1, column=1)
trigger = trigger+1

button_Turret_12=create_button(current_frame, "", i_vehicles_seat_operator_modes_remote_turret2_icon, trigger, "", "button", None, row=1, column=2)
trigger = trigger+1

button_Turret_13=create_button(current_frame, "", i_vehicles_seat_operator_modes_remote_turret3_icon, trigger, "", "button", None, row=1, column=3)
trigger = trigger+1

button_Turret_14=create_button(current_frame, "", i_turret_movement_previous_remote_turret, 1000, "e", "key", None, row=1, column=4)
trigger = trigger+1

button_Turret_15=create_button(current_frame, "", i_turret_advanced_turret_change_position_icon, 1000, "s", "key", None, row=1, column=5)
trigger = trigger+1

button_Turret_16=create_button(current_frame, "", i_turret_movement_next_remote_turret, 1000, "d", "key", None, row=1, column=6)
trigger = trigger+1

button_Turret_17=create_button(current_frame, "", i_turret_movement_exit_remote_turret, 1000, "y", "key", None, row=1, column=7)
trigger = trigger+1

button_Turret_21=create_button(current_frame, "", i_turret_advanced_instant_zoom_icon, trigger, "", "button", None, row=2, column=1)
trigger = trigger+1

button_Turret_32=create_button(current_frame, "", i_turret_movement_zoom_in_icon2, trigger, "", "button", None, row=3, column=1)
trigger = trigger+1

button_Turret_42=create_button(current_frame, "", i_turret_movement_zoom_out_icon2, trigger, "", "button", None, row=4, column=1)
trigger = trigger+1

button_Turret_22=create_button(current_frame, "", i_turret_advanced_turret_speed_limiter_text, trigger, "", "button", None, row=2, column=2)
trigger = trigger+1

button_Turret_32=create_button(current_frame, "", i_turret_advanced_turret_speed_limiter_increase_text, trigger, "", "button", None, row=3, column=2)
trigger = trigger+1

button_Turret_42=create_button(current_frame, "", i_turret_advanced_turret_speed_limiter_decrease_text, trigger, "", "button", None, row=4, column=2)
trigger = trigger+1

button_Turret_23=create_button(current_frame, "", i_vehicles_weapons_set_auto_gimbal_icon, trigger, "", "button", None, row=2, column=3)
trigger = trigger+1

button_Turret_33=create_button(current_frame, "", i_vehicles_weapons_set_manual_gimbal_icon, trigger, "", "button", None, row=3, column=3)
trigger = trigger+1

button_Turret_43=create_button(current_frame, "", i_vehicles_weapons_set_fixed_gimbal_icon, trigger, "", "button", None, row=4, column=3)
trigger = trigger+1

button_Turret_24=create_button(current_frame, "", i_vehicles_weapons_cycle_gimbal_icon, trigger, "", "button", None, row=2, column=4)
trigger = trigger+1

button_Turret_34=create_button(current_frame, "", i_vehicles_weapons_lock_gimbal_icon, trigger, "", "button", None, row=3, column=4)
trigger = trigger+1

button_Turret_26=create_button(current_frame, "", i_turret_movement_FPS_Vjoy, 1000, "q", "key", None, row=2, column=6)
trigger = trigger+1

button_Turret_44=create_button(current_frame, "", i_turret_movement_gyro_icon3, 1000, "e", "key", None, row=4, column=4)
trigger = trigger+1

button_Turret_25=create_button(current_frame, "", i_turret_advanced_turret_esp_icon, trigger, "", "button", None, row=2, column=5)
trigger = trigger+1

button_Turret_35=create_button(current_frame, "", i_turret_advanced_recenter_turret_icon, 1000, "c", "key", None, row=3, column=5)
trigger = trigger+1

button_Turret_45=create_button(current_frame, "", i_turret_advanced_cycle_fire_mode_icon, trigger, "", "button", None, row=4, column=5)
trigger = trigger+1

button_Turret_back=create_button(current_frame, "", i_general_ui_back, None, "", "redir", target_frame=frame_Flight, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)

#############################################################################################################################################################
### Camera Frame ############################################################################################################################################
#############################################################################################################################################################
trigger = 150
current_frame=frame_Camera
create_dummys(current_frame, i_empty)

#Images
i_look_view_1 = resize_image("look_view_1.png")
i_look_view_2 = resize_image("look_view_2.png")
i_look_view_3 = resize_image("look_view_3.png")
i_look_view_4 = resize_image("look_view_4.png")
i_look_view_5 = resize_image("look_view_5.png")
i_look_view_6 = resize_image("look_view_6.png")
i_look_view_7 = resize_image("look_view_7.png")
i_look_view_8 = resize_image("look_view_8.png")
i_look_view_9 = resize_image("look_view9.png")
i_view_3x3_icon_1 = resize_image("view_3x3_icon_1.png")
i_view_3x3_icon_2 = resize_image("view_3x3_icon_2.png")
i_view_3x3_icon_3 = resize_image("view_3x3_icon_3.png")
i_view_3x3_icon_6 = resize_image("view_3x3_icon_6.png")
i_view_3x3_icon_4 = resize_image("view_3x3_icon_4.png")
i_view_3x3_icon_5 = resize_image("view_3x3_icon_5.png")
i_view_3x3_icon_7 = resize_image("view_3x3_icon_7.png")
i_view_3x3_icon_8 = resize_image("view_3x3_icon_8.png")
i_view_3x3_icon_9 = resize_image("view_3x3_icon_9.png")
i_advanced_camera_control_modifier = resize_image("advanced_camera_control_modifier.png")

button_Camera_11=create_button(current_frame, "", i_look_view_1, trigger, "", "button", None, row=1, column=1)
trigger = trigger+1

button_Camera_12=create_button(current_frame, "", i_look_view_2, trigger, "", "button", None, row=1, column=2)
trigger = trigger+1

button_Camera_13=create_button(current_frame, "", i_look_view_3, trigger, "", "button", None, row=1, column=3)

button_Camera_21=create_button(current_frame, "", i_look_view_4, trigger, "", "button", None, row=2, column=1)
trigger = trigger+1

button_Camera_22=create_button(current_frame, "", i_look_view_5, trigger, "", "button", None, row=2, column=2)
trigger = trigger+1

button_Camera_23=create_button(current_frame, "", i_look_view_6, trigger, "", "button", None, row=2, column=3)
trigger = trigger+1

button_Camera_31=create_button(current_frame, "", i_look_view_7, trigger, "", "button", None, row=3, column=1)

button_Camera_32=create_button(current_frame, "", i_look_view_8, trigger, "", "button", None, row=3, column=2)
trigger = trigger+1

button_Camera_33=create_button(current_frame, "", i_look_view_9, trigger, "", "button", None, row=3, column=3)
trigger = trigger+1

button_Camera_15=create_button(current_frame, "", i_view_3x3_icon_1, trigger, "", "button", None, row=1, column=5)
trigger = trigger+1

button_Camera_16=create_button(current_frame, "", i_view_3x3_icon_2, trigger, "", "button", None, row=1, column=6)
trigger = trigger+1

button_Camera_17=create_button(current_frame, "", i_view_3x3_icon_3, trigger, "", "button", None, row=1, column=7)
trigger = trigger+1

button_Camera_25=create_button(current_frame, "", i_view_3x3_icon_6, trigger, "", "button", None, row=2, column=5)
trigger = trigger+1

button_Camera_26=create_button(current_frame, "", i_view_3x3_icon_4, trigger, "", "button", None, row=2, column=6)
trigger = trigger+1

button_Camera_27=create_button(current_frame, "", i_view_3x3_icon_5, trigger, "", "button", None, row=2, column=7)
trigger = trigger+1

button_Camera_35=create_button(current_frame, "", i_view_3x3_icon_7, trigger, "", "button", None, row=3, column=5)
trigger = trigger+1

button_Camera_36=create_button(current_frame, "", i_view_3x3_icon_8, trigger, "", "button", None, row=3, column=6)
trigger = trigger+1

button_Camera_37=create_button(current_frame, "", i_view_3x3_icon_9, trigger, "", "button", None, row=3, column=7)
trigger = trigger+1

button_Camera_016=create_button(current_frame, "", i_advanced_camera_control_modifier, None, "", "redir", target_frame=frame_AdvancedCamera1, row=4, column=1)

button_Camera_back=create_button(current_frame, "", i_general_ui_back, None, "", "redir", target_frame=frame_Flight, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Advanced Camera1 Frame ##################################################################################################################################
#############################################################################################################################################################
current_frame=frame_AdvancedCamera1
create_dummys(current_frame, i_empty)

#Images
i_advanced_camera_controls_1 = resize_image("advanced_camera_controls_1.png")
i_advanced_camera_controls_2 = resize_image("advanced_camera_controls_2.png")
i_advanced_camera_controls_3 = resize_image("advanced_camera_controls_3.png")
i_advanced_camera_controls_4 = resize_image("advanced_camera_controls_4.png")
i_advanced_camera_controls_5 = resize_image("advanced_camera_controls_5.png")
i_advanced_camera_controls_6 = resize_image("advanced_camera_controls_6.png")
i_advanced_camera_controls_7_alternate = resize_image("advanced_camera_controls_7_alternate.png")
i_advanced_camera_controls_8 = resize_image("advanced_camera_controls_8.png")
i_advanced_camera_controls_9 = resize_image("advanced_camera_controls_9.png")
i_advanced_camera_control_decrease_field_of_view_icon = resize_image("advanced_camera_control_decrease_field_of_view_icon.png")
i_advanced_camera_control_increase_field_of_view_icon = resize_image("advanced_camera_control_increase_field_of_view_icon.png")
i_advanced_camera_control_decrease_depth_of_field = resize_image("advanced_camera_control_decrease_depth_of_field.png")
i_advanced_camera_control_increase_depth_of_field = resize_image("advanced_camera_control_increase_depth_of_field.png")

button_AdvancedCamera1_11=create_button(current_frame, "", i_advanced_camera_controls_1, KEYB.KEY_PAGE_UP+100, "K", "key", None, row=1, column=1)
button_AdvancedCamera1_12=create_button(current_frame, "", i_advanced_camera_controls_2, KEYB.KEY_UP_ARROW+100, "K", "key", None, row=1, column=2)
button_AdvancedCamera1_13=create_button(current_frame, "", i_advanced_camera_controls_3, KEYB.KEY_KP_ASTERISK+100, "K", "key", None, row=1, column=3)
button_AdvancedCamera1_21=create_button(current_frame, "", i_advanced_camera_controls_4, KEYB.KEY_LEFT_ARROW+100, "K", "key", None, row=2, column=1)
button_AdvancedCamera1_22=create_button(current_frame, "", i_advanced_camera_controls_5, KEYB.KEY_F4, "K", "key", None, row=2, column=2)
button_AdvancedCamera1_23=create_button(current_frame, "", i_advanced_camera_controls_6, KEYB.KEY_RIGHT_ARROW+100, "K", "key", None, row=2, column=3)
button_AdvancedCamera1_31=create_button(current_frame, "", i_advanced_camera_controls_7_alternate, KEYB.KEY_F4, "K", "key", None, row=3, column=1)
button_AdvancedCamera1_32=create_button(current_frame, "", i_advanced_camera_controls_8, KEYB.KEY_DOWN_ARROW+100, "K", "key", None, row=3, column=2)
button_AdvancedCamera1_33=create_button(current_frame, "", i_advanced_camera_controls_9, KEYB.KEY_PAGE_DOWN+100, "K", "key", None, row=3, column=3)
button_AdvancedCamera1_15=create_button(current_frame, "", i_advanced_camera_control_decrease_field_of_view_icon, KEYB.KEY_KP_PLUS+100, "K", "key", None, row=1, column=5)
button_AdvancedCamera1_16=create_button(current_frame, "", i_advanced_camera_control_increase_field_of_view_icon, KEYB.KEY_KP_MINUS+100, "K", "key", None, row=1, column=6)
button_AdvancedCamera1_25=create_button(current_frame, "", i_advanced_camera_control_decrease_depth_of_field, KEYB.KEY_END+100, "K", "key", None, row=2, column=5)
button_AdvancedCamera1_26=create_button(current_frame, "", i_advanced_camera_control_increase_depth_of_field, KEYB.KEY_HOME+100, "K", "key", None, row=2, column=6)

button_AdvancedCamera1_camera=create_button(current_frame, "", i_advanced_camera_control_icon, None, "", "redir", target_frame=frame_Camera, row=4, column=1)
button_AdvancedCamera1_Previous=create_button(current_frame, "", i_general_ui_previous, None, "", "redir", target_frame=frame_AdvancedCamera3, row=4, column=4)
button_AdvancedCamera1_Next=create_button(current_frame, "", i_general_ui_next, None, "", "redir", target_frame=frame_AdvancedCamera2, row=4, column=5)
button_AdvancedCamera1_back=create_button(current_frame, "", i_general_ui_back, None, "", "redir", target_frame=frame_Flight, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Advanced Camera2 Frame ##################################################################################################################################
#############################################################################################################################################################
current_frame=frame_AdvancedCamera2
create_dummys(current_frame, i_empty)

#Images
i_advanced_camera_control_loadview01 = resize_image("advanced_camera_control_loadview01.png")
i_advanced_camera_control_loadview02 = resize_image("advanced_camera_control_loadview02.png")
i_advanced_camera_control_loadview03 = resize_image("advanced_camera_control_loadview03.png")
i_advanced_camera_control_loadview04 = resize_image("advanced_camera_control_loadview04.png")
i_advanced_camera_control_loadview05 = resize_image("advanced_camera_control_loadview05.png")
i_advanced_camera_control_loadview06 = resize_image("advanced_camera_control_loadview06.png")
i_advanced_camera_control_loadview07 = resize_image("advanced_camera_control_loadview07.png")
i_advanced_camera_control_loadview08 = resize_image("advanced_camera_control_loadview08.png")
i_advanced_camera_control_loadview09 = resize_image("advanced_camera_control_loadview09.png")
i_advanced_camera_control_saveview01 = resize_image("advanced_camera_control_saveview01.png")
i_advanced_camera_control_saveview02 = resize_image("advanced_camera_control_saveview02.png")
i_advanced_camera_control_saveview03 = resize_image("advanced_camera_control_saveview03.png")
i_advanced_camera_control_saveview04 = resize_image("advanced_camera_control_saveview04.png")
i_advanced_camera_control_saveview05 = resize_image("advanced_camera_control_saveview05.png")
i_advanced_camera_control_saveview06 = resize_image("advanced_camera_control_saveview06.png")
i_advanced_camera_control_saveview07 = resize_image("advanced_camera_control_saveview07.png")
i_advanced_camera_control_saveview08 = resize_image("advanced_camera_control_saveview08.png")
i_advanced_camera_control_saveview09 = resize_image("advanced_camera_control_saveview09.png")

button_AdvancedCamera2_15=create_button(current_frame, "", i_advanced_camera_control_loadview01, KEYB.KEY_KP_1+100, "K", "key", None, row=1, column=5)
button_AdvancedCamera2_16=create_button(current_frame, "", i_advanced_camera_control_loadview02, KEYB.KEY_KP_2+100, "K", "key", None, row=1, column=6)
button_AdvancedCamera2_17=create_button(current_frame, "", i_advanced_camera_control_loadview03, KEYB.KEY_KP_3+100, "K", "key", None, row=1, column=7)
button_AdvancedCamera2_25=create_button(current_frame, "", i_advanced_camera_control_loadview04, KEYB.KEY_KP_4+100, "K", "key", None, row=2, column=5)
button_AdvancedCamera2_26=create_button(current_frame, "", i_advanced_camera_control_loadview05, KEYB.KEY_KP_5+100, "K", "key", None, row=2, column=6)
button_AdvancedCamera2_27=create_button(current_frame, "", i_advanced_camera_control_loadview06, KEYB.KEY_KP_6+100, "K", "key", None, row=2, column=7)
button_AdvancedCamera2_35=create_button(current_frame, "", i_advanced_camera_control_loadview07, KEYB.KEY_KP_7+100, "K", "key", None, row=3, column=5)
button_AdvancedCamera2_36=create_button(current_frame, "", i_advanced_camera_control_loadview08, KEYB.KEY_KP_8+100, "K", "key", None, row=3, column=6)
button_AdvancedCamera2_37=create_button(current_frame, "", i_advanced_camera_control_loadview09, KEYB.KEY_KP_9+100, "K", "key", None, row=3, column=7)
button_AdvancedCamera2_11=create_button(current_frame, "", i_advanced_camera_control_saveview01, KEYB.KEY_KP_1+100, "K", "key", None, row=1, column=1)
button_AdvancedCamera2_12=create_button(current_frame, "", i_advanced_camera_control_saveview02, KEYB.KEY_KP_2+100, "K", "key", None, row=1, column=2)
button_AdvancedCamera2_13=create_button(current_frame, "", i_advanced_camera_control_saveview03, KEYB.KEY_KP_3+100, "K", "key", None, row=1, column=3)
button_AdvancedCamera2_21=create_button(current_frame, "", i_advanced_camera_control_saveview04, KEYB.KEY_KP_4+100, "K", "key", None, row=2, column=1)
button_AdvancedCamera2_22=create_button(current_frame, "", i_advanced_camera_control_saveview05, KEYB.KEY_KP_5+100, "K", "key", None, row=2, column=2)
button_AdvancedCamera2_23=create_button(current_frame, "", i_advanced_camera_control_saveview06, KEYB.KEY_KP_6+100, "K", "key", None, row=2, column=3)
button_AdvancedCamera2_31=create_button(current_frame, "", i_advanced_camera_control_saveview07, KEYB.KEY_KP_7+100, "K", "key", None, row=3, column=1)
button_AdvancedCamera2_32=create_button(current_frame, "", i_advanced_camera_control_saveview08, KEYB.KEY_KP_8+100, "K", "key", None, row=3, column=2)
button_AdvancedCamera2_33=create_button(current_frame, "", i_advanced_camera_control_saveview09, KEYB.KEY_KP_9+100, "K", "key", None, row=3, column=3)

button_AdvancedCamera2_camera=create_button(current_frame, "", i_advanced_camera_control_icon, None, "", "redir", target_frame=frame_Camera, row=4, column=1)
button_AdvancedCamera2_Previous=create_button(current_frame, "", i_general_ui_previous, None, "", "redir", target_frame=frame_AdvancedCamera1, row=4, column=4)
button_AdvancedCamera2_Next=create_button(current_frame, "", i_general_ui_next, None, "", "redir", target_frame=frame_AdvancedCamera3, row=4, column=5)
button_AdvancedCamera2_back=create_button(current_frame, "", i_general_ui_back, None, "", "redir", target_frame=frame_Flight, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Advanced Camera3 Frame ##################################################################################################################################
#############################################################################################################################################################
current_frame=frame_AdvancedCamera3
create_dummys(current_frame, i_empty)

#Images
i_advanced_camera_control_view01_icon = resize_image("advanced_camera_control_view01_icon.png")
i_advanced_camera_control_view02_icon = resize_image("advanced_camera_control_view02_icon.png")
i_advanced_camera_control_view03_icon = resize_image("advanced_camera_control_view03_icon.png")
i_advanced_camera_control_view04_icon = resize_image("advanced_camera_control_view04_icon.png")
i_advanced_camera_control_view05_icon = resize_image("advanced_camera_control_view05_icon.png")
i_advanced_camera_control_view06_icon = resize_image("advanced_camera_control_view06_icon.png")
i_advanced_camera_control_view07_icon = resize_image("advanced_camera_control_view07_icon.png")
i_advanced_camera_control_view08_icon = resize_image("advanced_camera_control_view08_icon.png")
i_advanced_camera_control_view09_icon = resize_image("advanced_camera_control_view09_icon.png")

button_AdvancedCamera3_11=create_button(current_frame, "", i_advanced_camera_control_view01_icon, KEYB.KEY_KP_1+100, "k", "key", None, row=1, column=1)
button_AdvancedCamera3_12=create_button(current_frame, "", i_advanced_camera_control_view02_icon, KEYB.KEY_KP_2+100, "k", "key", None, row=1, column=2)
button_AdvancedCamera3_13=create_button(current_frame, "", i_advanced_camera_control_view03_icon, KEYB.KEY_KP_3+100, "k", "key", None, row=1, column=3)
button_AdvancedCamera3_21=create_button(current_frame, "", i_advanced_camera_control_view04_icon, KEYB.KEY_KP_4+100, "k", "key", None, row=2, column=1)
button_AdvancedCamera3_22=create_button(current_frame, "", i_advanced_camera_control_view05_icon, KEYB.KEY_KP_5+100, "k", "key", None, row=2, column=2)
button_AdvancedCamera3_23=create_button(current_frame, "", i_advanced_camera_control_view06_icon, KEYB.KEY_KP_6+100, "k", "key", None, row=2, column=3)
button_AdvancedCamera3_31=create_button(current_frame, "", i_advanced_camera_control_view07_icon, KEYB.KEY_KP_7+100, "k", "key", None, row=3, column=1)
button_AdvancedCamera3_32=create_button(current_frame, "", i_advanced_camera_control_view08_icon, KEYB.KEY_KP_8+100, "k", "key", None, row=3, column=2)
button_AdvancedCamera3_33=create_button(current_frame, "", i_advanced_camera_control_view09_icon, KEYB.KEY_KP_9+100, "k", "key", None, row=3, column=3)

button_AdvancedCamera3_camera=create_button(current_frame, "", i_advanced_camera_control_icon, None, "", "redir", target_frame=frame_Camera, row=4, column=1)
button_AdvancedCamera3_Previous=create_button(current_frame, "", i_general_ui_previous, None, "", "redir", target_frame=frame_AdvancedCamera2, row=4, column=4)
button_AdvancedCamera3_Next=create_button(current_frame, "", i_general_ui_next, None, "", "redir", target_frame=frame_AdvancedCamera1, row=4, column=5)
button_AdvancedCamera3_back=create_button(current_frame, "", i_general_ui_back, None, "", "redir", target_frame=frame_Flight, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Engineering Frame #######################################################################################################################################
#############################################################################################################################################################
trigger = 210
current_frame=frame_Engineering
create_dummys(current_frame, i_empty)

#Images
i_flight_power_poweron = resize_image("flight_power_poweron.png")
i_flight_power_power = resize_image("flight_power_power.png")
i_flight_power_shieldon = resize_image("flight_power_shieldon.png")
i_flight_power_shield = resize_image("flight_power_shield.png")
i_flight_power_engineon = resize_image("flight_power_engineon.png")
i_flight_power_engine = resize_image("flight_power_engine.png")
i_flight_power_weaponon = resize_image("flight_power_weaponon.png")
i_flight_power_weapon = resize_image("flight_power_weapon.png")
i_flight_power_poweron = resize_image("flight_power_poweron.png")
i_flight_power_power = resize_image("flight_power_power.png")
i_flight_power_shield_icon = resize_image("flight_power_shield_icon.png")

button_Engineering_11=create_button(current_frame, "", i_flight_power_poweron, trigger, "", "button", None, row=1, column=1)
trigger = trigger+1

button_Engineering_21=create_button(current_frame, "", i_flight_power_power, trigger, "", "button", None, row=2, column=1)
trigger = trigger+1

button_Engineering_31=create_button(current_frame, "", i_general_increase, trigger, "", "button", None, row=3, column=1)
trigger = trigger+1

button_Engineering_41=create_button(current_frame, "", i_general_decrease, trigger, "", "button", None, row=4, column=1)
trigger = trigger+1

button_Engineering_11=create_button(current_frame, "", i_flight_power_shieldon, trigger, "", "button", None, row=1, column=1)
trigger = trigger+1

button_Engineering_21=create_button(current_frame, "", i_flight_power_shield, trigger, "", "button", None, row=2, column=1)
trigger = trigger+1

button_Engineering_31=create_button(current_frame, "", i_general_increase, trigger, "", "button", None, row=3, column=1)
trigger = trigger+1

button_Engineering_41=create_button(current_frame, "", i_general_decrease, trigger, "", "button", None, row=4, column=1)
trigger = trigger+1

button_Engineering_12=create_button(current_frame, "", i_flight_power_engineon, trigger, "", "button", None, row=1, column=2)
trigger = trigger+1

button_Engineering_22=create_button(current_frame, "", i_flight_power_engine, trigger, "", "button", None, row=2, column=2)
trigger = trigger+1

button_Engineering_32=create_button(current_frame, "", i_general_increase, trigger, "", "button", None, row=3, column=2)
trigger = trigger+1

button_Engineering_42=create_button(current_frame, "", i_general_decrease, trigger, "", "button", None, row=4, column=2)
trigger = trigger+1

button_Engineering_13=create_button(current_frame, "", i_flight_power_weaponon, trigger, "", "button", None, row=1, column=3)
trigger = trigger+1

button_Engineering_23=create_button(current_frame, "", i_flight_power_weapon, trigger, "", "button", None, row=2, column=3)
trigger = trigger+1

button_Engineering_33=create_button(current_frame, "", i_general_increase, trigger, "", "button", None, row=3, column=3)
trigger = trigger+1

button_Engineering_43=create_button(current_frame, "", i_general_decrease, trigger, "", "button", None, row=4, column=3)
trigger = trigger+1

button_Engineering_14=create_button(current_frame, "", i_flight_power_poweron, trigger, "", "button", None, row=1, column=4)
trigger = trigger+1

button_Engineering_24=create_button(current_frame, "", i_flight_power_power, trigger, "", "button", None, row=2, column=4)
trigger = trigger+1

#button_Engineering_Shield=create_button(current_frame, "", i_flight_power_shield_icon, None, "", "redir", target_frame=frame_Shield, row=1, column=7)
button_Engineering_Shield=create_button(current_frame, "SHLD\nCNTR", i_general_bright, None, "", "redir", target_frame=frame_Shield, row=1, column=7)
button_Engineering_back=create_button(current_frame, "", i_general_ui_back, None, "", "redir", target_frame=frame_Flight, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### FPS Frame ###############################################################################################################################################
#############################################################################################################################################################
trigger = 230
current_frame=frame_FPS
create_dummys(current_frame, i_empty)

#Images
i_on_foot_all_underbarrel_icon = resize_image("on_foot_all_underbarrel_icon.png")
i_on_foot_all_wipe_icon = resize_image("on_foot_all_wipe__icon.png")
i_on_foot_all_flashlight_icon = resize_image("on_foot_all_flashlight__icon.png")

button_FPS_11=create_button(current_frame, "", i_on_foot_all_underbarrel_icon, 1000, "u", "key", None, row=1, column=1)

button_FPS_12=create_button(current_frame, "", i_on_foot_all_wipe_icon, KEYB.KEY_LEFT_ALT, "x", "key", None, row=1, column=2)

button_FPS_13=create_button(current_frame, "", i_on_foot_all_flashlight_icon, 1000, "t", "key", None, row=1, column=3)

button_FPS_info=create_button(current_frame, "", i_general_ui_info, None, "", "redir", target_frame=frame_Info2, row=3, column=7)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Drive Frame #############################################################################################################################################
#############################################################################################################################################################
trigger = 260
current_frame=frame_Drive
create_dummys(current_frame, i_empty)

button_Drive_info=create_button(current_frame, "", i_general_ui_info, None, "", "redir", target_frame=frame_Info2, row=3, column=7)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Shield Frame ############################################################################################################################################
#############################################################################################################################################################
trigger = 290
current_frame=frame_Shield
create_dummys(current_frame, i_empty)

#Images
i_vehicles_shields_and_countermeasures_shield_level_1 = resize_image("vehicles_shields_and_countermeasures_shield_level_1_top.png")
i_vehicles_shields_and_countermeasures_shield_level_2 = resize_image("vehicles_shields_and_countermeasures_shield_level_2_front.png")
i_vehicles_shields_and_countermeasures_shield_level_3 = resize_image("vehicles_shields_and_countermeasures_shield_level_3_empty.png")
i_vehicles_shields_and_countermeasures_shield_level_4 = resize_image("vehicles_shields_and_countermeasures_shield_level_4_left.png")
i_vehicles_shields_and_countermeasures_shield_level_5 = resize_image("vehicles_shields_and_countermeasures_shield_level_5_reset.png")
i_vehicles_shields_and_countermeasures_shield_level_6 = resize_image("vehicles_shields_and_countermeasures_shield_level_6_right.png")
i_vehicles_shields_and_countermeasures_shield_level_7 = resize_image("vehicles_shields_and_countermeasures_shield_level_7_logo.png")
i_vehicles_shields_and_countermeasures_shield_level_8 = resize_image("vehicles_shields_and_countermeasures_shield_level_8_back.png")
i_vehicles_shields_and_countermeasures_shield_level_9 = resize_image("vehicles_shields_and_countermeasures_shield_level_9_bottom.png")
i_vehicles_shields_and_countermeasures_decoy_icon = resize_image("vehicles_shields_and_countermeasures_decoy_icon.png")
i_vehicles_shields_and_countermeasures_increase_decoy_size = resize_image("vehicles_shields_and_countermeasures_increase_decoy_size.png")
i_vehicles_shields_and_countermeasures_decrease_decoy_size = resize_image("vehicles_shields_and_countermeasures_decrease_decoy_size.png")
i_vehicles_shields_and_countermeasures_noise_icon = resize_image("vehicles_shields_and_countermeasures_noise_icon.png")
i_vehicles_shields_and_countermeasures_panic_decoy_icon = resize_image("vehicles_shields_and_countermeasures_panic_decoy_icon.png")

button_Shield_11=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_shield_level_1, trigger, "", "button", None, row=1, column=1)
trigger = trigger+1

button_Shield_12=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_shield_level_2, trigger, "", "button", None, row=1, column=2)
trigger = trigger+1

button_Shield_13=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_shield_level_3, trigger, "", "button", None, row=1, column=3)
trigger = trigger+1

button_Shield_21=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_shield_level_4, trigger, "", "button", None, row=2, column=1)
trigger = trigger+1

button_Shield_22=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_shield_level_5, trigger, "", "button", None, row=2, column=2)
trigger = trigger+1

button_Shield_23=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_shield_level_6, trigger, "", "button", None, row=2, column=3)
trigger = trigger+1

button_Shield_31=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_shield_level_7, trigger, "", "button", None, row=3, column=1)
trigger = trigger+1

button_Shield_32=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_shield_level_8, trigger, "", "button", None, row=3, column=2)
trigger = trigger+1

button_Shield_33=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_shield_level_9, trigger, "", "button", None, row=3, column=3)
trigger = trigger+1

button_Shield_15=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_decoy_icon, 1000, "h", "key", None, row=1, column=5)
button_Shield_25=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_increase_decoy_size, KEYB.KEY_RIGHT_ALT, "h", "key", None, row=2, column=5)
button_Shield_35=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_decrease_decoy_size, KEYB.KEY_LEFT_ALT, "h", "key", None, row=3, column=5)
button_Shield_16=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_noise_icon, 1000, "j", "key", None, row=1, column=6)

button_Shield_17=create_button(current_frame, "", i_vehicles_shields_and_countermeasures_panic_decoy_icon, trigger, "", "button", None, row=1, column=7)
trigger = trigger+1

button_Shield_back=create_button(current_frame, "", i_general_ui_back, None, "", "redir", target_frame=frame_Engineering, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Target Frame ############################################################################################################################################
#############################################################################################################################################################
trigger = 320
current_frame=frame_Target
create_dummys(current_frame, i_empty)

#Images
i_vehicles_weapons_aim_assist_icon = resize_image("vehicles_weapons_aim_assist_icon.png")
i_vehicles_weapons_supress_aim_assist_icon = resize_image("vehicles_weapons_supress_aim_assist_icon.png")
i_vehicles_weapons_set_auto_gimbal_icon = resize_image("vehicles_weapons_set_auto_gimbal_icon.png")
i_vehicles_weapons_set_fixed_gimbal_icon = resize_image("vehicles_weapons_set_fixed_gimbal_icon.png")
i_vehicles_weapons_set_manual_gimbal_icon = resize_image("vehicles_weapons_set_manual_gimbal_icon.png")
i_vehicles_weapons_set_pip_lag_icon = resize_image("vehicles_weapons_set_pip_lag_icon.png")
i_vehicles_weapons_set_pip_lead_icon = resize_image("vehicles_weapons_set_pip_lead_icon.png")
i_vehicles_weapons_mouse_mode_vjoy_fps_icon = resize_image("vehicles_weapons_mouse_mode_vjoy_fps_icon.png")
i_vehicles_weapons_fire_mode_icon = resize_image("vehicles_weapons_fire_mode_icon.png")
i_vehicles_weapons_pip_combination_type_toggle = resize_image("vehicles_weapons_pip_combination_type_toggle.png")
i_vehicles_weapons_pip_precision_fading_toggle = resize_image("vehicles_weapons_pip_precision_fading_toggle.png")
i_vehicles_weapons_pip_precision_line_toggle = resize_image("vehicles_weapons_pip_precision_line_toggle.png")
i_vehicles_weapons_precision_target_icon = resize_image("vehicles_weapons_precision_target_icon.png")
i_vehicles_weapons_reset_convergence_distance_text = resize_image("vehicles_weapons_reset_convergence_distance_text.png")
i_vehicles_weapons_increase_convergence_distance_text = resize_image("vehicles_weapons_increase_convergence_distance_text.png")
i_vehicles_weapons_decrease_convergence_distance_text = resize_image("vehicles_weapons_decrease_convergence_distance_text.png")
i_vehicles_weapons_Gunnery_UI_Magn_icon = resize_image("vehicles_weapons_Gunnery_UI_Magn_icon.png")


button_Target_11=create_button(current_frame, "", i_vehicles_weapons_aim_assist_icon, trigger, "", "button", None, row=1, column=1)
trigger = trigger+1

button_Target_21=create_button(current_frame, "", i_vehicles_weapons_supress_aim_assist_icon, trigger, "", "button", None, row=2, column=1)
trigger = trigger+1

button_Target_12=create_button(current_frame, "", i_vehicles_weapons_set_pip_lag_icon, trigger, "", "button", None, row=1, column=2)
trigger = trigger+1

button_Target_22=create_button(current_frame, "", i_vehicles_weapons_set_pip_lead_icon, trigger, "", "button", None, row=2, column=2)
trigger = trigger+1

button_Target_13=create_button(current_frame, "", i_vehicles_weapons_pip_precision_fading_toggle, trigger, "", "button", None, row=1, column=3)
trigger = trigger+1

button_Target_23=create_button(current_frame, "", i_vehicles_weapons_pip_precision_line_toggle, trigger, "", "button", None, row=2, column=3)
trigger = trigger+1

button_Target_14=create_button(current_frame, "", i_vehicles_weapons_set_auto_gimbal_icon, trigger, "", "button", None, row=1, column=4)
trigger = trigger+1

button_Target_15=create_button(current_frame, "", i_vehicles_weapons_set_fixed_gimbal_icon, trigger, "", "button", None, row=1, column=5)
trigger = trigger+1

button_Target_16=create_button(current_frame, "", i_vehicles_weapons_set_manual_gimbal_icon, trigger, "", "button", None, row=1, column=6)
trigger = trigger+1

button_Target_24=create_button(current_frame, "", i_vehicles_weapons_mouse_mode_vjoy_fps_icon, trigger, "", "button", None, row=2, column=4)
trigger = trigger+1

button_Target_25=create_button(current_frame, "", i_vehicles_weapons_fire_mode_icon, trigger, "", "button", None, row=2, column=5)
trigger = trigger+1

button_Target_26=create_button(current_frame, "", i_vehicles_weapons_pip_combination_type_toggle, trigger, "", "button", None, row=2, column=6)
trigger = trigger+1

button_Target_31=create_button(current_frame, "", i_vehicles_weapons_precision_target_icon, trigger, "", "button", None, row=3, column=1)
trigger = trigger+1

button_Target_32=create_button(current_frame, "", i_vehicles_weapons_Gunnery_UI_Magn_icon, trigger, "", "button", None, row=3, column=2)
trigger = trigger+1

button_Target_34=create_button(current_frame, "", i_vehicles_weapons_decrease_convergence_distance_text, trigger, "", "button", None, row=3, column=4)
trigger = trigger+1

button_Target_35=create_button(current_frame, "", i_vehicles_weapons_reset_convergence_distance_text, trigger, "", "button", None, row=3, column=5)
trigger = trigger+1

button_Target_36=create_button(current_frame, "", i_vehicles_weapons_increase_convergence_distance_text, trigger, "", "button", None, row=3, column=6)
trigger = trigger+1

button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Fight Frame ############################################################################################################################################
#############################################################################################################################################################
trigger = 350
current_frame=frame_Fight
create_dummys(current_frame, i_empty)

i_cycle_targeting_allnext = resize_image("cycle_targeting_allnext.png")
i_cycle_targeting_allprevious = resize_image("cycle_targeting_allprevious.png")
i_cycle_targeting_visiblenext = resize_image("cycle_targeting_visiblenext.png")
i_cycle_targeting_visibleprevious = resize_image("cycle_targeting_visibleprevious.png")
i_cycle_targeting_friendnext = resize_image("cycle_targeting_friendnext.png")
i_cycle_targeting_friendprevious = resize_image("cycle_targeting_friendprevious.png")
i_cycle_targeting_hostilenext = resize_image("cycle_targeting_hostilenext.png")
i_cycle_targeting_hostileprevious = resize_image("cycle_targeting_hostileprevious.png")
i_cycle_targeting_attackernext = resize_image("cycle_targeting_attackernext.png")
i_cycle_targeting_attackerprevious = resize_image("cycle_targeting_attackerprevious.png")
i_cycle_targeting_subnext = resize_image("cycle_targeting_subnext.png")
i_cycle_targeting_subprevious = resize_image("cycle_targeting_subprevious.png")
i_cycle_targeting_reticle = resize_image("cycle_targeting_reticle.png")
i_cycle_targeting_target = resize_image("cycle_targeting_target.png")
i_vehicles_targeting_auto_target = resize_image("vehicles_targeting_auto_target.png")
i_flight_movement_match_target_velocity_icon = resize_image("flight_movement_match_target_velocity_icon.png")
i_vehicles_targeting_target_tracking = resize_image("vehicles_targeting_target_tracking.png")
i_vehicles_targeting_targetlock = resize_image("vehicles_targeting_targetlock.png")
i_vehicles_targeting_unlock = resize_image("vehicles_targeting_unlock.png")
i_vehicles_targeting_autozoom_icon = resize_image("vehicles_targeting_autozoom_icon.png")
i_vehicles_targeting_lock01 = resize_image("vehicles_targeting_lock01.png")
i_vehicles_targeting_lock02 = resize_image("vehicles_targeting_lock02.png")
i_vehicles_targeting_lock03 = resize_image("vehicles_targeting_lock03.png")
i_vehicles_targeting_pin01 = resize_image("vehicles_targeting_pin01.png")
i_vehicles_targeting_pin02 = resize_image("vehicles_targeting_pin02.png")
i_vehicles_targeting_pin03 = resize_image("vehicles_targeting_pin03.png")

button_Fight_11=create_button(current_frame, "", i_cycle_targeting_allnext, 1000, "7", "key", None, row=1, column=1)
button_Fight_21=create_button(current_frame, "", i_cycle_targeting_allprevious, 1000, "7", "key", None, row=2, column=1)
button_Fight_12=create_button(current_frame, "", i_cycle_targeting_visiblenext, 1000, "t", "key", None, row=1, column=2)
button_Fight_22=create_button(current_frame, "", i_cycle_targeting_visibleprevious, 1000, "t", "key", None, row=2, column=2)
button_Fight_13=create_button(current_frame, "", i_cycle_targeting_friendnext, 1000, "6", "key", None, row=1, column=3)
button_Fight_23=create_button(current_frame, "", i_cycle_targeting_friendprevious, 1000, "6", "key", None, row=2, column=3)
button_Fight_14=create_button(current_frame, "", i_cycle_targeting_hostilenext, 1000, "5", "key", None, row=1, column=4)
button_Fight_24=create_button(current_frame, "", i_cycle_targeting_hostileprevious, 1000, "5", "key", None, row=2, column=4)
button_Fight_15=create_button(current_frame, "", i_cycle_targeting_attackernext, 1000, "4", "key", None, row=1, column=5)
button_Fight_25=create_button(current_frame, "", i_cycle_targeting_attackerprevious, 1000, "4", "key", None, row=2, column=5)

button_Fight_16=create_button(current_frame, "", i_cycle_targeting_subnext, 1000, "r", "key", None, row=1, column=6)
button_Fight_26=create_button(current_frame, "", i_cycle_targeting_subprevious, 1000, "t", "key", None, row=2, column=6)

button_Fight_17=create_button(current_frame, "", i_vehicles_targeting_targetlock, trigger, "", "button", None, row=1, column=7)
trigger = trigger+1

button_Fight_27=create_button(current_frame, "", i_vehicles_targeting_unlock, KEYB.KEY_LEFT_ALT, "t", "key", None, row=2, column=7)

button_Fight_31=create_button(current_frame, "", i_cycle_targeting_reticle, trigger, "", "button", None, row=3, column=1)
trigger = trigger+1

button_Fight_32=create_button(current_frame, "", i_cycle_targeting_target, trigger, "", "button", None, row=3, column=2)
trigger = trigger+1

button_Fight_33=create_button(current_frame, "", i_vehicles_targeting_auto_target, 1000, "t", "key", None, row=3, column=3)

button_Fight_34=create_button(current_frame, "", i_flight_movement_match_target_velocity_icon, trigger, "", "button", None, row=3, column=4)
trigger = trigger+1

button_Fight_35=create_button(current_frame, "", i_vehicles_targeting_target_tracking, trigger, "", "button", None, row=3, column=5)
trigger = trigger+1

button_Fight_36=create_button(current_frame, "", i_vehicles_targeting_autozoom_icon, trigger, "", "button", None, row=3, column=6)
trigger = trigger+1

button_Fight_41=create_button(current_frame, "", i_vehicles_targeting_lock01, 1000, "1", "key", None, row=4, column=1)
button_Fight_42=create_button(current_frame, "", i_vehicles_targeting_lock02, 1000, "2", "key", None, row=4, column=2)
button_Fight_43=create_button(current_frame, "", i_vehicles_targeting_lock03, 1000, "3", "key", None, row=4, column=3)
button_Fight_44=create_button(current_frame, "", i_vehicles_targeting_pin01, KEYB.KEY_LEFT_ALT, "1", "key", None, row=4, column=4)
button_Fight_45=create_button(current_frame, "", i_vehicles_targeting_pin02, KEYB.KEY_LEFT_ALT, "2", "key", None, row=4, column=5)
button_Fight_46=create_button(current_frame, "", i_vehicles_targeting_pin03, KEYB.KEY_LEFT_ALT, "3", "key", None, row=4, column=6)


button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Emotes Frame ############################################################################################################################################
#############################################################################################################################################################
trigger = 660
current_frame=frame_Emotes1
create_dummys(current_frame, i_empty)

#Images
i_social_emote_agree_icon = resize_image("social_emote_agree_icon.png")
i_social_emote_angry_icon = resize_image("social_emote_angry_icon.png")
i_social_emote_at_ease_icon = resize_image("social_emote_at_ease_icon.png")
i_social_emote_attention_icon = resize_image("social_emote_attention_icon.png")
i_social_emote_blah_icon = resize_image("social_emote_blah_icon.png")
i_social_emote_bored_icon = resize_image("social_emote_bored_icon.png")
i_social_emote_bow_icon = resize_image("social_emote_bow_icon.png")
i_social_emote_burp_icon = resize_image("social_emote_burp_icon.png")
i_social_emote_cheer_icon = resize_image("social_emote_cheer_icon.png")
i_social_emote_chicken_icon = resize_image("social_emote_chicken_icon.png")
i_social_emote_clap_icon = resize_image("social_emote_clap_icon.png")
i_social_emote_come_icon = resize_image("social_emote_come_icon.png")
i_social_emote_cry_icon = resize_image("social_emote_cry_icon.png")
i_social_emote_dance_icon = resize_image("social_emote_dance_icon.png")
i_social_emote_disagree_icon = resize_image("social_emote_disagree_icon.png")
i_social_emote_failure_icon = resize_image("social_emote_failure_icon.png")
i_social_emote_flex_icon = resize_image("social_emote_flex_icon.png")
i_social_emote_flirt_icon = resize_image("social_emote_flirt_icon.png")
i_social_emote_gasp_icon = resize_image("social_emote_gasp_icon.png")
i_social_emote_gloat_icon = resize_image("social_emote_gloat_icon.png")
i_social_emote_greet_icon = resize_image("social_emote_greet_icon.png")
i_social_emote_laugh_icon = resize_image("social_emote_laugh_icon.png")
i_social_emote_launch_icon = resize_image("social_emote_launch_icon.png")
i_social_emote_no_icon = resize_image("social_emote_no_icon.png")
i_social_emote_point_icon = resize_image("social_emote_point_icon.png")
i_social_emote_rude_icon = resize_image("social_emote_rude_icon.png")

button_Emotes1_11=create_button(current_frame, "", i_social_emote_agree_icon, trigger, "", "button", None, row=1, column=1)
trigger = trigger+1

button_Emotes1_12=create_button(current_frame, "", i_social_emote_angry_icon, trigger, "", "button", None, row=1, column=2)
trigger = trigger+1

button_Emotes1_13=create_button(current_frame, "", i_social_emote_at_ease_icon, trigger, "", "button", None, row=1, column=3)
trigger = trigger+1

button_Emotes1_14=create_button(current_frame, "", i_social_emote_attention_icon, trigger, "", "button", None, row=1, column=4)
trigger = trigger+1

button_Emotes1_15=create_button(current_frame, "", i_social_emote_blah_icon, trigger, "", "button", None, row=1, column=5)
trigger = trigger+1

button_Emotes1_16=create_button(current_frame, "", i_social_emote_bored_icon, trigger, "", "button", None, row=1, column=6)
trigger = trigger+1

button_Emotes1_17=create_button(current_frame, "", i_social_emote_bow_icon, trigger, "", "button", None, row=1, column=7)
trigger = trigger+1

button_Emotes1_21=create_button(current_frame, "", i_social_emote_burp_icon, trigger, "", "button", None, row=2, column=1)
trigger = trigger+1

button_Emotes1_22=create_button(current_frame, "", i_social_emote_cheer_icon, trigger, "", "button", None, row=2, column=2)
trigger = trigger+1

button_Emotes1_23=create_button(current_frame, "", i_social_emote_chicken_icon, trigger, "", "button", None, row=2, column=3)
trigger = trigger+1

button_Emotes1_24=create_button(current_frame, "", i_social_emote_clap_icon, trigger, "", "button", None, row=2, column=4)
trigger = trigger+1

button_Emotes1_25=create_button(current_frame, "", i_social_emote_come_icon, trigger, "", "button", None, row=2, column=5)
trigger = trigger+1

button_Emotes1_26=create_button(current_frame, "", i_social_emote_cry_icon, trigger, "", "button", None, row=2, column=6)
trigger = trigger+1

button_Emotes1_27=create_button(current_frame, "", i_social_emote_dance_icon, trigger, "", "button", None, row=2, column=7)
trigger = trigger+1

button_Emotes1_31=create_button(current_frame, "", i_social_emote_disagree_icon, trigger, "", "button", None, row=3, column=1)
trigger = trigger+1

button_Emotes1_32=create_button(current_frame, "", i_social_emote_failure_icon, trigger, "", "button", None, row=3, column=2)
trigger = trigger+1

button_Emotes1_33=create_button(current_frame, "", i_social_emote_flex_icon, trigger, "", "button", None, row=3, column=3)
trigger = trigger+1

button_Emotes1_34=create_button(current_frame, "", i_social_emote_flirt_icon, trigger, "", "button", None, row=3, column=4)
trigger = trigger+1

button_Emotes1_35=create_button(current_frame, "", i_social_emote_gasp_icon, trigger, "", "button", None, row=3, column=5)
trigger = trigger+1

button_Emotes1_36=create_button(current_frame, "", i_social_emote_gloat_icon, trigger, "", "button", None, row=3, column=6)
trigger = trigger+1

button_Emotes1_37=create_button(current_frame, "", i_social_emote_greet_icon, trigger, "", "button", None, row=3, column=7)
trigger = trigger+1

button_Emotes1_41=create_button(current_frame, "", i_social_emote_laugh_icon, trigger, "", "button", None, row=4, column=1)
trigger = trigger+1

button_Emotes1_42=create_button(current_frame, "", i_social_emote_launch_icon, trigger, "", "button", None, row=4, column=2)
trigger = trigger+1

button_Emotes1_43=create_button(current_frame, "", i_social_emote_no_icon, trigger, "", "button", None, row=4, column=3)
trigger = trigger+1

button_Emotes1_44=create_button(current_frame, "", i_social_emote_point_icon, trigger, "", "button", None, row=4, column=4)
trigger = trigger+1

button_Emotes1_45=create_button(current_frame, "", i_social_emote_rude_icon, trigger, "", "button", None, row=4, column=5)
trigger = trigger+1

button_Emotes1_frame_Emotes2=create_button(current_frame, "", i_general_ui_next, None, "", "redir", target_frame=frame_Emotes2, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Emotes2 Frame ############################################################################################################################################
#############################################################################################################################################################
current_frame=frame_Emotes2
create_dummys(current_frame, i_empty)

#Images
i_social_emote_salut_icon = resize_image("social_emote_salut_icon.png")
i_social_emote_sit_icon = resize_image("social_emote_sit_icon.png")
i_social_emote_sleep_icon = resize_image("social_emote_sleep_icon.png")
i_social_emote_smell_icon = resize_image("social_emote_smell_icon.png")
i_social_emote_taunt_icon = resize_image("social_emote_taunt_icon.png")
i_social_emote_threaten_icon = resize_image("social_emote_threaten_icon.png")
i_social_emote_wait_icon = resize_image("social_emote_wait_icon.png")
i_social_emote_wave_icon = resize_image("social_emote_wave_icon.png")
i_social_emote_whistle_icon = resize_image("social_emote_whistle_icon.png")
i_social_emote_yes_icon = resize_image("social_emote_yes_icon.png")

button_Emotes2_11=create_button(current_frame, "", i_social_emote_salut_icon, trigger, "", "button", None, row=1, column=1)
trigger = trigger+1

button_Emotes2_12=create_button(current_frame, "", i_social_emote_sit_icon, trigger, "", "button", None, row=1, column=2)
trigger = trigger+1

button_Emotes2_13=create_button(current_frame, "", i_social_emote_sleep_icon, trigger, "", "button", None, row=1, column=3)
trigger = trigger+1

button_Emotes2_14=create_button(current_frame, "", i_social_emote_smell_icon, trigger, "", "button", None, row=1, column=4)
trigger = trigger+1

button_Emotes2_15=create_button(current_frame, "", i_social_emote_taunt_icon, trigger, "", "button", None, row=1, column=5)
trigger = trigger+1

button_Emotes2_16=create_button(current_frame, "", i_social_emote_threaten_icon, trigger, "", "button", None, row=1, column=6)
trigger = trigger+1

button_Emotes2_17=create_button(current_frame, "", i_social_emote_wait_icon, trigger, "", "button", None, row=1, column=7)
trigger = trigger+1

button_Emotes2_21=create_button(current_frame, "", i_social_emote_wave_icon, trigger, "", "button", None, row=2, column=1)
trigger = trigger+1

button_Emotes2_22=create_button(current_frame, "", i_social_emote_whistle_icon, trigger, "", "button", None, row=2, column=2)
trigger = trigger+1

button_Emotes2_23=create_button(current_frame, "", i_social_emote_yes_icon, trigger, "", "button", None, row=2, column=3)
trigger = trigger+1

button_Emotes2_24=create_button(current_frame, "FORWARD", i_empty, trigger, "", "button", None, row=2, column=4)
trigger = trigger+1

button_Emotes2_25=create_button(current_frame, "LEFT", i_empty, trigger, "", "button", None, row=2, column=5)
trigger = trigger+1

button_Emotes2_26=create_button(current_frame, "RIGHT", i_empty, trigger, "", "button", None, row=2, column=6)
trigger = trigger+1

button_Emotes2_27=create_button(current_frame, "STOP", i_empty, trigger, "", "button", None, row=2, column=7)
trigger = trigger+1


button_Emotes2_frame_Emotes1=create_button(current_frame, "", i_general_ui_previous, None, "", "redir", target_frame=frame_Emotes1, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Debug Frame ############################################################################################################################################
#############################################################################################################################################################
current_frame=frame_Debug
create_dummys(current_frame, i_empty)

button_Debug_11=create_button(current_frame, "JOY1\nBTN1", i_general_dark, 1, "", "button", None, row=1, column=1)
button_Debug_12=create_button(current_frame, "JOY1\nBTN2", i_general_dark, 2, "", "button", None, row=1, column=2)
button_Debug_13=create_button(current_frame, "JOY1\nBTN3", i_general_dark, 3, "", "button", None, row=1, column=3)

button_Debug_15=create_button(current_frame, "JOY2\nBTN1", i_general_dark, 121, "", "button", None, row=1, column=5)
button_Debug_16=create_button(current_frame, "JOY2\nBTN2", i_general_dark, 122, "", "button", None, row=1, column=6)
button_Debug_17=create_button(current_frame, "JOY2\nBTN3", i_general_dark, 123, "", "button", None, row=1, column=7)

button_Debug_21=create_button(current_frame, "JOY3\nBTN1", i_general_dark, 241, "", "button", None, row=2, column=1)
button_Debug_22=create_button(current_frame, "JOY3\nBTN2", i_general_dark, 242, "", "button", None, row=2, column=2)
button_Debug_23=create_button(current_frame, "JOY3\nBTN3", i_general_dark, 243, "", "button", None, row=2, column=3)

button_Debug_25=create_button(current_frame, "JOY4\nBTN1", i_general_dark, 361, "", "button", None, row=2, column=5)
button_Debug_26=create_button(current_frame, "JOY4\nBTN2", i_general_dark, 362, "", "button", None, row=2, column=6)
button_Debug_27=create_button(current_frame, "JOY4\nBTN3", i_general_dark, 363, "", "button", None, row=2, column=7)

button_Debug_31=create_button(current_frame, "JOY5\nBTN1", i_general_dark, 481, "", "button", None, row=3, column=1)
button_Debug_32=create_button(current_frame, "JOY5\nBTN2", i_general_dark, 482, "", "button", None, row=3, column=2)
button_Debug_33=create_button(current_frame, "JOY5\nBTN3", i_general_dark, 483, "", "button", None, row=3, column=3)

button_Debug_35=create_button(current_frame, "JOY6\nBTN1", i_general_dark, 601, "", "button", None, row=3, column=5)
button_Debug_36=create_button(current_frame, "JOY6\nBTN2", i_general_dark, 602, "", "button", None, row=3, column=6)
button_Debug_37=create_button(current_frame, "JOY6\nBTN3", i_general_dark, 603, "", "button", None, row=3, column=7)



button_Debug_back=create_button(current_frame, "", i_general_ui_back, None, "", "redir", target_frame=frame_Setup, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)

#############################################################################################################################################################
### Controller Setup Frame ##################################################################################################################################
#############################################################################################################################################################
current_frame=frame_Setup
create_dummys(current_frame, i_empty)

#Images
i_controller_accel_on = resize_image("controller_accel_on.png")
i_controller_accel_off = resize_image("controller_accel_off.png")

button_Accel_On=create_button(current_frame, "", i_controller_accel_on, 3001, "t", "key", None, row=1, column=1)
button_Accel_Off=create_button(current_frame, "", i_controller_accel_off, 3002, "t", "key", None, row=2, column=1)

button_debug=create_button(current_frame, "Debug", i_general_bright, None, "", "redir", target_frame=frame_Debug, row=4, column=1)
button_Setup_back=create_button(current_frame, "", i_general_ui_back, None, "", "redir", target_frame=frame_Settings, row=4, column=6)
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### Settings Frame ##########################################################################################################################################
#############################################################################################################################################################
current_frame=frame_Settings
create_dummys(current_frame, i_empty)

#OUTPUT
text_output=tkinter.Text(current_frame, bg=b_c_bg, fg=b_c_text, font=(b_font, b_font_size, b_font_type), height=1, width=1)
text_output.grid(row=2, column=1, rowspan=2, columnspan=7, sticky=tkinter.N+tkinter.S+tkinter.W+tkinter.E)
text_output.see("end")
old_stdout = sys.stdout
sys.stdout = Redirect(text_output)

#Shutdown
button_shutdown=create_button(current_frame, "", i_general_ui_shutdown, None, "", "shutdown", None, row=1, column=1)

#DESKTOP
button_close=create_button(current_frame, "", i_general_ui_desktop, None, "", "close", None, row=1, column=2)

#Update
button_update=create_button(current_frame, "", i_general_ui_update, None, "", "update", None, row=1, column=3)

#Teamspeak
button_Teamspeak=create_button(current_frame, "", i_general_ui_team_speak, 2002, "t", "key", None, row=4, column=5)

#Voice Attack
button_VoiceAttack=create_button(current_frame, "", i_general_ui_voice_attack, 2001, "v", "key", None, row=4, column=6)

button_Main_Setup=create_button(current_frame, "", i_general_ui_setup, None, "", "redir", target_frame=frame_Setup, row=4, column=1)

#HOME
button_home=create_button(current_frame, "", i_general_ui_home, None, "", "redir", target_frame=frame_Main, row=4, column=7)


#############################################################################################################################################################
### END OF FRAMES ###########################################################################################################################################
#############################################################################################################################################################

raise_frame(frame_Main)

master.mainloop()
sys.stdout = old_stdout
