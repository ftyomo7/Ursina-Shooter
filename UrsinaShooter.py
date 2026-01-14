from ursina import *
from random import uniform
from ursina.application import pause
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import unlit_shader

buildings = []


def generate_buildings():
    for i in range(5):  # Create 5 random buildings
        bx = uniform(-20, 20)
        bz = uniform(-20, 20)
        height = uniform(3, 7)
        building = Entity(model="cube", texture="brick", scale=(3, height, 3),
                          position=(bx, height / 2, bz), collider="box")
        buildings.append(building)

def update_score():
    global score
    score += 1
    score_text.text = f"Score: {score}"

def pause_handler_input(key):
    if key == 'escape':
        application.paused = not application.paused
        pause_text.enabled = application.paused

        for wasp in wasps:
            if application.paused:
                wasp.animation.pause()  # Stop animation
            else:
                wasp.animation.resume()  # Resume animation

        for spider in spiders:
            if application.paused:
                spider.animation.pause()
            else:
                spider.animation.resume()


weapon_models = ["assets/gun.obj", "assets/Sting-Sword-lowpoly.obj"]  # Add weapons here
weapon_index = 0  # Start with the first weapon

def reset_environment():
    global wasps, spiders

    # Destroy old wasps and spiders, along with their health bars
    for wasp in wasps:
        if hasattr(wasp, 'health_bar'):
            destroy(wasp.health_bar)
        destroy(wasp)

    for spider in spiders:
        if hasattr(spider, 'health_bar'):
            destroy(spider.health_bar)
        destroy(spider)

    wasps.clear()
    spiders.clear()
    for b in buildings:
        destroy(b)
    buildings.clear()
    generate_buildings()

    # Create new wasps
    for _ in range(num):
        wx = uniform(-12, 12)
        wy = uniform(.1, 1.8)
        wz = uniform(.8, 3.8)
        wasp = Wasp(wx, wy, wz)
        wasp.animation = wasp.animate_x(wx + 0.5, duration=0.2, loop=True)
        wasps.append(wasp)

    # Create new spiders
    for _ in range(num):
        sx = uniform(-12, 12)
        sy = uniform(.2, 1.7)
        sz = uniform(5.5, 8.8)
        spider = Spider(sx, sy, sz)
        spider.animation = spider.animate_x(sx + 0.6, duration=0.2, loop=True)
        spiders.append(spider)

   

def reset_image_color():
    image1.color = color.white  # Restore normal color

    
def damage_player(amount):
    global player_health
    player_health -= amount
    player_health_bar.scale_x = player_health / 100 * 0.4  # Adjust bar width

    if player_health <= 0:
        print("Player is defeated!") 

def input(key):

    global weapon_index
 
    
    if key == "z":
        weapon_index = (weapon_index + 1) % 2  # 0 = gun, 1 = sword

        gun.enabled = (weapon_index == 0)
        sword.enabled = (weapon_index == 1)

        image1.color = color.yellow
        invoke(reset_image_color, delay=0.3)
    
    if key == "left mouse down":
        if weapon_index == 0:  # Gun
            Audio("assets/laser_sound.wav")
            Animation("assets/spark", parent=camera.ui, fps=5, scale=.1, position=(.13, -.09), loop=False)

            for wasp in wasps:
                if wasp.hovered:
                    wasp.take_damage(5)
                    update_score()
                    break

            for spider in spiders:
                if spider.hovered:
                    spider.take_damage(5)
                    update_score()
                    break

        if weapon_index == 1:  # Sword
            Audio("assets/slash.mp3")

            for wasp in wasps:
                if wasp.hovered:
                    wasp.take_damage(50)
                    update_score()
                    break

            for spider in spiders:
                if spider.hovered:
                    spider.take_damage(50)
                    update_score()
                    break

    if key == "x":
        reset_environment()
    if key == 'right mouse down':
        camera.fov = zoomed_fov

    if key == 'right mouse up':
        camera.fov = default_fov

class Wasp(Button):
    def __init__(self, x, y, z):
        super().__init__(
            parent=scene,
            model="assets/wasp.obj", scale=.1, position=(x, y, z), rotation=(0, 90, 0), collider="box")
        self.health = 50  # Wasp health
        self.health_bar = Entity(
             parent=scene,  # Not parented to self
             world_parent=scene,
             model='quad',
             color=color.green,
             scale=(0.2, 0.03),
             position=self.position + Vec3(0, 1, 0),  # Hovering above enemy
             billboard=True,  # Always faces camera
             shader=unlit_shader)
    def update(self):
        if hasattr(self, 'health_bar'):
            self.health_bar.position = self.world_position + Vec3(0, 1, 0)

    def take_damage(self, amount):
        self.health -= amount
        self.health_bar.scale_x = self.health / 50 * 0.2

        if self.health <= 0:
            self.enabled = False
            if self.health_bar:
                self.health_bar.enabled = False  # Hide the bar immediately
            invoke(destroy, self, delay=0.01)

class Spider(Button):
    def __init__(self, x, y, z):
        super().__init__(
            parent=scene, model="assets/spider.obj", scale=.02,
            position=(x, y, z), rotation=(0, 90, 0), collider="box")
        self.health = 50  #  health
        self.health_bar = Entity(
             parent=scene,  # Not parented to self
             world_parent=scene,
             model='quad',
             color=color.green,
             scale=(0.2, 0.03),
             position=self.position + Vec3(0, 1.2, 0),  # Hovering above enemy
             billboard=True,  # Always faces camera
             shader=unlit_shader)
    def update(self):
        if hasattr(self, 'health_bar'):
            self.health_bar.position = self.world_position + Vec3(0, 1.2, 0)

    def take_damage(self, amount):
        self.health -= amount
        self.health_bar.scale_x = self.health / 50 * 0.2

        if self.health <= 0:
            self.enabled = False
            if self.health_bar:
                self.health_bar.enabled = False  # Hide the bar immediately
            invoke(destroy, self, delay=0.01)
app= Ursina()
  

Sky()
player=FirstPersonController()
default_fov = camera.fov
zoomed_fov = 30
ground=Entity(model='plane', texture='grass',collider='mesh', scale=(50, 3,50))

wall_1=Entity(model="cube", collider="box", position=(-8, 0, 0), scale=(8, 5, 1), rotation=(0, 0, 0), texture="brick", 
              texture_scale=(5, 5), color=color.white)

block= Entity(model="cube", texture='assets/box_texture', collider="mesh", position=(3, 0.5, 3), shaders=unlit_shader)


score = 0
score_text = Text(text=f"Score: {score}", position=(-0.8, 0.4), scale=2, parent=camera.ui)


image1 = Entity(
    parent=camera.ui,
    model='quad',
    texture='assets/switch_weapon.png',
    scale=0.1,
    position=(0.83, 0.3),
    z=-1,
    color=color.white,
    shader=unlit_shader
)

image1.texture.filtering = False  # prevents blur

gun = Entity(model="assets/gun.obj", parent=camera.ui, scale=.13, color=color.gray,
             position=(.3, -0.3), rotation=(-5, -10, -10), texture="assets/Sting_Base_Color.png", enabled=True)

sword = Entity(model="assets/Sting-Sword-lowpoly.obj", parent=camera.ui, scale=0.015, color=color.white,
               position=(0.5, -0.3), rotation=(100, -50, -100), texture="assets/Sting_Base_Color.png", enabled=False)

pivot=Entity()
DirectionalLight(parent=pivot,y=2,z=3,rotation=(45,-45,45), shadows=True)

#window.fullscreen=True
num=6
wasps=[None]*num

spiders=[None]*num

for i in range(num):
    wx=uniform(-12, -7)         
    wy= uniform(.1, 1.8)
    wz= uniform(.8, 3.8)
    wasps[i]=Wasp(wx,wy,wz)
    wasps[i].animation = wasps[i].animate_x(wx+.5, duration=.2, loop=True)


    sx=uniform(-12, -6)
    sy=uniform(.2, 1.7)
    sz=uniform(5.5, 8.8)
    spiders[i]=Spider(sx,sy,sz)
    spiders[i].animation = spiders[i].animate_x(sx+.6, duration=.2, loop=True)

player_health = 100  # Starting health

player_health_bar = Entity(parent=camera.ui, model='quad', color=color.red, scale=(0.4, 0.03),
                           position=(-0.6, 0.45), enabled=True)

pause_handler= Entity(ignore_paused=True)
pause_text=Text('PAUSED', origin=(0,0), scale=2, enabled=False)
pause_handler.input=pause_handler_input

print("Image entity:", image1)
print("Texture loaded:", image1.texture)


app.run()