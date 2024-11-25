package io.github.algomaster99.reproducible_central;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.maven.model.Model;
import org.apache.maven.model.io.xpp3.MavenXpp3Reader;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.codehaus.plexus.util.xml.pull.XmlPullParserException;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;

public class ExtractUrlFromPom {
    private static final Logger logger = LogManager.getLogger(ExtractUrlFromPom.class);
    private static final File ARTIFACTS_JSON = Path.of("make-release-consistent-file-paths.json").toFile();

    public static void main(String[] args) throws IOException {
        ObjectMapper objectMapper = new ObjectMapper();
        AllReleasesJson allReleasesJson = objectMapper.readValue(ARTIFACTS_JSON, AllReleasesJson.class);

        for (Map.Entry<String, List<ArtifactInfo>> entry: allReleasesJson.getReleasesToJars().entrySet()) {
            String moduleName = entry.getKey();
            Pair<String, String> ga = getGA(moduleName);
            List<ArtifactInfo> artifactInfos = entry.getValue();
            for (ArtifactInfo artifactInfo: artifactInfos) {
                File referenceJar = new File(artifactInfo.getReference()).getAbsoluteFile();
                Set<String> referenceCandidateUrls = extractUrlFromPom(referenceJar, ga.getLeft(), ga.getRight());

                Set<String> rebuildCandidateUrls = Set.of();
                // TODO: fix artifacts where rebuild is null
                if (artifactInfo.getRebuild() != null) {
                    File rebuildJar = new File(artifactInfo.getRebuild()).getAbsoluteFile();
                    rebuildCandidateUrls = extractUrlFromPom(rebuildJar, ga.getLeft(), ga.getRight());
                }
                File versionDir = referenceJar.getParentFile().getParentFile();
                File buildSpec = Arrays.stream(versionDir.listFiles())
                    .filter(f -> f.getName().endsWith(".buildspec"))
                    .findFirst()
                    .orElse(null);

                if (buildSpec == null) {
                    throw new RuntimeException("No buildspec found for " + referenceJar.getAbsolutePath());
                }
                String sourceRepositoryUrl = normaliseSourceRepositoryUrl(extractUrlFromBuildSpec(buildSpec));

                if (!rebuildCandidateUrls.equals(referenceCandidateUrls) && artifactInfo.getRebuild() != null) {
                    throw new RuntimeException("different pom files");
                }
                if (referenceCandidateUrls.contains(sourceRepositoryUrl) && rebuildCandidateUrls.contains(sourceRepositoryUrl)) {
                    logger.info("Found: {} -> {}", referenceJar.getAbsolutePath(), sourceRepositoryUrl);
                } else {
                    logger.info("Not matched: {} -> {}", referenceJar.getAbsolutePath(), sourceRepositoryUrl);
                }
            }
        }
    }

    private static Set<String> extractUrlFromPom(File jar, String groupId, String artifactId) {
        try (JarFile jarFile = new JarFile(jar)) {
            JarEntry pomFile = jarFile.getJarEntry(
                String.format("META-INF/maven/%s/%s/pom.xml", groupId, artifactId));
            if (pomFile == null) {
                logger.error("No POM file found in jar: {}", jar.getAbsolutePath());
                return Set.of();
            }
            MavenXpp3Reader reader = new MavenXpp3Reader();
            Model pomModel = reader.read(jarFile.getInputStream(pomFile));
            Set<String> candidateUrls = new HashSet<>();

            if (pomModel.getUrl() != null) {
                candidateUrls.add(normaliseSourceRepositoryUrl(pomModel.getUrl()));
            }
            if (pomModel.getScm() != null) {
                if (pomModel.getScm().getUrl() != null) {
                    candidateUrls.add(normaliseSourceRepositoryUrl(pomModel.getScm().getUrl()));
                }
                if (pomModel.getScm().getDeveloperConnection() != null) {
                    candidateUrls.add(normaliseSourceRepositoryUrl(pomModel.getScm().getDeveloperConnection()));
                }
                if (pomModel.getScm().getConnection() != null) {
                    candidateUrls.add(normaliseSourceRepositoryUrl(pomModel.getScm().getConnection()));
                }
            }
            return candidateUrls;
        }
        catch (IOException e) {
            logger.error("Error reading jar file: {}", jar.getAbsolutePath());
        } catch (XmlPullParserException e) {
            logger.error("Error parsing POM file: {}", jar.getAbsolutePath());
        }
        return Set.of();
    }

    private static JarEntry findPomFile(JarFile jarFile) {
        return jarFile.stream().filter(jarEntry -> jarEntry.getName().endsWith("pom.xml")).findFirst().orElse(null);
    }

    private static String extractUrlFromBuildSpec(File buildspec) {
        ProcessBuilder processBuilder = new ProcessBuilder("/bin/bash", "-c", 
            String.format("source %s && echo $gitRepo", buildspec.getAbsolutePath()));
        try {
            Process process = processBuilder.start();
            process.waitFor();
            return new String(process.getInputStream().readAllBytes()).trim();
        } catch (IOException | InterruptedException e) {
            logger.error("Error executing buildspec: {}", buildspec.getAbsolutePath());
        }
        return null;
    }

    private static String normaliseSourceRepositoryUrl(String url) {
        if (url == null) {
            return null;
        }
        url = url.replaceAll("^(git://|scm:git:|git@)", "");
        url = url.replaceAll("\\.git$", "");
        url = url.replaceAll("git@github\\.com:", "github.com/");
        return url.toLowerCase();
    }

    private static Pair<String, String> getGA(String moduleName) {
        String[] parts = moduleName.split(":");
        return new Pair<>(parts[0], parts[1]);
    }
}