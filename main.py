import flet as ft

def main(page: ft.Page):
    page.title = "The Agency"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 800
    page.window_min_height = 600

    # Noir Theme
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1A2B3C"  # Dark navy blue
    page.navigation_bar = ft.NavigationBar(
        bgcolor="#2C3E50",  # Slightly lighter navy for nav bar
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.PUBLIC, label="World Builder"),
            ft.NavigationBarDestination(icon=ft.Icons.CASES, label="Case Builder"),
        ]
    )

    page.appbar = ft.AppBar(
        title=ft.Text("The Agency", color="#FFFFFF"),
        center_title=False,
        bgcolor="#2C3E50",
        actions=[
            ft.TextField(
                hint_text="Global Search...",
                width=300,
                content_padding=ft.padding.only(left=10, right=10),
                border_radius=5,
                filled=True,
                fill_color="#3A4D60",
                text_style=ft.TextStyle(color="#FFFFFF"),
                hint_style=ft.TextStyle(color="#9E9E9E"), # Grey 500 equivalent
                border_color="#00000000", # Transparent
            ),
            ft.IconButton(icon=ft.Icons.SEARCH, icon_color="#FFFFFF"),
        ]
    )

    page.add(
        ft.Row(
            [
                # Left-side navigation panel (Secondary Navigation)
                ft.Container(
                    content=ft.Column(
                        [
                            ft.IconButton(icon=ft.Icons.PERSON, tooltip="Characters"),
                            ft.IconButton(icon=ft.Icons.LOCATION_ON, tooltip="Locations"),
                            ft.IconButton(icon=ft.Icons.GROUPS, tooltip="Factions"),
                            ft.IconButton(icon=ft.Icons.HISTORY, tooltip="Lore & History"),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    width=70,
                    height=page.height, # This will be dynamic
                    bgcolor="#2C3E50",
                    padding=ft.padding.symmetric(vertical=10),
                    alignment=ft.alignment.top_center,
                ),
                # Main content area
                ft.Column(
                    [
                        ft.Text("Welcome to The Agency!", color="#FFFFFF", size=24),
                        ft.Text("Select a tab from above or an asset category from the left.", color="#9E9E9E"),
                    ],
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ],
            expand=True,
        )
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)