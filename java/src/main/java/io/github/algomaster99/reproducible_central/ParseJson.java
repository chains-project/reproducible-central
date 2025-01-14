package io.github.algomaster99.reproducible_central;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

import javax.net.ssl.SSLParameters;

import org.jsoup.Jsoup;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.algomaster99.reproducible_central.jsonutil.MavenProject;
import io.github.algomaster99.reproducible_central.jsonutil.MavenRelease;

public class ParseJson {
    private static final String MAVEN_CENTRAL_URL = "https://repo.maven.apache.org/maven2/";

    public static void main(String[] args) throws IOException, InterruptedException {
        Path jsonFile = Path.of(args[0]);
        ObjectMapper objectMapper = new ObjectMapper();
        List<MavenProject> mavenProjects = objectMapper.readValue(jsonFile.toFile(), new TypeReference<List<MavenProject>>() {});
        for (MavenProject mavenProject : mavenProjects) {
            for (MavenRelease mavenRelease : mavenProject.maven_releases()) {
                parseRelease(mavenRelease);
                boolean match = mavenRelease.getUnreproducibleArtifacts().stream().map(a -> a.replace(".diffoscope.json", "")).anyMatch(mavenRelease.getAllArtifacts()::contains);
				if (!match) {
					System.out.println("Does not match" + mavenRelease.getGav());
				}
            }
        }
        Files.writeString(Path.of("all_artifacts.json"), objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(mavenProjects));
    }

    public static void parseRelease(MavenRelease mavenRelease) throws IOException, InterruptedException {
        String[] gav = mavenRelease.getGav().split(":");
        String groupId = gav[0];
        String artifactId = gav[1];
        String version = gav[2];

		if ("None".equals(groupId) && "None".equals(artifactId) && "None".equals(version)) {
			groupId = "fr.inria.gforge.spoon";
			artifactId = "spoon-core";
			version = "10.4.0";
		}

        String artifactUrl = getArtifactUrl(groupId, artifactId, version);
        String indexPage = getIndexPageOfRepository(artifactUrl);
		if (indexPage == null) {
			System.out.println(artifactUrl);
			return;
		}
		mavenRelease.setUrl(artifactUrl);
        List<String> artifacts = extractArtifactsFromIndexPage(indexPage);
        mavenRelease.setAllArtifacts(artifacts);
    }

    private static String getArtifactUrl(String groupId, String artifactId, String version) {
        return MAVEN_CENTRAL_URL + groupId.replace(".", "/") + "/" + artifactId + "/" + version + "/";
    }

    private static String getIndexPageOfRepository(String artifactUrl) throws IOException, InterruptedException {
		SSLParameters sslParameters = new SSLParameters();
		sslParameters.setProtocols(new String[] {"TLSv1.2"});
		sslParameters.setNeedClientAuth(false);
		HttpClient client = HttpClient.newBuilder().sslParameters(sslParameters).build();

		HttpRequest request =
				HttpRequest.newBuilder().uri(URI.create(artifactUrl)).build();
		HttpResponse<String> result = client.send(request, HttpResponse.BodyHandlers.ofString());

		if (result.statusCode() != 200) {
			return null;
		}
		return result.body();
	}

    private static List<String> extractArtifactsFromIndexPage(String indexPageContent) {
		List<String> candidates = Jsoup.parse(indexPageContent).select("a").stream()
				.map(e -> e.attr("href"))
                .filter(c -> !"../".equals(c))
                .filter(c -> !c.endsWith(".asc"))
                .filter(c -> !c.endsWith(".md5"))
                .filter(c -> !c.endsWith(".sha1"))
                .filter(c -> !c.endsWith(".sha256"))
                .filter(c -> !c.endsWith(".sha512"))
				.collect(Collectors.toList());

		return candidates;
	}
}