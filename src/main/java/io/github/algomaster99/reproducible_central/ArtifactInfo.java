package io.github.algomaster99.reproducible_central;

public class ArtifactInfo {
	private String artifactName;
    private long size;
    private long numberOfClassfiles;

    public ArtifactInfo() {}

    public ArtifactInfo(String artifactName, long size, long classCount) {
        this.artifactName = artifactName;
        this.size = size;
        this.numberOfClassfiles = classCount;
    }

    public String getArtifactName() { return artifactName; }
    public void setArtifactName(String artifactName) { this.artifactName = artifactName; }
    public long getSize() { return size; }
    public void setSize(long size) { this.size = size; }
    public long getNumberOfClassfiles() { return numberOfClassfiles; }
    public void setNumberOfClassfiles(long count) { this.numberOfClassfiles = count; }
}
