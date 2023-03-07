# SIO GRANOS

## Introducción

SIO GRANOS es un sistema de información de operaciones de granos que tiene información hasta el día anterior al de la consulta. La carga de las operaciones a través de este sistema origina una **fuente de datos muy potente para los analistas del mercado granario**. No sólo la información es más actualizada que la que publican los organismos oficiales, si no que tiene mayores niveles de detalle. Las variables que se pueden explorar son:

* La procedencia a nivel de localidad de las operaciones.
* Los destinos por zona.
* Los tipos de contratos.
* Entre otros. 

Algunos trabajos a la fecha realizados con SIO GRANOS son [negociacion de soja por BCR](https://www.bcr.com.ar/es/mercados/investigacion-y-desarrollo/informativo-semanal/noticias-informativo-semanal/patrones-del), el [análisis del programa de incremento exportador de BCR](https://www.bcr.com.ar/es/mercados/mercado-de-granos/noticias/restando-5-dias-para-su-finalizacion-el-programa-de-incremento), o el [mapa de comercialización de granos en argentina de la Bolsa de Cereales de Buenos Aires](https://www.bolsadecereales.com/post-2#:~:text=SIO-GRANOS%20es%20un%20Sistema%20unificado%20de%20Informaci%C3%B3n%20Obligatoria,sistema%20y%20realizar%20declaraciones%20de%20las%20operaciones%20realizadas.).


## Inconvenientes

**El tratamiento de los datos ha sido un problema desde la aparición de SIO-granos.**

La problemática a la que se enfrenta quien por primera vez quiere analizar estos datos es la tediosa descarga de los mismos, que solo permite un máximo de 180 días de operaciones por descarga. Además, debido al gran volumen de datos no es posible que sean manipulados en excel.

Otro problema usual es la difícil interpretación de los datos, que puede llevar a diferencias entre distintos organismos en cuanto a criterios a tomar en cuenta para no duplicar información y analizar correctamente lo que se busca informar. Esto está fuera del alcance del trabajo y queda sujeto a la calidad del análisis de cada organismo.

## Soluciones

**El presente trabajo viene a solucionar dos cuestiones**:

1) Gestionar la descarga de datos a través de 2 componentes:
    
    a) **Web scraping:** se automatiza la consulta y descarga de los datos.
    
    b) **Servidor:** se introducen los datos en una base de datos relacional. 
  
2) Reducción de la cantidad de datos para permitir un análisis más fluido con herramientas de uso común como Excel.

Estas soluciones están separadas en dos programas que fueron creados para funcionar en cualquier dispositivo que cuente con Chrome, Python y MySQL. La salida es un documento con menor cantidad de datos pasible de ser analizado con excel.



