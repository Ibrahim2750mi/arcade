"""
Constructs, are prepared widget combinations, you can use for common use-cases
"""
from functools import partial
from pathlib import Path, PosixPath, WindowsPath
from typing import Callable, Union

import arcade
from arcade import load_texture
from arcade.gui.events import UIOnClickEvent
from arcade.gui.mixins import UIMouseFilterMixin
from arcade.gui.widgets.buttons import UIFlatButton, UITextureButton
from arcade.gui.widgets.layout import UIBoxLayout, UIAnchorLayout, UIGridLayout
from arcade.gui.widgets.text import UITextArea


class UIMessageBox(UIMouseFilterMixin, UIAnchorLayout):
    """
    A simple dialog box that pops up a message with buttons to close.

    :param width: Width of the message box
    :param height: Height of the message box
    :param message_text:
    :param buttons: List of strings, which are shown as buttons
    :param callback: Callback function, will receive the text of the clicked button
    """

    def __init__(
        self,
        *,
        width: float,
        height: float,
        message_text: str,
        buttons=("Ok",),
        callback=None
    ):
        super().__init__(size_hint=(1, 1))
        self._callback = callback  # type: ignore

        space = 10

        # setup frame which will act like the window
        frame = self.add(UIAnchorLayout(width=width, height=height))
        frame.with_padding(all=space)

        self._bg_tex = arcade.load_texture(
            ":resources:gui_basic_assets/window/grey_panel.png"
        )
        frame.with_background(texture=self._bg_tex)

        # Setup text
        self._text_area = UITextArea(
            text=message_text,
            width=width - space,
            height=height - space,
            text_color=arcade.color.BLACK,
        )
        frame.add(
            child=self._text_area,
            anchor_x="center",
            anchor_y="top",
        )

        # setup buttons
        button_group = UIBoxLayout(vertical=False, space_between=10)
        for button_text in buttons:
            button = UIFlatButton(text=button_text)
            button_group.add(button)
            button.on_click = self.on_ok  # type: ignore

        frame.add(
            child=button_group,
            anchor_x="right",
            anchor_y="bottom",
        )

    def on_ok(self, event):
        self.parent.remove(self)
        if self._callback is not None:
            self._callback(event.source.text)


class UIFIleChooser(UIGridLayout):
    """
    FIle chooser(dialogue).

    :param: path: 
    """
    def __init__(self, path: Union[PosixPath, WindowsPath]=Path.cwd(),
                 file_type: str=".*",
                 x: float = 0,
                 y: float = 0,
                 width: float = 600,
                 height: float = 500,
                 size_hint=(1, 1),
                 size_hint_min=None,
                 size_hint_max=None,
                 callback: Callable=None,
                 style=None, **kwargs):

        super().__init__(
                x=x,
                y=y,
                children=tuple(),
                size_hint=size_hint,
                size_hint_min=size_hint_min,
                size_hint_max=size_hint_max,
                style=style,
                column_count = 3,
                row_count = 2,
                horizontal_spacing = 0.2*600 - 100,
                vertical_spacing = 10,
                **kwargs)

        self._path = path
        self._callback = callback

        self._bg_tex = load_texture(file_name=":resources:gui_basic_assets/window/file_chooser.png")

        self.with_background(texture=self._bg_tex)

        select_button = UIFlatButton(text="SELECT", width=100)
        select_button.on_click = self._select
        self.add(select_button, 2, 0)

        # quick places
        self.quick_places = [Path.home(), ]

        self.setup()
        self.selected = False

    def _expand_dir(self, _: UIOnClickEvent, file_dir: Union[PosixPath, WindowsPath]):
        self._path = file_dir
        if file_dir.is_file():
            return
        self.clear()
        self.setup()

    def _select(self, _: UIOnClickEvent):
        if self._path.is_dir():
            return

        self.selected = True
        self.parent.remove(self)
        if self._callback is not None:
            self._callback(self._path)

    def setup(self):
        tex = load_texture(file_name=":resources:gui_basic_assets/icons/file_not_selected.png")
        for row_index, file in enumerate(self._path.iterdir()):
            if row_index >= self.row_count - 1:
                self.row_count += 1
            file_button = UITextureButton(texture=tex, width=220, height=40, text=file.name, style={"font_color": (0, 0, 0)})
            file_button.on_click = partial(self._expand_dir, file_dir=file)
            self.add(file_button, 1, row_index + 1)
    
    @property
    def path(self):
        if self.selected:
            return self._path
        return False
