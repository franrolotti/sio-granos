# SIO GRANOS

SIO GRANOS es un sistema de información de operaciones de granos que tiene información hasta el día anterior al de la solicitud de datos. La carga de las operaciones a través de este sistema origina una **fuente de datos muy potente para los analistas del mercado granario**. No sólo la información es más actualizada que la que publican los organismos oficiales, si no que tiene mayores niveles de detalle, como por ejemplo la procedencia a nivel de localidad de las operaciones, los destinos, los tipos de contratos, entre otros. Sin embargo, **el tratamiento de los datos ha sido un problema desde la aparición de SIO-granos.**

La problemática a la que se enfrenta quien por primera vez quiere analizar estos datos es la tediosa descarga de los mismos, que solo permite un máximo de 180 días de operaciones por descarga. Además, debido al gran volumen de datos no es posible que sean manipulados en excel.

**El presente trabajo viene a solucionar dos cuestiones**:

1) Gestionar la descarga de datos a través de 2 componentes:
    
    a) **Web scraping:** se automatiza la consulta y descarga de los datos.
    
    b) **Servidor:** se introducen los datos en una base de datos relacional. 
  
2) Reducción de la cantidad de datos para permitir un análisis más fluido con herramientas de uso común como Excel.

Estas soluciones están separadas en dos programas que fueron creados para funcionar en cualquier dispositivo que cuente con Chrome y con Python. 
