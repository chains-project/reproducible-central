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
	static final Path rootLogDir = Path.of("parallel_oss-rebuild-improved-2");
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

		List<String> gavs = Files.readAllLines(Paths.get("projects_with_all_differences.txt"));
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

		int exitCodeReference = -1;
		if (reference.toFile().exists()) {
			// Create the oss-rebuild directory if it doesn't exist
			Files.createDirectories(versionDir.resolve("oss-rebuild-improved-2").resolve("reference"));

			ProcessBuilder processBuilder1 = new ProcessBuilder(
					"docker", "run", "--rm",
					// "--user", System.getProperty("userid"),
					"-w", "/mnt",
					"--mount",
					String.format("type=bind,source=%s,target=/%s", reference.toAbsolutePath(), reference.getFileName()),
					"-v", versionDir.toAbsolutePath() + ":/mnt",
					"algomaster99/oss-rebuild-stabilize:6dd67d5c7ac4db112f3419b5132d8f80a22cbe65",
					"-infile", "/" + reference.getFileName().toString(),
					"-outfile", "/mnt/oss-rebuild-improved-2/reference/" + reference.getFileName().toString()
			);
			System.out.println("Running reference: " + processBuilder1.command());
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
				Files.write(versionDir.resolve("oss-rebuild-improved-2").resolve("reference").resolve(getPathFromArtifact(reference) + ".oss-rebuild-improved-2.log"), lines);

			} catch (Exception e) {
				System.out.println("Exception: " + e.getMessage());
				Thread.currentThread().interrupt();
			}
		}

		int exitCodeRebuild = -1;
		if (rebuild.toFile().exists()) {
			Files.createDirectories(versionDir.resolve("oss-rebuild-improved-2").resolve("rebuild"));
			ProcessBuilder processBuilder2 = new ProcessBuilder(
					"docker", "run", "--rm",
//		 		"--user", System.getProperty("userid"),
					"-w", "/mnt",
					"--mount",
					String.format("type=bind,source=%s,target=/%s", rebuild.toAbsolutePath(), rebuild.getFileName()),
					"-v", versionDir.toAbsolutePath() + ":/mnt",
					"algomaster99/oss-rebuild-stabilize:6dd67d5c7ac4db112f3419b5132d8f80a22cbe65",
					"-infile", "/" + rebuild.getFileName().toString(),
					"-outfile", "/mnt/oss-rebuild-improved-2/rebuild/" + rebuild.getFileName().toString()
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
				Files.write(versionDir.resolve("oss-rebuild-improved-2").resolve("rebuild").resolve(getPathFromArtifact(reference) + ".oss-rebuild-improved-2.log"), lines);

			} catch (Exception e) {
				System.out.println("Exception: " + e.getMessage());
				Thread.currentThread().interrupt();
			}
		}


		ProcessBuilder diffProcessBuilder = new ProcessBuilder(
				"diff",
				"-u",
				versionDir.resolve("oss-rebuild-improved-2").resolve("reference").resolve(reference.getFileName().toString()).toString(),
				versionDir.resolve("oss-rebuild-improved-2").resolve("rebuild").resolve(rebuild.getFileName().toString()).toString()
		);
		diffProcessBuilder.redirectOutput(versionDir.resolve("oss-rebuild-improved-2").resolve(getPathFromArtifact(reference) + ".diff").toFile());

		try {
			Process process = diffProcessBuilder.start();
			process.getErrorStream().transferTo(System.out);
			int exitCodeDiff = process.waitFor();

			Map<String, Integer> exitCodeMap = new HashMap<>();
			exitCodeMap.put("reference", exitCodeReference);
			exitCodeMap.put("rebuild", exitCodeRebuild);
			exitCodeMap.put("diff", exitCodeDiff);

			ObjectMapper objectMapper = new ObjectMapper();
			Files.writeString(versionDir.resolve("oss-rebuild-improved-2").resolve(getPathFromArtifact(reference) + ".json"), objectMapper.writeValueAsString(exitCodeMap) + "\n");

		} catch (IOException | InterruptedException e) {
			System.out.println("Exception: " + e.getMessage());
			Thread.currentThread().interrupt();
		}
	}
}
