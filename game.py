import tkinter as tk
import math
import random

import serial
root = tk.Tk()
root.title("Greg the Frog Game")


PORT = "COM3"
SERIAL_RATE = 9600

JYSTCK_LOWER = 450
JYSTCK_HIGHER = 550

allHistory = []

ser = serial.Serial(PORT, baudrate= SERIAL_RATE, timeout=1)


def get_data():
    # Set: x-val, y-val, hearth rate
    try:
        # clean = "-1, -1" # TODO: put the number of commmas for the default val

        # raw = ser.readline()

        # if raw:
        #     # raw = ser.read_all()
        #     clean = raw.decode('utf-8', errors='ignore').strip()
        #     # print(clean)
        # data = clean.split(", ")

        # for i in range(2):
        #     if data[i] == '-1':
        #         data[i] = None
        #     elif data[i] == '':
        #         data[i] = 0
        #     else:
        #         data[i] = int(data[i])
        #     # print(data[i], end=", ")

        # return data
        if ser.in_waiting > 0:
            raw = None
            # DRAIN THE BUFFER: Read all lines until empty, keeping only the last one
            while ser.in_waiting > 0:
                raw = ser.readline() 

            if raw:
                clean = raw.decode('utf-8', errors='ignore').strip()
                data = clean.split(", ")

                # Ensure we actually have both X and Y before parsing
                if len(data) >= 2:
                    x = int(data[0]) if data[0] not in ['-1', ''] else None
                    y = int(data[1]) if data[1] not in ['-1', ''] else None
                    return [x, y]
                    
        return [None, None]
    except Exception as e:
        return [None, None]


def detect_flick():
    # if type(allHistory[-1][0]) is str or type(allHistory[-2][0]) is str or type(allHistory[-1][1]) is str or type(allHistory[-2][1]) is str:
    #     return None
    try:
        motion = [0,0]
        isExtX = False
        isExtY = False
        
        if (len(allHistory) < 3):
            return None

        if int(allHistory[-1][0]) < 575 and int(allHistory[-1][0]) > 450:
            if int(allHistory[-2][0]) > 575 or int(allHistory[-2][0]) < 450:
                isExtX = True
        if int(allHistory[-1][1]) < 575 and int(allHistory[-1][1]) > 450:
            if int(allHistory[-2][1]) > 575 or int(allHistory[-2][1]) < 450:
                isExtY = True

        if isExtX or isExtY:
            motion[0] = allHistory[-2][0]
            motion[1] = allHistory[-2][1]
            deg = math.atan2(int(motion[0])-512, int(motion[1])-512)
        else:
            return None
        
        return deg / (math.pi) * 180
    except Exception as e:
        return None
    
def send_data(info:str):
    # Don't forget to add '\n' at the end
    ser.write(info)

class Asteroid:
    def __init__(self, canvas, size):
        self.canvas = canvas
        self.radius = random.randint(size-5, size+5)
        self.angle = 0
        self.spin_speed = random.uniform(-0.1, 0.1)
        
        side = random.choice(["top", "bottom", "left", "right"])
        if (side == "top"):
            self.x = random.randint(0, 800)
            self.y = -self.radius
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(1, 4)
        elif (side == "bottom"):
            self.x = random.randint(0, 800)
            self.y = 800 + self.radius
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-4, -1)
        elif (side == "left"):
            self.x = -self.radius
            self.y = random.randint(0, 800)
            self.vx = random.uniform(1, 4)
            self.vy = random.uniform(-2, 2)
        else: #spawning from the right sdie
            self.x = 800 + self.radius
            self.y = random.randint(0, 800)
            self.vx = random.uniform(-4, -1)
            self.vy = random.uniform(-2, 2)
            
        self.shape = []
        num_points = random.randint(5, 8)
        for i in range(num_points):
            angle = i * (2 * math.pi / num_points) + random.uniform(-0.2, 0.2)
            dist = self.radius * random.uniform(0.7, 1.3)
            self.shape.append((dist * math.cos(angle), dist * math.sin(angle)))            
        self.id = self.canvas.create_polygon(self.get_rotated_points(), fill="gray", outline="white")
            
    def get_rotated_points(self):
        points = []
        for px, py in self.shape:
            rotated_x = px * math.cos(self.angle) - py * math.sin(self.angle)
            rotated_y = px * math.sin(self.angle) + py * math.cos(self.angle)
            points.extend([self.x + rotated_x, self.y + rotated_y])
        return points

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.angle += self.spin_speed
        self.canvas.coords(self.id, self.get_rotated_points())
        
        if (self.x < -50 or self.x > 850 or self.y < -50 or self.y > 850):
            return False
        return True

    def destroy(self):
        self.canvas.delete(self.id)
        
    def check_collision(self, frog_x, frog_y):
        dist = math.sqrt((self.x - frog_x)**2 + (self.y - frog_y)**2)
        return dist < self.radius + 25
        
class StaticObject:
    def __init__(self, canvas, x, y, size, object_type):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.type = object_type
        self.id = self.canvas.create_oval(self.x-self.size, self.y-self.size, self.x+self.size, self.y+self.size, fill="yellow")
        self.time_left = 100 # 5 seconds at 60 fps
    
    def destroy(self):
        self.canvas.delete(self.id)
    
    def update(self):
        pass
    
    def check_collision(self, frog_x, frog_y):
        dist = math.sqrt((self.x - frog_x)**2 + (self.y - frog_y)**2)
        return dist < self.size + 25
        
        
        
class GregGame:
    def __init__(self, root):
        self.root = root
        root.geometry("800x800")
        
        self.game_state = "home"
        self.canvas_frame = tk.Frame(root)
        self.canvas = tk.Canvas(self.canvas_frame, width=800, height=800, bg="black")
        self.canvas.pack()
        self.canvas_frame.pack()
        
        self.home_frame = tk.Frame(root)
        self.home_label = tk.Label(self.home_frame, text="Welcome to Greg the Frog Game!", font=("Arial", 24))
        self.start_button = tk.Button(self.home_frame, text="Start Game", command=self.start_game)
        self.home_label.pack()
        self.start_button.pack()
        self.home_frame.pack()

        self.game_over_frame = tk.Frame(root)
        self.game_over_label = tk.Label(self.game_over_frame, text= "Game over, you have been hit by an astroid", font= ("Arial", 24))
        self.final_score_label = tk.Label(self.game_over_frame)
        self.restart_button = tk.Button(self.game_over_frame, text="Restart the Game", command=self.start_game)
        self.game_over_label.pack(side = "bottom", pady = 600, fill= "x")
        self.game_over_frame.pack()
        self.restart_button.pack(side = "bottom", pady=400)
        

        
        
        self.thruster_shape = [(-20, 10), (-20, -10), (-45, 0)]
        self.thruster_id = self.canvas.create_polygon(
            [0, 0, 0, 0, 0, 0], fill="white", state="hidden"
        )
        self.frog = self.canvas.create_oval(50, 50, 100, 100, fill="green")
        self.frog_x = 400 #center
        self.frog_y = 400
        self.frog_vx = 0
        self.frog_vy = 0
        self.is_accelerating = 0
        self.angle = 0
        self.border = self.canvas.create_rectangle(0, 0, 800, 800, outline="#212121", width=100)
        self.sizes = {
            "stardust": 30,
            "asteroid": 20
        }
        
        

        
        self.spawnrates = {
            "stardust": 0.03,
            "asteroid": 0.01
        }
        
        self.frame_delay = int(1000 / 60) # 60 fps
        self.game_loop()
        
        self.show_home()
        
        
        # testing only
        self.keys = {
            "Up": False,
            "Down": False,
            "Left": False,
            "Right": False
        }
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
    
    
    def on_key_press(self, event):
        key = event.keysym
        if key in self.keys:
            self.keys[key] = True

    def on_key_release(self, event):
        key = event.keysym
        if key in self.keys:
            self.keys[key] = False
        
    def show_game_over(self):
        self.game_state = "game over"

        self.canvas_frame.forget()
        self.home_frame.forget()
        self.game_over_frame.pack(expand=True, fill= "both")
        
        self.final_score_label.config(text=f"Final Score: {self.stardust}")
        self.final_score_label.pack(side="bottom")

        for item in self.objects:
            item.destroy()

        self.objects = []
        self.stardust = 0

    def game_loop(self):
        
        if (self.game_state == "game"):
            self.margin += 0.06
            self.sizes["stardust"] -= 0.009 # goes down by 0.540 every second
            self.sizes["asteroid"] += 0.004 # goes up by 0.06 every second
            if (self.sizes["stardust"] < 1):
                self.sizes["stardust"] = 1
            if (self.sizes["asteroid"] > 50):
                self.sizes["asteroid"] = 50
            self.canvas.itemconfigure(self.border, width=self.margin)
            self.spawnrates["asteroid"] += 0.00002
            self.spawnrates["stardust"] += 0.00001
            self.canvas.move(self.frog, 0.5, 0.5);
            
            
            if (self.keys["Up"]):
                self.apply_acceleration(270)
            elif (self.keys["Down"]):
                self.apply_acceleration(90)
            elif (self.keys["Left"]):
                self.apply_acceleration(180)
            elif (self.keys["Right"]):
                self.apply_acceleration(0)
            self.keys = {
                "Up": False,
                "Down": False,
                "Left": False,
                "Right": False
            }
            data = get_data()
            # print(data)
            if data[0] != "NULL":
                allHistory.append(data)
                if len(allHistory) > 5:
                    allHistory.pop(0)
            deg = detect_flick()
            if deg is not None:
                print(deg)
            if deg is not None:
                self.apply_acceleration(deg)
            else:
                #Stay at the same pos
                pass
        
            if (self.is_accelerating > 0):
                self.canvas.coords(self.thruster_id, self.thruster_points(self.angle))
                fill = '#%02x%02x%02x' % (int(self.is_accelerating * (255 / 5)), int(self.is_accelerating * (255 / 5)), int(self.is_accelerating * (255 / 5)))
                self.canvas.itemconfigure(self.thruster_id, state="normal", fill=fill)
                self.is_accelerating -= 1
            else:
                self.canvas.itemconfigure(self.thruster_id, state="hidden")
            
            # apply physics
            self.frog_x+=self.frog_vx
            self.frog_y+=self.frog_vy
            
            self.frog_vx *= 0.995
            self.frog_vy *= 0.995   
            
            if (self.frog_vx > 10):
                self.frog_vx = 10
            if (self.frog_vy > 10):
                self.frog_vy = 10
            if (self.frog_vx < -10):
                self.frog_vx = -10
            if (self.frog_vy < -10):
                self.frog_vy = -10
            
            if self.frog_x > 800: self.frog_x = 0
            elif self.frog_x < 0: self.frog_x = 800
            if self.frog_y > 800: self.frog_y = 0
            elif self.frog_y < 0: self.frog_y = 800
            
            self.canvas.coords(self.frog, self.frog_x-25, self.frog_y-25, self.frog_x+25, self.frog_y+25)
            
            
            #spawn objects here
            for probs in self.spawnrates:
                if random.random() < self.spawnrates[probs]:
                    if probs == "asteroid":
                        self.objects.append(Asteroid(self.canvas, int(self.sizes["asteroid"])))
                    elif probs == "stardust":
                        self.objects.append(StaticObject(self.canvas, random.randint(200, 600), random.randint(200, 600), int(self.sizes["stardust"]), "stardust"))
                        
            
            to_delete = []
            for item in self.objects:
                still_moving = item.update()
                if still_moving is False:
                    to_delete.append(item)         
                if isinstance(item, StaticObject):
                    self.canvas.itemconfigure(item.id, fill=self.grayscale((255, 255, 0), (100 - (item.time_left / 100) * 100)))
                    if item.check_collision(self.frog_x, self.frog_y):
                        self.stardust += 1
                        print("Stardust collected")
                        to_delete.append(item)    
                        
                    else:
                        item.time_left -= 1
                        if item.time_left <= 0:
                            to_delete.append(item)
                elif isinstance(item, Asteroid):
                    if item.check_collision(self.frog_x, self.frog_y):
                        print("Hit by asteroid! Game Over!")
                        
                        self.show_game_over()
                        # self.show_home()

            for item in to_delete:
                item.destroy()
                if isinstance(item, StaticObject) and item in self.objects:
                    self.objects.remove(item)
                
            self.canvas.tag_raise(self.border)
                
                
                            
            
            
        self.root.after(self.frame_delay, self.game_loop)
            
    def show_home(self):
        self.game_state = "home"
        self.home_frame.pack(expand=True, fill="both")
        self.canvas_frame.pack_forget()
        self.game_over_frame.pack_forget()
        
    def show_game(self):
        self.game_state = "game"
        self.home_frame.pack_forget()
        self.canvas_frame.pack(expand=True, fill="both")
        self.game_over_frame.pack_forget()
        
        # set up game preset data and stuff
        self.objects = []
        self.stardust = 0
        self.margin = 0
        self.sizes = {
            "stardust": 30,
            "asteroid": 20
        }
        
        # testing -> apply acceleration 
        # self.apply_acceleration(45)  
        
    def apply_acceleration(self, angle):
        
        acceleration = 2
        self.angle = angle
        self.frog_vx += acceleration * math.cos(math.radians(angle)) * -1
        self.frog_vy += acceleration * math.sin(math.radians(angle)) 
        self.is_accelerating = 5
    
    def thruster_points(self, angle):
        points = []
        # angle = (angle + 180) % 360
        rad_angle = math.radians(angle)
        for px, py in self.thruster_shape:
            flicker_x = px
            
            rotated_x = flicker_x * math.cos(rad_angle) - py * math.sin(rad_angle)
            rotated_y = flicker_x * math.sin(rad_angle) + py * math.cos(rad_angle)
            
            rotated_x *= -1
            points.extend([self.frog_x + rotated_x, self.frog_y + rotated_y])
        return points
        
        
        
    def start_game(self):
        self.show_game()
        
    def grayscale(self, rgb_tuple, percent_black):

        r, g, b = rgb_tuple
        remaining_factor = 1.0 - (percent_black / 100.0)
        
        final_r = int(r * remaining_factor)
        final_g = int(g * remaining_factor)
        final_b = int(b * remaining_factor)
        
        final_r = max(0, min(255, final_r))
        final_g = max(0, min(255, final_g))
        final_b = max(0, min(255, final_b))
        
        return '#%02x%02x%02x' % (final_r, final_g, final_b)
            

        



game = GregGame(root)
root.mainloop()
