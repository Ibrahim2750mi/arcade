import arcade
from arcade.gui.constructs import UIFIleChooser

class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 700, "Example", resizable=True)

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        
        self.file_dialog = UIFIleChooser(size_hint=(6/8, 4/7), callback=self.callback)

        self.manager.add(self.file_dialog)

        self.one_time = 0

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_mouse_press(self, x, y, *args, **kwargs,):
        print(x, y)

    def callback(self, path):
        print(path)


if __name__ == '__main__':
    window = MyWindow()
    arcade.run()