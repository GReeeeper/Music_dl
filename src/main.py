import flet as ft
import asyncio
import os
import sys
import subprocess
import platform

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import Downloader, TrackInfo

class MusicDownloaderApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Music Downloader"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window_width = 450
        self.page.window_height = 800
        self.page.padding = 0
        self.page.bgcolor = "#0f0f15" # Very dark background
        
        self.downloader = Downloader()
        
        # State
        self.current_tracks: list[TrackInfo] = []
        self.selected_indices = set()
        self.output_dir = os.path.join(os.getcwd(), "downloads")
        
        # UI Components
        self._init_ui()

    def _init_ui(self):
        # --- Styles ---
        self.gradient_shader_mask = ft.LinearGradient(
            colors=[ft.Colors.CYAN, ft.Colors.PURPLE],
            begin=ft.alignment.Alignment(-1, -1),
            end=ft.alignment.Alignment(1, 1),
        )
        
        # --- Header ---
        self.header = ft.Container(
            content=ft.Text("MUSIC DL", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            padding=ft.padding.only(top=30, bottom=20),
            alignment=ft.alignment.Alignment(0, 0)
        )

        # --- Input Section (Glass Card) ---
        self.url_input = ft.TextField(
            label="Paste URL (Sony/YT/SoundCloud)",
            label_style=ft.TextStyle(color=ft.Colors.CYAN_200),
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
            border_color=ft.Colors.CYAN_700,
            cursor_color=ft.Colors.CYAN,
            expand=True,
            on_submit=self.check_url
        )
        
        self.fetch_btn = ft.ElevatedButton(
            "FETCH",
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.CYAN_900,
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=5,
            ),
            on_click=self.check_url,
            width=100
        )

        input_container = ft.Container(
            content=ft.Column([
                ft.Row([self.url_input], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                ft.Row([self.fetch_btn], alignment=ft.MainAxisAlignment.END)
            ]),
            padding=20,
            margin=ft.margin.symmetric(horizontal=20),
            border_radius=15,
            bgcolor="#1a1a25", # Slightly lighter dark
            border=ft.border.all(1, ft.Colors.CYAN_900),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.CYAN),
            )
        )

        # --- Settings Section ---
        self.format_dropdown = ft.Dropdown(
            label="Format",
            width=120,
            options=[
                ft.dropdown.Option("wav"),
                ft.dropdown.Option("mp3"),
                ft.dropdown.Option("flac"),
                ft.dropdown.Option("m4a"),
            ],
            value="wav",
            border_color=ft.Colors.PURPLE_700,
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
            label_style=ft.TextStyle(color=ft.Colors.PURPLE_200),
        )

        settings_container = ft.Container(
            content=ft.Row([
                ft.Text("Settings", color=ft.Colors.GREY_500, size=16),
                self.format_dropdown
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=25, vertical=10)
        )

        # --- Status / Feedback Section ---
        self.status_title = ft.Text("Ready", size=16, color=ft.Colors.CYAN_100, weight=ft.FontWeight.BOLD)
        self.status_detail = ft.Text("Waiting for input...", size=12, color=ft.Colors.GREY_400)
        self.progress_bar = ft.ProgressBar(width=350, color=ft.Colors.CYAN, bgcolor="#2a2a35", value=0, visible=False)
        
        # --- Control Buttons ---
        self.pause_btn = ft.IconButton(ft.Icons.PAUSE_CIRCLE_FILLED, icon_color=ft.Colors.YELLOW, icon_size=30, tooltip="Pause (Stop & Resume later)", on_click=self.pause_download, visible=False)
        self.resume_btn = ft.IconButton(ft.Icons.PLAY_CIRCLE_FILLED, icon_color=ft.Colors.GREEN, icon_size=30, tooltip="Resume", on_click=self.resume_download, visible=False)
        self.stop_btn = ft.IconButton(ft.Icons.STOP_CIRCLE, icon_color=ft.Colors.RED, icon_size=30, tooltip="Stop/Cancel", on_click=self.stop_download, visible=False)
        self.delete_btn = ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.GREY, icon_size=20, tooltip="Delete File / Empty Folder", on_click=self.delete_file, visible=True)

        self.open_folder_btn = ft.ElevatedButton(
            "Open Folder", 
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self.open_output_folder,
            visible=True,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.PURPLE_900,
            )
        )

        status_card = ft.Container(
            content=ft.Column([
                ft.Row([self.status_title, self.delete_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.status_detail,
                ft.Container(height=10),
                self.progress_bar,
                ft.Row([self.pause_btn, self.resume_btn, self.stop_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                ft.Row([
                    ft.Text(f"Save Path: {self.output_dir}", size=10, color=ft.Colors.GREY_600, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                    self.open_folder_btn
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            padding=20,
            margin=20,
            border_radius=15,
            bgcolor="#1a1a25",
            border=ft.border.all(1, ft.Colors.PURPLE_900),
             shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.PURPLE),
            )
        )

        # Main Layout
        self.page.add(
            ft.Container(
                content=ft.Column([
                    self.header,
                    input_container,
                    settings_container,
                    status_card,
                    ft.Container(expand=True) # Spacer
                ]),
                expand=True,
                # image=ft.DecorationImage(src="") if needed
            )
        )
        
        # Dialogs
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Select Tracks", color=ft.Colors.CYAN),
            content=ft.Column([], height=300, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.ElevatedButton("Download Selected", on_click=self.start_download_from_dialog, style=ft.ButtonStyle(bgcolor=ft.Colors.CYAN_900, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor="#1a1a25",
        )
        
        self.dlg_confirm = ft.AlertDialog(
            modal=True,
            title=ft.Text("Empty Download Folder?", color=ft.Colors.RED),
            content=ft.Text("This will permanently delete ALL files in the download folder.\nAre you sure?", color=ft.Colors.WHITE),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_confirm),
                ft.ElevatedButton("Delete All", on_click=self.confirm_delete_folder, style=ft.ButtonStyle(bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor="#1a1a25",
        )
        
        # Persist logic
        self.last_tracks = []

    def check_url(self, e):
        # ... (same)
        url = self.url_input.value
        if not url:
            return
        
        self.status_title.value = "Fetching Metadata..."
        self.status_detail.value = "Please wait..."
        self.progress_bar.visible = True
        self.progress_bar.value = None # Indeterminate
        self.page.update()
        
        self.page.run_task(self.process_url, url)

    async def process_url(self, url):
        # ... (same)
        try:
            tracks = await self.downloader.get_metadata(url)
            self.current_tracks = tracks
            self.progress_bar.visible = False
            
            if len(tracks) == 0:
                self.status_title.value = "Error"
                self.status_detail.value = "No tracks found or invalid URL."
                self.status_title.color = ft.Colors.RED
                self.page.update()
                return

            self.status_title.color = ft.Colors.CYAN_100
            if len(tracks) > 1:
                self.show_playlist_dialog(tracks)
            else:
                self.status_title.value = f"Found: {tracks[0].title}"
                self.status_detail.value = f"Artist: {tracks[0].artist}"
                self.page.update()
                await self.download_tracks(tracks)
                
        except Exception as e:
            self.status_title.value = "Error"
            self.status_detail.value = str(e)
            self.status_title.color = ft.Colors.RED
            self.progress_bar.visible = False
            self.page.update()

    def show_playlist_dialog(self, tracks: list[TrackInfo]):
        # ... (same)
        self.selected_indices = set(t.index for t in tracks)
        checklist = ft.Column()
        
        def on_checkbox_change(e):
            idx = e.control.data
            if e.control.value:
                self.selected_indices.add(idx)
            else:
                self.selected_indices.discard(idx)
        
        # Add "Select All/None" logic later if needed, for now just list
        for t in tracks:
            checklist.controls.append(
                ft.Checkbox(
                    label=f"{t.index}. {t.artist} - {t.title}", 
                    value=True, 
                    data=t.index,
                    on_change=on_checkbox_change,
                    fill_color=ft.Colors.CYAN_700
                )
            )
            
        self.dlg_modal.content = checklist
        self.page.dialog = self.dlg_modal
        self.dlg_modal.open = True
        self.page.update()

    def close_dialog(self, e):
        self.dlg_modal.open = False
        self.page.update()
        
    def close_confirm(self, e):
        self.dlg_confirm.open = False
        self.page.update()

    def start_download_from_dialog(self, e):
        self.close_dialog(e)
        selected_tracks = [t for t in self.current_tracks if t.index in self.selected_indices]
        if not selected_tracks:
            return
        self.page.run_task(self.download_tracks, selected_tracks)

    async def download_tracks(self, tracks: list[TrackInfo]):
        self.last_tracks = tracks # save for resume
        self.progress_bar.visible = True
        self.progress_bar.value = None
        
        # Show Controls
        self.pause_btn.visible = True
        self.resume_btn.visible = False # Hide resume initially
        self.stop_btn.visible = True
        self.delete_btn.visible = False 
        self.page.update()
        
        total = len(tracks)
        url = self.url_input.value
        fmt = self.format_dropdown.value
        
        indices = [t.index for t in tracks] if len(tracks) > 1 else None
        if len(self.current_tracks) > 1 and len(tracks) == 1:
             indices = [tracks[0].index]

        self.status_title.value = f"Downloading {total} Items..."
        self.status_detail.value = "Initializing..."
        self.page.update()

        def update_progress(msg):
            print(msg)
            if "Downloading:" in msg:
                self.status_detail.value = msg
                try:
                    pct_str = msg.replace("Downloading:", "").replace("%", "").strip()
                    val = float(pct_str) / 100.0
                    self.progress_bar.value = val
                except:
                    pass
            else:
                self.status_detail.value = msg
            self.page.update()

        try:
            await self.downloader.download(
                url=url,
                output_dir=self.output_dir,
                format=fmt,
                track_indices=indices,
                progress_callback=update_progress
            )
            self.status_title.value = "COMPLETED"
            self.status_title.color = ft.Colors.GREEN
            self.status_detail.value = f"Saved in {self.output_dir}"
            self.progress_bar.value = 1.0
            
            # Show Delete (Cleanup)
            self.delete_btn.visible = True
            
            # Hide download controls if done
            self.pause_btn.visible = False
            self.stop_btn.visible = False
            self.resume_btn.visible = False
            
        except Exception as e:
            # Show Delete (Cleanup) even on failure/stop so user can empty folder
            self.delete_btn.visible = True
            
            if "Cancelled" in str(e):
                self.status_title.value = "PAUSED / STOPPED"
                self.status_title.color = ft.Colors.YELLOW
                self.status_detail.value = "Download stopped by user."
                
                # Logic to determine if it was paused vs stopped
                # If paused, show resume button
                if self.pause_btn.visible == False and self.resume_btn.visible == True:
                    # User clicked pause
                    pass # logic handled in pause_download
            else:
                self.status_title.value = "FAILED"
                self.status_title.color = ft.Colors.RED
                self.status_detail.value = str(e)
                # Hide controls on failure
                self.pause_btn.visible = False
                self.stop_btn.visible = False
        
        self.page.update()

    def stop_download(self, e):
        self.status_detail.value = "Stopping..."
        # Reset resume state
        self.resume_btn.visible = False
        self.pause_btn.visible = False
        self.page.update()
        self.downloader.cancel()

    def pause_download(self, e):
        self.status_detail.value = "Pausing..."
        # Swap buttons
        self.pause_btn.visible = False
        self.resume_btn.visible = True
        self.page.update()
        self.downloader.cancel()

    def resume_download(self, e):
        self.status_detail.value = "Resuming..."
        self.page.update()
        # triggering download again with last tracks
        if self.last_tracks:
            self.page.run_task(self.download_tracks, self.last_tracks)

    def delete_file(self, e):
        # Open confirmation dialog instead of just clearing
        self.page.dialog = self.dlg_confirm
        self.dlg_confirm.open = True
        self.page.update()

    def confirm_delete_folder(self, e):
        self.close_confirm(e)
        self.status_detail.value = "Deleting files..."
        self.page.update()
        
        try:
            # Delete all files in output_dir
            if os.path.exists(self.output_dir):
                count = 0
                for filename in os.listdir(self.output_dir):
                    file_path = os.path.join(self.output_dir, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                            count += 1
                        elif os.path.isdir(file_path):
                            # Optional: remove subdirs? Let's just remove files for safety
                            # shutil.rmtree(file_path)
                            pass
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Reason: {e}")
                
                self.status_title.value = "Deleted"
                self.status_title.color = ft.Colors.YELLOW
                self.status_detail.value = f"Removed {count} files from folder."
            else:
                 self.status_detail.value = "Folder does not exist."

        except Exception as e:
             self.status_detail.value = f"Error deleting: {e}"
        
        self.progress_bar.value = 0
        self.progress_bar.visible = False
        self.delete_btn.visible = False
        self.page.update()

    def open_output_folder(self, e):
        path = self.output_dir
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as ex:
                print(f"Error creating directory: {ex}")
                return

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else: # Linux
            subprocess.Popen(["xdg-open", path])

def main(page: ft.Page):
    app = MusicDownloaderApp(page)

if __name__ == "__main__":
    ft.app(target=main)
