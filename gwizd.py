from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy_garden.mapview import MapView
import time
from kivy.uix.screenmanager import ScreenManager, Screen
import requests
import base64
from PIL import Image
from io import BytesIO
import json

# import cv2

# from plyer import gps


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
        mapview = MapView(zoom=6, lat=51.91, lon=19.08)
        # layout = RelativeLayout()
        self.add_widget(mapview)
        self.add_widget(main_buttons)


class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super(ReportScreen, self).__init__(**kwargs)


class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)

    def sendImage(self, img: Image.Image):
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

    def capture(self):
        """
        Function to capture the images and give them the names
        according to their captured time and date.
        """
        camera = self.ids["camera"]
        timestr = time.strftime("%Y%m%d_%H%M%S")
        # camera.export_to_png("IMG_{}.png".format(timestr))
        size=camera.texture.size
        frame=camera.texture.pixels
        image = Image.frombytes(mode='RGBA', size=size,data=frame)
        print("Captured")
        self.sendImage(image)
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
    def photo_upload(self):
        pass


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
