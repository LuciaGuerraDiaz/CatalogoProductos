# 📂 Estructura del proyecto Gestor de Catálogos de Películas

# El proyecto está organizado de la siguiente manera:

# catalogos/
# Carpeta principal donde se almacenan los distintos catálogos de películas.

#     PresentacionFinal/
#     Contiene un subcatálogo con sus propios archivos.

#     portadas/ → Carpeta destinada a guardar las imágenes de portada de las películas.

#     catalogo.json → Archivo JSON con la información del catálogo de películas de esta sección.

#     Terror/
#     Otro subcatálogo de películas, especializado en el género de terror.

#     portadas/ → Carpeta con las portadas de las películas de terror.

#     catalogo.json → Archivo JSON que almacena los datos del catálogo de películas de terror.

# catalogo.py
# Script en Python que probablemente maneja la lógica de carga, guardado y gestión de los catálogos.

# interfaz.py
# Archivo encargado de la interfaz gráfica, posiblemente construida con PyQt5.

# main.py
# Archivo principal del proyecto. Es muy probable que este sea el punto de entrada para ejecutar la aplicación.

# pelicula.py
# Script que podría definir la clase o estructura de datos de una película (título, género, portada, etc.).

# LICENSE
# Archivo de licencia del proyecto.

# README.md
# Documento de introducción y guía sobre el uso del proyecto.

# requirements.txt
# Archivo con las dependencias necesarias para ejecutar el proyecto. En este caso:

# PyQt5==5.15.7
# Pillow==10.4.0

# PRESENTACIÓN DEL PROYECTO

# El objetivo consiste en desarrollar un programa que permita llevar un registro de películas aplicando conceptos de programación orientada a objetos.
# El funcionamiento esperado es el siguiente:
# Al ejecutar el programa se solicita ingresar el nombre del catálogo de películas:
# Si el catálogo de películas no existe se creará uno nuevo. Este catálogo se va a guardar en un archivo txt donde posteriormente se guardarán las películas. Si el catálogo existe se podrá seguir modificando el archivo.
# Se debe mostrar un menú de opciones, que permita realizar las siguientes operaciones:
# Agregar Película
# Listar Películas
# Eliminar catálogo películas
# Salir

# OBJETIVOS

# Funcionamiento de las opciones:
# Agregar Película: se va a solicitar el nombre de la película y esta película se va a guardar en el archivo txt.
# Listar Películas: va a mostrar todas las películas del catálogo y guardadas en el archivo txt.
# Eliminar catálogo: elimina el archivo txt que corresponde al catálogo de películas.
# Salir: debe finalizar el programa mostrando un mensaje al usuario.
# Implementación POO:
# El programa debe implementar programación orientada a objetos.
# Se solicita:
# Clase Pelicula.
# Uno de sus atributos debe ser privado.
# Clase CatalogoPelicula.
# atributo nombre
# atributo ruta_archivo
# métodos: agregar, listar, eliminar