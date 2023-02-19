import arcade.color
import arcade
import arcade.gui

from arcade.gui.widgets import UIScrollArea, UISpace
from arcade.gui.ui_manager import UIManager
from arcade.gui.widgets.layout import UIAnchorLayout

MOVEMENT_SPEED = 5


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        child = UISpace(width=100, height=100, color=arcade.color.RED)
        self.parent = UIScrollArea(children=[child], pixels_scroll=MOVEMENT_SPEED).with_border()

        self.manager = UIManager()
        self.manager.enable()

        anchor = self.manager.add(UIAnchorLayout())

        anchor.add(
            child=self.parent,
            anchor_x="center",
            anchor_y="center",
            )

        anchor.add(
            child=child,
            anchor_x="center",
            anchor_y="center",
            align_x=100,
            )

    def on_draw(self):
        self.clear()

        self.manager.draw()

    def on_update(self, delta_time):
        self.parent.on_update(delta_time)

if __name__ == "__main__":
    window = UIMockup()
    arcade.run()
