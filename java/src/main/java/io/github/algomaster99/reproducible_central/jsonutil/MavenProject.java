package io.github.algomaster99.reproducible_central.jsonutil;

import java.util.List;
import io.github.algomaster99.reproducible_central.jsonutil.MavenRelease;

public record MavenProject(String name, List<MavenRelease> maven_releases) {
}
