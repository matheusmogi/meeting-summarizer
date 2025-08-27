import pystray
from pystray import MenuItem as menuItem
from PIL import Image, ImageDraw


def create_icon_image(recording=False):
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    if recording:
        draw.ellipse([8, 8, 56, 56], fill=(220, 20, 20, 255), outline=(255, 255, 255, 255), width=3)
        draw.ellipse([26, 26, 38, 38], fill=(255, 255, 255, 255))
    else:
        draw.ellipse([8, 8, 56, 56], fill=(20, 100, 220, 255), outline=(255, 255, 255, 255), width=3)
        draw.rectangle([28, 16, 36, 40], fill=(255, 255, 255, 255))
        draw.ellipse([24, 12, 40, 28], fill=(255, 255, 255, 255))
        draw.rectangle([30, 40, 34, 50], fill=(255, 255, 255, 255))
        draw.rectangle([24, 46, 40, 52], fill=(255, 255, 255, 255))
    return image


class TrayIcon:
    def __init__(self, recorder, on_start, on_stop, on_test, on_open, on_exit):
        self.recorder = recorder
        self.icon = None
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_test = on_test
        self.on_open = on_open
        self.on_exit = on_exit
        self.create_icon()

    def create_icon(self):
        image = create_icon_image(False)
        menu = pystray.Menu(
            menuItem('Meeting Recorder', lambda icon, item: None, enabled=False),
            pystray.Menu.SEPARATOR,
            menuItem('Start Recording (Ctrl+Shift+R)', self.on_start, enabled=lambda item: not self.recorder.recording),
            menuItem('Stop Recording', self.on_stop, enabled=lambda item: self.recorder.recording),
            pystray.Menu.SEPARATOR,
            menuItem('Test Audio Devices', self.on_test),
            menuItem('Open Audio Folder', self.on_open),
            pystray.Menu.SEPARATOR,
            menuItem('Exit', self.on_exit)
        )
        self.icon = pystray.Icon("meeting_recorder", image, "Meeting Recorder", menu)

    def update_icon_status(self, recording=False):
        if self.icon:
            self.icon.icon = create_icon_image(recording)
            self.icon.update_menu()

    def run(self):
        self.icon.run()

    def stop(self):
        self.icon.stop()

    def notify(self, title, message):
        if self.icon:
            self.icon.notify(title, message)

