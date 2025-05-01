### Dataset

1. List of [unreproducible Maven releases](java/unreproducible_maven_projects_to_releases.json).
2. All files are hosted on http://130.237.222.185/chains-reproducible-central/.

#### Structured as `<groupId>`/`<artifactId>`/`<version>`

Each of these directories have:
1. `reference` - artifact on Maven central
    1. `<unreproducible-reference-artifact:unreproducible-rebuild-artifact>` - unreproducible artifact
2. `rebuild` - artifact that is built using `buildspec`
    1. `<unreproducible-reference-artifact:unreproducible-rebuild-artifact>` - unreproducible artifact
3. `*.diffoscope.json` - difference between reference and rebuild
4. `jnorm` - https://github.com/stschott/jnorm-tool/tree/cec4645c5c9b52f73c347349bf14945b0eb55c87
    1. `reference` - bytecode canonicalization of reference artifact
        1. `<unreproducible-reference-artifact:unreproducible-rebuild-artifact>/*.jimple` - directory of Jimple files
        2. `<unreproducible-reference-artifact>.log` - log of the canonicalization process
    2. `rebuild` - bytecode canonicalization of rebuild artifact
        1. `<unreproducible-reference-artifact:unreproducible-rebuild-artifact>/*.jimple` - directory of Jimple files
        2. `<unreproducible-reference-artifact>.log` - log of the canonicalization process
    3. `*.diff` - difference between canonicalized reference and rebuild
    4. `*.json` - exit code of reference canonicalization, rebuild canonicalization, and diff.
5. `oss-rebuild` - https://github.com/google/oss-rebuild/commit/4ef4c013fe6903cda40a9ee4244e3b65b5834325
    1. `reference` - artifact canonicalization of reference artifact
        1. `<unreproducible-reference-artifact:unreproducible-rebuild-artifact>.*` - canonicalized reference artifact
        2. `<unreproducible-reference-artifact:unreproducible-rebuild-artifact>.log` - log of the canonicalization process
    2. `rebuild` - artifact canonicalization of rebuild artifact
        1. `<unreproducible-reference-artifact:unreproducible-rebuild-artifact>.*` - canonicalized rebuild artifact
        2. `<unreproducible-reference-artifact:unreproducible-rebuild-artifact>.log` - log of the canonicalization process
    3. `*.diff` - difference between canonicalized reference and rebuild
    4. `*.json` - exit code of reference canonicalization, rebuild canonicalization, and diff.
6. `oss-rebuild-improved` - same structure as `oss-rebuild`, but with improved canonicalization (https://github.com/chains-project/chains-rebuild/commit/4ef4c013fe6903cda40a9ee4244e3b65b5834325)
6. `oss-rebuild-improved-2` - same structure as `oss-rebuild`, but with improved canonicalization (https://github.com/chains-project/chains-rebuild/commit/6dd67d5c7ac4db112f3419b5132d8f80a22cbe65)
   > This also has the diffoscope files between the canonicalized artifacts, but they are not used in the paper.

6. `copy_reference.log` and `copy_rebuild.log` - log if the artifact is copied from build directory to `reference` or `rebuild` directory
6. `mvn.log` - log of the build process
7. `output.txt` and `output.json` - module hierarchy of the project
> If there are no diffoscope files, it means that the build either failed or there is no difference between the artifacts.
You can see failed builds in `mvn.log`. You can confirm the project is fully reproducible by referring to `ko` attribute in `.buildcompare`.

> Note that `oss-rebuild-improved-2` is called CHAINS-rebuild in the paper.
