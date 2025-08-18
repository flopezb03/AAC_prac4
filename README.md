# Arquitecturas Avanzadas de Computadores - Practica 4. Arquitecturas de Memoria Compartida

La memoria compartida es un tipo de memoria que puede ser accedida desde múltiples procesos. Esta memoria se puede usar para la comunicación entre procesos, los cuales pueden estar ejecutándose en el mismo procesador o en diferentes. La memoria usada entre hilos también es memoria compartida. 

En arquitecturas de memoria compartida, esta es un recurso común que sirve para comunicación, sincronización y evitar redundancia entre varios procesos o hilos. Sin embargo, esta capacidad conlleva ciertos problemas relacionados con la sincronización de los accesos a la memoria compartida ya que múltiples procesos o hilos pueden intentar modificar los mismos datos simultáneamente provocando “condiciones de carrera”. Para evitar estos problemas se usan mecanismos de sincronización que permiten coordinar los accesos a recursos compartidos. Semáforos y mutex (semáforos binarios) son algunos de estos mecanismos.

Las arquitecturas de memoria compartida permiten maximizar el rendimiento de los programas mediante la ejecución en paralelo de múltiples procesos o hilos.

Con la práctica realizada se pretende hacer un programa con múltiples hilos que deben sincronizarse para usar recursos compartidos sin condiciones de carrera. El contexto del programa será el juego de la sabana africana donde habrá un entorno (tablero con casillas) y varias manadas de animales de diferentes especies (leones, hienas y cebras). Los animales (cada uno es un hilo) deberán interactuar con el entorno o con otros animales. Podrán moverse a otras casillas, cazar a otros animales o descansar. Las cazas se traducen en puntos para la manada del animal cazador, y la primera manada que llegue a 20 puntos ganará el juego.
