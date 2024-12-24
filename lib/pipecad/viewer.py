import pyvista as pv
import numpy as np
from pathlib import Path
import flet as ft
import uuid
from lib.pipecad.commands import CommandHistory, AddObjectCommand, DeleteObjectCommand, DuplicateObjectCommand

class Viewer3D(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.plotter = None
        self.screenshot_path = Path("temp_screenshot.png")
        self.is_dragging = False
        self.last_x = 0
        self.last_y = 0
        self.camera_distance = 5.0
        self.azimuth = 45.0
        self.elevation = 45.0
        self.objects = {}  # id: {object_data}
        self.selected_object = None
        self.on_selection_change = None
        self.last_click_position = None
        self.command_history = CommandHistory()
        self.view_presets = {
            "正面": {"azimuth": 0, "elevation": 0},
            "上面": {"azimuth": 0, "elevation": 90},
            "右側面": {"azimuth": 90, "elevation": 0},
            "アイソメトリック": {"azimuth": 45, "elevation": 35.264},  # arctan(1/√2)
        }

    def initialize_plotter(self):
        self.plotter = pv.Plotter(off_screen=True)
        self.plotter.background_color = '#ffffff'
        self.plotter.window_size = [800, 600]
        
        # グリッドの追加
        grid = pv.Plane(i_size=10, j_size=10, i_resolution=10, j_resolution=10)
        self.plotter.add_mesh(grid, color='gray', opacity=0.5)
        
        # 座標軸の追加
        self.plotter.add_axes()
        
        self.update_camera()
        self.update_view()
        
        print("Plotter initialized:", self.plotter is not None)  # デバッグ用

    def update_camera(self):
        # 球面座標からカメラ位置を計算
        x = self.camera_distance * np.cos(np.radians(self.elevation)) * np.cos(np.radians(self.azimuth))
        y = self.camera_distance * np.cos(np.radians(self.elevation)) * np.sin(np.radians(self.azimuth))
        z = self.camera_distance * np.sin(np.radians(self.elevation))
        
        self.plotter.camera_position = [(x, y, z), (0, 0, 0), (0, 0, 1)]

    def update_view(self):
        if self.plotter is None:
            print("Plotter is not initialized")
            return
        self.plotter.screenshot(str(self.screenshot_path))
        self.update()

    def add_cube(self, position=(0, 0, 0), size=1.0):
        obj_id = str(uuid.uuid4())
        cube = pv.Cube(center=position, x_length=size, y_length=size, z_length=size)
        self.plotter.add_mesh(cube, color='blue', opacity=0.8, name=obj_id)
        
        self.objects[obj_id] = {
            "id": obj_id,
            "type": "cube",
            "name": f"Cube_{len(self.objects)}",
            "position_x": position[0],
            "position_y": position[1],
            "position_z": position[2],
            "size": size,
            "mesh": cube
        }
        
        self.update_view()
        command = AddObjectCommand(self, "cube", {
            "x": position[0], "y": position[1], "z": position[2],
            "size": size
        })
        self.command_history.execute(command)
        return command.obj_id

    def add_cylinder(self, start=(0, 0, 0), end=(0, 0, 1), radius=0.5):
        obj_id = str(uuid.uuid4())
        direction = np.array(end) - np.array(start)
        height = np.linalg.norm(direction)
        cylinder = pv.Cylinder(center=start, direction=direction, height=height, radius=radius)
        self.plotter.add_mesh(cylinder, color='red', opacity=0.8, name=obj_id)
        
        self.objects[obj_id] = {
            "id": obj_id,
            "type": "cylinder",
            "name": f"Cylinder_{len(self.objects)}",
            "start_x": start[0],
            "start_y": start[1],
            "start_z": start[2],
            "end_x": end[0],
            "end_y": end[1],
            "end_z": end[2],
            "radius": radius,
            "mesh": cylinder
        }
        
        self.update_view()
        command = AddObjectCommand(self, "cylinder", {
            "start_x": start[0], "start_y": start[1], "start_z": start[2],
            "end_x": end[0], "end_y": end[1], "end_z": end[2],
            "radius": radius
        })
        self.command_history.execute(command)
        return command.obj_id

    def select_object(self, obj_id):
        if obj_id in self.objects:
            self.selected_object = self.objects[obj_id]
            # 選択オブジェクトをハイライト
            for id, obj in self.objects.items():
                color = 'yellow' if id == obj_id else ('blue' if obj["type"] == "cube" else 'red')
                self.plotter.add_mesh(obj["mesh"], color=color, opacity=0.8, name=id)
            
            if self.on_selection_change:
                self.on_selection_change(self.selected_object)
            
            self.update_view()

    def update_object_property(self, obj_id, property_name, value):
        if obj_id not in self.objects:
            return

        obj = self.objects[obj_id]
        try:
            value = float(value) if isinstance(obj[property_name], (int, float)) else value
            obj[property_name] = value
            
            # オブジェクトの再生成
            if obj["type"] == "cube":
                position = (obj["position_x"], obj["position_y"], obj["position_z"])
                new_mesh = pv.Cube(center=position, x_length=obj["size"], y_length=obj["size"], z_length=obj["size"])
            elif obj["type"] == "cylinder":
                start = (obj["start_x"], obj["start_y"], obj["start_z"])
                end = (obj["end_x"], obj["end_y"], obj["end_z"])
                direction = np.array(end) - np.array(start)
                height = np.linalg.norm(direction)
                new_mesh = pv.Cylinder(center=start, direction=direction, height=height, radius=obj["radius"])
            
            obj["mesh"] = new_mesh
            self.plotter.add_mesh(new_mesh, color='yellow', opacity=0.8, name=obj_id)
            self.update_view()
            
        except (ValueError, KeyError):
            print(f"Failed to update property: {property_name}")

    def handle_mouse_move(self, e: ft.DragUpdateEvent):
        if not self.is_dragging:
            return

        dx = e.delta_x
        dy = e.delta_y
        
        # カメラの回転
        self.azimuth += dx * 0.5
        self.elevation = max(-89, min(89, self.elevation - dy * 0.5))
        
        self.update_camera()
        self.update_view()

    def handle_mouse_wheel(self, e: ft.ScrollEvent):
        # ズーム処理
        if e.delta_y > 0:
            self.camera_distance *= 0.9
        else:
            self.camera_distance *= 1.1
            
        self.camera_distance = max(2.0, min(20.0, self.camera_distance))
        self.update_camera()
        self.update_view()

    def handle_click(self, e: ft.TapEvent):
        # クリック位置を正規化座標に変換
        width = self.plotter.window_size[0]
        height = self.plotter.window_size[1]
        x = e.local_x / width
        y = 1.0 - (e.local_y / height)  # PyVistaは下から上が正

        # ピッキング
        picked = self.plotter.picking_point(x, y)
        if picked is not None:
            # 最も近いオブジェクトを選択
            closest_obj_id = None
            min_distance = float('inf')
            
            for obj_id, obj in self.objects.items():
                distance = np.linalg.norm(np.array(picked) - np.array(obj["mesh"].center))
                if distance < min_distance:
                    min_distance = distance
                    closest_obj_id = obj_id
            
            if closest_obj_id:
                self.select_object(closest_obj_id)

    def remove_object(self, obj_id: str) -> None:
        if obj_id in self.objects:
            if self.selected_object and self.selected_object["id"] == obj_id:
                self.selected_object = None
            
            del self.objects[obj_id]
            self.plotter.remove_actor(obj_id)
            self.update_view()
            
            if self.on_selection_change:
                self.on_selection_change(None)

    def restore_object(self, obj_id: str, obj_data: dict) -> None:
        self.objects[obj_id] = obj_data
        self.plotter.add_mesh(
            obj_data["mesh"],
            color='blue' if obj_data["type"] == "cube" else 'red',
            opacity=0.8,
            name=obj_id
        )
        self.update_view()

    def handle_key(self, e: ft.KeyboardEvent):
        if e.key == "Delete" and self.selected_object:
            command = DeleteObjectCommand(self, self.selected_object["id"])
            self.command_history.execute(command)
        elif e.control and e.key == "Z":  # Ctrl+Z
            if self.command_history.undo():
                self.update_view()
        elif e.control and e.key == "Y":  # Ctrl+Y
            if self.command_history.redo():
                self.update_view()
        elif e.control and e.key == "D":  # Ctrl+D
            self.duplicate_selected_object()

    def duplicate_selected_object(self):
        if self.selected_object:
            command = DuplicateObjectCommand(self, self.selected_object["id"])
            self.command_history.execute(command)
            return command.new_obj_id
        return None

    def set_view_preset(self, preset_name: str):
        if preset_name in self.view_presets:
            preset = self.view_presets[preset_name]
            self.azimuth = preset["azimuth"]
            self.elevation = preset["elevation"]
            self.update_camera()
            self.update_view()

    def update_grid(self):
        self.plotter.clear_actors()
        if self.grid_visible:
            grid = pv.Grid(
                dimensions=(self.grid_size, self.grid_size, 1),
                spacing=(self.grid_spacing, self.grid_spacing, self.grid_spacing)
            )
            self.plotter.add_mesh(grid, color='gray', opacity=0.5)
        
        # オブジェクトの再描画
        for obj_id, obj in self.objects.items():
            color = 'yellow' if obj == self.selected_object else ('blue' if obj["type"] == "cube" else 'red')
            self.plotter.add_mesh(obj["mesh"], color=color, opacity=0.8, name=obj_id)

    def toggle_grid(self):
        self.grid_visible = not self.grid_visible
        self.update_grid()
        self.update_view()

    def set_grid_settings(self, size: int = None, spacing: float = None):
        if size is not None:
            self.grid_size = max(2, min(50, size))
        if spacing is not None:
            self.grid_spacing = max(0.1, min(10.0, spacing))
        self.update_grid()
        self.update_view()

    def build(self):
        if self.plotter is None:
            self.initialize_plotter()
            
        return ft.GestureDetector(
            content=ft.Container(
                content=ft.Image(
                    src=str(self.screenshot_path),
                    fit=ft.ImageFit.CONTAIN,
                ),
                border=ft.border.all(1, ft.colors.GREY_400),
                expand=True
            ),
            on_pan_start=lambda _: setattr(self, 'is_dragging', True),
            on_pan_update=self.handle_mouse_move,
            on_pan_end=lambda _: setattr(self, 'is_dragging', False),
            on_scroll=self.handle_mouse_wheel,
            on_tap=self.handle_click,
            on_key_event=self.handle_key,
        ) 