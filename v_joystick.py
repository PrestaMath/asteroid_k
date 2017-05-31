# -*- coding: utf8 -*-
from kivy.core.window import Window


class game_input(object):
    # desactiver l'un ou l'autre clavier ou keyboard suivant plateforme
    screen_btn = []
    milieu = int(Window.width/2)
    btn_name = ('up','spacebar','left','right')
    def __init__(self,b_use_keyboard,btn_size):
        self.key_dict = {}
        
        if b_use_keyboard:
                self._keyboard = Window.request_keyboard(
                    self._keyboard_closed, self)
                self._keyboard.bind(on_key_down=self._key_down)
                self._keyboard.bind(on_key_up=self._key_up)

        self.taille = btn_size

        self.screen_btn.append((0,self.taille))
        self.screen_btn.append((1*self.taille+1,2*self.taille))

        self.screen_btn.append((8*self.taille,9*self.taille))
        self.screen_btn.append((9*self.taille+1,10*self.taille))

    def key_value(self,key):
        #print self.key_dict
        if key in self.key_dict:
            if self.key_dict[key] == False:
                return 0
            else:
                return 1
        return 0
    
    def _key_down(self,keyboard, keycode, text, modifiers):
        self.key_dict[keycode[1]] = True
        #print self.key_dict
        #print "down",keycode
        
    def _key_up(self,keyboard, keycode):
        self.key_dict[keycode[1]] = False
        #print "up",keycode
        
    def _keyboard_closed(self):
        #print 'My keyboard have been closed!'
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None
    def _on_touch_down(self,touch):
        #return
        self.key_dict[self.screen_zone(touch)] = True
        #print "class touch_screen"

    def _on_touch_up(self,touch):    
        touch_btn = self.screen_zone(touch)
        self.key_dict[touch_btn] = False
        #return touch_btn
        return ''
    def _on_touch_move(self,touch):
        #return
        ''' touche droite ou gauche
        suivre main, puis touche 
        '''
        btn = self.screen_zone(touch)

        if btn == 'nop':        #must desactive btn
            
            if touch.x <= self.milieu:                #self.screen_btn[2][0] :
                self.key_dict['up'] = False
                self.key_dict['spacebar'] = False

            else:
                self.key_dict['left'] = False
                self.key_dict['right'] = False
            return



        if btn == 'left' or btn == 'right':
            self.key_dict['left'] = False
            self.key_dict['right'] = False
            self.key_dict[btn] = True
            return

        if btn == 'spacebar' or btn == 'up':
            self.key_dict['up'] = False
            self.key_dict['spacebar'] = False
            self.key_dict[btn] = True
            return
            
        
    def screen_zone(self,touch):

        #thrust - fire  - left - right 'screen button'
        if touch.y > self.taille:
            return 'nop'

        for i in range(0,4):
            if touch.x >= self.screen_btn[i][0] and touch.x<=self.screen_btn[i][1]:        
                return self.btn_name[i]
        return 'nop'


