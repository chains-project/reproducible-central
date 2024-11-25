package io.github.algomaster99.reproducible_central;

import com.fasterxml.jackson.annotation.JsonAnySetter;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class AllReleasesJson {
	private Map<String, List<ArtifactInfo>> releasesToJars = new HashMap<>();

	public Map<String, List<ArtifactInfo>> getReleasesToJars() {
		return releasesToJars;
	}

	@JsonAnySetter
	public void addModule(String key, List<ArtifactInfo> artifacts) {
		releasesToJars.put(key, artifacts);
	}
}
