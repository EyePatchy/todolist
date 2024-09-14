from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.popup import Popup
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior

Window.clearcolor = (0.97, 0.97, 0.97, 1)

class TaskRow(BoxLayout):
    def __init__(self, task_text, remove_task_callback, **kwargs):
        super(TaskRow, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 60
        self.spacing = 10
        self.padding = [10, 10]
        
        task_text = " ".join(task_text.split())
        self.task_label = Label(text=task_text, size_hint_x=0.8, font_size=18, color=(0.1, 0.1, 0.1, 1))

        self.delete_button = Button(text="Delete", size_hint_x=0.2, font_size=16, background_normal='', background_color=(1, 0.4, 0.4, 1),
                                    color=(1, 1, 1, 1), on_press=lambda x: remove_task_callback(self))
        self.add_widget(self.task_label)
        self.add_widget(self.delete_button)

        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

        self.bind(pos=self.update_rect, size=self.update_rect)

        self.delete_button.bind(on_enter=self.on_hover, on_leave=self.on_leave)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_hover(self, instance):
        anim = Animation(background_color=(1, 0.2, 0.2, 1), duration=0.2)
        anim.start(instance)

    def on_leave(self, instance):
        anim = Animation(background_color=(1, 0.4, 0.4, 1), duration=0.2)
        anim.start(instance)



class TaskManager(BoxLayout):
    def __init__(self, **kwargs):
        super(TaskManager, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = [20, 10, 20, 10]
        self.deleted_task = None

        self.add_widget(Label(text='To-Do List', font_size=36, color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=70))

        self.scroll_view = ScrollView(size_hint=(1, 0.8))
        self.task_layout = GridLayout(cols=1, spacing=15, size_hint_y=None)
        self.task_layout.bind(minimum_height=self.task_layout.setter('height'))
        self.scroll_view.add_widget(self.task_layout)

        self.add_widget(self.scroll_view)

        self.input_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.task_input = TextInput(hint_text="Add a task", multiline=False, size_hint=(0.8, 1),
                                    background_color=(1, 1, 1, 1), foreground_color=(0.2, 0.2, 0.2, 1),
                                    padding=[10, 10], font_size=16)
        self.add_button = Button(text="Add", size_hint=(0.2, 1), background_color=(0, 0.6, 1, 1), color=(1, 1, 1, 1),
                                 on_press=self.add_task)
        self.input_box.add_widget(self.task_input)
        self.input_box.add_widget(self.add_button)
        self.add_widget(self.input_box)

        self.task_input.bind(on_text_validate=self.add_task)

        self.add_button.bind(on_enter=self.on_add_hover, on_leave=self.on_add_leave)

    def add_task(self, instance):
        task_text = self.task_input.text.strip()
        if not task_text:
            return

        task_row = TaskRow(task_text, self.remove_task)
        self.task_layout.add_widget(task_row)

        anim = Animation(opacity=1, duration=0.3)
        task_row.opacity = 0
        anim.start(task_row)

        self.task_input.text = ""

    def remove_task(self, task_row):
        self.deleted_task = task_row

        anim = Animation(opacity=0, duration=0.3)
        anim.bind(on_complete=lambda *args: self.task_layout.remove_widget(task_row))
        anim.start(task_row)


    def undo_task(self, instance):
        if self.deleted_task:
            self.task_layout.add_widget(self.deleted_task)
            self.deleted_task.opacity = 0
            Animation(opacity=1, duration=0.3).start(self.deleted_task)

    def on_add_hover(self, instance):
        anim = Animation(background_color=(0, 0.8, 1, 1), duration=0.2)
        anim.start(instance)

    def on_add_leave(self, instance):
        anim = Animation(background_color=(0, 0.6, 1, 1), duration=0.2)
        anim.start(instance)


class ToDoApp(App):
    def build(self):
        return TaskManager()


if __name__ == "__main__":
    ToDoApp().run()
