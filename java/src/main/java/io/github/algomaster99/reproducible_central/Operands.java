package io.github.algomaster99.reproducible_central;

import java.io.File;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

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

	private Operands(String groupId, String artifactId, String version, List<Pair<Path, Path>> referenceRebuildPairs, Path versionDir) {
		this.groupId = groupId;
		this.artifactId = artifactId;
		this.version = version;
		this.referenceRebuildPairs = referenceRebuildPairs;
		this.versionDir = versionDir;
	}

	public static Operands fromTestDirectory(Path versionDir) {
		String artifactId = versionDir.getParent().getFileName().toString();
		String groupId = versionDir.getParent().getParent().getFileName().toString();
		String version = versionDir.getFileName().toString();

		// empty version dir
		if (Objects.requireNonNull(versionDir.toFile().listFiles()).length == 0) {
			return new Operands(groupId, artifactId, version, List.of(), versionDir);
		}

		// non-existent reference or rebuild
		if (!versionDir.resolve(REF_DIR).toFile().exists() || !versionDir.resolve(REB_DIR).toFile().exists()) {
			return new Operands(groupId, artifactId, version, List.of(), versionDir);
		}

		// empty reference or rebuild
		if (versionDir.resolve(REF_DIR).toFile().list().length == 0 || versionDir.resolve(REB_DIR).toFile().list().length == 0) {
			return new Operands(groupId, artifactId, version, List.of(), versionDir);
		}

		Set<String> refArtifacts = Arrays.stream(versionDir.resolve(REF_DIR).toFile().list())
				.collect(Collectors.toSet());
		Set<String> rebArtifacts = Arrays.stream(versionDir.resolve(REB_DIR).toFile().list())
				.collect(Collectors.toSet());

		if (!refArtifacts.equals(rebArtifacts)) {
			System.out.println("Reference and rebuild directories do not contain the same artifacts" + versionDir.toAbsolutePath());
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
