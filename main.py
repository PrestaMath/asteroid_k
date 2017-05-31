# -*- coding: utf8 -*-

import kivy
kivy.require('1.0.6') # replace with your current kivy version !
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from os import sep
import time             
import platform
import random
import v_joystick

USE_KEYBOARD = True
processor = platform.uname()[4]
if processor[0:3] == 'arm': USE_KEYBOARD = False   #si arm, linux et version entre 2.1 et 4.5 alors android ou alors recherche existence dossier?


#Window.size = (320,200)


SCREEN_BTN_SIZE =  int(Window.width * 0.1)


# Optimisation : avoid fixed division in loops
# add mad space ship
# Attention à la suppresion des objets !!!
# attention au parcours des tableaux lors des suppressions
# make script IamAndroidVersion get rid of dev folder
# todo : add "thrust audio" in ogg format or other music

IMG_DIR = 'img%s' % sep
WW = Window.width
WH = Window.height

if WH>WW:
    WH = Window.width
    WW = Window.height

'''    xlarge screens are at least 960dp x 720dp
    large screens are at least 640dp x 480dp
    normal screens are at least 470dp x 320dp
    small screens are at least 426dp x 320dp'''

SCALE =2

if WW<801 and WH<601:
    SCALE =1

if WW<471 and WH<320:
    SCALE =0


SPRITE_SIZE =  (int(16*pow(2,SCALE)),int(16*pow(2,SCALE)))

JOYSTICK = v_joystick.game_input(USE_KEYBOARD,SCREEN_BTN_SIZE)


def loop_between(val,min,max):
    mod = (val-min) % (max-min)
    return min+mod

def cycling_pos(x,y):           # 
    x = loop_between(x,0,Window.width)
    y = loop_between(y,0,Window.height)
    return (x,y)

class SoundSys:
    playing =''
    sounds = {}
    current_sound = None
    @staticmethod 
    def init():
        SoundSys.sounds['fire'] = SoundLoader.load('sound%sshot.wav' % sep)
        SoundSys.sounds['explosion'] = SoundLoader.load('sound%skick.wav' % sep)
        SoundSys.current_sound = SoundSys.sounds['fire']
    @staticmethod
    def play(action):

        if SoundSys.current_sound.state == 'play':
            if SoundSys.playing ==  action or action == 'explosion' :                # stop and play same sound
                SoundSys.current_sound.stop()

            else:
                return
        SoundSys.playing =action
        SoundSys.current_sound = SoundSys.sounds[action]        
        SoundSys.current_sound.volume = .1
        SoundSys.current_sound.play()                

SoundSys.init()

# Static class : Color_rotation
# Color_rotation.init() 
# Color_rotation.get_color()
class Color_rotation:
    @staticmethod 
    def init():
        Color_rotation.c = 0
        Color_rotation.tbl=[0,0,0]
        Color_rotation.val = 0
        Color_rotation.step = 0.1
        Color_rotation.i = 0
        
    @staticmethod
    def get_color():
        if Color_rotation.i == 297:       #max iteration
            return (0,0,0)

        Color_rotation.val += Color_rotation.step
        if Color_rotation.val>1:
            Color_rotation.val = Color_rotation.step
            Color_rotation.c +=1

        if Color_rotation.c<3:
            Color_rotation.tbl[Color_rotation.c] = Color_rotation.val    
        
        Color_rotation.i +=1
        return Color_rotation.tbl

class Sprite(Widget):
    fpos = (0,0)
    sprite_texture = ObjectProperty(None)
    def __init__(self, **kwargs):
        self.velocity = kwargs["velocity"]
        super(Sprite, self).__init__(**kwargs)  
        self.fpos = (self.x,self.y)
    def move(self,dt):
        self.fpos= Vector(self.velocity)*(1+dt) + (self.pos)
        self.pos = self.fpos
        self.pos = cycling_pos(self.x,self.y)    #check for boundary and vector to come back in opposite side of screen

class Asteroid(Sprite):
    
    eclairage = ListProperty((1,0,0))
    colors = ((1,0,0),(0,1,0),(0,0,1),(1,1,1),(1,.8,0),(1,1,0),(0,1,1),(1,0,1) ,(.6,.4,0),(0,0.4,0))
    def __init__(self, **kwargs):
        self.sprite_texture = Image(source= '%sasteroid.png' % IMG_DIR).texture
        level = kwargs["level"] #define asteroid color
        self.eclairage = self.colors[loop_between(level,0, len(self.colors))]
        if kwargs.has_key('size'):
            self.size=kwargs['size']
        else:
            self.size=(SPRITE_SIZE)

        super(Asteroid, self).__init__(**kwargs) #constructeur du parent
        
    def detect_collision(self):
        # based on center of circle and distance
        pass
    
class Ship(Sprite):
    thrust_triangle = ListProperty(None)
    eclairage = (1,1,1)
    triggered = False
    max_speed = 3
    max_bullet = 5
    vbullets = ListProperty(None)
    line_shape = ListProperty(None)
    explosion = []
    bullets = []
    textures = {}
    
    b_poll_fire = 0

    def __init__(self, **kwargs):
        for idx in range(0,360,10):
            self.textures["%i" % idx]=Image(source="%sship%i.png" % (IMG_DIR,idx)).texture
        self.textures["fragment"]=Image(source="%sship_fragment.png" % IMG_DIR).texture
        self.size=(SPRITE_SIZE)
        self.init_ship()
        super(Ship, self).__init__(**kwargs) #constructeur du parent
        
    def init_ship(self):
        self.pos = (Window.width/2,Window.height/2)
        self.velocity=(0,0)
        self.rotation = 90
        self.sprite_texture = self.textures['90']
        self.triggered = False
        #Clock.schedule_interval(self.poll_firing, 0.2)

    def explode(self):
        Color_rotation.init()
        self.particles = []
        for i in range(0,36):
            speed = random.uniform(0.3,0.5)
            v= Vector(1,1).rotate(i*10)
            self.particles.append((v,speed))
        Clock.schedule_interval(self.update_explosion, 0.1)


    def update_explosion(self,dt):
        xe = self.center_x
        ye = self.center_y
        adv = []
        disp = []
        for particle in self.particles:
            v = Vector(particle[0])* (1 +particle[1])

            if  v.x+xe>0 and v.x+xe<Window.width and v.y+ye>0 and v.y+ye<Window.height:            
                adv.append((v,particle[1]))
                disp.append(v.x+xe)
                disp.append(v.y+ye)
        self.explosion = disp
        self.particles = adv

    def get_thrust_shape(self):
        #initial pos 0 degree is ship toward right !
        #nose
        teq = self.height/2
        arr = []
        vShip = Vector(-teq-3,0).rotate(self.rotation)
        arr.append(vShip[0]+self.center_x)
        arr.append(vShip[1]+self.center_y)
        #left edge
        vShip = Vector(-teq+6,teq/2).rotate(self.rotation)
        arr.append(vShip[0]+self.center_x)
        arr.append(vShip[1]+self.center_y)
        #right edge
        vShip = Vector(-teq+6,-teq/2).rotate(self.rotation)
        arr.append(vShip[0]+self.center_x)
        arr.append(vShip[1]+self.center_y)
        return arr
        

    def get_ship_shape_pos(self):
        #initial pos 0 degree is ship toward right !
        #nose
        teq = self.height/2
        arr = []
        vShip = Vector(teq,0).rotate(self.rotation)
        arr.append(vShip[0]+self.center_x)
        arr.append(vShip[1]+self.center_y)
        #left edge
        vShip = Vector(-teq,teq).rotate(self.rotation)
        arr.append(vShip[0]+self.center_x)
        arr.append(vShip[1]+self.center_y)
        #right edge
        vShip = Vector(-teq,-teq).rotate(self.rotation)
        arr.append(vShip[0]+self.center_x)
        arr.append(vShip[1]+self.center_y)
        self.line_shape = arr
        
    def get_nose_pos(self):
        vShip = Vector(self.width/2,0).rotate(self.rotation)
        #must use fixed point self.center because self.pos moves with rotation
        return vShip.x+self.center_x,vShip.y + self.center_y

    
    def poll_firing(self,dt):
        if JOYSTICK.key_value("spacebar") or self.triggered:
            self.triggered = False
            self.fire()
        
    def fire(self):
        #Rate of fire is set with a timer
        if len(self.bullets)> self.max_bullet :
            return
        nose = self.get_nose_pos()

        x = nose[0]
        y = nose[1]
        
        # shoot direction
        velocity = Vector(1 ,0).rotate(self.rotation) * 3 + self.velocity
        
        ttl=time.time()
        self.bullets.append((x,y,velocity,ttl))
        
        self.vbullets.append(x)
        self.vbullets.append(y)
        SoundSys.play('fire')
    def rotate_ship(self,deg):

        self.rotation = loop_between(self.rotation + deg, 0,360)
        idx = int(self.rotation/10)
        self.sprite_texture = self.textures['%i' % (idx*10)]


    def thrust_ship(self):
        # angle rotation et angle de la poussée
        #print self.rotation


        #....................................................
        # normalize de trop
        # 0.25 ?
        # +1.05 de plus ?
        # parent.move rajoute encore une fois le vecteur velocity
        #....................................................
        orientation_vector = Vector(1,0).rotate(self.rotation) /10 #soit 0.10 de longueur
        #print "orientation vector : %s" % orientation_vector
        # angle de déplacement
        moving_angle = Vector(self.velocity).angle((100,0))

        speed = Vector(self.velocity).length()
        #print "speed %s" % speed
        

        #apply the thrust
        thrust = Vector(self.velocity) #* 1.05
        #apply the angle of thrust
        thrust = Vector(thrust) + orientation_vector

        if Vector(thrust).length()>self.max_speed:
            thrust = self.max_speed * Vector(thrust).normalize()

        speed = Vector(thrust).length()
        
        #self.velocity = Vector(thrust) + orientation_vector
        self.velocity = thrust

    def move(self,dt):
        if self.b_poll_fire == 0:
           self.poll_firing(dt)
        self.b_poll_fire = loop_between(self.b_poll_fire+1,0,14)         #poll fire each 1/30 second

        # remove keyboard for android
        if JOYSTICK.key_value("up"):
            #display thrust
            
            self.thrust_ship()
        
                    
        if JOYSTICK.key_value("left"):
            self.rotate_ship(5)
        if JOYSTICK.key_value("right"):
            self.rotate_ship(-5)

        if JOYSTICK.key_value("spacebar"):
            self.triggered = True

        super(Ship,self).move(dt)
        
        if JOYSTICK.key_value("up"):    
            self.thrust_triangle = self.get_thrust_shape()  # here to fit moving ship position
        else:
            self.thrust_triangle = (1,1,1,1,1,1)
            
        self.get_ship_shape_pos()
        

    def update_bullet(self):
        
        # bullets movement        
        if len(self.bullets) == 0 :
            return
        ttl_now = time.time()
        arr = []
        new_bullet =[]
        for bullet in self.bullets:
            x = bullet[0]
            y = bullet[1]
            v = bullet[2]
            ttl = bullet[3]
            new_pos = Vector(v) + (x,y)

            if (ttl_now - ttl ) < 2:    #fire ttl is max 2 seconds
                new_pos = cycling_pos(new_pos[0],new_pos[1])
                arr.append( new_pos[0])
                arr.append( new_pos[1])
                new_bullet.append((new_pos[0],new_pos[1],v,ttl))
        
        self.bullets = new_bullet    
        self.vbullets = arr
        
        
    def detect_collision(self,center_pos,size,life,velocity):
        #based on first approx with circle and then with shape
        min_dist = size[0]/2 + self.width/2

        if Ground.lock_game:
            return
        if Vector(self.center).distance(center_pos)<min_dist:
            if life == 1:
                Ground.lock_game = True
                Clock.unschedule(self.poll_firing)
                self.explode()
            else:
                self.velocity = Vector(self.velocity)*(-1)+velocity                #bounce back
            return True
            
        
        

class Ground(Widget):
    smallest_fragment = pow(2,SCALE)*8
    explosion_color = ListProperty((0,0,0))
    explosion = ListProperty(None)
    score = StringProperty('')
    int_life = 5
    life = StringProperty('')
    lock_game = False
    i_score = 0

    level = 0
    asteroids = []
    bullets= ListProperty(None)
    nose = ListProperty(None)
    dt=0

    def continue_game(self,dt):
        self.ship.init_ship()
        Ground.lock_game = False
    
    def __init__(self, **kwargs):
        super(Ground, self).__init__(**kwargs) #constructeur du parent
        
        self.ship = Ship(pos=(Window.width/2,Window.height/2),velocity=(0,0))
        self.new_level()
        self.update_label()
        self.add_widget(self.ship) 
        Clock.schedule_interval(self.run, 1/60) # 0 : wait for next frame
        

    def fragmentation(self,asteroid):
        SoundSys.play('explosion')
        
        if asteroid.width == self.smallest_fragment:        #Minimum size to fragment an asteroid, remove completly
            self.remove_widget(asteroid)        
            return
        
        asteroid.size = (asteroid.width/2,asteroid.height/2)        #keep this one and resize it
        self.updated_asteroids.append(asteroid)                
        for v in [Vector(asteroid.velocity).rotate(-30),Vector(asteroid.velocity).rotate(30)]:
            ast = Asteroid(pos = asteroid.center, velocity = v, size = asteroid.size, level = self.level)
            self.updated_asteroids.append(ast)
            self.add_widget(ast)

    def run(self,dt):

        #detect bullet impact
        self.updated_asteroids = []
        for asteroid in self.asteroids:
            idx = 0
            noboom = True
            for bullet in self.ship.bullets:

                distance = Vector(asteroid.center).distance((bullet[0], bullet[1]))

                if  distance < asteroid.width/2:
                    self.i_score += asteroid.width        
                    self.fragmentation(asteroid)        #deal with obj reuse or delete                        
                    noboom=False
                    #remove bullet                    
                    del self.ship.vbullets[idx]
                    self.ship.bullets.remove(bullet)  # array.remove(elt_value) not index
                    break
                idx += 1 # ???
            if noboom:
                self.updated_asteroids.append(asteroid)

        self.asteroids = self.updated_asteroids
        self.explosion = self.ship.explosion   
        
        if len(self.ship.explosion)>0 :
            self.explosion_color = Color_rotation.get_color() 
        else:
            if Ground.lock_game == False:
                self.ship.move(dt)
                


        self.updated_asteroids = []

        for asteroid in self.asteroids:
            asteroid.move(dt)
            if Ground.lock_game == False:
                res = self.ship.detect_collision(asteroid.center,asteroid.size,self.int_life,asteroid.velocity)
                if res == True:

                    self.fragmentation(asteroid)
                    self.int_life -=1

                    if self.int_life == 0: 
                        self.ship.sprite_texture = self.ship.textures['fragment']
                        #Clock.schedule_once(self.continue_game,5) # deprecated bouncing  and continue game

                        btn_new_game = Button(text = 'New game')
                        self.popup = Popup(title='Game Over', content=btn_new_game,
                        auto_dismiss=False, size_hint = (.5,.5))
                        self.popup.open()
                        btn_new_game.bind(on_press=self.new_game)
                else:
                   self.updated_asteroids.append(asteroid)
            else:
                self.updated_asteroids.append(asteroid)
                #self.updated_asteroids = self.asteroids
        self.ship.update_bullet()                
        self.bullets = self.ship.vbullets  #???
        self.asteroids = self.updated_asteroids

        if len(self.asteroids) == 0:
            self.level += 1
            self.new_level()
        self.update_label()

    def update_label(self):
        self.score = "Score %i" % self.i_score #Clock.get_rfps() # % Clock.frametime  # (Clock.get_rfps()-60) #,)Clock.get_fps()
        self.life =  "Shield %i" % self.int_life
        
    def new_game(self,btn_instance):
        while len(self.asteroids)>0: 
            ast = self.asteroids[0]
            del self.asteroids[0]
            self.remove_widget(ast)

        self.popup.dismiss()
        
        self.int_life = Ground.int_life
        self.level = -1
        self.i_score = 0
        self.update_label()
        self.continue_game(0)

    def remove_from_canvas(self):
        self.canvas.clear()

    def new_level(self):
        self.asteroids.append(Asteroid(pos=(Window.width*.25,Window.height),velocity=(1,-1),size=Vector(SPRITE_SIZE)*2,level = self.level))
        self.asteroids.append(Asteroid(pos=(Window.width*.75,Window.height),velocity=(1,-1),size=Vector(SPRITE_SIZE)*2,level = self.level))
        for asteroid in self.asteroids:
            self.add_widget(asteroid)
    def on_touch_down(self,touch):
        JOYSTICK._on_touch_down(touch)
        return True
    def on_touch_up(self,touch):
        key = JOYSTICK._on_touch_up(touch)
        if key =="spacebar" : self.ship.fire()
        if key == 'up': self.ship.thrust_ship()
        if key == 'left': self.ship.rotate_ship(10)
        if key == 'right': self.ship.rotate_ship(-10)
        return True

    def on_touch_move(selt,touch):
        JOYSTICK._on_touch_move(touch)
        return True
class MyApp(App):
    def build(self):
        return Ground()

                
if __name__ in ( '__main__','__android__'): # au lieu de == '__main__'  nécessite pour fonctionner avec le kivy launcher !!!
    MyApp().run()
