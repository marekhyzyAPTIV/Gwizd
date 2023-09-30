from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy_garden.mapview import MapView
import time
from kivy.uix.screenmanager import ScreenManager, Screen

class MainButtons(AnchorLayout):
    def __init__(self, **kwargs):
        super(MainButtons, self).__init__(**kwargs)
        self.anchor_x = 'right'
        self.anchor_y = 'bottom'
        
    def add_click(self):
        print("Clicked add animal")
        self.parent.manager.current = 'Report Screen'
    
    def gps_click(self):
        print("Localizing")
    
    def alerts_click(self):
        print("Showing alerts")
        
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        main_buttons = MainButtons()
        mapview = MapView(zoom=6, lat=51.91, lon=19.08)
        #layout = RelativeLayout()
        self.add_widget(mapview)
        self.add_widget(main_buttons)
        
class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super(ReportScreen, self).__init__(**kwargs)
        

class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)
        
    def capture(self):
        '''
        Function to capture the images and give them the names
        according to their captured time and date.
        '''
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        camera.export_to_png("IMG_{}.png".format(timestr))
        print("Captured")
        self.manager.current = 'Main Screen'

class LostAnimalScreen(Screen):
    pass

class Gwizd(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='Main Screen'))
        sm.add_widget(ReportScreen(name='Report Screen'))
        sm.add_widget(CameraScreen(name='Camera Screen'))
        sm.add_widget(LostAnimalScreen(name='Lost Animal Screen'))
        return sm


if __name__ == '__main__':
    Gwizd().run()