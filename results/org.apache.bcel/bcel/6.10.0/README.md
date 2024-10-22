There is only one artifact `bcel-6.10.0-tests.jar` which cannot be normalised by `jNorm`.

```
Running jNorm with the following configuration: -i bcel-6.10.0-tests.jar -d . -o -n -a -s -p
Class names not equal! issue368.Test != jira368.Test
Class names not equal! module-info != jpms.java11.commons-io.module-info
Class names not equal! module-info != jpms.java17.commons-io.module-info
Class names not equal! module-info != jpms.java18.commons-io.module-info
Class names not equal! module-info != jpms.java19-ea.commons-io.module-info
Class names not equal! test$method name with () in it$1 != kotlin.test$method name with () in it$1
Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index 6 out of bounds for length 0
        at org.objectweb.asm.ClassReader.readShort(ClassReader.java:3608)
        at org.objectweb.asm.ClassReader.<init>(ClassReader.java:197)
        at org.objectweb.asm.ClassReader.<init>(ClassReader.java:180)
        at org.objectweb.asm.ClassReader.<init>(ClassReader.java:166)
        at org.objectweb.asm.ClassReader.<init>(ClassReader.java:287)
        at soot.asm.AsmClassSource.resolve(AsmClassSource.java:66)
        at soot.SootResolver.bringToHierarchyUnchecked(SootResolver.java:274)
        at soot.SootResolver.bringToHierarchy(SootResolver.java:243)
        at soot.SootResolver.bringToSignatures(SootResolver.java:313)
        at soot.SootResolver.processResolveWorklist(SootResolver.java:198)
        at soot.SootResolver.resolveClass(SootResolver.java:155)
        at soot.Scene.loadClass(Scene.java:1016)
        at soot.Scene.loadClassAndSupport(Scene.java:1003)
        at soot.Scene.loadNecessaryClasses(Scene.java:1968)
        at jnorm.core.SootHandler.loadDir(SootHandler.java:78)
        at jnorm.core.Normalizer.normalize(Normalizer.java:43)
        at jnorm.cli.Main.main(Main.java:39)
```

Core reason: reference version is compiled to Java 8 while newer version is compiled to Java 4.
See https://github.com/apache/commons-bcel/blob/rel/commons-bcel-6.10.0/src/test/java/org/apache/bcel/data/SWAP.java.

It is part of test so we ignore for now.