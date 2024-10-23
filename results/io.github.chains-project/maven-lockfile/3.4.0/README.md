It stores `Properties` object in a `Map` which is dependent upon the system.

Names of classes are different. They are dependent upon number.
For example,
```diff
-io.quarkus.smallrye.context.runtime.SmallRyeContextPropagationProvider_ProducerMethod_getAllThreadContext_0976a7142503aa8fe2c89bb7ef3f2613a1f1e921_Bean v49;
+io.quarkus.smallrye.context.runtime.SmallRyeContextPropagationProvider_ProducerMethod_getAllThreadContext_0976a7142503aa8fe2c89bb7ef3f2613a1f1e921_Bean v51;
```

It seems to create a lot of build time generated code that in non-reproducible.

```
@@ -131,7 +131,7 @@
 v15 = virtualinvoke v13.<org.kohsuke.github.Requester: org.kohsuke.github.GitHubRequest$Builder withPreview(org.kohsuke.github.internal.Previews)>(v14);
 v16 = <org.kohsuke.github.internal.Previews: org.kohsuke.github.internal.Previews FLASH>;
 v17 = virtualinvoke v15.<org.kohsuke.github.Requester: org.kohsuke.github.GitHubRequest$Builder withPreview(org.kohsuke.github.internal.Previews)>(v16);
-v18 = staticinvoke <org.kohsuke.github.GHRepository$lambda_listDeployments_0__3313: java.util.function.Consumer bootstrap$(org.kohsuke.github.GHRepository)>(v0);
+v18 = staticinvoke <org.kohsuke.github.GHRepository$lambda_listDeployments_0__3312: java.util.function.Consumer bootstrap$(org.kohsuke.github.GHRepository)>(v0);
 v19 = virtualinvoke v17.<org.kohsuke.github.Requester: org.kohsuke.github.PagedIterable toIterable(java.lang.Class,java.util.function.Consumer)>(class "[Lorg/kohsuke/github/GHDeployment;", v18);
 return v19;
 }
@@ -603,7 +603,7 @@
 v3 = virtualinvoke v0.<org.kohsuke.github.GHRepository: java.lang.String getApiTailUrl(java.lang.String)>("releases");
 v4 = newarray (java.lang.String)[0];
 v5 = virtualinvoke v2.<org.kohsuke.github.Requester: org.kohsuke.github.GitHubRequest$Builder withUrlPath(java.lang.String,java.lang.String[])>(v3, v4);
-v6 = staticinvoke <org.kohsuke.github.GHRepository$lambda_listReleases_1__3314: java.util.function.Consumer bootstrap$(org.kohsuke.github.GHRepository)>(v0);
+v6 = staticinvoke <org.kohsuke.github.GHRepository$lambda_listReleases_1__3313: java.util.function.Consumer bootstrap$(org.kohsuke.github.GHRepository)>(v0);
 v7 = virtualinvoke v5.<org.kohsuke.github.Requester: org.kohsuke.github.PagedIterable toIterable(java.lang.Class,java.util.function.Consumer)>(class "[Lorg/kohsuke/github/GHRelease;", v6);
 return v7;
 }
```
In rebuild, `org.kohsuke.github.GHRepository`, `3312` is added by `jNorm`. It is not present in the bytecode.

For some weird reason, the following exists.

```
         catch (final Throwable t8) {
-            ComponentsProvider.unableToLoadRemovedBeanType("org.jboss.logging.BasicLogger", t8);
+            ComponentsProvider.unableToLoadRemovedBeanType("java.lang.Boolean", t8);
```
