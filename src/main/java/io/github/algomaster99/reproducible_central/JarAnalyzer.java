package io.github.algomaster99.reproducible_central;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.jsoup.Jsoup;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import javax.net.ssl.SSLParameters;
import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.zip.ZipFile;

public class JarAnalyzer {
	private static final File ARTIFACTS_JSON = Path.of("make-release-consistent-file-paths.json").toFile();
	private static final String MAVEN_CENTRAL_URL = "https://repo.maven.apache.org/maven2/";
	private static final Logger logger = LogManager.getLogger(JarAnalyzer.class);

	public static void main(String[] args) throws IOException, URISyntaxException, InterruptedException {
		ObjectMapper objectMapper = new ObjectMapper();
		AllReleasesJson allReleasesJson = objectMapper.readValue(ARTIFACTS_JSON, AllReleasesJson.class);

		Map<String, List<File>> gavToJars = new HashMap<>();
		for (Map.Entry<String, List<ArtifactPath>> entry : allReleasesJson.getReleasesToJars().entrySet()) {
			String moduleName = entry.getKey();
			String[] gav = moduleName.split(":");
			String groupId = gav[0];
			String artifactId = gav[1];
			String version = gav[2];

			gavToJars.put(moduleName, downloadArtifact(groupId, artifactId, version));
		}
		analyzeJars(gavToJars);
    }

	private static Map<String, List<ArtifactInfo>> analyzeJars(Map<String, List<File>> gavToJars) throws IOException {
		Map<String, List<ArtifactInfo>> result = new HashMap<>();
		
		int total = gavToJars.size();
		int current = 0;
		logger.info("Starting analysis of {} GAVs", total);
		
		for (Map.Entry<String, List<File>> entry : gavToJars.entrySet()) {
			current++;
			if (current % 10 == 0 || current == total) {  // Log every 10 items and at the end
				logger.info("Progress: {}/{} GAVs processed ({} %)", 
					current, total, String.format("%.1f", (current * 100.0 / total)));
			}
			
			String gav = entry.getKey();
			List<ArtifactInfo> jarInfos = new ArrayList<>();
			
			for (File jarFile : entry.getValue()) {
				// Strip .cache from path
				String artifactName = jarFile.getPath().replace(".cache/", "");
				long size = jarFile.length();
				
				// Count class files
				long classCount;
				try (ZipFile zip = new ZipFile(jarFile)) {
					classCount = zip.stream()
						.filter(zipEntry -> zipEntry.getName().endsWith(".class"))
						.count();
				}
				
				jarInfos.add(new ArtifactInfo(artifactName, size, classCount));
			}
			
			result.put(gav, jarInfos);
		}
		
		logger.info("Completed analysis of all {} GAVs", total);
		
		// Write to JSON file
		ObjectMapper mapper = new ObjectMapper();
		mapper.enable(SerializationFeature.INDENT_OUTPUT);
		mapper.writerWithDefaultPrettyPrinter()
			.writeValue(new File("jar_analysis.json"), result);
		
		return result;
	}


	private static List<File> downloadArtifact(String groupId, String artifactId, String version) throws IOException, InterruptedException, URISyntaxException {
		String artifactUrl = getArtifactUrl(groupId, artifactId, version);
		String indexPageContent = getIndexPageOfRepository(artifactUrl);
		
		if (indexPageContent == null) {
			logger.error("Failed to retrieve index page for URL: {}", artifactUrl);
			throw new IOException("Failed to retrieve index page for URL: " + artifactUrl);
		}
		
		List<String> jarUrls = extractJarUrlsFromIndexPage(indexPageContent, artifactUrl);
		List<File> downloadedJars = new ArrayList<>();
		
		for (String jarUrl : jarUrls) {
			Path cacheDir = Path.of(".cache");
			String jarName = jarUrl.split("/")[jarUrl.split("/").length-1];
			Path cachedFile = cacheDir.resolve(jarName);

			if (Files.exists(cachedFile)) {
				downloadedJars.add(cachedFile.toFile());
			} else {
				Files.createDirectories(cacheDir);
				HttpClient client = HttpClient.newHttpClient();
				HttpRequest request = HttpRequest.newBuilder().uri(URI.create(jarUrl)).build();
				
				try {
					Path tempFile = File.createTempFile(jarName, "").toPath();
					HttpResponse<Path> result = client.send(request, HttpResponse.BodyHandlers.ofFile(tempFile));
					Files.move(tempFile, cachedFile, StandardCopyOption.REPLACE_EXISTING);
					downloadedJars.add(cachedFile.toFile());
				} catch (IOException | InterruptedException e) {
					logger.error("Failed to download JAR from URL: {}", jarUrl, e);
					throw e;
				}
			}
		}
		return downloadedJars;
    }

	private static List<String> extractJarUrlsFromIndexPage(String indexPageContent, String indexPageUrl) {
		List<String> candidates = Jsoup.parse(indexPageContent).select("a").stream()
				.map(e -> e.attr("href"))
				.collect(Collectors.toList());

		List<String> jars = candidates.stream()
				.filter(c -> c.endsWith(".jar"))
				.map(c -> indexPageUrl + c)
				.collect(Collectors.toList());

		return jars;
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

    
}
