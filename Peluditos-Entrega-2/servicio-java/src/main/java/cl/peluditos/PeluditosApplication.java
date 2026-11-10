package cl.peluditos;

import java.net.URI;
import org.glassfish.jersey.jackson.JacksonFeature;
import org.glassfish.grizzly.http.server.HttpServer;
import org.glassfish.jersey.grizzly2.httpserver.GrizzlyHttpServerFactory;
import org.glassfish.jersey.server.ResourceConfig;

public class PeluditosApplication {
    public static void main(String[] args) throws Exception {
        int puerto = Integer.parseInt(System.getenv().getOrDefault("PELUDITOS_API_PORT", "8091"));
        URI uri = URI.create("http://127.0.0.1:" + puerto + "/");
        HttpServer servidor = GrizzlyHttpServerFactory.createHttpServer(uri,
                new ResourceConfig(PeluditosResource.class, JacksonFeature.class));
        System.out.println("Servicio Peluditos activo en " + uri);
        Thread.currentThread().join();
        servidor.shutdownNow();
    }
}
