from abc import ABC, abstractmethod
from typing import Dict, Any
import copy

class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

class AddObjectCommand(Command):
    def __init__(self, viewer, obj_type: str, params: Dict[str, Any]):
        self.viewer = viewer
        self.obj_type = obj_type
        self.params = params
        self.obj_id = None

    def execute(self) -> None:
        if self.obj_type == "cube":
            self.obj_id = self.viewer.add_cube(
                position=(self.params.get("x", 0), self.params.get("y", 0), self.params.get("z", 0)),
                size=self.params.get("size", 1.0)
            )
        elif self.obj_type == "cylinder":
            self.obj_id = self.viewer.add_cylinder(
                start=(self.params.get("start_x", 0), self.params.get("start_y", 0), self.params.get("start_z", 0)),
                end=(self.params.get("end_x", 0), self.params.get("end_y", 1), self.params.get("end_z", 0)),
                radius=self.params.get("radius", 0.5)
            )

    def undo(self) -> None:
        if self.obj_id:
            self.viewer.remove_object(self.obj_id)
            self.obj_id = None

class DeleteObjectCommand(Command):
    def __init__(self, viewer, obj_id: str):
        self.viewer = viewer
        self.obj_id = obj_id
        self.obj_data = None

    def execute(self) -> None:
        self.obj_data = copy.deepcopy(self.viewer.objects.get(self.obj_id))
        self.viewer.remove_object(self.obj_id)

    def undo(self) -> None:
        if self.obj_data:
            self.viewer.restore_object(self.obj_id, self.obj_data)

class DuplicateObjectCommand(Command):
    def __init__(self, viewer, obj_id: str, offset=(1, 1, 0)):
        self.viewer = viewer
        self.source_id = obj_id
        self.new_obj_id = None
        self.offset = offset

    def execute(self) -> None:
        source_obj = self.viewer.objects.get(self.source_id)
        if not source_obj:
            return

        if source_obj["type"] == "cube":
            pos = (
                source_obj["position_x"] + self.offset[0],
                source_obj["position_y"] + self.offset[1],
                source_obj["position_z"] + self.offset[2]
            )
            self.new_obj_id = self.viewer.add_cube(
                position=pos,
                size=source_obj["size"]
            )
        elif source_obj["type"] == "cylinder":
            start = (
                source_obj["start_x"] + self.offset[0],
                source_obj["start_y"] + self.offset[1],
                source_obj["start_z"] + self.offset[2]
            )
            end = (
                source_obj["end_x"] + self.offset[0],
                source_obj["end_y"] + self.offset[1],
                source_obj["end_z"] + self.offset[2]
            )
            self.new_obj_id = self.viewer.add_cylinder(
                start=start,
                end=end,
                radius=source_obj["radius"]
            )

    def undo(self) -> None:
        if self.new_obj_id:
            self.viewer.remove_object(self.new_obj_id)
            self.new_obj_id = None

class CommandHistory:
    def __init__(self):
        self.history: list[Command] = []
        self.current: int = -1

    def execute(self, command: Command) -> None:
        # 現在位置より後のコマンドを削除
        self.history = self.history[:self.current + 1]
        
        # 新しいコマンドを実行して履歴に追加
        command.execute()
        self.history.append(command)
        self.current += 1

    def undo(self) -> bool:
        if self.current >= 0:
            self.history[self.current].undo()
            self.current -= 1
            return True
        return False

    def redo(self) -> bool:
        if self.current + 1 < len(self.history):
            self.current += 1
            self.history[self.current].execute()
            return True
        return False

    def clear(self) -> None:
        self.history.clear()
        self.current = -1 