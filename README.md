overdrive_tool!
--------------

Es un script realizado en python para windows que permite guardar la configuración del overclocking de GPUs AMDs

Intalación
--------------

Puedes descargar esta projecto o hacer un git clone a 

#### Como usar:
* **Establecer un número de serie** diferente a cada tarjeta. Para ello utilizar atiflash --prod N [numero_serie de 12 dígitos] ej: atiflash --prod 0 000000000001 . En la carpeta "atiflash_284" tenemos la version de atiflash compatible con el script
* **Configurar cada GPU** con el programa OverdriveNtool el cual está en la carpeta "overdrive"
* **Guardar profile** una vez estén configuradas todas las tarjetas gráficas ejecutar como administrador overdrive_configure.py --profile [nombre de fichero] . Con este comando se creará un fichero con los datos de configuracion actual de las tarjetas.
* **Establecer profile** a las tarjetas. Para ello una vez que ya se tenga el profile se ejecuta overdrive_configure.py --configure [nombre del fichero]


#### Tips:
* **Insertar una tarjeta nueva** o cambiar alguna de posición si ya tienes el fichero de configuracion. Primero ejecutas overdrive_configure.py --configure para las tarjetas con la configuracion que tenías y despues ejecutas overdrive_configure.py --profile y así obtienes un profile ordenado según el orden de tarjetas actual.