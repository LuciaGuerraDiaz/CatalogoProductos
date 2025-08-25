import os
import json
import shutil
from producto import Producto

class CatalogoProducto:
    def __init__(self, nombre_catalogo):
        self.nombre = nombre_catalogo
        self.base_path = os.path.join("catalogos", self.nombre)
        self.productos_path = os.path.join(self.base_path, "productos")
        self.ruta_archivo = os.path.join(self.base_path, "catalogo.json")
        self._inicializar_catalogo()

    def _inicializar_catalogo(self):
        os.makedirs(self.productos_path, exist_ok=True)
        if not os.path.exists(self.ruta_archivo):
            with open(self.ruta_archivo, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _cargar_datos(self):
        if os.path.exists(self.ruta_archivo):
            with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _guardar_datos(self, data):
        with open(self.ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def producto_existe(self, nombre):
        productos = self._cargar_datos()
        return any(p["nombre"].lower() == nombre.lower() for p in productos)

    def agregar_producto(self, producto_obj, src_path_original=None):
        try:
            if src_path_original:
                if os.path.exists(src_path_original):
                    nombre_foto_orig = os.path.basename(src_path_original)
                    dest_path_orig = os.path.join(self.productos_path, nombre_foto_orig)
                    if os.path.abspath(src_path_original) != os.path.abspath(dest_path_orig):
                        shutil.copy2(src_path_original, dest_path_orig)
                    producto_obj.ruta_foto_original = os.path.relpath(dest_path_orig, self.base_path).replace("\\", "/")
            else:
                producto_obj.ruta_foto_original = None
                producto_obj.ruta_foto_optimizada = None

            productos = self._cargar_datos()
            productos.append(producto_obj.to_dict())
            self._guardar_datos(productos)
            return True
        except Exception as e:
            print(f"❌ Error al agregar producto: {e}")
            return False

    def editar_producto(self, nombre_original, producto_actualizado, src_path_original=None):
        try:
            productos = self._cargar_datos()
            for i, p in enumerate(productos):
                if p["nombre"].lower() == nombre_original.lower():
                    if src_path_original and os.path.exists(src_path_original):
                        nombre_foto_orig = os.path.basename(src_path_original)
                        dest_path_orig = os.path.join(self.productos_path, nombre_foto_orig)
                        if os.path.abspath(src_path_original) != os.path.abspath(dest_path_orig):
                            shutil.copy2(src_path_original, dest_path_orig)
                        producto_actualizado.ruta_foto_original = os.path.relpath(dest_path_orig, self.base_path).replace("\\", "/")
                    else:
                        producto_actualizado.ruta_foto_original = p.get("ruta_foto_original")
                        producto_actualizado.ruta_foto_optimizada = p.get("ruta_foto_optimizada")

                    productos[i] = producto_actualizado.to_dict()
                    self._guardar_datos(productos)
                    return True
            return False
        except Exception as e:
            print(f"❌ Error al editar producto: {e}")
            return False

    def listar_productos(self):
        data = self._cargar_datos()
        return [Producto.from_dict(d) for d in data]

    def eliminar_producto(self, nombre):
        productos = self._cargar_datos()
        producto_a_eliminar = next((p for p in productos if p["nombre"] == nombre), None)
        if not producto_a_eliminar:
            return False

        nuevos_productos = [p for p in productos if p["nombre"] != nombre]

        if producto_a_eliminar.get("ruta_foto_original"):
            ruta_foto = producto_a_eliminar["ruta_foto_original"]
            es_usada = any(p.get("ruta_foto_original") == ruta_foto for p in nuevos_productos)
            if not es_usada:
                ruta_abs_foto = os.path.join(self.base_path, ruta_foto)
                if os.path.exists(ruta_abs_foto):
                    try:
                        os.remove(ruta_abs_foto)
                    except OSError as e:
                        print(f"Error eliminando foto: {e}")

        self._guardar_datos(nuevos_productos)
        return True

    def destruir_catalogo(self):
        try:
            if os.path.exists(self.base_path):
                shutil.rmtree(self.base_path)
            return True
        except Exception as e:
            print(f"Error al eliminar catálogo: {e}")
            return False
