package cl.peluditos;

import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.FormParam;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.BadRequestException;
import java.time.LocalDate;
import java.util.Map;

@Path("/")
public class PeluditosResource {
    // La prueba de integración usa esta ruta para comprobar que Java responde.
    @GET
    @Path("health")
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, String> health() {
        return Map.of("estado", "ok");
    }

    // El worker pide un borrador que la dueña revisará en la bandeja del proceso.
    @POST
    @Path("api/sugerencia")
    @Consumes(MediaType.APPLICATION_FORM_URLENCODED)
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, String> sugerencia(
            @FormParam("nombre") String nombre,
            @FormParam("mascota") String mascota,
            @FormParam("tipo") String tipo,
            @FormParam("evento") String evento) {
        String cliente = valor(nombre, "cliente");
        String nombreMascota = valor(mascota, "tu mascota");
        String tipoMascota = valor(tipo, "mascota");
        String ocasion = valor(evento, "CUMPLEANOS");
        String mensaje;
        if ("CUMPLEANOS".equalsIgnoreCase(ocasion)) {
            mensaje = "Hola " + cliente + ", se acerca el cumpleaños de " + nombreMascota
                    + ". En Peluditos Pet Chile podemos preparar una torta especial para tu "
                    + tipoMascota + ". Si te interesa, responde este mensaje y coordinamos los detalles.";
        } else {
            mensaje = "Hola " + cliente + ", para " + ocasion + " tenemos una idea especial para "
                    + nombreMascota + " en Peluditos Pet Chile. Si te interesa, conversemos.";
        }
        return Map.of("mensaje", mensaje);
    }

    // El código se genera con el día y el mes y es el mismo para todos los clientes de ese día.
    @POST
    @Path("api/cupon")
    @Consumes(MediaType.APPLICATION_FORM_URLENCODED)
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, String> cupon(@FormParam("clienteId") String clienteId) {
        if (clienteId == null || clienteId.isBlank()) throw new BadRequestException("Falta clienteId");
        LocalDate hoy = LocalDate.now();
        String[] meses = {"ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
                          "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"};
        return Map.of("codigo", "PELUDITOS-" + String.format("%02d", hoy.getDayOfMonth())
                + meses[hoy.getMonthValue() - 1]);
    }

    // Traduce el resultado del BPMN al estado que el worker guarda en la ficha del panel.
    @POST
    @Path("api/estado")
    @Consumes(MediaType.APPLICATION_FORM_URLENCODED)
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, String> estado(@FormParam("resultado") String resultado) {
        if ("COMPRA".equals(resultado)) return Map.of("estado", "CLIENTE");
        if ("NO_CONCRETADA".equals(resultado)) return Map.of("estado", "NO CONCRETADO");
        throw new BadRequestException("Resultado inválido");
    }

    @POST
    @Path("api/envio")
    @Consumes(MediaType.APPLICATION_FORM_URLENCODED)
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, Object> envio(@FormParam("destinatario") String destinatario,
                                     @FormParam("mensaje") String mensaje) {
        if (destinatario == null || destinatario.isBlank() || mensaje == null || mensaje.isBlank())
            throw new BadRequestException("Faltan destinatario o mensaje");
        // Devuelve una confirmación simulada para que el worker pueda continuar el proceso.
        return Map.of("simulado", true, "destinatario", destinatario);
    }

    private String valor(String texto, String defecto) {
        return texto == null || texto.isBlank() ? defecto : texto.trim();
    }
}
