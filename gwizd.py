from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Ellipse, Color
from kivy.clock import Clock
from kivy_garden.mapview import MapView, MapMarkerPopup
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

def sendImage(img: Image.Image):
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
        # self.sendImage()
        self.parent.manager.current = "Report Screen"

    def gps_click(self):
        print("Localizing")

    def alerts_click(self):
        print("Showing alerts")


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        main_buttons = MainButtons()
        self.mapview = MapView(zoom=10, lat=50.00, lon=19.90)
        self.add_widget(self.mapview)
        self.add_widget(main_buttons)
        self.points = []
        self.points_ts = []
        self.circles = []
        self.update_reports()
        Clock.schedule_interval(self.update_circles, 1/30)

    def update_reports(self):
        r = requests.get("http://localhost:8080/get-reports")
        if r.status_code == 200:
            timestamp_now = time.time()
            json_dict = r.json()
            for value in json_dict.values():
                point = MapMarkerPopup(lat=value["latitude"], lon=value["longitude"])
                point.anchor_x
                point.add_widget(Label(text=str(value["animal_id"]), color=(0, 0, 0)))
                self.mapview.add_marker(point)
                self.points.append(point)
                timestamp = value["timestamp"]
                self.points_ts.append(timestamp)
                with self.canvas:
                    ts_diff = (timestamp_now - timestamp)
                    radius = max(3, ts_diff / 60)
                    alpha = max(0, 2*60*60 - ts_diff) / (2*60*60)
                    Color(1, 0, 0, alpha)
                    circle = Ellipse(pos=point.pos, size=(radius, radius))
                    self.circles.append(circle)

    def update_circles(self, *args):
        timestamp_now = time.time()
        with self.canvas:
                for point, timestamp, circle in zip(self.points, self.points_ts, self.circles):
                    ts_diff = (timestamp_now - timestamp)
                    radius = max(3, ts_diff / 60)
                    circle.size = (radius, radius)
                    circle.pos = point.pos

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
        sendImage(image)
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
        sendImage(image)
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
