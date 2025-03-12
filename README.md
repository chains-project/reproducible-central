Structured as
<groupId>/<artifactId>/<version>

Each of these directories have:
1. `reference` - artifact on Maven central
2. `rebuild` - artifact that is built using `buildspec`
3. `*.diffoscope.json` - difference between reference and rebuild
> If there are no diffoscope files, it means that the build either failed or there is no difference between the artifacts.
You can see failed builds in `mvn.log`. You can confirm the project is fully reproducible by referring to `ko` attribute in `.buildcompare`.

