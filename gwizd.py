from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy_garden.mapview import MapView
import time
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
import requests
import base64
from PIL import Image
from io import BytesIO
import json
from kivy.uix.popup import Popup
import os
# import cv2

# from plyer import gps

def send_image(img: Image.Image):
    buffer = BytesIO()
    img.save(buffer, format="png")
    im_base = base64.b64encode(buffer.getvalue()).decode("utf8")
    payload = json.dumps(
        {"Uploaded file": im_base, "latitude": "50.0647", "longitude": "19.9450"}
    )
    headers = {"Content-type": "application/json", "Accept": "text/plain"}

    r = requests.post(
        "http://localhost:8080/init-report",
        data=payload,
        headers=headers,
    )
    if r.status_code == 200:
        image_id = int(r.text)
        print(f"Image sent, id: {image_id}")
        return image_id
    return None
            
def get_animal(image_id):
    predictions_response = requests.get(
            "http://localhost:8080/get-images"
        )
    animals_response = requests.get(
        "http://localhost:8080/get-animals",
    )
    predictions = json.loads(predictions_response.content.decode('utf-8'))
    animals = json.loads(animals_response.content.decode('utf-8'))
    return animals[str(predictions[str(image_id)]['animal_id'])]

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    
class MainButtons(AnchorLayout):
    def __init__(self, **kwargs):
        super(MainButtons, self).__init__(**kwargs)
        self.anchor_x = "right"
        self.anchor_y = "bottom"

    def add_click(self):
        print("Clicked add animal")
        self.parent.manager.current = "Report Screen"

    def gps_click(self):
        print("Localizing")
        krakow_gps = (19.5611, 50.0341)
        self.parent.children[1].lon = krakow_gps[0]
        self.parent.children[1].lat = krakow_gps[1]
        self.parent.children[1].zoom = 10

    def alerts_click(self):
        print("Showing alerts")


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        main_buttons = MainButtons()
        mapview = MapView(zoom=6, lat=51.91, lon=19.08)
        self.add_widget(mapview)
        self.add_widget(main_buttons)


class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super(ReportScreen, self).__init__(**kwargs)


class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)


    def capture(self):
        """
        Function to capture the images and give them the names
        according to their captured time and date.
        """
        camera = self.ids["camera"]
        timestr = time.strftime("%Y%m%d_%H%M%S")
        size=camera.texture.size
        frame=camera.texture.pixels
        image = Image.frombytes(mode='RGBA', size=size,data=frame).convert('RGB')
        # image.save("IMG_{}.png".format(timestr))
        print("Captured")
        image_id = send_image(image)
        seen_animal = get_animal(image_id)
        
        print(f"Recognized: {seen_animal['name']}, {seen_animal['description']}, Dangerous: {'yes' if seen_animal['dangerous'] else 'no'}")
    
        self.manager.current = "Main Screen"


class ReportWildScreen(Screen):
    # Receive animal classification
    # Show editable interface - (Make new photo, animal type - possibility to correct, SEND)
    pass


class LostAnimalScreen(Screen):
    def __init__(self, **kwargs):
        super(LostAnimalScreen, self).__init__(**kwargs)

    # Upload photo -> Wait for response
    # If not uploaded -> Type in animal type by user
    # Show prediction, text fields: (Animal name, last seen, additional info)
    def dismiss_popup(self):
        self._popup.dismiss()
    
    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as f:
            image = Image.open(f.name)
        image_id = send_image(image)
        seen_animal = get_animal(image_id)
        self.ids['animal_type'].text = seen_animal['name']
        self.dismiss_popup()
        
    def photo_upload(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()


class Gwizd(App):
    def on_start(self):
        super().on_start()
        # gps.configure(on_location=self.on_gps_location)
        # gps.start()

    # def on_gps_location(self, **kwargs):
    #     print(kwargs["lat"])
    #     print(kwargs["lon"])

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="Main Screen"))
        sm.add_widget(ReportScreen(name="Report Screen"))
        sm.add_widget(CameraScreen(name="Camera Screen"))
        sm.add_widget(LostAnimalScreen(name="Lost Animal Screen"))
        return sm


if __name__ == "__main__":
    Gwizd().run()
