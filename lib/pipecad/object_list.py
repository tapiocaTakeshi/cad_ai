import flet as ft

class ObjectListPanel(ft.UserControl):
    def __init__(self, on_select=None):
        super().__init__()
        self.on_select = on_select
        self.objects = {}
        self.list_view = None

    def update_objects(self, objects):
        self.objects = objects
        self.update()

    def build(self):
        def on_select_changed(e):
            if e.control.selected_index is not None and self.on_select:
                selected_id = list(self.objects.keys())[e.control.selected_index]
                self.on_select(selected_id)

        def show_context_menu(e: ft.TapEvent, obj_id: str):
            menu = ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(
                        text="複製",
                        icon=ft.icons.CONTENT_COPY,
                        on_click=lambda _: self.on_select(obj_id) and self.viewer.duplicate_selected_object()
                    ),
                    ft.PopupMenuItem(
                        text="削除",
                        icon=ft.icons.DELETE,
                        on_click=lambda _: self.on_select(obj_id) and self.viewer.handle_key(ft.KeyboardEvent(key="Delete"))
                    ),
                ]
            )
            menu.show_menu(e)

        items = [
            ft.ListTile(
                leading=ft.Icon(
                    ft.icons.CUBE if obj["type"] == "cube" else ft.icons.CYLINDER,
                    color=ft.colors.BLUE if obj["type"] == "cube" else ft.colors.RED
                ),
                title=ft.Text(obj["name"]),
                on_long_press=lambda e, id=obj["id"]: show_context_menu(e, id)
            ) for obj in self.objects.values()
        ]

        self.list_view = ft.ListView(
            controls=items,
            expand=1,
            spacing=2,
            padding=10,
            on_select_changed=on_select_changed
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("オブジェクトリスト", size=16, weight=ft.FontWeight.BOLD),
                    self.list_view
                ],
                spacing=10
            ),
            padding=10,
            expand=True
        ) 