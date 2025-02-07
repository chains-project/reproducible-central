package io.github.algomaster99.reproducible_central;


import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Stream;

public class ParallelRunner {
    private static final String BASE_DIR = "results";
    private static final int MAX_WORKERS = Math.max(1, Runtime.getRuntime().availableProcessors() / 2);

	static final Path rootLogDir = Path.of("parallel_diffoscope");
	private static final Path noDifference = rootLogDir.resolve("no_difference.log");
	private static final Path difference = rootLogDir.resolve("difference.log");

	static {
		try {
			Files.createDirectories(rootLogDir);
			Files.createFile(noDifference);
			Files.createFile(difference);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

    public static void main(String[] args) throws IOException {
        ExecutorService executor = Executors.newFixedThreadPool(MAX_WORKERS);

        try (Stream<Path> paths = Files.walk(Paths.get(BASE_DIR))) {
            paths
				.filter(Files::isDirectory)
				.filter(path -> path.getNameCount() == Paths.get(BASE_DIR).getNameCount() + 3)
				.filter(path -> !path.getFileName().toString().equals("buildcache"))
				.map(Operands::fromTestDirectory)
				.forEach(operands -> {
					operands.referenceRebuildPairs.forEach(pair -> {
						executor.submit(() -> {
							processPair(pair.left(), pair.right(), operands.versionDir);
						});
					});
				});
		}

		executor.shutdown();
	}

	private static String getPathFromArtifact(Path artifactPath) {
		return artifactPath.getFileName().toString().split(":")[0];
	}

	private static void processPair(Path reference, Path rebuild, Path versionDir) {
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
				"algomaster99/diffoscope:latest",
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
		} catch (IOException | InterruptedException e) {
			System.out.println("Exception: " + e.getMessage());
			Thread.currentThread().interrupt();
		}
	}
}
