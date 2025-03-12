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
import java.util.stream.Stream;

import com.fasterxml.jackson.databind.ObjectMapper;

public class ParallelRunner {
	static final Path rootLogDir = Path.of("parallel_jnorm");
	private static final String BASE_DIR = "results";
	private static final Path skippedFile = rootLogDir.resolve("skipped");
	private static final int MAX_WORKERS = Math.max(1, Runtime.getRuntime().availableProcessors() / 2);

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

		List<String> gavs = Files.readAllLines(Paths.get("projects_with_jvm_differences.txt"));
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

		executor.shutdown();
	}

	private static String getPathFromArtifact(Path artifactPath) {
		return artifactPath.getFileName().toString().split(":")[0];
	}

	private static void processPair(Path reference, Path rebuild, Path versionDir) throws IOException {
		System.out.println("Processing: " + reference + " and " + rebuild);

		int exitCodeReference = -1;
		if (reference.toFile().exists()) {
			ProcessBuilder processBuilder1 = new ProcessBuilder(
					"docker", "run", "--rm",
					// "--user", System.getProperty("userid"),
					"-w", "/mnt",
					"--mount",
					String.format("type=bind,source=%s,target=/reference.jar", reference.toAbsolutePath()),
					"-v", versionDir.toAbsolutePath() + ":/mnt",
					"algomaster99/jnorm:latest",
					"-o",
					"-n",
					"-a",
					"-s",
					"-p",
					"-c",
					"-r2",
					"-i", "/reference.jar",
					"-d", "/mnt/jnorm/reference/" + reference.getFileName().toString() + "/"
			);
			processBuilder1.redirectErrorStream(true);

			try {
				Process process = processBuilder1.start();
				exitCodeReference = process.waitFor();

				BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
				String line;
				List<String> lines = new ArrayList<>();
				while ((line = reader.readLine()) != null) {
					lines.add(line);
				}
				Files.write(versionDir.resolve("jnorm").resolve("reference").resolve(getPathFromArtifact(reference) + ".jnorm.log"), lines);

			} catch (Exception e) {
				System.out.println("Exception: " + e.getMessage());
				Thread.currentThread().interrupt();
			}
		}

		int exitCodeRebuild = -1;
		if (rebuild.toFile().exists()) {
			ProcessBuilder processBuilder2 = new ProcessBuilder(
					"docker", "run", "--rm",
//		 		"--user", System.getProperty("userid"),
					"-w", "/mnt",
					"--mount",
					String.format("type=bind,source=%s,target=/rebuild.jar", rebuild.toAbsolutePath()),
					"-v", versionDir.toAbsolutePath() + ":/mnt",
					"algomaster99/jnorm:latest",
					"-o",
					"-n",
					"-a",
					"-s",
					"-p",
					"-c",
					"-r2",
					"-i", "/rebuild.jar",
					"-d", "/mnt/jnorm/rebuild/" + rebuild.getFileName().toString() + "/"
			);
			processBuilder2.redirectErrorStream(true);

			try {
				Process process = processBuilder2.start();
				exitCodeRebuild = process.waitFor();

				BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
				String line;
				List<String> lines = new ArrayList<>();
				while ((line = reader.readLine()) != null) {
					lines.add(line);
				}
				Files.write(versionDir.resolve("jnorm").resolve("rebuild").resolve(getPathFromArtifact(reference) + ".jnorm.log"), lines);

			} catch (Exception e) {
				System.out.println("Exception: " + e.getMessage());
				Thread.currentThread().interrupt();
			}
		}


		ProcessBuilder diffProcessBuilder = new ProcessBuilder(
				"diff",
				"-u",
				versionDir.resolve("jnorm").resolve("reference").resolve(reference.getFileName().toString()).toString(),
				versionDir.resolve("jnorm").resolve("rebuild").resolve(rebuild.getFileName().toString()).toString()
		);
		diffProcessBuilder.redirectOutput(versionDir.resolve("jnorm").resolve(getPathFromArtifact(reference) + ".diff").toFile());

		try {
			Process process = diffProcessBuilder.start();
			process.getErrorStream().transferTo(System.out);
			int exitCodeDiff = process.waitFor();

			Map<String, Integer> exitCodeMap = new HashMap<>();
			exitCodeMap.put("reference", exitCodeReference);
			exitCodeMap.put("rebuild", exitCodeRebuild);
			exitCodeMap.put("diff", exitCodeDiff);

			ObjectMapper objectMapper = new ObjectMapper();
			Files.writeString(versionDir.resolve("jnorm").resolve(getPathFromArtifact(reference) + ".json"), objectMapper.writeValueAsString(exitCodeMap) + "\n");

		} catch (IOException | InterruptedException e) {
			System.out.println("Exception: " + e.getMessage());
			Thread.currentThread().interrupt();
		}
	}
}
