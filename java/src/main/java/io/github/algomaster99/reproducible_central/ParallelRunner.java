package io.github.algomaster99.reproducible_central;


import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Stream;

public class ParallelRunner {
	static final Path rootLogDir = Path.of("parallel_daleq");
	private static final String BASE_DIR = "results";
	private static final Path skippedFile = rootLogDir.resolve("skipped");
	private static final int MAX_WORKERS = Math.max(1, (Runtime.getRuntime().availableProcessors() / 3) * 2);

	private static final Path noDifference = rootLogDir.resolve("no_difference.log");
 

	private static final Path difference = rootLogDir.resolve("difference.log");

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
					.filter(path -> path.getFileName().toString().equals("oss-rebuild-improved-2"))
					.map(Operands::fromOssRebuildDirectory)
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
				"--user", System.getProperty("userid"),
				"-w", "/mnt",
				"--mount",
				String.format("type=bind,source=%s,target=/input1", reference.toAbsolutePath()),
				"--mount",
				String.format("type=bind,source=%s,target=/input2", rebuild.toAbsolutePath()),
				"-v", versionDir.toAbsolutePath() + ":/mnt",
				"algomaster99/diffoscope:294",
				"/input1", "/input2",
				"--json", "/mnt/" + getPathFromArtifact(reference.toAbsolutePath()) + ".diffoscope.json"
		);
		processBuilder.inheritIO();
		
		try {
			Process process = processBuilder.start();
			process.getErrorStream().transferTo(System.out);
			int exitCode = process.waitFor();
			switch (exitCode) {
				case 0:
					System.out.printf("There is a no difference between %s and %s%n", reference, rebuild);
					Files.writeString(noDifference, reference + "," + rebuild + "\n", java.nio.file.StandardOpenOption.APPEND);
					break;
				case 1:
					System.out.printf("Difference between %s and %s%n", reference, rebuild);
					Files.writeString(difference, reference + "," + rebuild + "\n", java.nio.file.StandardOpenOption.APPEND);
					break;
				default:
					throw new RuntimeException("exit code: " + exitCode);
			}
		} catch (Exception e) {
		}
	}
}
