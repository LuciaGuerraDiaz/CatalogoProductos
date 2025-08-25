import os
import datetime
from catalogo import CatalogoProducto
from producto import Producto

def mostrar_menu():
    print("\n--- Gestor de Catálogos ---")
    print("1. Agregar Producto")
    print("2. Listar Productos")
    print("3. Eliminar Producto")
    print("4. Eliminar Catálogo Completo")
    print("5. Salir")
    print("6. Editar Producto")
    return input("Seleccione una opción: ")

def main():
    nombre_catalogo = input("Ingrese el nombre del catálogo a gestionar: ").strip()
    if not nombre_catalogo:
        print("Error: El nombre del catálogo no puede estar vacío.")
        return
        
    catalogo = CatalogoProducto(nombre_catalogo)
    print(f"Catálogo '{nombre_catalogo}' cargado/creado exitosamente.")

    while True:
        opcion = mostrar_menu()

        if opcion == '1':
            print("\n--- Agregar Nuevo Producto ---")
            nombre = input("Nombre del producto: ").strip()
            if not nombre:
                print("Error: El nombre del producto es obligatorio.")
                continue

            caracteristicas = input("Características: ")
            color = input("Color: ")
            tipo = input("Tipo (ej: Remera manga corta): ")
            try:
                precio_original = float(input("Precio Original: ").replace(',', '.'))
                precio = float(input("Precio de Venta: ").replace(',', '.'))
            except ValueError:
                print("Error: Los precios deben ser números válidos.")
                continue
            
            fecha_publicacion = input("Fecha de publicación (YYYY-MM-DD) [auto: hoy]: ") or datetime.date.today().isoformat()
            src_path = input("Ruta de la foto del producto (dejar vacío si no hay foto): ").strip() or None

            nuevo_producto = Producto(
                nombre=nombre,
                caracteristicas=caracteristicas,
                color=color,
                tipo=tipo,
                precio_original=precio_original,
                precio=precio,
                fecha_publicacion=fecha_publicacion
            )
            
            if catalogo.agregar_producto(nuevo_producto, src_path):
                print(f"Producto '{nombre}' agregado con éxito.")
            else:
                print("Hubo un error al agregar el producto.")

        elif opcion == '2':
            print("\n--- Listado de Productos ---")
            productos = catalogo.listar_productos()
            if not productos:
                print("El catálogo está vacío.")
            else:
                for p in productos:
                    print(f"- Nombre: {p.nombre}, Tipo: {p.tipo}, Precio: ${p.precio:,.2f}")

        elif opcion == '3':
            nombre_prod_eliminar = input("Ingrese el nombre exacto del producto a eliminar: ").strip()
            if catalogo.eliminar_producto(nombre_prod_eliminar):
                print(f"Producto '{nombre_prod_eliminar}' eliminado correctamente.")
            else:
                print(f"Error: No se encontró un producto con el nombre '{nombre_prod_eliminar}'.")

        elif opcion == '4':
            confirmacion = input(f"¿Está SEGURO de que desea eliminar el catálogo '{catalogo.nombre}'? (s/n): ").lower()
            if confirmacion == 's':
                if catalogo.destruir_catalogo():
                    print(f"Catálogo '{catalogo.nombre}' eliminado con éxito.")
                    break 
                else:
                    print("Ocurrió un error al eliminar el catálogo.")

        elif opcion == '5':
            print("\nGracias por usar el gestor de catálogos.")
            break

        elif opcion == '6':
            print("\n--- Editar Producto ---")
            nombre_original = input("Nombre del producto a editar: ").strip()
            productos = catalogo.listar_productos()
            prod = next((p for p in productos if p.nombre.lower() == nombre_original.lower()), None)
            if not prod:
                print("Error: Producto no encontrado.")
                continue

            print("Dejar en blanco para mantener el valor actual.")
            nombre = input(f"Nombre [{prod.nombre}]: ").strip() or prod.nombre
            caracteristicas = input(f"Características [{prod.caracteristicas}]: ").strip() or prod.caracteristicas
            color = input(f"Color [{prod.color}]: ").strip() or prod.color
            tipo = input(f"Tipo [{prod.tipo}]: ").strip() or prod.tipo
            try:
                precio_original = float(input(f"Precio Original [{getattr(prod, '_Producto__precio_original', 0)}]: ").replace(',', '.') or getattr(prod, '_Producto__precio_original', 0))
                precio = float(input(f"Precio de Venta [{prod.precio}]: ").replace(',', '.') or prod.precio)
            except ValueError:
                print("Error: Los precios deben ser números válidos.")
                continue
            fecha_publicacion = input(f"Fecha de publicación [{prod.fecha_publicacion}]: ").strip() or prod.fecha_publicacion
            src_path = input("Nueva ruta de foto (ENTER para mantener actual / vacío para quitar): ").strip() or None

            producto_actualizado = Producto(
                nombre=nombre,
                caracteristicas=caracteristicas,
                color=color,
                tipo=tipo,
                precio_original=precio_original,
                precio=precio,
                fecha_ingreso=prod.fecha_ingreso,
                fecha_publicacion=fecha_publicacion
            )

            if catalogo.editar_producto(nombre_original, producto_actualizado, src_path):
                print("Producto actualizado con éxito.")
            else:
                print("Error al actualizar el producto.")

        else:
            print("Opción no válida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main()
