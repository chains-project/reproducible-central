package io.github.algomaster99.reproducible_central.jsonutil;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.ArrayList;
import java.util.List;

import java.util.List;
import java.util.Objects;

public class MavenRelease {
    private String gav;
    private List<String> unreproducibleArtifacts;
    private List<String> allArtifacts;
    private String url;

    // Constructor
    public MavenRelease(@JsonProperty("gav") String gav, @JsonProperty("unreproducible_artifacts") List<String> unreproducibleArtifacts, @JsonProperty("all_artifacts") List<String> allArtifacts, @JsonProperty("url") String url) {
        this.gav = gav;
        this.unreproducibleArtifacts = unreproducibleArtifacts;
		this.allArtifacts = Objects.requireNonNullElseGet(allArtifacts, ArrayList::new);
        this.url = url;
    }

    // Getter for GAV
    public String getGav() {
        return gav;
    }

    // Setter for GAV
    public void setGav(String gav) {
        this.gav = gav;
    }

    // Getter for unreproducibleArtifacts
    public List<String> getUnreproducibleArtifacts() {
        return unreproducibleArtifacts;
    }

    // Setter for unreproducibleArtifacts
    public void setUnreproducibleArtifacts(List<String> unreproducibleArtifacts) {
        this.unreproducibleArtifacts = unreproducibleArtifacts;
    }

    // Getter for allArtifacts
    public List<String> getAllArtifacts() {
        return allArtifacts;
    }

    // Setter for allArtifacts
    public void setAllArtifacts(List<String> allArtifacts) {
        this.allArtifacts = allArtifacts;
    }

    // Getter for URL
    public String getUrl() {
        return url;
    }

    // Setter for URL
    public void setUrl(String url) {
        this.url = url;
    }
}

