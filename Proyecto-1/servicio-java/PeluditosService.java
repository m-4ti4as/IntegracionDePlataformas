// Importa la clase que contiene una petición HTTP y su respuesta.
import com.sun.net.httpserver.HttpExchange;
// Importa el servidor HTTP que viene con Java.
import com.sun.net.httpserver.HttpServer;
// Importa el tipo de error de entrada y salida.
import java.io.IOException;
// Importa la dirección compuesta por IP y puerto.
import java.net.InetSocketAddress;
// Importa el decodificador de datos de formulario.
import java.net.URLDecoder;
// Importa la codificación de texto UTF-8.
import java.nio.charset.StandardCharsets;
// Importa la implementación del mapa de campos.
import java.util.HashMap;
// Importa la interfaz que describe un mapa clave-valor.
import java.util.Map;

/** Servicio REST de prueba: genera una sugerencia de campaña para una mascota. */
// Declara la clase principal del servicio y evita que otras clases la hereden.
public final class PeluditosService {
    // Define una función para escapar texto que irá dentro de JSON.
    private static String escape(String value) {
        // Escapa barras invertidas y comillas dobles para que el JSON sea válido.
        return value.replace("\\", "\\\\").replace("\"", "\\\"")
                // Escapa saltos de línea y retornos de carro.
                .replace("\n", "\\n").replace("\r", "\\r");
    // Cierra la función que escapa texto.
    }

    // Define una función que interpreta los campos enviados como formulario.
    private static Map<String, String> form(String body) {
        // Crea un mapa vacío donde se guardarán los campos recibidos.
        Map<String, String> values = new HashMap<>();
        // Recorre los campos separados por el carácter &.
        for (String item : body.split("&")) {
            // Divide cada campo en nombre y valor; el límite de dos preserva signos igual dentro del valor.
            String[] pair = item.split("=", 2);
            // Procesa solamente los campos que tienen nombre y valor.
            if (pair.length == 2) {
                // Decodifica el nombre del campo y comienza a guardarlo en el mapa.
                values.put(URLDecoder.decode(pair[0], StandardCharsets.UTF_8),
                        // Decodifica el valor del campo y completa su inserción en el mapa.
                        URLDecoder.decode(pair[1], StandardCharsets.UTF_8));
            // Cierra la comprobación del par nombre-valor.
            }
        // Termina de recorrer los campos del formulario.
        }
        // Devuelve el mapa con los datos recibidos.
        return values;
    // Cierra la función que interpreta el formulario.
    }

    // Define una función para enviar una respuesta HTTP con código de estado y JSON.
    private static void respond(HttpExchange exchange, int status, String json) throws IOException {
        // Convierte el texto JSON en bytes con codificación UTF-8.
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        // Informa al cliente que el cuerpo de la respuesta contiene JSON en UTF-8.
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        // Envía el código de estado y el tamaño del cuerpo de la respuesta.
        exchange.sendResponseHeaders(status, bytes.length);
        // Abre el cuerpo de salida y garantiza que se cierre automáticamente.
        try (var output = exchange.getResponseBody()) {
            // Escribe los bytes JSON en la respuesta.
            output.write(bytes);
        // Cierra el cuerpo de respuesta.
        }
    // Cierra la función que envía respuestas HTTP.
    }

    // Define una función que lee un campo con valor alternativo.
    private static String field(Map<String, String> values, String key, String fallback) {
        // Lee el campo, usa texto vacío si no existe y quita espacios exteriores.
        String value = values.getOrDefault(key, "").trim();
        // Devuelve el valor alternativo cuando el campo quedó vacío.
        return value.isEmpty() ? fallback : value;
    // Cierra la función que lee un campo.
    }

    // Define el punto de entrada que Java ejecuta al iniciar el servicio.
    public static void main(String[] args) throws Exception {
        // Obtiene el puerto de la variable de entorno o usa 8091 por defecto.
        int port = Integer.parseInt(System.getenv().getOrDefault("PELUDITOS_API_PORT", "8091"));
        // Crea el servidor en la interfaz local y el puerto elegido.
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", port), 0);
        // Publica una ruta de salud que devuelve estado ok.
        server.createContext("/health", exchange -> respond(exchange, 200, "{\"estado\":\"ok\"}"));
        // Publica la ruta que generará la sugerencia de mensaje.
        server.createContext("/api/sugerencia", exchange -> {
            // Comprueba si la solicitud usa el método POST.
            if (!"POST".equals(exchange.getRequestMethod())) {
                // Devuelve el error HTTP 405 cuando se usa otro método.
                respond(exchange, 405, "{\"error\":\"Use POST\"}");
                // Detiene el procesamiento de esa solicitud incorrecta.
                return;
            // Cierra la comprobación del método HTTP.
            }
            // Lee todo el cuerpo de la solicitud como texto UTF-8.
            String body = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
            // Convierte el cuerpo del formulario en un mapa de campos.
            Map<String, String> values = form(body);
            // Lee el nombre de quien recibirá el mensaje o usa cliente.
            String dueno = field(values, "nombre", "cliente");
            // Lee el nombre de la mascota o usa un texto general.
            String mascota = field(values, "mascota", "tu mascota");
            // Lee el tipo de mascota o usa mascota.
            String tipo = field(values, "tipo", "mascota");
            // Lee el evento o usa cumpleaños como valor predeterminado.
            String evento = field(values, "evento", "CUMPLEANOS");
            // Declara la variable donde se guardará el mensaje sugerido.
            String mensaje;
            // Decide si corresponde utilizar el texto específico de cumpleaños.
            if ("CUMPLEANOS".equalsIgnoreCase(evento)) {
                // Comienza a construir el saludo y menciona la mascota.
                mensaje = "Hola " + dueno + ", se acerca el cumpleaños de " + mascota
                        // Agrega la propuesta de una torta de Peluditos Pet Chile.
                        + ". En Peluditos Pet Chile podemos preparar una torta especial para tu "
                        // Agrega el tipo de mascota y la invitación a conversar.
                        + tipo + ". Si te interesa, responde este mensaje y coordinamos los detalles.";
            // Abre la alternativa para otros eventos.
            } else {
                // Comienza un mensaje que menciona el evento recibido.
                mensaje = "Hola " + dueno + ", para " + evento + " tenemos una idea especial para "
                        // Completa la propuesta y la invitación a conversar.
                        + mascota + " en Peluditos Pet Chile. Si te interesa, conversemos.";
            // Cierra la elección entre cumpleaños y otros eventos.
            }
            // Devuelve el mensaje sugerido en formato JSON con estado HTTP 200.
            respond(exchange, 200, "{\"mensaje\":\"" + escape(mensaje) + "\"}");
        // Cierra la configuración de la ruta de sugerencias.
        });
        // Enciende el servidor para comenzar a recibir solicitudes.
        server.start();
        // Muestra en consola la dirección local donde quedó disponible.
        System.out.println("Servicio Peluditos activo en http://127.0.0.1:" + port);
    // Cierra el método principal.
    }
// Cierra la clase del servicio.
}
