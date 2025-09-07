package io.github.algomaster99.reproducible_central;


import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;

import com.fasterxml.jackson.databind.ObjectMapper;

public class ParallelRunnerDaleq {
	static final Path rootLogDir = Path.of("parallel_daleq");
	private static final String BASE_DIR = "results";
	private static final Path skippedFile = rootLogDir.resolve("skipped");
	private static final int MAX_WORKERS = Math.max(1, (Runtime.getRuntime().availableProcessors() / 3) * 2);


	static {
		try {
			Files.createDirectories(rootLogDir);
			Files.createFile(skippedFile);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	public static void main(String[] args) throws IOException {
		ExecutorService executor = Executors.newFixedThreadPool(MAX_WORKERS);

		List<String> gavs = Files.readAllLines(Paths.get("gradle_projects_with_jvm_differences.txt"));
		try (Stream<Path> paths = Files.walk(Paths.get(BASE_DIR))) {
			paths
					.filter(Files::isDirectory)
					.filter(path -> path.getNameCount() == Paths.get(BASE_DIR).getNameCount() + 3)
					.filter(path -> !path.getFileName().toString().equals("buildcache"))
					.map(Operands::fromTestDirectory)
					.forEach(operands -> {
						if (gavs.contains(String.format("%s:%s:%s", operands.groupId, operands.artifactId, operands.version))) {
							operands.referenceRebuildPairs.forEach(pair -> {
								executor.submit(() -> {
									try {
										processPair(pair.left(), pair.right(), operands.versionDir);
									} catch (IOException e) {
										throw new RuntimeException(e);
									}
								});
							});
						} else {
							try {
								Files.writeString(skippedFile,String.format("%s:%s:%s\n", operands.groupId, operands.artifactId, operands.version), java.nio.file.StandardOpenOption.APPEND);
							} catch (IOException e) {
								throw new RuntimeException(e);
							}
						}
					});
		}
        finally {
            executor.shutdown();
        }
	}

	private static String getPathFromArtifact(Path artifactPath) {
		return artifactPath.getFileName().toString().split(":")[0];
	}

	// old: 4ef4c013fe6903cda40a9ee4244e3b65b5834325
	// new: 1f0625a9cf3511f8ce0385ec0c91b4f64895fd58
	// new 2: 6dd67d5c7ac4db112f3419b5132d8f80a22cbe65
	private static void processPair(Path reference, Path rebuild, Path versionDir) throws IOException {
		System.out.println("Processing: " + reference + " and " + rebuild);

        ProcessBuilder processBuilder = new ProcessBuilder(
            "docker", "run", "--rm",
            "-w", "/mnt",
            "--mount",
            String.format("type=bind,source=%s,target=/reference.jar", reference.toAbsolutePath()),
            "--mount",
            String.format("type=bind,source=%s,target=/rebuild.jar", rebuild.toAbsolutePath()),
            "-v", versionDir.toAbsolutePath() + ":/mnt",
            "algomaster99/daleq:latest",
            "-j1", "/reference.jar",
            "-j2", "/rebuild.jar",
            "-o", "/mnt/daleq/" + getPathFromArtifact(reference) + "/"
        );
        System.out.println(processBuilder.command());
        processBuilder.redirectErrorStream(true);
		
		try {
			Process process = processBuilder.start();
			process.getErrorStream().transferTo(System.out);

			int exitCodeDiff = process.waitFor();

			Map<String, Integer> exitCodeMap = new HashMap<>();
			exitCodeMap.put("diff", exitCodeDiff);

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));

            String line;
            List<String> lines = new ArrayList<>();
            while ((line = reader.readLine()) != null) {
                lines.add(line);
            }

            Files.write(versionDir.resolve("daleq").resolve(getPathFromArtifact(reference) + ".log"), lines); 
			ObjectMapper objectMapper = new ObjectMapper();
			Files.writeString(versionDir.resolve("daleq").resolve(getPathFromArtifact(reference) + ".json"), objectMapper.writeValueAsString(exitCodeMap) + "\n");


		} catch (Exception e) {
		}
	}
}
