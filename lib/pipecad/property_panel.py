import flet as ft

class PropertyPanel(ft.UserControl):
    def __init__(self, on_property_change=None):
        super().__init__()
        self.on_property_change = on_property_change
        self.current_object = None

    def update_object(self, obj_data):
        self.current_object = obj_data
        self.update()

    def build(self):
        if not self.current_object:
            return ft.Container(
                content=ft.Text("オブジェクトが選択されていません"),
                padding=10
            )

        def on_change(e):
            if self.on_property_change:
                self.on_property_change(self.current_object["id"], e.control.label, e.control.value)

        properties = []
        for key, value in self.current_object.items():
            if key == "id":
                continue
                
            if isinstance(value, (int, float)):
                properties.append(
                    ft.TextField(
                        label=key,
                        value=str(value),
                        on_change=on_change
                    )
                )
            elif isinstance(value, str):
                properties.append(
                    ft.TextField(
                        label=key,
                        value=value,
                        on_change=on_change
                    )
                )
            elif isinstance(value, bool):
                properties.append(
                    ft.Checkbox(
                        label=key,
                        value=value,
                        on_change=on_change
                    )
                )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        f"オブジェクト: {self.current_object.get('name', 'Unknown')}",
                        size=16,
                        weight=ft.FontWeight.BOLD
                    ),
                    *properties
                ],
                spacing=10
            ),
            padding=10
        ) 