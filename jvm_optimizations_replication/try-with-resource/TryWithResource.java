import java.io.PrintWriter;

// https://github.com/dropwizard/metrics/blob/2211303e17805e98aec320a877862096f07f49a9/metrics-servlets/src/main/java/com/codahale/metrics/servlets/CpuProfileServlet.java#L29
public class TryWithResource {
    public static void main(String[] args) {
        try (PrintWriter writer = new PrintWriter(System.out)) {
            writer.println("Hello, World!");
        }
    }
}
