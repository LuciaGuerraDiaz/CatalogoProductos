import datetime

class Producto:
    def __init__(self, nombre, caracteristicas, color, tipo, precio_original, precio, fecha_ingreso=None, fecha_publicacion=None):
        self.nombre = nombre
        self.caracteristicas = caracteristicas
        self.color = color
        self.tipo = tipo
        self.__precio_original = precio_original
        self.precio = precio
        self.fecha_ingreso = fecha_ingreso or datetime.date.today().isoformat()
        self.fecha_publicacion = fecha_publicacion or ""
        self.ruta_foto_original = None
        self.ruta_foto_optimizada = None

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "caracteristicas": self.caracteristicas,
            "color": self.color,
            "tipo": self.tipo,
            "precio_original": self.__precio_original,
            "precio": self.precio,
            "fecha_ingreso": self.fecha_ingreso,
            "fecha_publicacion": self.fecha_publicacion,
            "ruta_foto_original": self.ruta_foto_original,
            "ruta_foto_optimizada": self.ruta_foto_optimizada
        }

    @classmethod
    def from_dict(cls, data):
        p = cls(
            nombre=data["nombre"],
            caracteristicas=data.get("caracteristicas", ""),
            color=data.get("color", ""),
            tipo=data.get("tipo", ""),
            precio_original=data.get("precio_original", 0),
            precio=data.get("precio", 0),
            fecha_ingreso=data.get("fecha_ingreso"),
            fecha_publicacion=data.get("fecha_publicacion", "")
        )
        p.ruta_foto_original = data.get("ruta_foto_original")
        p.ruta_foto_optimizada = data.get("ruta_foto_optimizada")
        return p
