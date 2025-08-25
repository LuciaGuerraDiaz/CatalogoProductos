import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from catalogo import CatalogoProducto
from producto import Producto
from PIL import Image, ImageTk
import os
import datetime
import pandas as pd


def obtener_catalogos_existentes():
    if not os.path.exists("catalogos"):
        os.makedirs("catalogos")
    return [d for d in os.listdir("catalogos") if os.path.isdir(os.path.join("catalogos", d))]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Catálogos")
        self.geometry("1400x800")

        self.catalogo_actual = None
        self.ruta_foto_seleccionada_src = ""
        self.producto_seleccionado = None
        self.img_tk_preview = None
        self.img_tk_detail = None

        self._crear_widgets()
        self._actualizar_lista_catalogos()

    # ---------------- UI ----------------

    def _crear_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(top_frame, text="Nombre del Catálogo:").pack(side="left")
        self.catalogo_combobox = ttk.Combobox(top_frame, width=40, values=obtener_catalogos_existentes())
        self.catalogo_combobox.pack(side="left", padx=5)

        self.cargar_btn = ttk.Button(top_frame, text="Cargar Catálogo", command=self._cargar_catalogo)
        self.cargar_btn.pack(side="left", padx=5)

        self.nuevo_catalogo_btn = ttk.Button(top_frame, text="Nuevo Catálogo", command=self._nuevo_catalogo)
        self.nuevo_catalogo_btn.pack(side="left", padx=5)
        
        self.eliminar_catalogo_btn = ttk.Button(top_frame, text="Eliminar Catálogo", command=self._eliminar_catalogo)
        self.eliminar_catalogo_btn.pack(side="left", padx=5)
        
        self.export_btn = ttk.Button(top_frame, text="Exportar a Excel", command=self._exportar_a_excel)
        self.export_btn.pack(side="left", padx=5)

        # Layout principal (3 columnas)
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Columna 1: Formulario
        self.form_frame = ttk.Frame(main_frame, width=400)
        self.form_frame.pack(side="left", fill="y", padx=(0, 10))
        self.form_frame.pack_propagate(False)

        # Columna 2: Lista de productos
        self.tree_frame = ttk.Frame(main_frame)
        self.tree_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Columna 3: Detalles
        self.detail_frame = ttk.Frame(main_frame, width=300)
        self.detail_frame.pack(side="right", fill="y")
        self.detail_frame.pack_propagate(False)

        self._crear_formulario()
        self._crear_visor_productos()
        self._crear_panel_detalles()

    def _crear_formulario(self):
        form_frame = self.form_frame

        ttk.Label(form_frame, text="📝 Formulario de Producto", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        labels = ["Nombre:", "Características:", "Color:", "Tipo:", "Precio Original:", "Precio:", "Fecha Publicación:"]
        self.entries = {}

        for label_text in labels:
            ttk.Label(form_frame, text=label_text).pack(fill="x", padx=5, pady=(5, 0))
            entry = ttk.Entry(form_frame)
            entry.pack(fill="x", padx=5, pady=(0, 5))
            self.entries[label_text[:-1].lower().replace(" ", "")] = entry  # ej: "preciooriginal", "fechapublicación"
        
        # Botones del formulario
        button_frame_form = ttk.Frame(form_frame)
        button_frame_form.pack(fill="x", pady=10)

        self.guardar_btn = ttk.Button(button_frame_form, text="Guardar Producto", command=self._guardar_producto)
        self.guardar_btn.pack(side="left", expand=True, padx=2)

        self.limpiar_btn = ttk.Button(button_frame_form, text="Limpiar", command=self._limpiar_formulario_y_seleccion)
        self.limpiar_btn.pack(side="left", expand=True, padx=2)

        # Canvas para preview
        ttk.Label(form_frame, text="📷 Vista Previa", font=("Arial", 10, "bold")).pack(pady=(10, 5))
        self.preview_canvas = tk.Canvas(form_frame, bg="lightgrey", height=200, width=380, relief="solid", bd=1)
        self.preview_canvas.pack(pady=5)

        # Controles de foto
        photo_frame = ttk.Frame(form_frame)
        photo_frame.pack(fill="x", pady=5)

        self.select_photo_btn = ttk.Button(photo_frame, text="Seleccionar Foto", command=self._seleccionar_foto)
        self.select_photo_btn.pack(side="left", padx=5)
        
        self.no_photo_var = tk.BooleanVar()
        self.no_photo_check = ttk.Checkbutton(photo_frame, text="Sin foto", variable=self.no_photo_var, command=self._toggle_photo_selection)
        self.no_photo_check.pack(side="left", padx=5)

        self.foto_path_label = ttk.Label(form_frame, text="No se ha seleccionado ninguna foto.", wraplength=380, foreground="gray")
        self.foto_path_label.pack(fill="x", padx=5, pady=5)

    def _crear_visor_productos(self):
        ttk.Label(self.tree_frame, text="📋 Lista de Productos", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        view_options_frame = ttk.Frame(self.tree_frame)
        view_options_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(view_options_frame, text="Vista:").pack(side="left")
        self.view_selector = ttk.Combobox(view_options_frame, values=["Vista Simple", "Vista Completa"], state="readonly")
        self.view_selector.pack(side="left", padx=5)
        self.view_selector.set("Vista Completa")
        self.view_selector.bind("<<ComboboxSelected>>", self._cambiar_vista_productos)

        tree_container = ttk.Frame(self.tree_frame)
        tree_container.pack(fill="both", expand=True)

        cols = ("nombre", "tipo", "color", "precio", "fecha_publicacion")
        self.tree = ttk.Treeview(tree_container, columns=cols, show="headings")
        
        self.col_headers = {
            "nombre": "Nombre", "tipo": "Tipo", "características": "Características",
            "color": "Color", "preciooriginal": "Precio Original", "precio": "Precio",
            "fecha_publicacion": "Fecha Publicación", "fecha_ingreso": "Fecha Ingreso"
        }
        
        for col in cols:
            self.tree.heading(col, text=self.col_headers[col])
            self.tree.column(col, width=120)

        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self._on_producto_select)
        
        # Acciones
        action_frame = ttk.Frame(self.tree_frame)
        action_frame.pack(fill="x", pady=10)

        button_frame1 = ttk.Frame(action_frame)
        button_frame1.pack(fill="x", pady=2)

        self.editar_btn = ttk.Button(button_frame1, text="✏️ Editar Producto", command=self._editar_producto_seleccionado, state="disabled")
        self.editar_btn.pack(side="left", padx=5, expand=True, fill="x")

        self.duplicar_btn = ttk.Button(button_frame1, text="📄 Duplicar Producto", command=self._duplicar_producto, state="disabled")
        self.duplicar_btn.pack(side="right", padx=5, expand=True, fill="x")

        button_frame2 = ttk.Frame(action_frame)
        button_frame2.pack(fill="x", pady=2)

        self.eliminar_btn = ttk.Button(button_frame2, text="🗑️ Eliminar Producto", command=self._eliminar_producto, state="disabled")
        self.eliminar_btn.pack(expand=True, fill="x")

    def _crear_panel_detalles(self):
        ttk.Label(self.detail_frame, text="🔍 Detalles del Producto", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        detail_canvas = tk.Canvas(self.detail_frame, highlightthickness=0)
        detail_scrollbar = ttk.Scrollbar(self.detail_frame, orient="vertical", command=detail_canvas.yview)
        detail_canvas.configure(yscrollcommand=detail_scrollbar.set)

        self.detail_content_frame = ttk.Frame(detail_canvas)
        detail_canvas.create_window((0, 0), window=self.detail_content_frame, anchor="nw")

        # Imagen
        self.detail_image_frame = ttk.LabelFrame(self.detail_content_frame, text="📷 Imagen", padding="10")
        self.detail_image_frame.pack(fill="x", pady=(0, 10))
        self.detail_image_canvas = tk.Canvas(self.detail_image_frame, bg="lightgray", height=200, width=260, relief="solid", bd=1)
        self.detail_image_canvas.pack()

        # Info
        self.detail_info_frame = ttk.LabelFrame(self.detail_content_frame, text="ℹ️ Información", padding="10")
        self.detail_info_frame.pack(fill="x", pady=(0, 10))

        self.detail_labels = {}
        info_fields = ["Nombre", "Características", "Color", "Tipo", "Precio Original", "Precio", "Fecha Publicación", "Fecha Ingreso"]
        for field in info_fields:
            frame = ttk.Frame(self.detail_info_frame)
            frame.pack(fill="x", pady=2)
            ttk.Label(frame, text=f"{field}:", font=("Arial", 9, "bold")).pack(side="left")
            label = ttk.Label(frame, text="-", wraplength=200, justify="left")
            label.pack(side="right", fill="x", expand=True)
            self.detail_labels[field.lower().replace(" ", "_")] = label

        detail_canvas.pack(side="left", fill="both", expand=True)
        detail_scrollbar.pack(side="right", fill="y")

        def configure_scroll_region(event=None):
            detail_canvas.configure(scrollregion=detail_canvas.bbox("all"))
        self.detail_content_frame.bind("<Configure>", configure_scroll_region)

        self._mostrar_detalle_vacio()

    # ------------- Panel detalles -------------

    def _mostrar_detalle_vacio(self):
        self.detail_image_canvas.delete("all")
        self.detail_image_canvas.create_text(130, 100, text="Seleccione un producto\npara ver su imagen", 
                                             fill="gray", font=("Arial", 10), justify="center")
        for label in self.detail_labels.values():
            label.config(text="-", foreground="gray")

    def _actualizar_panel_detalles(self, producto):
        self.detail_image_canvas.delete("all")
        self.img_tk_detail = None
        
        if producto.ruta_foto_original:
            ruta_abs = os.path.join(self.catalogo_actual.base_path, producto.ruta_foto_original)
            if os.path.exists(ruta_abs):
                try:
                    img = Image.open(ruta_abs)
                    img.thumbnail((260, 200))
                    self.img_tk_detail = ImageTk.PhotoImage(img)
                    self.detail_image_canvas.create_image(130, 100, image=self.img_tk_detail)
                except Exception as e:
                    self.detail_image_canvas.create_text(130, 100, text=f"Error al cargar imagen:\n{e}", 
                                                         fill="red", font=("Arial", 9), width=250, justify="center")
            else:
                self.detail_image_canvas.create_text(130, 100, text="Imagen no encontrada", fill="red", font=("Arial", 10))
        else:
            self.detail_image_canvas.create_text(130, 100, text="Sin imagen", fill="gray", font=("Arial", 10))

        precio_original = getattr(producto, '_Producto__precio_original', 0)
        info_data = {
            "nombre": producto.nombre,
            "características": producto.caracteristicas or "No especificadas",
            "color": producto.color or "No especificado",
            "tipo": producto.tipo or "No especificado",
            "precio_original": f"${precio_original:,.2f}" if precio_original and precio_original > 0 else "No especificado",
            "precio": f"${producto.precio:,.2f}",
            "fecha_publicación": producto.fecha_publicacion or "No especificada",
            "fecha_ingreso": producto.fecha_ingreso or "No especificada"
        }
        for key, value in info_data.items():
            if key in self.detail_labels:
                self.detail_labels[key].config(text=str(value), foreground="black")

    # ------------- Catálogo -------------

    def _toggle_photo_selection(self):
        if self.no_photo_var.get():
            self.select_photo_btn.config(state="disabled")
            self.ruta_foto_seleccionada_src = ""
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(190, 100, text="Sin foto seleccionada", fill="gray")
            self.foto_path_label.config(text="No se ha seleccionado ninguna foto.", foreground="gray")
        else:
            self.select_photo_btn.config(state="normal")

    def _actualizar_lista_catalogos(self):
        self.catalogo_combobox['values'] = obtener_catalogos_existentes()

    def _cargar_catalogo(self):
        nombre_catalogo = self.catalogo_combobox.get()
        if not nombre_catalogo:
            messagebox.showerror("Error", "Por favor, seleccione o ingrese un nombre para el catálogo.")
            return
        
        self.catalogo_actual = CatalogoProducto(nombre_catalogo)
        self.title(f"Gestor de Catálogos - {nombre_catalogo}")
        self._cargar_productos()

    def _nuevo_catalogo(self):
        nombre_nuevo = simpledialog.askstring("Nuevo Catálogo", "Ingrese el nombre del nuevo catálogo:")
        if nombre_nuevo and nombre_nuevo.strip():
            if nombre_nuevo in obtener_catalogos_existentes():
                messagebox.showerror("Error", f"El catálogo '{nombre_nuevo}' ya existe.")
            else:
                self.catalogo_actual = CatalogoProducto(nombre_nuevo)
                self.title(f"Gestor de Catálogos - {nombre_nuevo}")
                self._actualizar_lista_catalogos()
                self.catalogo_combobox.set(nombre_nuevo)
                self._cargar_productos()
        elif nombre_nuevo is not None:
            messagebox.showerror("Error", "El nombre del catálogo no puede estar vacío.")

    def _eliminar_catalogo(self):
        if not self.catalogo_actual:
            messagebox.showerror("Error", "No hay ningún catálogo cargado para eliminar.")
            return

        nombre = self.catalogo_actual.nombre
        if messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar el catálogo '{nombre}'? Esta acción no se puede deshacer."):
            if self.catalogo_actual.destruir_catalogo():
                messagebox.showinfo("Éxito", f"Catálogo '{nombre}' eliminado.")
                self.catalogo_actual = None
                self.title("Gestor de Catálogos")
                self._actualizar_lista_catalogos()
                self.catalogo_combobox.set("")
                self._limpiar_formulario_y_seleccion()
                self.tree.delete(*self.tree.get_children())
                self._mostrar_detalle_vacio()
            else:
                messagebox.showerror("Error", "Ocurrió un error al eliminar el catálogo.")

    def _exportar_a_excel(self):
        if not self.catalogo_actual:
            messagebox.showerror("Error", "No hay un catálogo cargado.")
            return

        productos = self.catalogo_actual.listar_productos()
        if not productos:
            messagebox.showinfo("Información", "El catálogo está vacío, no hay nada que exportar.")
            return
            
        try:
            data = [p.to_dict() for p in productos]
            df = pd.DataFrame(data)
            for col in ['ruta_foto_original', 'ruta_foto_optimizada']:
                if col in df.columns:
                    df = df.drop(columns=col)
            df = df.rename(columns={"precio_original": "preciooriginal"})

            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                title="Guardar como archivo de Excel",
                initialfile=f"catalogo_{self.catalogo_actual.nombre}.xlsx"
            )

            if filepath:
                df.to_excel(filepath, index=False, engine='openpyxl')
                messagebox.showinfo("Éxito", f"Catálogo exportado exitosamente a:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Error al Exportar", f"Ocurrió un error al exportar a Excel: {e}")

    def _cambiar_vista_productos(self, event=None):
        vista = self.view_selector.get()
        if vista == "Vista Simple":
            self.tree["columns"] = ("nombre", "tipo", "precio")
        else:
            self.tree["columns"] = ("nombre", "tipo", "color", "precio", "fecha_publicacion")

        for col in self.tree["columns"]:
            self.tree.heading(col, text=self.col_headers.get(col, col.capitalize()))
        
        self._cargar_productos()

    def _cargar_productos(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        if self.catalogo_actual:
            productos = self.catalogo_actual.listar_productos()
            for p in productos:
                valores = [getattr(p, col, '') for col in self.tree["columns"]]
                self.tree.insert("", "end", values=valores, iid=p.nombre)
        
        # Limpiar selección y panel
        self._limpiar_formulario_y_seleccion()
        self._mostrar_detalle_vacio()

    # ------------- Selección y edición -------------

    def _on_producto_select(self, event=None):
        if self.tree.selection():
            self.editar_btn.config(state="normal")
            self.duplicar_btn.config(state="normal")
            self.eliminar_btn.config(state="normal")
            
            item_id = self.tree.selection()[0]
            productos = self.catalogo_actual.listar_productos()
            self.producto_seleccionado = next((p for p in productos if p.nombre == item_id), None)
            
            if self.producto_seleccionado:
                self._actualizar_panel_detalles(self.producto_seleccionado)
        else:
            self.editar_btn.config(state="disabled")
            self.duplicar_btn.config(state="disabled")
            self.eliminar_btn.config(state="disabled")
            self.producto_seleccionado = None
            self._mostrar_detalle_vacio()

    def _editar_producto_seleccionado(self):
        if not self.producto_seleccionado:
            messagebox.showerror("Error", "Por favor, seleccione un producto para editar.")
            return
        self._rellenar_formulario(self.producto_seleccionado)

    def _rellenar_formulario(self, producto):
        self._limpiar_formulario()
        p = producto
        self.entries["nombre"].insert(0, p.nombre)
        self.entries["características"].insert(0, p.caracteristicas)
        self.entries["color"].insert(0, p.color)
        self.entries["tipo"].insert(0, p.tipo)
        precio_orig = getattr(p, '_Producto__precio_original', '')
        self.entries["preciooriginal"].insert(0, str(precio_orig))
        self.entries["precio"].insert(0, str(p.precio))
        self.entries["fechapublicación"].insert(0, p.fecha_publicacion)
        
        self.ruta_foto_seleccionada_src = ""
        if p.ruta_foto_original:
            ruta_abs = os.path.join(self.catalogo_actual.base_path, p.ruta_foto_original)
            if os.path.exists(ruta_abs):
                self.ruta_foto_seleccionada_src = ruta_abs  # ← mantengo ruta ABS para reusar
                self.mostrar_imagen_preview(ruta_abs)
                self.foto_path_label.config(text=os.path.basename(p.ruta_foto_original), foreground="black")
                self.no_photo_var.set(False)
                self._toggle_photo_selection()
        else:
            self.no_photo_var.set(True)
            self._toggle_photo_selection()

        self.guardar_btn.config(text="Actualizar Producto")

    def _limpiar_formulario(self):
        for entry in self.entries.values():
            entry.delete(0, "end")
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(190, 100, text="Sin imagen", fill="gray")
        self.img_tk_preview = None
        self.foto_path_label.config(text="No se ha seleccionado ninguna foto.", foreground="gray")
        self.ruta_foto_seleccionada_src = ""
        self.guardar_btn.config(text="Guardar Producto")
        self.no_photo_var.set(False)
        self.select_photo_btn.config(state="normal")

    def _limpiar_formulario_y_seleccion(self):
        self._limpiar_formulario()
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])
        self.producto_seleccionado = None
        self.editar_btn.config(state="disabled")
        self.duplicar_btn.config(state="disabled")
        self.eliminar_btn.config(state="disabled")

    # ------------- Imagen -------------

    def _seleccionar_foto(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen", 
            filetypes=(("Archivos de imagen", "*.jpg *.jpeg *.png *.gif *.bmp"), ("Todos los archivos", "*.*"))
        )
        if ruta:
            self.ruta_foto_seleccionada_src = ruta  # ← ruta ABS
            self.mostrar_imagen_preview(ruta)
            self.foto_path_label.config(text=os.path.basename(ruta), foreground="black")

    def mostrar_imagen_preview(self, ruta_imagen):
        try:
            img = Image.open(ruta_imagen)
            img.thumbnail((380, 200))
            self.img_tk_preview = ImageTk.PhotoImage(img)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(190, 100, image=self.img_tk_preview)
        except Exception as e:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(190, 100, text=f"Error al cargar imagen:\n{e}", 
                                            fill="red", width=370, font=("Arial", 9), justify="center")

    # ------------- Guardar / Editar / Eliminar / Duplicar -------------

    def _guardar_producto(self):
        if not self.catalogo_actual:
            messagebox.showerror("Error", "No hay un catálogo cargado.")
            return

        nombre = self.entries["nombre"].get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre del producto es obligatorio.")
            return

        es_actualizacion = self.producto_seleccionado is not None

        # ↳ si renombra en edición, validar duplicados
        if es_actualizacion:
            if nombre.lower() != self.producto_seleccionado.nombre.lower() and self.catalogo_actual.producto_existe(nombre):
                messagebox.showerror("Error", f"Ya existe un producto con el nombre '{nombre}'.")
                return
        else:
            if self.catalogo_actual.producto_existe(nombre):
                messagebox.showerror("Error", f"Ya existe un producto con el nombre '{nombre}'.")
                return

        try:
            precio_orig = float(self.entries["preciooriginal"].get().replace(",", ".")) if self.entries["preciooriginal"].get() else 0.0
            precio = float(self.entries["precio"].get().replace(",", ".")) if self.entries["precio"].get() else 0.0
        except ValueError:
            messagebox.showerror("Error de Formato", "El precio debe ser un número válido.")
            return

        datos_producto = {
            "nombre": nombre,
            "caracteristicas": self.entries["características"].get(),
            "color": self.entries["color"].get(),
            "tipo": self.entries["tipo"].get(),
            "precio_original": precio_orig,
            "precio": precio,
            "fecha_publicacion": self.entries["fechapublicación"].get() or datetime.date.today().isoformat()
        }
        if es_actualizacion:
            datos_producto["fecha_ingreso"] = self.producto_seleccionado.fecha_ingreso

        nuevo_producto = Producto.from_dict(datos_producto)
        # Reutiliza foto
        src_path = None
        if not self.no_photo_var.get():
            if self.ruta_foto_seleccionada_src:
                src_path = self.ruta_foto_seleccionada_src

        if es_actualizacion:
            ok = self.catalogo_actual.editar_producto(self.producto_seleccionado.nombre, nuevo_producto, src_path)
            if ok:
                messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
                self._limpiar_formulario_y_seleccion()
                self._cargar_productos()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el producto.")
        else:
            ok = self.catalogo_actual.agregar_producto(nuevo_producto, src_path)
            if ok:
                messagebox.showinfo("Éxito", "Producto agregado correctamente.")
                self._limpiar_formulario_y_seleccion()
                self._cargar_productos()
            else:
                messagebox.showerror("Error", "No se pudo agregar el producto.")

    def _eliminar_producto(self):
        if not self.producto_seleccionado:
            messagebox.showerror("Error", "Por favor, seleccione un producto para eliminar.")
            return
        
        nombre = self.producto_seleccionado.nombre
        if messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar el producto '{nombre}'?"):
            if self.catalogo_actual.eliminar_producto(nombre):
                messagebox.showinfo("Éxito", "Producto eliminado.")
                self._limpiar_formulario_y_seleccion()
                self._cargar_productos()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el producto.")

    def _duplicar_producto(self):
        if not self.producto_seleccionado:
            messagebox.showerror("Error", "Por favor, seleccione un producto para duplicar.")
            return

        nuevo_nombre = simpledialog.askstring(
            "Duplicar Producto", 
            "Ingrese el nuevo nombre para el producto duplicado:",
            initialvalue=f"{self.producto_seleccionado.nombre} - Copia"
        )
        if nuevo_nombre is None:
            return
        if not nuevo_nombre.strip():
            messagebox.showerror("Error", "El nombre del producto duplicado no puede estar vacío.")
            return
        if self.catalogo_actual.producto_existe(nuevo_nombre):
            messagebox.showerror("Error", f"Ya existe un producto con el nombre '{nuevo_nombre}'.")
            return

        datos = self.producto_seleccionado.to_dict()
        datos["nombre"] = nuevo_nombre
        nuevo_producto = Producto.from_dict(datos)

        # Ruta absoluta
        src_path = None
        if self.producto_seleccionado.ruta_foto_original:
            posible_abs = os.path.join(self.catalogo_actual.base_path, self.producto_seleccionado.ruta_foto_original)
            if os.path.exists(posible_abs):
                src_path = posible_abs

        if self.catalogo_actual.agregar_producto(nuevo_producto, src_path):
            messagebox.showinfo("Éxito", "Producto duplicado correctamente.")
            self._cargar_productos()
        else:
            messagebox.showerror("Error", "No se pudo duplicar el producto.")


if __name__ == "__main__":
    App().mainloop()
