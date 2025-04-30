package io.github.algomaster99.reproducible_central;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

import static io.github.algomaster99.reproducible_central.ParallelRunner.rootLogDir;

/**
 * Class to provide test resources.
 */
public class Operands {
	static final String REF_DIR = "reference";
	static final String REB_DIR = "rebuild";
	final String groupId;
	final String artifactId;
	final String version;
	final Path versionDir;

	List<Pair<Path, Path>> referenceRebuildPairs;

	private static final Path logEmptyVersionDirectory = rootLogDir.resolve("empty_version_directory.log");
	private static final Path nonExistentReferenceOrRebuild = rootLogDir.resolve("non_existent_reference_or_rebuild.log");
	private static final Path emptyReferenceOrRebuild = rootLogDir.resolve("empty_reference_or_rebuild.log");
	private static final Path artifactMismatch = rootLogDir.resolve("artifact_mismatch.log");

	static {
		try {
			Files.createFile(logEmptyVersionDirectory);
			Files.createFile(nonExistentReferenceOrRebuild);
			Files.createFile(emptyReferenceOrRebuild);
			Files.createFile(artifactMismatch);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	private Operands(String groupId, String artifactId, String version, List<Pair<Path, Path>> referenceRebuildPairs, Path versionDir) {
		this.groupId = groupId;
		this.artifactId = artifactId;
		this.version = version;
		this.referenceRebuildPairs = referenceRebuildPairs;
		this.versionDir = versionDir;
	}

	public static Operands fromOssRebuildDirectory(Path ossRebuildDir) {
		String artifactId = ossRebuildDir.getParent().getParent().getFileName().toString();
		String groupId = ossRebuildDir.getParent().getParent().getParent().getFileName().toString();
		String version = ossRebuildDir.getParent().getFileName().toString();

		// empty version dir
		if (Objects.requireNonNull(ossRebuildDir.toFile().listFiles()).length == 0) {
			return new Operands(groupId, artifactId, version, List.of(), ossRebuildDir);
		}

		if (!ossRebuildDir.resolve(REF_DIR).toFile().exists() || !ossRebuildDir.resolve(REB_DIR).toFile().exists()) {
			try {
				Files.writeString(nonExistentReferenceOrRebuild, ossRebuildDir.toAbsolutePath() + "\n", java.nio.file.StandardOpenOption.APPEND);
			} catch (IOException e) {
				throw new RuntimeException(e);
			}
			return new Operands(groupId, artifactId, version, List.of(), ossRebuildDir);
		}

		// empty reference or rebuild
		if (ossRebuildDir.resolve(REF_DIR).toFile().list().length == 0 || ossRebuildDir.resolve(REB_DIR).toFile().list().length == 0) {
			try {
				Files.writeString(emptyReferenceOrRebuild, ossRebuildDir.toAbsolutePath() + "\n", java.nio.file.StandardOpenOption.APPEND);
			} catch (IOException e) {
				throw new RuntimeException(e);
			}
			return new Operands(groupId, artifactId, version, List.of(), ossRebuildDir);
		}

		Set<String> refArtifacts = Arrays.stream(ossRebuildDir.resolve(REF_DIR).toFile().list())
		.collect(Collectors.toSet());
		Set<String> rebArtifacts = Arrays.stream(ossRebuildDir.resolve(REB_DIR).toFile().list())
				.collect(Collectors.toSet());

		if (!refArtifacts.equals(rebArtifacts)) {
			System.out.println("Reference and rebuild directories do not contain the same artifacts" + ossRebuildDir.toAbsolutePath());
			try {
				Files.writeString(artifactMismatch, ossRebuildDir.toAbsolutePath() + "\n", java.nio.file.StandardOpenOption.APPEND);
			} catch (IOException e) {
				throw new RuntimeException(e);
			}
			return new Operands(groupId, artifactId, version, List.of(), ossRebuildDir);
		}

		File refDir = ossRebuildDir.resolve(REF_DIR).toFile();
		List<Pair<Path, Path>> referenceRebuildPairs = new ArrayList<>();
		Arrays.stream(Objects.requireNonNull(refDir.listFiles()))
				.forEach(f -> {
					Path ref = f.toPath();
					Path reb = ossRebuildDir.resolve(REB_DIR).resolve(ref.getFileName());
					if (reb.toFile().exists()) {
						referenceRebuildPairs.add(Pair.of(ref, reb));
					}
				});

		return new Operands(groupId, artifactId, version, referenceRebuildPairs, ossRebuildDir);
	}

	public static Operands fromTestDirectory(Path versionDir) {
		String artifactId = versionDir.getParent().getFileName().toString();
		String groupId = versionDir.getParent().getParent().getFileName().toString();
		String version = versionDir.getFileName().toString();

		// empty version dir
		if (Objects.requireNonNull(versionDir.toFile().listFiles()).length == 0) {
			try {
				Files.writeString(logEmptyVersionDirectory, versionDir.toAbsolutePath() + "\n", java.nio.file.StandardOpenOption.APPEND);
			} catch (IOException e) {
				throw new RuntimeException(e);
			}
			return new Operands(groupId, artifactId, version, List.of(), versionDir);
		}

		// non-existent reference or rebuild
		if (!versionDir.resolve(REF_DIR).toFile().exists() || !versionDir.resolve(REB_DIR).toFile().exists()) {
			try {
				Files.writeString(nonExistentReferenceOrRebuild, versionDir.toAbsolutePath() + "\n", java.nio.file.StandardOpenOption.APPEND);
			} catch (IOException e) {
				throw new RuntimeException(e);
			}
			return new Operands(groupId, artifactId, version, List.of(), versionDir);
		}

		// empty reference or rebuild
		if (versionDir.resolve(REF_DIR).toFile().list().length == 0 || versionDir.resolve(REB_DIR).toFile().list().length == 0) {
			try {
				Files.writeString(emptyReferenceOrRebuild, versionDir.toAbsolutePath() + "\n", java.nio.file.StandardOpenOption.APPEND);
			} catch (IOException e) {
				throw new RuntimeException(e);
			}
			return new Operands(groupId, artifactId, version, List.of(), versionDir);
		}

		Set<String> refArtifacts = Arrays.stream(versionDir.resolve(REF_DIR).toFile().list())
				.collect(Collectors.toSet());
		Set<String> rebArtifacts = Arrays.stream(versionDir.resolve(REB_DIR).toFile().list())
				.collect(Collectors.toSet());

		if (!refArtifacts.equals(rebArtifacts)) {
			System.out.println("Reference and rebuild directories do not contain the same artifacts" + versionDir.toAbsolutePath());
			try {
				Files.writeString(artifactMismatch, versionDir.toAbsolutePath() + "\n", java.nio.file.StandardOpenOption.APPEND);
			} catch (IOException e) {
				throw new RuntimeException(e);
			}
			return new Operands(groupId, artifactId, version, List.of(), versionDir);
		}

		File refDir = versionDir.resolve(REF_DIR).toFile();
		List<Pair<Path, Path>> referenceRebuildPairs = new ArrayList<>();
		Arrays.stream(Objects.requireNonNull(refDir.listFiles()))
				.forEach(f -> {
					Path ref = f.toPath();
					Path reb = versionDir.resolve(REB_DIR).resolve(ref.getFileName());
					if (reb.toFile().exists()) {
						referenceRebuildPairs.add(Pair.of(ref, reb));
					}
				});

		return new Operands(groupId, artifactId, version, referenceRebuildPairs, versionDir);
	}
}
