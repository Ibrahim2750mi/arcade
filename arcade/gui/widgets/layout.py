from typing import Iterable, TypeVar

from arcade.gui.property import bind
from arcade.gui.widgets import UIWidget, UILayout, Rect

W = TypeVar("W", bound="UIWidget")


class UIAnchorLayout(UILayout):
    """
    Places children based on anchor values.
    Defaults to `size_hint = (1, 1)`.

    Supports `size_hint_min` of direct children.

    Allowed keyword options for `UIAnchorLayout.add()`
    - anchor_x: str = None - uses `self.default_anchor_x` as default
    - align_x: float = 0
    - anchor_y: str = None - uses `self.default_anchor_y` as default
    - align_y: float = 0

    """
    default_anchor_x = "center"
    default_anchor_y = "center"

    def __init__(self,
                 x: float = 0,
                 y: float = 0,
                 width: float = 100,
                 height: float = 100,
                 children: Iterable["UIWidget"] = tuple(),
                 size_hint=(1, 1),
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs):
        super().__init__(x, y, width, height, children, size_hint, size_hint_min, size_hint_max, style, **kwargs)

    def do_layout(self):
        for child, data in self._children:
            self._place_child(child, **data)

    def add(
            self,
            child: W,
            *,
            anchor_x: str = None,
            align_x: float = 0,
            anchor_y: str = None,
            align_y: float = 0,
            **kwargs
    ) -> W:
        return super(UIAnchorLayout, self).add(
            child=child,
            anchor_x=anchor_x,
            align_x=align_x,
            anchor_y=anchor_y,
            align_y=align_y,
            **kwargs
        )

    def _place_child(
            self,
            child: UIWidget,
            anchor_x: str = None,
            align_x: float = 0,
            anchor_y: str = None,
            align_y: float = 0,
    ):
        anchor_x = anchor_x or self.default_anchor_x
        anchor_y = anchor_y or self.default_anchor_y

        # Handle size_hint_min (e.g. UIBoxLayout)
        new_child_rect = child.rect

        if child.size_hint_min:
            new_child_rect = new_child_rect.min_size(*child.size_hint_min)

        # calculate wanted position
        content_rect = self.content_rect

        anchor_x = "center_x" if anchor_x == "center" else anchor_x
        child_anchor_x_value = getattr(new_child_rect, anchor_x)
        own_anchor_x_value = getattr(content_rect, anchor_x)
        diff_x = own_anchor_x_value + align_x - child_anchor_x_value

        anchor_y = "center_y" if anchor_y == "center" else anchor_y
        child_anchor_y_value = getattr(new_child_rect, anchor_y)
        own_anchor_y_value = getattr(content_rect, anchor_y)
        diff_y = own_anchor_y_value + align_y - child_anchor_y_value

        # check if changes are required
        if diff_x or diff_y or child.rect != new_child_rect:
            child.rect = new_child_rect.move(diff_x, diff_y)


class UIBoxLayout(UILayout):
    """
    Places widgets next to each other.
    Depending on the vertical attribute, the Widgets are placed top to bottom or left to right.

    Hint: UIBoxLayout does not adjust its own size, if children are added. This requires a UIManager or UIAnchorLayout as parent.
    Use `self.fit_content()` to resize, bottom-left is used as anchor point.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param vertical: Layout children vertical (True) or horizontal (False)
    :param align: Align children in orthogonal direction (x: left, center, right / y: top, center, bottom)
    :param children: Initial children, more can be added
    :param size_hint: A hint for :class:`UILayout`, if this :class:`UIWidget` would like to grow
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param space_between: Space between the children
    """

    def __init__(
            self,
            x=0,
            y=0,
            vertical=True,
            align="center",
            children: Iterable[UIWidget] = tuple(),
            size_hint=None,
            size_hint_min=None,
            size_hint_max=None,
            space_between=0,
            style=None,
            **kwargs
    ):
        self.align = align
        self.vertical = vertical
        self._space_between = space_between
        super().__init__(
            x=x,
            y=y,
            width=0,
            height=0,
            children=children,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            style=style,
            **kwargs
        )

        bind(self, "_children", self._update_size_hints)

        # initially update size hints
        self._update_size_hints()

    def _update_size_hints(self):
        required_space_between = max(0, len(self.children) - 1) * self._space_between

        if len(self.children) == 0:
            width = 0
            height = 0
        elif self.vertical:
            width = max(child.width for child in self.children)
            height_of_children = sum(child.height for child in self.children)
            height = height_of_children + required_space_between
        else:
            width_of_children = sum(child.width for child in self.children)
            width = width_of_children + required_space_between
            height = max(child.height for child in self.children)

        base_width = self.padding_left + self.padding_right + 2 * self.border_width
        base_height = self.padding_top + self.padding_bottom + 2 * self.border_width
        self.size_hint_min = base_width + width, base_height + height

    def fit_content(self):
        """
        Resize to fit content, using `self.size_hint_min`
        """
        self.rect = self.rect.resize(*self.size_hint_min)

    def do_layout(self):
        start_y = self.content_rect.top
        start_x = self.content_rect.left

        if not self.children:
            return

        if self.vertical:
            for child in self.children:
                if self.align == "left":
                    new_rect = child.rect.align_left(start_x)
                elif self.align == "right":
                    new_rect = child.rect.align_right(start_x + self.content_width)
                else:
                    center_x = start_x + self.content_width // 2
                    new_rect = child.rect.align_center_x(center_x)

                new_rect = new_rect.align_top(start_y)
                if new_rect != child.rect:
                    child.rect = new_rect
                start_y -= child.height
                start_y -= self._space_between
        else:
            center_y = start_y - self.content_height // 2

            for child in self.children:
                if self.align == "top":
                    new_rect = child.rect.align_top(start_y)
                elif self.align == "bottom":
                    new_rect = child.rect.align_bottom(start_y - self.content_height)
                else:
                    new_rect = child.rect.align_center_y(center_y)

                new_rect = new_rect.align_left(start_x)
                if new_rect != child.rect:
                    child.rect = new_rect
                start_x += child.width
                start_x += self._space_between

class UIGridLayout(UILayout):
    """
    Places widget in a grid layout.
    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param float align_horizontal: Align children in orthogonal direction (x: left, center, right)
    :param float align_vertical: Align children in orthogonal direction (y: top, center, bottom)
    :param Iterable[UIWidget] children: Initial children, more can be added
    :param size_hint: A hint for :class:`UILayout`, if this :class:`UIWidget` would like to grow
    :param size_hint_min: Min width and height in pixel
    :param size_hint_max: Max width and height in pixel
    :param horizontal_spacing: Space between columns
    :param vertical_spacing: Space between rows
    :param int column_count: Number of columns in the grid, can be changed
    :param int row_count: Number of rows in the grid, can be changed
    """
    def __init__(self, x=0,
                 y=0,
                 align_horizontal="center",
                 align_vertical="center",
                 children: Iterable[UIWidget] = tuple(),
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 horizontal_spacing: int = 0,
                 vertical_spacing: int = 0,
                 column_count: int = 1,
                 row_count: int = 1, style=None, **kwargs):

        super(UIGridLayout, self).__init__(x=x, y=y, width=0, height=0, children=children,
                                           size_hint=size_hint, size_hint_min=size_hint_min,
                                           size_hint_max=size_hint_max, style=style, **kwargs)

        self._horizontal_spacing = horizontal_spacing
        self._vertical_spacing = vertical_spacing

        self.column_count = column_count
        self.row_count = row_count

        self.align_horizontal = align_horizontal
        self.align_vertical = align_vertical

        bind(self, "_children", self._update_size_hints)

        # initially update size hints
        self._update_size_hints()

    def _update_size_hints(self):
        max_width_per_column = [0] * self.column_count
        max_height_per_row = [0] * self.row_count

        child_sorted_row_wise = [[None for _ in range(self.column_count)] for _ in range(self.row_count)]

        for child, data in self._children:
            col_num = data["col_num"]
            row_num = data["row_num"]

            if child.width > max_width_per_column[col_num]:
                max_width_per_column[col_num] = child.width

            if child.height > max_height_per_row[row_num]:
                max_height_per_row[row_num] = child.height

            child_sorted_row_wise[row_num][col_num] = child

        base_width = self.padding_left + self.padding_right + 2 * self.border_width
        base_height = self.padding_top + self.padding_bottom + 2 * self.border_width
        content_height = sum(max_height_per_row) + (self.row_count - 1) * self._vertical_spacing
        content_width = sum(max_width_per_column) + (self.column_count - 1) * self._horizontal_spacing

        self.size_hint_min = (base_width + content_width, base_height + content_height)

    def add(self,
            child: W,
            col_num: int = 0,
            row_num: int = 0,
            **kwargs) -> W:
        """
        Adds widgets in the grid.

        :param UIWidget child: The widget which is to be added in the grid
        :param int col_num: The column number in which the widget is to be added (first column is numbered 0; left)
        :param int row_num: The row number in which the widget is to be added (first row is numbered 0; top)
        """
        return super().add(child, col_num=col_num, row_num=row_num, **kwargs)

    def do_layout(self):
        initial_left_x = self.content_rect.left
        start_y = self.content_rect.top

        if not self.children:
            return

        max_width_per_column = [0] * self.column_count
        max_height_per_row = [0] * self.row_count

        child_sorted_row_wise = [[None for _ in range(self.column_count)] for _ in range(self.row_count)]

        for child, data in self._children:
            col_num = data["col_num"]
            row_num = data["row_num"]

            if child.width > max_width_per_column[col_num]:
                max_width_per_column[col_num] = child.width

            if child.height > max_height_per_row[row_num]:
                max_height_per_row[row_num] = child.height

            child_sorted_row_wise[row_num][col_num] = child

        # row wise rendering children
        for row_num, row in enumerate(child_sorted_row_wise):
            max_height = max_height_per_row[row_num] + self._vertical_spacing
            center_y = start_y - (max_height // 2)

            start_x = initial_left_x

            for col_num, child in enumerate(row):
                max_width = max_width_per_column[col_num] + self._horizontal_spacing
                center_x = start_x + max_width // 2

                start_x += max_width

                if child is not None:
                    if self.align_vertical == "top":
                        new_rect = child.rect.align_top(start_y)
                    elif self.align_vertical == "bottom":
                        new_rect = child.rect.align_bottom(start_y - max_height)
                    else:
                        new_rect = child.rect.align_center_y(center_y)

                    if self.align_horizontal == "left":
                        new_rect = new_rect.align_left(start_x - max_width)
                    elif self.align_horizontal == "right":
                        new_rect = new_rect.align_right(start_x)
                    else:
                        new_rect = new_rect.align_center_x(center_x)

                    if new_rect != child.rect:
                        child.rect = new_rect

            start_y -= max_height
