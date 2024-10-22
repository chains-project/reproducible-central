### There seems to be problem with enums.

```diff
         JavaVersion.JAVA9 = (JavaVersion)new JavaVersion.Types$JavaVersion$4("JAVA9", 3);
-        JavaVersion.$VALUES = $values();
+        JavaVersion.$VALUES = new JavaVersion[] { JavaVersion.JAVA6, JavaVersion.JAVA7, JavaVersion.JAVA8, JavaVersion.JAVA9 };
         if (AnnotatedElement.class.isAssignableFrom(TypeVariable.class)) {
```

Same bytecode target but enum values are different. The compiler is implicitly creating `$values()` method.

```
-  private static com.google.common.reflect.Types$JavaVersion[] $values();
-    descriptor: ()[Lcom/google/common/reflect/Types$JavaVersion;
-    flags: (0x100a) ACC_PRIVATE, ACC_STATIC, ACC_SYNTHETIC
-    Code:
-      stack=4, locals=0, args_size=0
-         0: iconst_4
-         1: anewarray     #2                  // class com/google/common/reflect/Types$JavaVersion
-         4: dup
-         5: iconst_0
-         6: getstatic     #3                  // Field JAVA6:Lcom/google/common/reflect/Types$JavaVersion;
-         9: aastore
-        10: dup
-        11: iconst_1
-        12: getstatic     #4                  // Field JAVA7:Lcom/google/common/reflect/Types$JavaVersion;
-        15: aastore
-        16: dup
-        17: iconst_2
-        18: getstatic     #5                  // Field JAVA8:Lcom/google/common/reflect/Types$JavaVersion;
-        21: aastore
-        22: dup
-        23: iconst_3
-        24: getstatic     #6                  // Field JAVA9:Lcom/google/common/reflect/Types$JavaVersion;
-        27: aastore
         ...
```

See where `$values()` is called in `JavaVersion` https://github.com/google/guava/blob/10c64d93b767b5f6cea850dcb8ea8e65124cc1b9/guava/src/com/google/common/reflect/Types.java#L629.
Running `procyon` on `Types\$JavaVersion.class` reveals this.

### Second problem

```diff
@@ -1,13 +1,13 @@
 
 package com.google.common.cache;
 
 final class KeyIterator extends LocalCache.HashIterator<Object>
 {
     KeyIterator(final LocalCache this$0) {
-        super(this$0);
+        super(this.this$0 = this$0);
     }
     
     public Object next() {
         return this.nextEntry().getKey();
     }
 }
```

Synthetic field is being created.
```
+  final com.google.common.cache.LocalCache this$0;
+    descriptor: Lcom/google/common/cache/LocalCache;
+    flags: (0x1010) ACC_FINAL, ACC_SYNTHETIC
+
```
` 2: putfield      #1                  // Field this$0:Lcom/google/common/cache/LocalCache;` is also added as an OPCODE.
Bytecode target (JDK8) is the same but synthetic field is being created.

Synthetic field `this$0` is being created for the other two tests artifacts as well.