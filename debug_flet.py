import flet as ft
import sys

print(f"Python: {sys.version}")
print(f"Flet version: {ft.version}")
print("dir(ft):", dir(ft))

try:
    print("ft.colors:", ft.colors)
    print("ft.colors.GREEN:", ft.colors.GREEN)
except AttributeError as e:
    print(f"Error accessing ft.colors: {e}")

try:
    print("ft.Colors:", ft.Colors)
except AttributeError as e:
    print(f"Error accessing ft.Colors: {e}")
