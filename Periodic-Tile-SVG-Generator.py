import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import StringVar, IntVar
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from PIL import Image, ImageDraw, ImageTk
import io
import cairosvg

class SVGTileGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("SVG Periodic Table Tile Generator")

        self.setup_variables()
        self.setup_gui()

    def setup_variables(self):
        self.width = IntVar(value=100)
        self.height = IntVar(value=100)
        self.border_thickness = IntVar(value=2)
        self.corner_type = StringVar(value="square")
        self.corner_radius = IntVar(value=10)
        self.font_family = StringVar(value="Arial")
        self.element_symbol = StringVar(value="H")
        self.element_number = IntVar(value=1)
        self.element_name = StringVar(value="Hydrogen")
        self.align_symbol = StringVar(value="center")
        self.align_number = StringVar(value="right")
        self.align_name = StringVar(value="center")

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=0, column=0, sticky=tk.N)

        preview_frame = ttk.Frame(main_frame)
        preview_frame.grid(row=0, column=1, sticky=tk.N, padx=(10, 0))

        ttk.Label(options_frame, text="Width").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.width).grid(row=0, column=1)

        ttk.Label(options_frame, text="Height").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.height).grid(row=1, column=1)

        ttk.Label(options_frame, text="Border Thickness").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.border_thickness).grid(row=2, column=1)

        ttk.Label(options_frame, text="Corner Type").grid(row=3, column=0, sticky=tk.W)
        corner_menu = ttk.OptionMenu(options_frame, self.corner_type, self.corner_type.get(), "square", "rounded")
        corner_menu.grid(row=3, column=1)

        ttk.Label(options_frame, text="Corner Radius").grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.corner_radius).grid(row=4, column=1)

        ttk.Label(options_frame, text="Font Family").grid(row=5, column=0, sticky=tk.W)
        font_menu = ttk.OptionMenu(options_frame, self.font_family, self.font_family.get(), "Arial", "Verdana", "Times New Roman", "Courier New")
        font_menu.grid(row=5, column=1)

        ttk.Label(options_frame, text="Element Symbol").grid(row=6, column=0, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.element_symbol).grid(row=6, column=1)

        ttk.Label(options_frame, text="Element Number").grid(row=7, column=0, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.element_number).grid(row=7, column=1)

        ttk.Label(options_frame, text="Element Name").grid(row=8, column=0, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.element_name).grid(row=8, column=1)

        ttk.Label(options_frame, text="Symbol Align").grid(row=9, column=0, sticky=tk.W)
        ttk.OptionMenu(options_frame, self.align_symbol, self.align_symbol.get(), "left", "center", "right").grid(row=9, column=1)

        ttk.Label(options_frame, text="Number Align").grid(row=10, column=0, sticky=tk.W)
        ttk.OptionMenu(options_frame, self.align_number, self.align_number.get(), "left", "center", "right").grid(row=10, column=1)

        ttk.Label(options_frame, text="Name Align").grid(row=11, column=0, sticky=tk.W)
        ttk.OptionMenu(options_frame, self.align_name, self.align_name.get(), "left", "center", "right").grid(row=11, column=1)

        self.canvas = tk.Canvas(preview_frame, width=200, height=200, bg="white")
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        button_frame = ttk.Frame(preview_frame)
        button_frame.grid(row=1, column=0, pady=(5, 10))

        ttk.Button(button_frame, text="Update Preview", command=self.update_preview).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Save as SVG", command=self.save_svg).grid(row=0, column=1, padx=5)

        self.preview_text = tk.Text(self.root, height=15, width=100)
        self.preview_text.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="we")

        self.update_preview()

    def get_alignment_x(self, alignment, width):
        if alignment == "left":
            return 5, "start"
        elif alignment == "center":
            return width / 2, "middle"
        elif alignment == "right":
            return width - 5, "end"

    def update_preview(self):
        svg = self.generate_svg()
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, svg)

        png_data = cairosvg.svg2png(bytestring=svg.encode('utf-8'))
        image = Image.open(io.BytesIO(png_data))
        image.thumbnail((200, 200))
        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image)

    def generate_svg(self):
        width = self.width.get()
        height = self.height.get()
        border = self.border_thickness.get()
        radius = self.corner_radius.get() if self.corner_type.get() == "rounded" else 0
        font = self.font_family.get()

        symbol_font_size = int(min(width, height) * 0.4)
        number_font_size = int(min(width, height) * 0.15)
        name_font_size = int(min(width, height) * 0.15)

        svg = Element('svg', width=str(width), height=str(height), xmlns="http://www.w3.org/2000/svg")

        SubElement(svg, 'rect', x="0", y="0", width=str(width), height=str(height),
                   rx=str(radius), ry=str(radius),
                   fill="white", stroke="black",
                   **{"stroke-width": str(border)})

        x_number, anchor_number = self.get_alignment_x(self.align_number.get(), width)
        x_symbol, anchor_symbol = self.get_alignment_x(self.align_symbol.get(), width)
        x_name, anchor_name = self.get_alignment_x(self.align_name.get(), width)

        SubElement(svg, 'text', x=str(x_number), y=str(number_font_size + 5),
                   fill="black", style=f"font-family:{font}; font-size:{number_font_size}px;",
                   **{"text-anchor": anchor_number}).text = str(self.element_number.get())

        SubElement(svg, 'text', x=str(x_symbol), y=str(height / 2 + symbol_font_size / 3),
                   fill="black", style=f"font-family:{font}; font-size:{symbol_font_size}px;",
                   **{"text-anchor": anchor_symbol}).text = self.element_symbol.get()

        SubElement(svg, 'text', x=str(x_name), y=str(height - 5),
                   fill="black", style=f"font-family:{font}; font-size:{name_font_size}px;",
                   **{"text-anchor": anchor_name}).text = self.element_name.get()

        rough_string = tostring(svg, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def save_svg(self):
        svg = self.generate_svg()
        file_path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG files", "*.svg")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(svg)

if __name__ == '__main__':
    root = tk.Tk()
    app = SVGTileGenerator(root)
    root.mainloop()
