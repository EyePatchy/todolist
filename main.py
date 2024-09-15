import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.animation import Animation
from kivy.core.text import LabelBase
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.core.window import Window

Window.clearcolor = (0.97, 0.97, 0.97, 1)

# File to store tasks for persistence
TASKS_FILE = "tasks.json"

class HoverButton(Button):
    def __init__(self, **kwargs):
        super(HoverButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (1, 0.4, 0.4, 1)

    def on_enter(self):
        anim = Animation(background_color=(1, 0.2, 0.2, 1), duration=0.2)
        anim.start(self)

    def on_leave(self):
        anim = Animation(background_color=(1, 0.4, 0.4, 1), duration=0.2)
        anim.start(self)

class TaskRow(BoxLayout):
    def __init__(self, task_text, remove_task_callback, move_up_callback, move_down_callback, **kwargs):
        super(TaskRow, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 60
        self.spacing = 10
        self.padding = [10, 10]

        task_text = " ".join(task_text.split())
        self.task_label = Label(text=task_text, size_hint_x=0.6, font_size=18, color=(0.1, 0.1, 0.1, 1))

        self.move_up_button = Button(text="Up", size_hint_x=0.1, on_press=lambda x: move_up_callback(self))
        self.move_down_button = Button(text="Down", size_hint_x=0.1, on_press=lambda x: move_down_callback(self))
        self.delete_button = HoverButton(text="Delete", size_hint_x=0.2, font_size=16, background_color=(1, 0.4, 0.4, 1),
                                         color=(1, 1, 1, 1), on_press=lambda x: remove_task_callback(self))

        self.add_widget(self.task_label)
        self.add_widget(self.move_up_button)
        self.add_widget(self.move_down_button)
        self.add_widget(self.delete_button)

        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

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

        self.load_tasks()

    def add_task(self, instance):
        task_text = self.task_input.text.strip()
        if not task_text:
            return

        task_row = TaskRow(task_text, self.remove_task, self.move_task_up, self.move_task_down)
        self.task_layout.add_widget(task_row)

        anim = Animation(opacity=1, duration=0.3)
        task_row.opacity = 0
        anim.start(task_row)

        self.task_input.text = ""
        self.save_tasks()

    def remove_task(self, task_row):
        anim = Animation(opacity=0, duration=0.3)
        anim.bind(on_complete=lambda *args: self._complete_task_removal(task_row))
        anim.start(task_row)

    def _complete_task_removal(self, task_row):
        self.task_layout.remove_widget(task_row)
        self.save_tasks()

    def move_task_up(self, task_row):
        index = self.task_layout.children.index(task_row)
        if index < len(self.task_layout.children) - 1:
            self.task_layout.remove_widget(task_row)
            self.task_layout.add_widget(task_row, index + 1)
        self.save_tasks()

    def move_task_down(self, task_row):
        index = self.task_layout.children.index(task_row)
        if index > 0:
            self.task_layout.remove_widget(task_row)
            self.task_layout.add_widget(task_row, index - 1)
        self.save_tasks()

    def save_tasks(self):
        tasks = [task_row.task_label.text for task_row in reversed(self.task_layout.children)]
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f)

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as f:
                tasks = json.load(f)
            for task in tasks:
                task_row = TaskRow(task, self.remove_task, self.move_task_up, self.move_task_down)
                self.task_layout.add_widget(task_row)

class ToDoApp(App):
    def build(self):
        return TaskManager()

if __name__ == "__main__":
    ToDoApp().run()
