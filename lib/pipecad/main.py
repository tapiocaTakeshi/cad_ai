import flet as ft
from pathlib import Path
from .viewer import Viewer3D
from .property_panel import PropertyPanel
from .object_list import ObjectListPanel
from .settings_panel import SettingsPanel

def main():
    def page_setup(page: ft.Page):
        page.title = "CAD-AI"
        page.theme_mode = ft.ThemeMode.SYSTEM
        page.padding = 10
        
        def open_project_dialog():
            def close_dlg():
                dlg.open = False
                page.update()

            dlg = ft.AlertDialog(
                title=ft.Text("プロジェクトを開く"),
                content=ft.TextField(label="プロジェクトパス"),
                actions=[
                    ft.TextButton("キャンセル", on_click=lambda _: close_dlg()),
                    ft.TextButton("開く", on_click=lambda _: close_dlg()),
                ],
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        def create_new_project():
            # 新規プロジェクト作成の処理
            print("新規プロジェクトが作成されました")
            # ビューアをリセット
            viewer.objects.clear()
            viewer.initialize_plotter()  # plotterを再初期化
            page.update()

        viewer = Viewer3D()
        viewer.initialize_plotter()  # ページに追加する前に初期化

        def add_sample_geometry(_):
            viewer.add_cube(position=(1, 1, 0))
            viewer.add_cylinder(start=(0, 0, 0), end=(0, 0, 2))

        def toggle_3d_view(_):
            if content_area.content == viewer:
                content_area.content = welcome_content
            else:
                content_area.content = viewer
            page.update()

        # ツールバー
        toolbar = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.icons.SAVE,
                    tooltip="保存",
                    on_click=lambda _: print("Save")
                ),
                ft.VerticalDivider(width=1),
                ft.IconButton(
                    icon=ft.icons.UNDO,
                    tooltip="元に戻す",
                    on_click=lambda _: viewer.command_history.undo() and viewer.update_view()
                ),
                ft.IconButton(
                    icon=ft.icons.REDO,
                    tooltip="やり直し",
                    on_click=lambda _: viewer.command_history.redo() and viewer.update_view()
                ),
                ft.VerticalDivider(width=1),
                ft.IconButton(
                    icon=ft.icons.CONTENT_COPY,
                    tooltip="複製 (Ctrl+D)",
                    on_click=lambda _: viewer.duplicate_selected_object()
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE,
                    tooltip="削除 (Delete)",
                    on_click=lambda _: viewer.handle_key(ft.KeyboardEvent(key="Delete"))
                ),
                ft.VerticalDivider(width=1),
                ft.IconButton(
                    icon=ft.icons.GRID_4X4,
                    tooltip="グリッド表示切替",
                    on_click=lambda _: viewer.toggle_grid()
                ),
                ft.IconButton(
                    icon=ft.icons.VIEW_IN_AR,
                    tooltip="3Dビュー",
                    on_click=toggle_3d_view
                ),
                ft.IconButton(
                    icon=ft.icons.ADD_BOX,
                    tooltip="サンプル形状追加",
                    on_click=add_sample_geometry
                ),
            ],
            spacing=0,
        )

        # サイドパネル
        side_panel = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.FOLDER_OUTLINED,
                    selected_icon=ft.icons.FOLDER,
                    label="プロジェクト"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.ARCHITECTURE_OUTLINED,
                    selected_icon=ft.icons.ARCHITECTURE,
                    label="モデリング"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon=ft.icons.SETTINGS,
                    label="設定"
                ),
            ],
            on_change=lambda e: update_side_content(e.control.selected_index)
        )

        object_list = ObjectListPanel(
            on_select=lambda obj_id: viewer.select_object(obj_id)
        )
        viewer.on_selection_change = lambda obj: (
            property_panel.update_object(obj),
            object_list.update_objects(viewer.objects)
        )

        def update_side_content(index):
            if index == 0:
                side_content.content = object_list
            elif index == 1:
                side_content.content = property_panel
            elif index == 2:
                side_content.content = settings_panel
            page.update()

        side_content = ft.Container(
            content=ft.Text("プロジェクト"),
            padding=10,
            expand=True
        )

        property_panel = PropertyPanel(
            on_property_change=lambda obj_id, prop, value: viewer.update_object_property(obj_id, prop, value)
        )
        viewer.on_selection_change = property_panel.update_object

        settings_panel = SettingsPanel(viewer)

        # ウェルカムコンテンツ
        welcome_content = ft.Column(
            controls=[
                ft.Text("ようこそ CAD-AI へ", size=32, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            text="プロジェクトを開く",
                            icon=ft.icons.FOLDER_OPEN,
                            on_click=lambda _: open_project_dialog()
                        ),
                        ft.ElevatedButton(
                            text="新規プロジェクト",
                            icon=ft.icons.ADD,
                            on_click=lambda _: create_new_project()
                        ),
                    ],
                    spacing=10
                )
            ],
            spacing=20
        )

        # メインコンテンツエリア
        content_area = ft.Container(
            content=viewer,  # ここでViewer3Dをページに追加
            padding=20,
            expand=True
        )

        # メインレイアウト
        main_layout = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        side_panel,
                        side_content
                    ],
                    expand=1
                ),
                ft.VerticalDivider(width=1),
                ft.Column(
                    controls=[
                        toolbar,
                        ft.Divider(height=1),
                        content_area
                    ],
                    expand=3
                )
            ],
            expand=True
        )
        
        page.add(main_layout)
        page.update()

    ft.app(target=page_setup)

if __name__ == "__main__":
    main() 