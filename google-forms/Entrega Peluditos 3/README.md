# Google Forms

El [formulario público de interesados](https://docs.google.com/forms/d/e/1FAIpQLSfQXc1wRTgWDC87UfuDrFk_r70bbCT563iSCGbNKLHf--LBfg/viewform) ya está publicado. El enlace viene en `config.example` y aparece en **Formulario** después de la instalación. Puedes compartir ese enlace con interesados.

## Usar el formulario ya publicado

La copia privada para la dueña incluye `config.local.forms` en la misma carpeta que `iniciar-panel.cmd`. Extrae el ZIP completo. El panel lee este archivo al arrancar, incluso si se mueve la carpeta. PostgreSQL conserva por separado la configuración propia del computador. [Instalación y arranque](../README.md)

Para una instalación existente, el equipo puede copiar únicamente `config.local.forms` desde la copia privada junto a `iniciar-panel.cmd` y reiniciar el panel. Las instalaciones anteriores que ya tienen los valores en `config.local` también funcionan. Para GitHub usa la copia pública. Comparte el ZIP privado solo con quienes estén autorizados a leer las respuestas.

`config.local` está excluido por Git. Al incorporar esta carpeta al monorepo, usa un commit de Git y comprueba que el archivo no aparezca entre los cambios preparados. La clave da acceso a respuestas de personas interesadas.

## Crear y publicar un formulario nuevo

Se hace una vez desde la cuenta de Peluditos. Google solicita a la persona titular que autorice al script a crear el formulario y acceder a sus respuestas.

1. Ejecuta `configurar-google-forms.cmd`. Se abrirá `config.local` con una clave aleatoria de sincronización. Guarda esa clave para el paso 4.
2. En la cuenta de Peluditos, abre [Google Apps Script](https://script.google.com/), crea un proyecto, sustituye el contenido del editor por [Code.gs](Code.gs) y guarda. En **Configuración del proyecto**, selecciona la zona horaria de Santiago.
3. Selecciona la función `crearFormulario`, pulsa **Ejecutar** y autoriza el acceso. En el registro de ejecución aparece el enlace **Editar y publicar**. Ábrelo, pulsa **Publicar** y en el acceso para responder elige **Cualquier persona con el enlace**. Copia el enlace para responder y ábrelo en una ventana privada para comprobar que permite responder sin iniciar sesión.
4. Vuelve a Apps Script. En **Configuración del proyecto → Propiedades de la secuencia de comandos**, agrega la propiedad `SYNC_KEY` con el valor de `GOOGLE_FORMS_SYNC_KEY` de tu `config.local`.
5. En Apps Script, pulsa **Implementar → Nueva implementación → Aplicación web**. Selecciona **Ejecutar como yo** y **Quién tiene acceso → Cualquiera**. Implementa y copia la URL que termina en `/exec`.
6. En `config.local`, pon el enlace para responder en `GOOGLE_FORMS_PUBLIC_URL` y la URL de Apps Script en `GOOGLE_FORMS_EXEC_URL`. Guarda y reinicia el panel.

El formulario pide nombre y apellido, WhatsApp, correo, red social, tipo de mascota, nombre de la mascota y cumpleaños. La pestaña **Formulario** permite copiar el enlace para responder.

Para comprobar la integración, envía una respuesta ficticia, abre el panel y espera a que el worker la procese. En **Hoy** debe aparecer el interesado. Si abres el panel de nuevo o pulsas **Actualizar respuestas**, la misma respuesta conserva un solo registro. Con el panel abierto se consulta cada 30 segundos. Flowable registra el cupón y el servicio simula el envío por correo.
