import flet as ft

class SettingsPanel(ft.UserControl):
    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer

    def build(self):
        grid_size_slider = ft.Slider(
            min=2,
            max=50,
            value=self.viewer.grid_size,
            label="グリッドサイズ",
            on_change=lambda e: self.viewer.set_grid_settings(size=int(e.control.value))
        )

        grid_spacing_slider = ft.Slider(
            min=0.1,
            max=10.0,
            value=self.viewer.grid_spacing,
            label="グリッド間隔",
            on_change=lambda e: self.viewer.set_grid_settings(spacing=e.control.value)
        )

        grid_toggle = ft.Switch(
            label="グリッド表示",
            value=self.viewer.grid_visible,
            on_change=lambda _: self.viewer.toggle_grid()
        )

        view_buttons = [
            ft.ElevatedButton(
                text=name,
                on_click=lambda _, n=name: self.viewer.set_view_preset(n)
            ) for name in self.viewer.view_presets.keys()
        ]

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("表示設定", size=16, weight=ft.FontWeight.BOLD),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("グリッド設定"),
                                    grid_toggle,
                                    grid_size_slider,
                                    grid_spacing_slider,
                                ],
                                spacing=10
                            ),
                            padding=10
                        )
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("ビュープリセット"),
                                    ft.Row(controls=view_buttons, wrap=True)
                                ],
                                spacing=10
                            ),
                            padding=10
                        )
                    )
                ],
                spacing=20
            ),
            padding=10
        ) 