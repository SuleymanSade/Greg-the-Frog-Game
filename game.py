import tkinter as tk
import math
from PIL import Image, ImageTk, ImageColor
import random

import time
import serial
root = tk.Tk()
root.title("Space Greg")


PORT = "COM3"
SERIAL_RATE = 9600

JYSTCK_LOWER = 450
JYSTCK_HIGHER = 550

allHistory = []

ser = serial.Serial(PORT, baudrate=SERIAL_RATE, timeout=0.01)


def change_opacity(image_path, opacity=1.0, size=30):
    img = Image.open(image_path).resize((size, size)).convert("RGBA")
    r, g, b, alpha = img.split()
    alpha = alpha.point(lambda p: int(p * max(0.0, min(opacity, 1.0))))
    img_with_opacity = Image.merge("RGBA", (r, g, b, alpha))
    return ImageTk.PhotoImage(img_with_opacity)


def send_data(info: str):
    ser.write(info.encode("utf-8"))


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
        motion = [0, 0]
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


class Asteroid:
    def __init__(self, canvas, size, m_type="normal"):
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
        else:  # spawning from the right sdie
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
        if (m_type == "mega"):
            self.spin_speed *= 2
            self.id = self.canvas.create_polygon(
                self.get_rotated_points(), fill="#1a0f0b", outline="white")
            self.vx *= 2
            self.vy *= 2
        else:
            self.id = self.canvas.create_polygon(
                self.get_rotated_points(), fill="#353535", outline="white")

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

        if (self.x < -150 or self.x > 950 or self.y < -150 or self.y > 950):
            return False
        return True

    def destroy(self):
        self.canvas.delete(self.id)

    def check_collision(self, frog_x, frog_y):
        dist = math.sqrt((self.x - frog_x)**2 + (self.y - frog_y)**2)
        return dist < self.radius + 25


class StaticObject:
    def __init__(self, canvas, x, y, size, object_type, image=None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.type = object_type
        self.image = image
        if self.image:
            img = Image.open("fuel.png").resize(
                (self.size*2, self.size*2), Image.Resampling.LANCZOS)
            self.image = ImageTk.PhotoImage(img)
            self.id = self.canvas.create_image(
                self.x, self.y, image=self.image)
        else:
            if (self.type == "comet"):
                self.id = self.canvas.create_oval(
                    self.x-self.size, self.y-self.size, self.x+self.size, self.y+self.size, fill="white")
            else:
                self.id = self.canvas.create_oval(
                self.x-self.size, self.y-self.size, self.x+self.size, self.y+self.size, fill="yellow")
        self.time_left = 100  # 5 seconds at 60 fps

    def destroy(self):
        self.canvas.delete(self.id)

    def update(self):
        pass

    def check_collision(self, frog_x, frog_y):
        dist = math.sqrt((self.x - frog_x)**2 + (self.y - frog_y)**2)
        return dist < self.size + 25

class Wormholes:
    def __init__(self, canvas):
        self.canvas = canvas
        self.image = Image.open("wormhole.png").resize((60, 60), Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(self.image)
        self.size = 30  

        self.x1 = random.randint(100, 700)
        self.y1 = random.randint(100, 700)
        
        self.x2 = random.randint(100, 700)
        self.y2 = random.randint(100, 700)
        
        while math.sqrt((self.x1 - self.x2)**2 + (self.y1 - self.y2)**2) < 200: # makes sure that they are at least 200 aprt
            self.x2 = random.randint(100, 700)
            self.y2 = random.randint(100, 700)

        self.id1 = self.canvas.create_image(self.x1, self.y1, image=self.image)
        self.id2 = self.canvas.create_image(self.x2, self.y2, image=self.image)
        self.time_left = 300
    
    def update(self):
        self.time_left -= 1
        if (self.time_left <= 0):
            return False
        return True
    
    def destroy(self):
        self.canvas.delete(self.id1)
        self.canvas.delete(self.id2)
    
    def check_collision(self, frog_x, frog_y):
        dist1 = math.sqrt((self.x1 - frog_x)**2 + (self.y1 - frog_y)**2)
        if (dist1 < 35):
            return 1 # portal 1
        dist2 = math.sqrt((self.x2 - frog_x)**2 + (self.y2 - frog_y)**2)
        if (dist2 < 35):
            return 2 # portal 2
        return 0 # no collision

class Comet(Asteroid):
    def __init__(self, canvas, game_instance):
        super().__init__(canvas, 20, m_type="normal")
        self.size = 20
        self.game = game_instance 
        self.canvas.itemconfigure(self.id, fill="white", outline="#eeeeee")
        self.vx *= 3.0
        self.vy *= 3.0
        self.spin_speed = random.uniform(-0.02, 0.02)
        
        self.trail_timer = 0

    def update(self):
        still_moving = super().update()
        if still_moving:
            self.trail_timer += 1
            if self.trail_timer >= 3:
                self.trail_timer = 0
                if random.random() < 0.6:
                    stardust = StaticObject(
                        self.canvas, 
                        self.x + random.uniform(-10, 10), 
                        self.y + random.uniform(-10, 10), 
                        10, 
                        "comet"
                    )
                    stardust.time_left = 90  
                    self.game.objects.append(stardust)
                    
        return still_moving
    

class GregGame:
    def __init__(self, root):
        self.start_time = time.time()

        self.root = root

        root.geometry("800x800")

        self.game_state = "home"
        self.canvas_frame = tk.Frame(root)
        self.canvas = tk.Canvas(
            self.canvas_frame, width=800, height=800, bg="black")
        self.canvas.pack()
        self.canvas_frame.pack()
        self.background_image = change_opacity("background.png", 0.2, 800)
        self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")
        self.home_frame = tk.Frame(root, bg="black")
        self.header_image = Image.open("ship.png").resize(
            (100, 100), Image.Resampling.LANCZOS)
        self.header_image = ImageTk.PhotoImage(self.header_image)
        self.home_label = tk.Label(
            self.home_frame, text="Space Greg", font=("Arial", 50, "bold"), bg="black", fg="white")
        self.header_label = tk.Label(self.home_frame, image=self.header_image, bg="black")
        self.start_button = tk.Button(
            self.home_frame, text="Start Game", command=self.start_game, bg="black", fg="white", height=2, width=17, font=("Arial", 16))
        self.guide_button = tk.Button(
            self.home_frame, text="Guide", command=self.show_guide, bg="black", fg="white", height=2, width=17, font=("Arial", 16))
        
        
        self.home_label.pack()
        self.home_label.place(relx=0.5, rely=.4, anchor=tk.CENTER)
        self.header_label.pack()
        self.header_label.place(relx=0.5, rely=.27, anchor=tk.CENTER)
        self.start_button.pack()
        self.start_button.place(relx=.5, rely=.52, anchor=tk.CENTER)
        self.guide_button.pack()
        self.guide_button.place(relx=.5, rely=.63, anchor=tk.CENTER)
        self.home_frame.pack()
        self.high_score = 0
        

        self.game_over_frame = tk.Frame(root, bg="black")
        self.game_over_label = tk.Label(
            self.game_over_frame, text="Mission Failed!", font=("Arial", 35, "bold"), bg="black", fg="white")
        self.game_over_label2 = tk.Label(
            self.game_over_frame, text="You've been hit by an asteroid", font=("Arial", 20), bg="black", fg="white")
        self.high_score_label = tk.Label(self.game_over_frame, text=f"High Score: {self.high_score}", font=("Arial", 20), bg="black", fg="white")
        self.high_score_label.pack()
        self.high_score_label.place(relx=.5, rely=.73, anchor=tk.CENTER)
        self.new_high_score = tk.Label(self.game_over_frame, text="New High Score!", font=("Arial", 25), bg="black", fg="#50ba6c")
        self.new_high_score.pack()
        self.new_high_score.place(relx=.5, rely=.78, anchor=tk.CENTER)

        self.final_score_label1 = tk.Label(
            self.game_over_frame, font=("Arial", 20), bg="black", fg="white")
        self.final_score_label2 = tk.Label(
            self.game_over_frame, font=("Arial", 45, "bold"), bg="black", fg="white")
        self.restart_button = tk.Button(self.game_over_frame, text="Restart the Game",
                                        command=self.start_game, width=17, height=2, font=("Arial", 14), bg="black", fg="white")
        self.return_home = tk.Button(self.game_over_frame, text="Return Home",
                                        command=self.show_home, width=17, height=2, font=("Arial", 14), bg="black", fg="white")
        self.game_over_label.pack()
        self.game_over_label.place(relx=.5, rely=.4, anchor=tk.CENTER)
        self.game_over_label2.pack()
        self.game_over_label2.place(relx=.5, rely=.47, anchor=tk.CENTER)
        self.game_over_frame.pack()
        self.restart_button.pack()
        self.restart_button.place(relx=.35, rely=.3, anchor=tk.CENTER)
        self.return_home.pack()
        self.return_home.place(relx=.65, rely=.3, anchor=tk.CENTER)
        
        self.guide_frame = tk.Frame(root, bg="black")
        self.guide_header = tk.Label(self.guide_frame, text="Space Greg - Game Guide", font=("Arial", 30, "bold"), bg="black", fg="white")
        self.guide_header.pack()
        self.guide_header.place(relx=.5, rely=.06, anchor=tk.CENTER)
        self.guide_descrpition = tk.Label(self.guide_frame, text="Welcome to Space Greg! You're playing as Greg, a brave frog who is collecting stardust to save the solar system and the rest of the frog species! But this mission is not without its challenges; there are multiple obstacles you'll have to face, all while managing your fuel. ", font=("Arial", 16), bg="black", fg="white", wraplength=700, justify="center")
        self.guide_descrpition.pack()
        self.guide_descrpition.place(relx=.5, rely=.16, anchor=tk.CENTER)
        
        self.guide_controls = tk.Label(self.guide_frame, text="Controls: \n- Joystick to move Greg (using flicking in direction of intended motion)\n- Shift key to boost speed (uses more fuel)", font=("Arial", 16), bg="black", fg="white", justify="left")
        self.guide_controls.pack()
        self.guide_controls.place(relx=.5, rely=.28, anchor=tk.CENTER) 
        self.guide_return = tk.Button(self.guide_frame, text="Return Home", command=self.show_home, width=17, height=2, font=("Arial", 13), bg="black", fg="white")
        self.guide_return.pack()
        self.guide_return.place(relx=.5, rely=.93, anchor=tk.CENTER)
        # description of each object
        texts = ["This is Greg, in his spaceship. Use the joystick to move him around.", "Stardust is what you need to collect to win the game. These get smaller as the game progresses, making them harder to collect!", "Collect fuel objects to replenish your fuel, it runs out quickly! These get smaller as the game progresses, making them harder to collect!", "Asteroids are obstacles you must avoid. You'll explode if you collide with them!", "Be especially careful of asteroid clusters. They are fast moving groups of asteroids that are hard to navigate through!", "Comets are dangerously fast objects that leave a trail of valuable stardust, but be careful as they can be hard to avoid!", "Wormholes are mysterious portals that can transport you to their pair, but be cautious where you go!"] 
        for img in ["ship.png", "stardust.png", "fuel.png", "asteroid.png", "cluster.png","comet.png", "wormhole.png"]:
            loaded_img = Image.open(img).resize((50, 50), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(loaded_img)
            label = tk.Label(self.guide_frame, image=tk_img, bg="black")
            label.image = tk_img
            label.pack()
            label.place(relx=.17, rely=.38 + 0.08 * ["ship.png", "stardust.png", "fuel.png", "asteroid.png", "cluster.png","comet.png", "wormhole.png"].index(img), anchor=tk.CENTER)  
            text = tk.Label(self.guide_frame, text=texts[["ship.png", "stardust.png", "fuel.png", "asteroid.png", "cluster.png","comet.png", "wormhole.png"].index(img)], font=("Arial", 13), bg="black", fg="white", justify="left", wraplength=500)
            text.pack()
            text.place(relx=.57, rely=.38 + 0.08 * ["ship.png", "stardust.png", "fuel.png", "asteroid.png", "cluster.png","comet.png", "wormhole.png"].index(img), anchor=tk.CENTER)
        # self.guide_img1 = Image.open("ship.png").resize((50, 50), Image.Resampling.LANCZOS)
        # self.guide_img1.pack()
        # self.guide_img1.place(relx=.25, rely=.45, anchor=tk.CENTER)
        # self.guide_img2 = Image.open("stardust.png").resize((50, 50), Image.Resampling.LANCZOS)
        # self.guide_img2.pack()
        # self.guide_img2.place(relx=.25, rely=.50, anchor=tk.CENTER)
        # self.guide_img3 = Image.open("fuel.png").resize((50, 50), Image.Resampling.LANCZOS)
        # self.guide_img3.pack()
        # self.guide_img3.place(relx=.25, rely=.55, anchor=tk.CENTER)

        self.thruster_shape = [(-20, 10), (-20, -10), (-45, 0)]
        self.thruster_shape2 = [(-10, 15), (-10, -15), (-45, 0)]  # bigger
        self.fuel_frames = {} # hold different sizes too
        print("Preloading and caching assets...")
        self.base_fuel_img = Image.open("fuel.png").convert("RGBA")
        
        for s in range(7, 22):
            self.fuel_frames[s] = []
            sized_img = self.base_fuel_img.resize((s * 2, s * 2), Image.Resampling.LANCZOS)
            
            for i in range(101):
                opacity = i / 100.0
                r, g, b, alpha = sized_img.split()
                alpha = alpha.point(lambda p: int(p * opacity))
                final_img = Image.merge("RGBA", (r, g, b, alpha))
                self.fuel_frames[s].append(ImageTk.PhotoImage(final_img))
            
        self.wormhole_frames = []
        base_wormhole = Image.open("wormhole.png").resize((60, 60), Image.Resampling.LANCZOS).convert("RGBA")
        for i in range(301): 
            rotated_img = base_wormhole.rotate(i * 10)
            r, g, b, alpha = rotated_img.split()
            opacity = max(0.0, min(i / 200.0, 1.0))
            alpha = alpha.point(lambda p: int(p * opacity))
            final_img = Image.merge("RGBA", (r, g, b, alpha))
            self.wormhole_frames.append(ImageTk.PhotoImage(final_img))
        
        
        # self.stardust_frames = []
        self.stardust_frames = {}  #multiple sizes
        base_stardust = Image.open("stardust.png").convert("RGBA")
        for s in range(7, 32):
            self.stardust_frames[s] = []
            sized_img = base_stardust.resize((s * 2, s * 2), Image.Resampling.LANCZOS)
            for i in range(101):
                opacity = i / 100.0
                r, g, b, alpha = sized_img.split()
                alpha = alpha.point(lambda p: int(p * opacity))
                final_img = Image.merge("RGBA", (r, g, b, alpha))
                self.stardust_frames[s].append(ImageTk.PhotoImage(final_img))

        self.last_sent_fuel = -1

        self.thruster_id = self.canvas.create_polygon(
            [0, 0, 0, 0, 0, 0], fill="white", state="hidden"
        )
        frog_image = Image.open("ship.png").resize(
            (50, 50), Image.Resampling.LANCZOS)
        frog_image = ImageTk.PhotoImage(frog_image)
        self.frog_image = frog_image
        self.frog = self.canvas.create_image(400, 400, image=self.frog_image)
        self.fuel_image = tk.PhotoImage(file="fuel.png")
        self.frog_x = 400  # center
        self.frog_y = 400
        self.frog_vx = 0
        self.frog_vy = 0
        self.is_accelerating = 0
        self.angle = 0
        self.border = self.canvas.create_rectangle(
            0, 0, 800, 800, outline="#212121", width=100)
        self.sizes = {
            "stardust": 30,
            "asteroid": 20,
            "fuel": 15,
            "asteroid-cluster": 40
        }
        self.fuel = 40
        self.shiftdown = False
        self.root.bind("<KeyPress-Shift_L>", lambda e: self.set_shift(True))
        self.root.bind("<KeyRelease-Shift_L>", lambda e: self.set_shift(False))
        self.root.bind("<KeyPress-Shift_R>", lambda e: self.set_shift(True))
        self.root.bind("<KeyRelease-Shift_R>", lambda e: self.set_shift(False))
        self.temp_text = []
        self.particles = []

        self.fuel_label = self.canvas.create_text(
            10, 15, text=f"Fuel: ", fill="#ffffff", font=("Arial", 16), anchor="nw")
        self.fuel_progress = self.canvas.create_rectangle(
            70, 15, 70 + self.fuel, 40, fill="#19c809", outline="")
        self.fuel_border = self.canvas.create_rectangle(
            70, 15, 70 + 200, 40, outline="#434343", width=2)  # max is 200
        self.time_label = self.canvas.create_text(
            750, 15, text=f"0s", fill="#ffffff", font=("Arial", 16), anchor="ne")

        self.spawnrates = {
            "stardust": 0.03,
            "asteroid": 0.01,
            "fuel": 0.005,
            "asteroid-cluster": 0.0005,
            "comet": 0.0003
        }

        self.frame_delay = int(1000 / 60)  # 60 fps
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

    def set_shift(self, value):
        self.shiftdown = value

    def on_key_press(self, event):
        key = event.keysym
        if key in self.keys:
            self.keys[key] = True

    def on_key_release(self, event):
        key = event.keysym
        if key in self.keys:
            self.keys[key] = False

    def show_game_over(self, reason="You've been hit by an asteroid!"):
        self.game_state = "game over"

        final_score = round(
            self.stardust * (time.time()-self.start_time)) + self.fuel
        self.canvas_frame.forget()
        self.home_frame.forget()
        self.guide_frame.forget()
        self.game_over_frame.pack(expand=True, fill="both")
        
        self.game_over_label.config(text="Mission Failed!")
        self.game_over_label2.config(text=reason)
        
        self.final_score_label1.config(
            text=f"Final Score: {self.stardust} stardust x {round(time.time()-self.start_time, 2)} sec + {self.fuel} fuel")
        self.final_score_label1.pack()
        self.final_score_label1.place(relx=.5, rely=.55, anchor=tk.CENTER)
        self.final_score_label2.config(
            text=f"= {final_score} pts")
        self.final_score_label2.pack()
        self.final_score_label2.place(relx=.5, rely=.63, anchor=tk.CENTER)
        self.high_score_label.config(text=f"High Score: {self.high_score}")
        if final_score > self.high_score:
            self.high_score_label.config(text=f"Previous High Score: {self.high_score}")

            self.high_score = final_score
            self.new_high_score.config(text="New High Score!")
            self.new_high_score.pack()
            self.new_high_score.place(relx=.5, rely=.78, anchor=tk.CENTER)
        else:
            self.new_high_score.pack_forget()
            self.new_high_score.place_forget()
        # self.final_score_label.pack(side="top")

        for item in self.objects:
            item.destroy()

        send_data("0,1\n")

        self.objects = []
        self.stardust = 0

        self.start_time = time.time()

    def game_loop(self):

        if (self.game_state == "game"):
            self.margin += 0.06
            self.sizes["stardust"] -= 0.009  # goes down by 0.540 every second
            self.sizes["asteroid"] += 0.004  # goes up by 0.24 every second
            self.sizes["fuel"] -= 0.006  # goes down by 0.36 every second
            if (self.sizes["fuel"] < 7):
                self.sizes["fuel"] = 7
            if (self.sizes["stardust"] < 7):
                self.sizes["stardust"] = 7
            if (self.sizes["asteroid"] > 50):
                self.sizes["asteroid"] = 50
            self.canvas.itemconfigure(self.border, width=self.margin)
            self.spawnrates["asteroid"] += 0.00002
            self.spawnrates["stardust"] += 0.00001
            self.spawnrates["fuel"] += 0.000005
            self.canvas.move(self.frog, 0.5, 0.5)

            if (self.keys["Up"]):
                self.apply_acceleration(270)
            elif (self.keys["Down"]):
                self.apply_acceleration(90)
            elif (self.keys["Left"]):
                self.apply_acceleration(0)
            elif (self.keys["Right"]):
                self.apply_acceleration(180)
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
                self.apply_acceleration(deg)
            else:
                # Stay at the same pos
                pass

            if (self.is_accelerating > 0):
                points = self.thruster_points(self.angle, "normal")
                if (self.a_type == "boost"):
                    points = self.thruster_points(self.angle, "boost")
                self.canvas.coords(self.thruster_id, points)
                fill = '#%02x%02x%02x' % (int(self.is_accelerating * (255 / 4)), int(
                    self.is_accelerating * (255 / 4)), int(self.is_accelerating * (255 / 4)))
                if (self.a_type == "boost"):
                    fill = '#%02x%02x%02x' % (int(self.is_accelerating * (140 / 8)), int(
                        self.is_accelerating * (159 / 8)), int(self.is_accelerating * (255 / 8)))
                self.canvas.itemconfigure(
                    self.thruster_id, state="normal", fill=fill)
                self.is_accelerating -= 1
            else:
                self.canvas.itemconfigure(self.thruster_id, state="hidden")

            # apply physics
            self.frog_x += self.frog_vx
            self.frog_y += self.frog_vy

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

            if self.frog_x > 800:
                self.frog_x = 0
            elif self.frog_x < 0:
                self.frog_x = 800
            if self.frog_y > 800:
                self.frog_y = 0
            elif self.frog_y < 0:
                self.frog_y = 800

            self.canvas.coords(self.frog, self.frog_x, self.frog_y)

            # spawn objects here
            for probs in self.spawnrates:
                if random.random() < self.spawnrates[probs]:
                    if probs == "asteroid":
                        self.objects.append(
                            Asteroid(self.canvas, int(self.sizes["asteroid"])))
                    elif probs == "comet":
                        self.objects.append(Comet(self.canvas, self))
                    elif probs == "stardust":
                        spawn_size = int(self.sizes["stardust"])
                        clamped_size = max(7, min(31, spawn_size))
                        starting_image = self.stardust_frames[clamped_size][100]                        
                        stardust = StaticObject(self.canvas, random.randint(
                            200, 600), random.randint(200, 600), spawn_size, "stardust", starting_image)
                        self.objects.append(stardust)
                    elif probs == "fuel":
                        spawn_size = int(self.sizes["fuel"])
                        clamped_size = max(7, min(21, spawn_size))
                        starting_image = self.fuel_frames[clamped_size][100]
                        fuel = StaticObject(self.canvas, random.randint(
                            200, 600), random.randint(200, 600), spawn_size, "fuel", starting_image)
                        self.objects.append(fuel)
                        print("fuel spawned at ", fuel.x, fuel.y)
                    elif probs == "asteroid-cluster":
                        main_size = int(self.sizes["asteroid-cluster"])
                        main = Asteroid(self.canvas, main_size, m_type="mega")
                        self.objects.append(main)

                        num_debris = random.randint(3, 6)

                        for _ in range(num_debris):
                            debris_size = int(self.sizes["asteroid"] * random.uniform(0.4, 1.2))
                            asteroid = Asteroid(self.canvas, debris_size, m_type="mega")
                            angle = random.uniform(0, 2 * math.pi)
                            distance = random.uniform(main_size * 0.8, main_size * 2.2)
                            
                            asteroid.x = main.x + math.cos(angle) * distance
                            asteroid.y = main.y + math.sin(angle) * distance
                            asteroid.vx = main.vx + random.uniform(-0.4, 0.4)
                            asteroid.vy = main.vy + random.uniform(-0.4, 0.4)
                            
                            # asteroid.spin_speed = main.spin_speed + random.uniform(-0.05, 0.05)
                            asteroid.spin_speed = random.uniform(-0.15, 0.15)

                            self.canvas.coords(asteroid.id, asteroid.get_rotated_points())
                            
                            self.objects.append(asteroid)
                    elif probs == "wormhole":
                        # too many wormholes = bad
                        if not any(isinstance(obj, Wormholes) for obj in self.objects):
                            wormhole = Wormholes(self.canvas)
                            self.objects.append(wormhole)
                        
            to_delete = []
            for item in self.objects:
                still_moving = item.update()
                if still_moving is False:
                    to_delete.append(item)
                if isinstance(item, StaticObject):
                    if (item.image is None):
                        if item.type == "comet":
                            self.canvas.itemconfigure(item.id, fill=self.grayscale(
                                (255, 255, 255), (100 - (item.time_left / 100) * 100)))
                        else:
                            self.canvas.itemconfigure(item.id, fill=self.grayscale(
                                (255, 255, 0), (100 - (item.time_left / 100) * 100)))
                    else:
                        if (item.type == "fuel"):
                            frame_index = max(0, min(100, int(item.time_left)))
                            clamped_size = max(7, min(21, int(item.size)))
                            item.image = self.fuel_frames[clamped_size][frame_index]
                            self.canvas.itemconfigure(item.id, image=item.image)
                        elif (item.type == "stardust"):
                            frame_index = max(0, min(100, int(item.time_left)))
                            clamped_size = max(7, min(31, int(item.size)))
                            item.image = self.stardust_frames[clamped_size][frame_index]
                            self.canvas.itemconfigure(item.id, image=item.image)
                    if item.check_collision(self.frog_x, self.frog_y):
                        to_delete.append(item)
                        if (item.type == "stardust"):
                            self.stardust += 1
                            label = self.canvas.create_text(
                                self.frog_x+(self.sizes["stardust"]/2), self.frog_y+(self.sizes["stardust"]/2), text="+1", fill="yellow", font=("Arial", 16, "bold"))
                            self.temp_text.append([label, 30, "#FFFF00"])

                        elif (item.type == "comet"):
                            self.stardust += 2
                            label = self.canvas.create_text(
                                self.frog_x+(item.size/2), self.frog_y+(item.size/2), text="+2", fill="white", font=("Arial", 16, "bold"))
                            self.temp_text.append([label, 30, "#FFFFFF"])

                        elif (item.type == "fuel"):
                            fuel_change = random.randint(25, 50)
                            self.fuel += fuel_change
                            label = self.canvas.create_text(
                                self.frog_x+(self.sizes["fuel"]/2), self.frog_y+(self.sizes["fuel"]/2), text=f"+{fuel_change}", fill="#19c809", font=("Arial", 16, "bold"))
                            self.temp_text.append([label, 30, "#19c809"])

                            if (self.fuel > 200):
                                self.fuel = 200

                    else:
                        item.time_left -= 1
                        if item.time_left <= 0:
                            to_delete.append(item)
                elif isinstance(item, Asteroid):
                    if item.check_collision(self.frog_x, self.frog_y):
                        print("Hit by asteroid! Game Over!")
                        self.particles = []
                        colors = ["#ff0000", "#ff4000",
                                  "#ff8000", "#ffbf00", "#ffff00"]
                        for i in range(120):
                            size = random.uniform(1, 3)
                            color = random.choice(colors)
                            particle = self.canvas.create_oval(
                                self.frog_x-size, self.frog_y-size, self.frog_x+size, self.frog_y+size, fill=color, outline="", state="hidden")
                            angle = random.uniform(0, math.pi * 2)
                            speed = random.uniform(0.25, 0.90)
                            vx = math.cos(angle) * speed
                            vy = math.sin(angle) * speed
                            self.particles.append(
                                {"id": particle, "vx": vx, "vy": vy, "life": 80, "delay": random.randint(0, 3), "color": color})
                        self.game_state = "exploding"
                        self.explode()
                        # self.show_home()
                elif isinstance(item, Wormholes):
                    frame_index = max(0, min(300, int(item.time_left)))
                    
                    item.image = self.wormhole_frames[frame_index]
                    self.canvas.itemconfigure(item.id1, image=item.image)
                    self.canvas.itemconfigure(item.id2, image=item.image)
                    
                    if item.check_collision(self.frog_x, self.frog_y) == 1:
                        print("Entered wormhole! Teleporting...")
                        self.frog_x = item.x2
                        self.frog_y = item.y2
                        self.canvas.coords(self.frog, self.frog_x, self.frog_y)
                        to_delete.append(item)
                    elif item.check_collision(self.frog_x, self.frog_y) == 2:
                        print("Entered wormhole! Teleporting...")
                        self.frog_x = item.x1
                        self.frog_y = item.y1
                        self.canvas.coords(self.frog, self.frog_x, self.frog_y)
                        to_delete.append(item)
                    

            for item in to_delete:
                item.destroy()
                if (isinstance(item, StaticObject) or isinstance(item, Wormholes)) and item in self.objects:
                    self.objects.remove(item)

            self.canvas.tag_raise(self.border)
            for i in range(len(self.temp_text) - 1, -1, -1):
                self.temp_text[i][1] -= 1
                rgb = ImageColor.getcolor(self.temp_text[i][2], "RGB")
                self.canvas.itemconfigure(self.temp_text[i][0], fill=self.grayscale(
                    rgb, (100 - (self.temp_text[i][1] / 30) * 100)))
                if (self.temp_text[i][1] < 0):
                    self.canvas.delete(self.temp_text[i][0])
                    self.temp_text.pop(i)
            time_elapsed = int(time.time() - self.start_time)

            if (self.fuel < 0):
                self.fuel = 0
                # end game here
                self.show_game_over(reason="You've run out of fuel!")
            if (self.fuel > 90):
                self.canvas.itemconfigure(self.fuel_progress, fill="#19c809")
            elif (self.fuel > 60):
                self.canvas.itemconfigure(self.fuel_progress, fill="#c8c809")
            elif (self.fuel > 30):
                self.canvas.itemconfigure(self.fuel_progress, fill="#c86f09")
            else:
                if ((time_elapsed*2) % 2 == 0):
                    self.canvas.itemconfigure(self.fuel_progress, fill="#b22121")
                else:
                    self.canvas.itemconfigure(self.fuel_progress, fill="#C64141")
            time_elapsed = int(time_elapsed)
            self.canvas.coords(self.fuel_progress, 70, 15, 70 + self.fuel, 40)

            self.canvas.tag_raise(self.fuel_label)
            self.canvas.tag_raise(self.fuel_progress)
            self.canvas.tag_raise(self.fuel_border)

            minutes = time_elapsed // 60
            seconds = time_elapsed % 60
            self.canvas.itemconfigure(
                self.time_label, text=f"{minutes}m {seconds}s")
            self.canvas.tag_raise(self.time_label)

        if self.game_state == "game":
            if int(self.fuel) != self.last_sent_fuel: 
                try:
                    fuel_string = str(int(self.fuel)) +  ", 0\n"
                    send_data(fuel_string)
                    self.last_sent_fuel = int(self.fuel)
                except Exception as e:
                        print(f"Serial write error: {e}")

        self.root.after(self.frame_delay, self.game_loop)

    def show_home(self):
        self.game_state = "home"
        self.home_frame.pack(expand=True, fill="both")
        self.canvas_frame.pack_forget()
        self.game_over_frame.pack_forget()
        self.guide_frame.pack_forget()
    
    def show_guide(self):
        self.game_state = "guide"
        self.home_frame.pack_forget()
        self.canvas_frame.pack_forget()
        self.game_over_frame.pack_forget()
        self.guide_frame.pack(expand=True, fill="both")

    def show_game(self):
        self.game_state = "game"
        self.home_frame.pack_forget()
        self.canvas_frame.pack(expand=True, fill="both")
        self.game_over_frame.pack_forget()
        self.guide_frame.pack_forget()

        # set up game preset data and stuff
        self.objects = []
        self.stardust = 0
        self.margin = 0
        self.sizes = {
            "stardust": 30,
            "asteroid": 20,
            "fuel": 20,
            "asteroid-cluster": 40
        }
        self.particles = []
        self.frog_x = 400
        self.frog_y = 400
        self.frog_vx = 0
        self.frog_vy = 0
        self.is_accelerating = 0
        self.angle = 0
        self.start_time = time.time()
        self.spawnrates = {
            "stardust": 0.03,
            "asteroid": 0.01,
            "fuel": 0.005,
            "asteroid-cluster": 0.002,
            "comet": 0.001,
            "wormhole": 0.004
        }
        self.fuel = 100

        # testing -> apply acceleration
        # self.apply_acceleration(45)

    def apply_acceleration(self, angle):
        acceleration = 2
        self.is_accelerating = 4
        self.a_type = "normal"
        self.fuel -= 1

        if (self.shiftdown):
            acceleration = 4
            self.is_accelerating = 8
            self.a_type = "boost"
            self.fuel -= 2

        self.angle = angle
        self.frog_vx += acceleration * math.cos(math.radians(angle)) * -1
        self.frog_vy += acceleration * math.sin(math.radians(angle))

    def thruster_points(self, angle, size):
        points = []
        # angle = (angle + 180) % 360
        rad_angle = math.radians(angle)
        shape = self.thruster_shape
        if (size == "boost"):
            shape = self.thruster_shape2
        for px, py in shape:
            flicker_x = px

            rotated_x = flicker_x * \
                math.cos(rad_angle) - py * math.sin(rad_angle)
            rotated_y = flicker_x * \
                math.sin(rad_angle) + py * math.cos(rad_angle)

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

    def explode(self):
        if (len([p for p in self.particles if p["life"] > 60]) == 0):
            for i in range(len(self.particles)):
                self.canvas.itemconfigure(
                    self.particles[i]["id"], state="hidden")
                self.canvas.delete(self.particles[i]["id"])
            self.particles = []

            self.show_game_over()
        else:

            for p in self.particles:
                if p["delay"] > 0:
                    p["delay"] -= 1
                    continue
                self.canvas.move(p["id"], p["vx"], p["vy"])
                p["life"] -= 1
                self.canvas.scale(p["id"], self.frog_x,
                                  self.frog_y, 1.09, 1.09)
                self.canvas.itemconfigure(p["id"], fill=self.grayscale((int(p["color"][1:3], 16), int(
                    p["color"][3:5], 16), int(p["color"][5:7], 16)), (100 - (p["life"] / 80) * 100)), state="normal")

            if (len([p for p in self.particles if p["life"] > 60]) > 0):
                self.root.after(1000 // 60, self.explode)
            else:
                self.root.after(2500, self.explode)


game = GregGame(root)
root.mainloop()
